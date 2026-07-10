"""
Building opp_env projects as read-only Nix store packages ("@" version suffix),
and exporting the flakes that generate them.

Engine contract:

- build_store_package() generates a flake for the target project and its dependencies
  under <workspace>/.opp_env_workspace/packages/, then builds the target project's
  attribute with `nix build 'path:<flake_dir>#<attr>' --out-link <workspace>/<name>@`.
  That '@'-suffixed workspace symlink doubles as the Nix garbage-collection root, so
  deleting it exposes the package to the next `nix store gc`. The caller (opp_env.py)
  removes a stale link before the call and verifies the link and its target afterwards.

- target_project is one element of effective_project_descriptions; the caller
  guarantees that target_project and all of its transitive dependencies in that
  list have store_backed == True, that their download source is an immutable
  release tarball (download_url set, no git_url), and that the active option
  names are recorded in each description's active_options attribute.

- Source hashes are obtained trust-on-first-use via `nix store prefetch-file` and
  cached in the user-level cache directory (see get_cache_dir()); they are embedded
  into the generated flakes and never stored in the project database.

Generation notes:

- The command strings in the project database are written as Nix indented-string
  content: they may contain ${pkgs.foo} interpolations (resolved by Nix) and escape
  shell ${...} as ''${...}. They are spliced verbatim into the ''...'' phase strings
  of the generated derivations, exactly as they are spliced into the shellHook of
  the dev-shell flake by opp_env.py.

- The derivations unpack and build directly in $out: OMNeT++ source trees are not
  relocatable (configure bakes absolute paths into Makefile.inc and rpaths), so
  building in the final store path makes every baked path correct.

- The Nix build sandbox has no /usr/bin/env, so scripts executed during the build
  (opp_makemake etc.) get their shebangs store-patched at the end of the patch
  phase ("patchShebangs --build ."), not only in the fixup phase.
"""

import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys

_logger = logging.getLogger("opp_env")

NIX = "nix --extra-experimental-features nix-command --extra-experimental-features flakes"
DEFAULT_STDENV = "llvmPackages.stdenv"

# ---------------------------------------------------------------------------
# TOFU source-hash cache
# ---------------------------------------------------------------------------

def get_cache_dir():
    """User-level cache directory for TOFU source hashes and generated flake locks."""
    return os.path.join(os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"), "opp_env")

def _get_hash_cache_file():
    return os.path.join(get_cache_dir(), "source-hashes.json")

def _read_hash_cache():
    try:
        with open(_get_hash_cache_file()) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _write_hash_cache(cache):
    os.makedirs(get_cache_dir(), exist_ok=True)
    tmp_file = _get_hash_cache_file() + ".tmp"
    with open(tmp_file, "w") as f:
        json.dump(cache, f, indent=2)
    os.replace(tmp_file, _get_hash_cache_file())

def prefetch_source_hash(url, refresh=False):
    """
    Return the SRI hash ("sha256-...") of the file at url, using the user-level
    hash cache; on a cache miss (or refresh=True) download via
    `nix store prefetch-file` and record the result (trust-on-first-use).
    """
    cache = _read_hash_cache()
    if not refresh and url in cache:
        return cache[url]["hash"]
    _logger.info(f"Prefetching source archive to determine its hash: {url}")
    result = subprocess.run(f"{NIX} store prefetch-file --json {_shell_quote(url)}",
                            shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Prefetching '{url}' failed: {result.stderr.strip()}")
    hash = json.loads(result.stdout)["hash"]
    import datetime
    cache[url] = {"hash": hash, "prefetched": datetime.datetime.now().isoformat(timespec="seconds")}
    _write_hash_cache(cache)
    return hash

def _shell_quote(s):
    return "'" + s.replace("'", "'\\''") + "'"

# ---------------------------------------------------------------------------
# Command translation
# ---------------------------------------------------------------------------

# commands that would access the network inside the (network-less) build sandbox
_NETWORK_COMMAND_RE = re.compile(r"\b(curl|wget|git\s+clone|git\s+fetch|git\s+pull)\b")

# recognized rewritable fetch pattern: curl -L -sS -o <file> <url>
_CURL_TO_FILE_RE = re.compile(r"curl\s+(?:-L\s+|-sS\s+|--fail\s+)*-o\s+(\S+)\s+(\S+)")

def rewrite_curl_commands(commands, project_name):
    """
    Rewrite network fetches in patch/setenv/build commands into references to
    fixed-output fetches, so that the commands work inside the network-less Nix
    build sandbox. Returns (rewritten_commands, urls) where the rewritten commands
    contain "@FETCHED:<url>@" placeholders that the flake generator replaces with
    ${fetchurl {...}} store paths. Any unrecognized network command is a hard error.
    """
    rewritten = []
    urls = []
    for command in commands:
        match = _CURL_TO_FILE_RE.search(command)
        if match:
            file, url = match.groups()
            command = command[:match.start()] + f"cp @FETCHED:{url}@ {file}" + command[match.end():]
            urls.append(url)
        elif _NETWORK_COMMAND_RE.search(command):
            raise Exception(f"Project '{project_name}': cannot build as a Nix store package, the command "
                            f"'{command.strip()}' would access the network inside the Nix build sandbox "
                            f"(only 'curl -L -sS -o <file> <url>' style fetches can be rewritten automatically)")
        rewritten.append(command)
    return rewritten, urls

def _substitute_fetched_urls(text, url_fetch_vars):
    for url, var in url_fetch_vars.items():
        text = text.replace(f"@FETCHED:{url}@", "${" + var + "}")
    return text

# ---------------------------------------------------------------------------
# Derivation / flake generation
# ---------------------------------------------------------------------------

def _indent(text, spaces):
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in text.splitlines())

def _join_commands(commands):
    return "\n".join(c for c in commands if c and c.strip())

def _get_dependencies_among(project, projects):
    """Direct+transitive dependencies of project among the given project descriptions, dependencies first."""
    result = []
    todo = [project]
    while todo:
        p = todo.pop()
        for dep in projects:
            if dep.name in p.required_projects and dep is not p and dep not in result:
                result.append(dep)
                todo.append(dep)
    # dependencies first (projects is sorted dependent-first by the engine)
    return list(reversed(result))

def _root_var(project):
    return f"{project.name.upper()}_ROOT"

def generate_project_derivation(project, dep_projects, build_modes, hashes, dep_refs, opp_env_support_ref="opp_env_support"):
    """
    Generate the Nix text of one mkDerivation for the given (option-activated) project
    description. dep_projects are its store-backed dependencies (dependencies first);
    dep_refs maps dependency name -> Nix expression referring to its derivation
    (e.g. "omnetpp" for a let-bound sibling, or "omnetpp.packages.${system}.omnetpp"
    for a flake input). hashes maps url -> SRI hash.
    """
    stdenv = project.stdenv or DEFAULT_STDENV
    modes = " ".join(build_modes)

    patch_commands, patch_urls = rewrite_curl_commands(project.patch_commands, project.get_full_name())
    setenv_commands, setenv_urls = rewrite_curl_commands(project.setenv_commands, project.get_full_name())
    build_commands, build_urls = rewrite_curl_commands(project.build_commands, project.get_full_name())

    # let-bound fetchurl variables for URLs fetched by rewritten commands
    url_fetch_vars = {}
    fetch_bindings = []
    for i, url in enumerate(dict.fromkeys(patch_urls + setenv_urls + build_urls)):
        var = f"{project.name}_fetch_{i}"
        url_fetch_vars[url] = var
        fetch_bindings.append(f'{var} = pkgs.fetchurl {{ url = "{url}"; hash = "{hashes[url]}"; }};')

    dep_env_exports = []
    dep_setenv_replays = []
    for dep in dep_projects:
        ref = dep_refs[dep.name]
        dep_env_exports.append(f'export {_root_var(dep)}=${{{ref}}}')
        dep_env_exports.append(f'export {dep.name.upper()}_VERSION="{dep.version}"')
        if dep.setenv_commands:
            dep_setenv_replays.append(f'pushd ${{{ref}}} > /dev/null')
            dep_setenv_replays.append(_join_commands(dep.setenv_commands))
            dep_setenv_replays.append('popd > /dev/null')

    patch_url_command = ""
    if project.patch_url:
        patch_url_command = f'git apply --whitespace=nowarn ${{pkgs.fetchurl {{ url = "{project.patch_url}"; hash = "{hashes[project.patch_url]}"; }}}}'

    # mirror the dev shell semantics (run_commands_with_projects): the build environment is
    # the union of the project's and all its dependencies' nix packages -- e.g. inet's build
    # invokes 'ccache clang++' baked into omnetpp's Makefile.inc, and ccache comes from
    # omnetpp's package list
    packages = list(project.nix_packages)
    for dep in dep_projects:
        packages += [pkg for pkg in dep.nix_packages if pkg not in packages]
    build_inputs = " ".join(packages + [dep_refs[dep.name] for dep in dep_projects])

    check_phase = ""
    if project.smoke_test_commands:
        check_phase = f"""
        doCheck = false;  # opt-in: smoke tests roughly double the build time
        checkPhase = ''
          cd $out
{_indent(_substitute_fetched_urls(_join_commands(project.smoke_test_commands), url_fetch_vars), 10)}
        '';
"""

    derivation = f"""{project.name} = pkgs.{stdenv}.mkDerivation rec {{
      pname = "{project.name}";
      version = "{project.version}";
      src = pkgs.fetchurl {{
        url = "{project.download_url}";
        hash = "{hashes[project.download_url]}";
      }};
      buildInputs = with pkgs; [ {build_inputs} ];
      # the same baseline tools the opp_env dev shell provides (opp_env.py tools_nix_packages),
      # minus the network tools -- project scripts (e.g. inet_version) invoke them from PATH
      nativeBuildInputs = with pkgs; [ gitMinimal which gnused gnutar gzip perl findutils coreutils ];
      strictDeps = false;              # buildInputs must be on PATH, like in the opp_env dev shell
      hardeningDisable = [ "all" ];
      enableParallelBuilding = true;   # provides $NIX_BUILD_CORES
      dontStrip = true;                # stripping would gut the debug-mode libraries
      dontWrapQtApps = true;           # the qtbase setup hook would abort the fixup phase otherwise
      dontConfigure = true;            # configuring is driven by the project's build commands
      dontCheckForBrokenSymlinks = true; # release tarballs may ship dangling doc symlinks (e.g. inet showcases)

      preHook = ''
        set +u                         # the project's setenv scripts assume unset variables are tolerated
        export HOME=$TMPDIR
        export OPP_ENV_VERSION=nix     # constant (not the real opp_env version), keeps the derivation stable
        export OPP_ENV_DIR=${{{opp_env_support_ref}}}
        export IN_NIX_SHELL=1          # 'nix build' sandboxes do not set this, but nix-gated database commands rely on it
        export LOCAL_OPERATION=
        export CCACHE_DISABLE=1
        export OPP_ENV_STORE_BUILD=1   # gates out database commands that assume a writable workspace layout
        export BUILD_MODES="{modes}"
        export {_root_var(project)}=$out
        export {project.name.upper()}_VERSION="{project.version}"
{_indent(_join_commands(dep_env_exports), 8)}
      '';

      # unpack and build directly in $out: the tree is not relocatable, paths baked in
      # by configure must be the final store path
      unpackPhase = ''
        mkdir -p $out && cd $out
        tar --strip-components=1 -xzf $src
      '';

      patchPhase = ''
        cd $out
{_indent(patch_url_command, 8)}
{_indent(_substitute_fetched_urls(_join_commands(patch_commands), url_fetch_vars), 8)}
        # the sandbox has no /usr/bin/env: shebangs of scripts executed during the
        # build (opp_makemake etc.) must be store-patched before the build phase
        patchShebangs --build . > /dev/null 2>&1 || true
      '';

      buildPhase = ''
{_indent(_join_commands(dep_setenv_replays), 8)}
        cd $out
{_indent(_substitute_fetched_urls(_join_commands(setenv_commands), url_fetch_vars), 8)}
        for BUILD_MODE in {modes}; do
          export BUILD_MODE
{_indent(_substitute_fetched_urls(_join_commands(build_commands), url_fetch_vars), 10)}
        done
      '';
{check_phase}
      installPhase = ''
        cd $out
        rm -f tar.log
        rm -rf .venv
        # object files of an opp_makemake build tree are dead weight in a read-only package:
        # the makefiles hardlink or copy the finished libraries and executables into
        # lib/, bin/ and src/. The mode subdirectory test keeps this from mistaking a
        # source folder that merely happens to be named 'out' for a build output tree.
        for outdir in $(find $out -type d -name out); do
          if [ -n "$(find "$outdir" -maxdepth 1 -type d \\( -name '*-debug' -o -name '*-release' \\) -print -quit)" ]; then
            echo "pruning build output tree ''${{outdir#$out/}}"
            rm -rf "$outdir"
          fi
        done
      '';
    }};"""

    return derivation, fetch_bindings

def collect_source_urls(project):
    """All URLs the project's derivation needs fixed-output fetches for."""
    urls = [project.download_url]
    if project.patch_url:
        urls.append(project.patch_url)
    for commands in [project.patch_commands, project.setenv_commands, project.build_commands]:
        _, fetch_urls = rewrite_curl_commands(commands, project.get_full_name())
        urls += fetch_urls
    return [url for url in dict.fromkeys(urls) if url]

def prefetch_hashes_for(projects, refresh=False):
    hashes = {}
    for project in projects:
        for url in collect_source_urls(project):
            hashes[url] = prefetch_source_hash(url, refresh=refresh)
    return hashes

def generate_packages_flake(store_projects, nixos, build_modes, hashes, description="opp_env-generated Nix packages"):
    """
    Generate a self-contained flake with one let-bound derivation per store project
    (dependencies referenced as let-bound siblings), exposing all of them under
    packages.<system>. store_projects must be ordered dependencies-first.
    """
    derivations = []
    fetch_bindings = []
    for project in store_projects:
        deps = _get_dependencies_among(project, store_projects)
        dep_refs = {dep.name: dep.name for dep in deps}  # let-bound siblings
        derivation, bindings = generate_project_derivation(project, deps, build_modes, hashes, dep_refs)
        fetch_bindings += bindings
        derivations.append(derivation)

    package_names = [p.name for p in store_projects]
    fetch_bindings_text = _indent("\n".join(fetch_bindings), 4) + "\n" if fetch_bindings else ""
    derivations_text = "\n\n    ".join(derivations)

    return f"""# Generated by opp_env. This flake builds {', '.join(p.get_full_name() for p in store_projects)}
# as Nix packages. Do not edit manually; regenerate with opp_env.
{{
  description = "{description}";
  inputs = {{
    nixpkgs.url = "nixpkgs/{nixos}";
    flake-utils.url = "github:numtide/flake-utils";
  }};
  outputs = {{ self, nixpkgs, flake-utils }}: flake-utils.lib.eachDefaultSystem (system:
    let
      # allow python2 to be installed despite being EOL and having known vulnerabilities
      overlay = final: prev: (if prev ? python2 then {{
        python2 = prev.python2.overrideAttrs (oldAttrs: {{
          meta = oldAttrs.meta // {{ knownVulnerabilities = []; }};
        }});
      }} else {{ }});
      pkgs = import nixpkgs {{ inherit system; overlays = [ overlay ]; }};
      opp_env_support = ./opp_env_support;
{fetch_bindings_text}
    {derivations_text}
    in {{
      packages = {{
        inherit {' '.join(package_names)};
        default = {store_projects[-1].name};
      }};
    }});
}}
"""

# ---------------------------------------------------------------------------
# Flake directory preparation and building
# ---------------------------------------------------------------------------

def _get_templates_dir():
    return os.path.join(os.path.dirname(__file__), "templates")

def prepare_flake_dir(flake_dir, flake_text, nixos):
    """Write flake.nix, bundle the opp_env support files, and seed/generate flake.lock."""
    os.makedirs(flake_dir, exist_ok=True)
    with open(os.path.join(flake_dir, "flake.nix"), "w") as f:
        f.write(flake_text)

    # bundle the support files referenced via $OPP_ENV_DIR, so the flake is self-sufficient
    support_dir = os.path.join(flake_dir, "opp_env_support")
    metadata_template_dir = os.path.join(_get_templates_dir(), "metadata")
    os.makedirs(os.path.join(support_dir, "templates"), exist_ok=True)
    if os.path.isdir(metadata_template_dir):
        shutil.copytree(metadata_template_dir, os.path.join(support_dir, "templates", "metadata"), dirs_exist_ok=True)
    else:
        # the path must exist for the flake to evaluate
        with open(os.path.join(support_dir, "templates", ".keep"), "w") as f:
            f.write("")

    _seed_or_generate_flake_lock(flake_dir, nixos)

def _seed_or_generate_flake_lock(flake_dir, nixos):
    lock_file = os.path.join(flake_dir, "flake.lock")
    if os.path.isfile(lock_file):
        return
    template_lock = os.path.join(_get_templates_dir(), "workspace", nixos, "flake.lock")
    cached_lock = os.path.join(get_cache_dir(), "flake-locks", f"{nixos}.lock")
    if os.path.isfile(template_lock):
        shutil.copy(template_lock, lock_file)
    elif os.path.isfile(cached_lock):
        shutil.copy(cached_lock, lock_file)
    else:
        _logger.warning(f"No pinned flake.lock template for nixpkgs {nixos}, generating one (requires network access). "
                        f"Consider adding templates/workspace/{nixos}/flake.lock to opp_env.")
        result = subprocess.run(f"cd {_shell_quote(flake_dir)} && {NIX} flake lock 'path:.'", shell=True)
        if result.returncode != 0 or not os.path.isfile(lock_file):
            raise Exception(f"Generating flake.lock for nixpkgs {nixos} failed")
        os.makedirs(os.path.dirname(cached_lock), exist_ok=True)
        shutil.copy(lock_file, cached_lock)

def compute_package_identity(flake_text):
    """Short identity hash for the generated flake, used for the flake directory name."""
    return hashlib.sha256(flake_text.encode()).hexdigest()[:12]

def _generate_flake_for_target(workspace, effective_project_descriptions, target_project, build_modes, refresh_hashes=False):
    store_projects = [p for p in effective_project_descriptions if p.store_backed]
    deps = _get_dependencies_among(target_project, store_projects)
    flake_projects = deps + [target_project]  # dependencies first
    hashes = prefetch_hashes_for(flake_projects, refresh=refresh_hashes)
    nixos = _get_unique_nixos(flake_projects, workspace)
    flake_text = generate_packages_flake(flake_projects, nixos, build_modes, hashes)
    return flake_text, nixos

def compute_flake_identity(workspace, effective_project_descriptions, target_project, build_modes, refresh_hashes=False):
    """
    Identity of the flake that would be generated for the target project -- covers
    everything that determines the derivation (sources, options, build modes, nixos,
    and the generator itself), so that e.g. generator changes in a new opp_env
    version correctly trigger a rebuild instead of a false "up to date".
    """
    flake_text, _ = _generate_flake_for_target(workspace, effective_project_descriptions, target_project, build_modes, refresh_hashes=refresh_hashes)
    return compute_package_identity(flake_text)

def build_store_package(workspace, effective_project_descriptions, target_project, build_modes, refresh_hashes=False):
    """
    Build target_project as a Nix derivation into /nix/store, creating the GC-rooting
    out-link symlink at the project's '@'-suffixed workspace directory.
    Returns the resulting /nix/store path. Raises on failure.
    """
    flake_text, nixos = _generate_flake_for_target(workspace, effective_project_descriptions, target_project, build_modes, refresh_hashes=refresh_hashes)

    identity = compute_package_identity(flake_text)
    flake_dir = os.path.join(workspace.get_workspace_admin_directory(), "packages",
                             f"{target_project.get_full_folder_name()}-{identity}")
    prepare_flake_dir(flake_dir, flake_text, nixos)

    out_link = workspace.get_store_link_directory(target_project)
    _logger.info(f"Building Nix derivation for {target_project.get_full_name()} (flake: {flake_dir})")
    command = f"{NIX} build 'path:{flake_dir}#{target_project.name}' --out-link {_shell_quote(out_link)} --print-out-paths -L"
    _logger.debug(f"Running: {command}")
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise Exception(f"Building the Nix store package for {target_project.get_full_name()} failed. "
                        f"If the error above is a fixed-output derivation hash mismatch, the source archive has likely "
                        f"changed upstream; retry with --refresh-source-hashes.")
    store_path = result.stdout.strip().splitlines()[-1]
    for problem in verify_store_package(store_path):
        _logger.warning(problem)
    return store_path

def _get_unique_nixos(projects, workspace=None):
    values = {p.nixos for p in projects if p.nixos}
    if len(values) > 1:
        raise Exception(f"The projects disagree on the choice of nixos version: {sorted(values)}")
    if values:
        return values.pop()
    return workspace.default_nixos if workspace else "22.11"

# ---------------------------------------------------------------------------
# Flake export
# ---------------------------------------------------------------------------

def _generate_dev_shell(store_projects, dep_refs):
    """
    Generate a devShells.default that mirrors the opp_env dev shell for the exported
    packages: all runtime nix packages + the package derivations, with <NAME>_ROOT
    exports, shell hook commands and setenv replay -- usable without opp_env.
    """
    nix_packages = []
    for p in store_projects:
        nix_packages += [pkg for pkg in p.nix_packages if pkg not in nix_packages]
    hook_lines = ['export OPP_ENV_VERSION=nix']
    for p in store_projects:
        hook_lines.append(f'export {_root_var(p)}=${{{dep_refs[p.name]}}}')
        hook_lines.append(f'export {p.name.upper()}_VERSION="{p.version}"')
    for p in store_projects:
        hook_lines += p.shell_hook_commands
    for p in store_projects:  # dependencies first, like run_commands_with_projects
        if p.setenv_commands:
            hook_lines.append(f'pushd ${{{dep_refs[p.name]}}} > /dev/null')
            hook_lines += p.setenv_commands
            hook_lines.append('popd > /dev/null')
    packages = " ".join(nix_packages + [dep_refs[p.name] for p in store_projects] + ["bashInteractive"])
    return f"""devShells.default = pkgs.mkShell {{
        buildInputs = with pkgs; [ {packages} ];
        shellHook = ''
{_indent(_join_commands(hook_lines), 10)}
        '';
      }};"""

def _generate_split_flake(project, dep_projects, nixos, build_modes, hashes, output_dir, include_dev_shell=False, all_projects=None):
    """
    Generate a flake for one project that references its (transitive) store
    dependencies as flake inputs named after the projects, with 'path:' URLs
    pointing at the sibling export directories. The URLs are absolute: relative
    'path:../...' inputs resolve against /nix/store after the flake is copied
    there for evaluation (see https://github.com/NixOS/nix/issues/9339), so they
    cannot be used. Edit the URLs (e.g. to 'github:' ones) when publishing.
    """
    dep_inputs = []
    for dep in dep_projects:
        dep_flake_dir = os.path.join(output_dir, dep.get_full_folder_name())
        dep_inputs.append(f'{dep.name}.url = "path:{dep_flake_dir}";  # edit when publishing or moving the directory')
        dep_inputs.append(f'{dep.name}.inputs.nixpkgs.follows = "nixpkgs";  # keep a single nixpkgs pin (ABI!)')
    dep_input_args = "".join(f", {dep.name}" for dep in dep_projects)
    dep_refs = {dep.name: f"{dep.name}.packages.${{system}}.{dep.name}" for dep in dep_projects}

    derivation, fetch_bindings = generate_project_derivation(project, dep_projects, build_modes, hashes, dep_refs)
    fetch_bindings_text = _indent("\n".join(fetch_bindings), 6) + "\n" if fetch_bindings else ""

    dev_shell = ""
    if include_dev_shell:
        shell_projects = (all_projects or dep_projects + [project])
        shell_refs = dict(dep_refs)
        shell_refs[project.name] = project.name
        dev_shell = "\n      " + _generate_dev_shell(shell_projects, shell_refs)

    return f"""# Generated by opp_env. This flake builds {project.get_full_name()} as a Nix package.
# Dependencies are referenced as flake inputs with 'path:' URLs pointing at sibling
# directories; edit them (e.g. to 'github:' URLs) when publishing the flakes separately.
{{
  description = "{project.get_full_name()} (generated by opp_env)";
  inputs = {{
    nixpkgs.url = "nixpkgs/{nixos}";
    flake-utils.url = "github:numtide/flake-utils";
{_indent(_join_commands(dep_inputs), 4)}
  }};
  outputs = {{ self, nixpkgs, flake-utils{dep_input_args} }}: flake-utils.lib.eachDefaultSystem (system:
    let
      # allow python2 to be installed despite being EOL and having known vulnerabilities
      overlay = final: prev: (if prev ? python2 then {{
        python2 = prev.python2.overrideAttrs (oldAttrs: {{
          meta = oldAttrs.meta // {{ knownVulnerabilities = []; }};
        }});
      }} else {{ }});
      pkgs = import nixpkgs {{ inherit system; overlays = [ overlay ]; }};
      opp_env_support = ./opp_env_support;
{fetch_bindings_text}
      {derivation}
    in {{
      packages = {{
        inherit {project.name};
        default = {project.name};
      }};{dev_shell}
    }});
}}
"""

_PUSH_TO_CACHIX_SCRIPT = """#!/usr/bin/env bash
#
# Builds the package(s) of this flake and pushes their full runtime closure to a
# cachix binary cache. Requires cachix (https://docs.cachix.org) and a configured
# auth token ('cachix authtoken ...').
#
# Usage: ./push-to-cachix.sh <cache-name> [attribute]
#
set -euo pipefail
CACHE="${1:?usage: push-to-cachix.sh <cache-name> [attribute]}"
ATTR="${2:-default}"
nix --extra-experimental-features 'nix-command flakes' build "path:.#$ATTR" --print-out-paths --no-link \\
    | xargs nix --extra-experimental-features nix-command path-info -r \\
    | cachix push "$CACHE"
echo "Done. Consumers can enable the cache with: cachix use $CACHE"
"""

def _write_export_readme(dir, store_projects, bundle):
    layout = "a single self-contained flake" if bundle else "one flake directory per project"
    with open(os.path.join(dir, "README.md"), "w") as f:
        f.write(f"""# Nix flake export of {', '.join(p.get_full_name() for p in store_projects)}

This directory was generated by `opp_env export-flake` and contains {layout}
that builds the project(s) as Nix packages, independently of opp_env.

## Building

    nix --extra-experimental-features 'nix-command flakes' build .#{store_projects[-1].name}

The result symlink points to the read-only package in /nix/store.

## Development shell

    nix --extra-experimental-features 'nix-command flakes' develop

opens a shell with the packages and their runtime dependencies on the environment
(<NAME>_ROOT variables set, setenv scripts sourced), similar to `opp_env shell`.

## Publishing to a binary cache

Use `./push-to-cachix.sh <cache-name>` to push the built closure to a cachix
binary cache, so that consumers can download the prebuilt package instead of
compiling it. Consumers enable the cache with `cachix use <cache-name>`.
Note that binary caches are per-system (e.g. x86_64-linux).

## Notes

- The flakes pin nixpkgs to the same release the opp_env project database uses;
  do not change the pin, the builds are only tested against it.
- Split-mode dependency inputs use absolute 'path:' URLs (relative ones do not
  survive Nix's copy-to-store evaluation); when publishing the flakes to separate
  repositories, or after moving this directory, edit them to 'github:...' style
  URLs (and re-run 'nix flake lock').
""")

def _write_push_script(dir):
    script_file = os.path.join(dir, "push-to-cachix.sh")
    with open(script_file, "w") as f:
        f.write(_PUSH_TO_CACHIX_SCRIPT)
    os.chmod(script_file, 0o755)

def export_flake(effective_project_descriptions, target_project, build_modes, output_dir, bundle=False, refresh_hashes=False):
    """
    Write the flake(s) that build target_project and its dependencies into output_dir.
    Default layout is split: one flake directory per project, referencing each other
    via 'path:' flake inputs. With bundle=True, a single self-contained flake is
    written with all dependency derivations inlined.
    """
    store_projects = [p for p in effective_project_descriptions if p.store_backed]
    deps = _get_dependencies_among(target_project, store_projects)
    flake_projects = deps + [target_project]  # dependencies first

    hashes = prefetch_hashes_for(flake_projects, refresh=refresh_hashes)
    nixos = _get_unique_nixos(flake_projects)
    os.makedirs(output_dir, exist_ok=True)

    if bundle:
        flake_text = generate_packages_flake(flake_projects, nixos, build_modes, hashes)
        # bundle flake gets a devShell too: splice it in next to the packages output
        dep_refs = {p.name: p.name for p in flake_projects}
        dev_shell = _generate_dev_shell(flake_projects, dep_refs)
        flake_text = flake_text.replace("    in {\n      packages = {", "    in {\n      " + dev_shell + "\n      packages = {")
        prepare_flake_dir(output_dir, flake_text, nixos)
        _write_export_readme(output_dir, flake_projects, bundle=True)
        _write_push_script(output_dir)
        _logger.info(f"Exported self-contained flake to {output_dir}")
    else:
        for i, project in enumerate(flake_projects):
            project_deps = _get_dependencies_among(project, flake_projects)
            is_target = project is target_project
            flake_dir = os.path.join(output_dir, project.get_full_folder_name())
            flake_text = _generate_split_flake(project, project_deps, nixos, build_modes, hashes, output_dir,
                                               include_dev_shell=is_target, all_projects=flake_projects if is_target else None)
            prepare_flake_dir(flake_dir, flake_text, nixos)
            _write_push_script(flake_dir)
            _logger.info(f"Exported flake for {project.get_full_name()} to {flake_dir}")
        _write_export_readme(output_dir, flake_projects, bundle=False)
        # lock the flakes dependencies-first, so that 'path:' inputs resolve;
        # note: must be run in the directory WITHOUT a 'path:' flake ref, otherwise the
        # flake is copied to the store first and the relative inputs resolve against /nix/store
        for project in flake_projects:
            flake_dir = os.path.join(output_dir, project.get_full_folder_name())
            result = subprocess.run(f"cd {_shell_quote(flake_dir)} && {NIX} flake lock", shell=True)
            if result.returncode != 0:
                _logger.warning(f"Locking the flake of {project.get_full_name()} failed; "
                                f"run 'nix flake lock' in {flake_dir} manually")

def verify_store_package(store_path, quiet=False):
    """
    Run purity/binary-cache-readiness checks on a built store package.
    Returns a list of problem description strings (empty means all checks passed).
    """
    problems = []

    result = subprocess.run(f"{NIX} path-info --json {_shell_quote(store_path)}", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        problems.append(f"'nix path-info' failed for {store_path}: {result.stderr.strip()}")
    result = subprocess.run(f"{NIX} path-info -rS {_shell_quote(store_path)} | tail -1", shell=True, capture_output=True, text=True)
    if result.returncode == 0 and not quiet:
        parts = result.stdout.split()
        if len(parts) >= 2 and parts[-1].isdigit():
            _logger.info(f"Store package closure size: {int(parts[-1]) / 1e9:.2f} GB")

    result = subprocess.run(f"{NIX} store verify --no-trust {_shell_quote(store_path)}", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        problems.append(f"'nix store verify' reported problems: {result.stderr.strip()}")

    # scan text files for absolute paths leaking from the build machine
    result = subprocess.run(f"grep -RIl '/home/' {_shell_quote(store_path)} 2>/dev/null | head -5", shell=True, capture_output=True, text=True)
    leaks = [l for l in result.stdout.splitlines() if l.strip()]
    if leaks:
        problems.append(f"References to '/home/' found in: {', '.join(leaks)} -- the package may not be reproducible/publishable")

    return problems
