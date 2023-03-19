#!/usr/bin/env python3

import argparse
import copy
import itertools
import json
import logging
import os
import shlex
import subprocess
import sys

# Import omnetpp and inet versions.
# Do it conditionally because we may be running either as a module with __package__ == "opp_env"
# or we may be running as the __main__ module (when opp_env was started by directly invoking opp_env.py
# or python -m opp_env)
try:
    from opp_env.omnetpp_versions import get_all_omnetpp_versions
except ImportError:
    from omnetpp_versions import get_all_omnetpp_versions

try:
    from opp_env.inet_versions import get_all_inet_versions
except ImportError:
    from inet_versions import get_all_inet_versions

_logger = logging.getLogger(__file__)

def repr(object):
    return f"{object.__class__.__name__}({', '.join([f'{prop}={value}' for prop, value in object.__dict__.items()])})"

COLOR_GRAY = "\033[38;20m"
COLOR_RED = "\033[1;31m"
COLOR_YELLOW = "\033[1;33m"
COLOR_CYAN = "\033[0;36m"
COLOR_GREEN = "\033[0;32m"
COLOR_RESET = "\033[0;0m"

def cyan(x):
    return COLOR_CYAN + str(x) + COLOR_RESET
def green(x):
    return COLOR_GREEN + str(x) + COLOR_RESET
def red(x):
    return COLOR_RED + str(x) + COLOR_RESET

class ColoredLoggingFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: COLOR_GREEN,
        logging.INFO: COLOR_GREEN,
        logging.WARNING: COLOR_YELLOW,
        logging.ERROR: COLOR_RED,
        logging.CRITICAL: COLOR_RED
    }

    def format(self, record):
        format = self.COLORS.get(record.levelno) + "%(levelname)s " + COLOR_RESET + "%(message)s"
        formatter = logging.Formatter(format)
        return formatter.format(record)

def parse_arguments():
    description = "Sets up the development environment for OMNeT++ projects"
    parser = argparse.ArgumentParser(prog="opp_env", description=description)
    parser.add_argument("-q", "--quiet", action=argparse.BooleanOptionalAction, default=False, help="Suppress the standard output of executed commands")
    parser.add_argument("-l", "--log-level", choices=["ERROR", "WARN", "INFO", "DEBUG"], default="INFO", help="Verbose output mode")
    parser.add_argument("-w", "--workspace", dest="workspace_directory", help="Workspace directory")
    parser.add_argument("-x", "--handle-exception", action=argparse.BooleanOptionalAction, default=True, help="Don't print exception stacktrace")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", required=True)

    parser_list = subparsers.add_parser("list", help="Lists all available projects")
    parser_list.add_argument("-m", "--mode", dest="list_mode", choices=["flat", "grouped", "names"], default="grouped", help="Listing mode")

    parser_describe = subparsers.add_parser("describe", help="Describes the specified project")
    parser_describe.add_argument("project", help="The project name")

    parser_download = subparsers.add_parser("download", help="Downloads the specified projects into the workspace")
    parser_download.add_argument("projects", nargs="+", help="List of projects")

    parser_configure = subparsers.add_parser("configure", help="Configures the specified projects for their environment")
    parser_configure.add_argument("projects", nargs="+", help="List of projects")
    parser_configure.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading them")

    parser_build = subparsers.add_parser("build", help="Builds the specified projects in their environment")
    parser_build.add_argument("projects", nargs="+", help="List of projects")
    parser_build.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=True, help="Run in isolated environment from the host operating system")
    parser_build.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading and configuring them")

    parser_clean = subparsers.add_parser("clean", help="Cleans the specified projects in their environment")
    parser_clean.add_argument("projects", nargs="+", help="List of projects")
    parser_clean.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=True, help="Run in isolated environment from the host operating system")
    parser_clean.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading and configuring them")

    parser_shell = subparsers.add_parser("shell", help="Runs a shell in the environment of the specified projects")
    parser_shell.add_argument("projects", nargs="+", help="List of projects")
    parser_shell.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=True, help="Run in isolated environment from the host operating system")
    parser_shell.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading, configuring, and building them")

    parser_run = subparsers.add_parser("run", help="Runs a command in the environment of the specified projects")
    parser_run.add_argument("projects", nargs="+", help="List of projects")
    parser_run.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=True, help="Run in isolated environment from the host operating system")
    parser_run.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading, configuring, and building them")
    parser_run.add_argument("-c", "--command", help="Specifies the command that is run in the environment")

    return parser.parse_args(sys.argv[1:])

def process_arguments():
    args = parse_arguments()
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredLoggingFormatter())
    _logger.setLevel(args.log_level)
    _logger.handlers = []
    _logger.addHandler(handler)
    kwargs = {k: v for k, v in vars(args).items() if v is not None}
    if "workspace_directory" in kwargs:
        kwargs["workspace_directory"] = os.path.abspath(kwargs["workspace_directory"])
    return kwargs

def run_command(command, quiet=False, check_exitcode=True, tweak_env_for_nix=True, extra_env_vars=None, **kwargs):
    _logger.debug(f"Running command: {command}")

    env = dict(os.environ)

    if tweak_env_for_nix:
        # This is a workaround for an error message that is printed multiple times when the "shell" command starts e.g. with Ubuntu 22.04 Unity desktop:
        # ERROR: ld.so: object 'libgtk3-nocsd.so.0' from LD_PRELOAD cannot be preloaded (cannot open shared object file): ignored.
        # The reason is that under NIX, the lib's directory is not in the default linker path. Workaround: use full path for lib.
        libname = "libgtk3-nocsd.so.0"
        libdir = "/usr/lib/x86_64-linux-gnu/"
        if "LD_PRELOAD" in env and libname in env["LD_PRELOAD"].split(" ") and os.path.isfile(libdir+libname):
            env["LD_PRELOAD"] = env["LD_PRELOAD"].replace(libname, libdir+libname)

        # This is a workaround for a warning message printed by Perl:
        # perl: warning: Setting locale failed.
        # perl: warning: Please check that your locale settings:
        #     LANGUAGE = (unset),
        #     LC_ALL = (unset),
        #     ...
        #     LANG = "en_US.UTF-8"
        #     are supported and installed on your system.
        # perl: warning: Falling back to the standard locale ("C").
        env["LC_ALL"] = "C.utf8"

    if extra_env_vars:
        env.update(extra_env_vars)

    result = subprocess.run(["bash", "-c", command],
                            env=env,
                            stdout=subprocess.DEVNULL if quiet else sys.stdout,
                            stderr=subprocess.STDOUT if quiet else sys.stderr)
    if check_exitcode:
        assert(result.returncode==0)
    return result

class Workspace:
    def __init__(self, root_directory):
        assert(os.path.isabs(root_directory))
        self.root_directory = root_directory
        opp_env_directory = os.path.join(self.root_directory, ".opp_env")
        if not os.path.exists(opp_env_directory):
            os.mkdir(opp_env_directory)

    def get_project_root_directory(self, project_description):
        return os.path.join(self.root_directory, project_description.get_full_folder_name())

    def print_project_state(self, project_description):
        _logger.info(f"Project {project_description.get_full_name(colored=True)} is {self.check_project_state(project_description)}")

    def is_project_downloaded(self, project_description):
        return os.path.exists(self.get_project_root_directory(project_description))

    def download_project(self, project_description, **kwargs):
        _logger.info(f"Downloading project {cyan(project_description.get_full_name())} in workspace {cyan(self.root_directory)}")
        project_dir = self.root_directory + "/" + project_description.get_full_name()
        if os.path.exists(project_dir):
            raise Exception("f{project_dir} already exists")
        if project_description.download_command:
            run_command(f"cd {self.root_directory} && {project_description.download_command}", **kwargs)
        elif project_description.download_url:
            # TODO it seems to be science fiction to download using piping into tar, with progress bar but no final success report, HOWEVER showing errors from failed download such as 404 BUT not the consequence errors from "tar"
            os.makedirs(project_dir)
            run_command(f"cd {project_dir} && wget -O - -q -nv --show-progress {project_description.download_url} | tar --strip-components=1 -xzf -", **kwargs)
        else:
            raise Exception("no download_url or download_command in project description")
        if not os.path.exists(project_dir):
            raise Exception(f"download process did not create {project_dir}")

        # TODO run patch_command

        self.mark_project_state(project_description)

    def configure_project(self, project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs):
        _logger.info(f"Configuring project {cyan(project_description.get_full_name())} in workspace {cyan(self.root_directory)}")
        nix_develop(self.root_directory, effective_project_descriptions, external_nix_packages, f"{' && '.join(project_setenv_commands)} && cd {self.get_project_root_directory(project_description)} && {project_description.configure_command}", **kwargs)

    def build_project(self, project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs):
        _logger.info(f"Building project {cyan(project_description.get_full_name())} in workspace {cyan(self.root_directory)}")
        nix_develop(self.root_directory, effective_project_descriptions, external_nix_packages, f"{' && '.join(project_setenv_commands)} && cd {self.get_project_root_directory(project_description)} && {project_description.build_command}", **kwargs)

    def clean_project(self, project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs):
        _logger.info(f"Cleaning project {cyan(project_description.get_full_name())} in workspace {cyan(self.root_directory)}")
        nix_develop(self.root_directory, effective_project_descriptions, external_nix_packages, f"{' && '.join(project_setenv_commands)} && cd {self.get_project_root_directory(project_description)} && {project_description.clean_command}", **kwargs)

    def mark_project_state(self, project_description):
        file_list_file_name = os.path.join(self.root_directory, ".opp_env/" + project_description.get_full_folder_name() + ".md5")
        run_command(f"find {self.get_project_root_directory(project_description)} -type f -print0 | xargs -0 md5sum > {file_list_file_name}")

    def check_project_state(self, project_description):
        file_list_file_name = os.path.join(self.root_directory, ".opp_env/" + project_description.get_full_folder_name() + ".md5")
        if not os.path.exists(file_list_file_name):
            return red('UNKNOWN -- project state not yet marked')
        # note: this won't detect if extra files were added to the project
        result = run_command(f"md5sum -c --quiet {file_list_file_name} > {file_list_file_name + '.out'}", quiet=True, check_exitcode=False)
        return green("UNMODIFIED") if result.returncode == 0 else f"{red('MODIFIED')} -- see {file_list_file_name + '.out'} for details"

class ProjectDescription:
    def __init__(self, name, version, description=None, stdenv="llvmPackages_14.stdenv", folder_name=None, required_projects={}, external_nix_packages=[], download_url=None, download_command=None, patch_command=None, setenv_command=None, configure_command=None, build_command=None, clean_command=None):
        self.name = name
        self.version = version
        self.description = description
        self.stdenv = stdenv
        self.folder_name = folder_name or name
        self.required_projects = required_projects
        self.external_nix_packages = external_nix_packages
        self.download_url = download_url
        self.download_command = download_command
        self.patch_command = patch_command
        self.setenv_command = setenv_command
        self.configure_command = configure_command
        self.build_command = build_command
        self.clean_command = clean_command
        if download_url and download_command:
            raise Exception(f"project {name}-{version}: download_url and download_command are mutually exclusive")

    def __repr__(self):
        return self.get_full_name()

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self, colored=False):
        full_name = self.name + "-" + self.version
        return cyan(full_name) if colored else full_name

    def get_full_folder_name(self):
        return f"{self.folder_name}-{self.version}"

def get_all_omnetpp_project_descriptions():
    return [ProjectDescription(**e) for e in get_all_omnetpp_versions()]

def get_all_inet_project_descriptions():
    return [ProjectDescription(**e) for e in get_all_inet_versions()]

def get_all_external_project_descriptions():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "external_versions.json")) as f:
        return [ProjectDescription(**e) for e in json.load(f)]

all_project_descriptions = None

def get_all_project_descriptions():
    global all_project_descriptions
    if not all_project_descriptions:
        all_project_descriptions = [
            *get_all_omnetpp_project_descriptions(),
            *get_all_inet_project_descriptions(),
            *get_all_external_project_descriptions(),
        ]
    return all_project_descriptions

def get_project_names():
    return list(dict.fromkeys([p.name for p in get_all_project_descriptions()]))

def get_project_versions(project_name):
    return [p.version for p in get_all_project_descriptions() if p.name == project_name]

def get_project_latest_version(project_name):
    versions = get_project_versions(project_name)
    numbered_versions = [v for v in versions if v and v[0] in '0123456789']
    return sorted(numbered_versions)[-1] if numbered_versions else None  # TODO use semantic version sorting, not plain alphanumeric; exclude 'git' etc!

def find_project_description(project_reference):
    if project_reference.name not in get_project_names():
         raise Exception(f"Cannot resolve '{project_reference}': Unknown project '{project_reference.name}'")
    if not project_reference.version:
         raise Exception(f"Which version of '{project_reference.name}' do you mean? (Use '{project_reference.name}-latest' for latest version)")
    if project_reference.version == "latest":
        project_reference.version = get_project_latest_version(project_reference.name)

    project_descriptions = [x for x in get_all_project_descriptions() if x.name == project_reference.name and x.version == project_reference.version]
    if len(project_descriptions) == 0:
         raise Exception(f"Project version '{project_reference}' not found")
    elif len(project_descriptions) > 1:
         raise Exception("More than one project descriptions were found for " + str(project_reference))
    else:
        return project_descriptions[0]

class ProjectReference:
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def __repr__(self):
        return self.get_full_name()

    def __str__(self):
        return self.get_full_name()

    @classmethod
    def parse(self, string):
        return ProjectReference(*string.rsplit("-", 1)) if "-" in string else ProjectReference(string, "")

    def get_full_name(self):
        return self.name + "-" + self.version if self.version else self.name

def compute_effective_project_descriptions(specified_project_descriptions):
    # 1. collect all required projects ignoring the project versions
    required_project_names = []
    for specified_project_description in specified_project_descriptions:
        required_project_names.append(specified_project_description.name)
        for project_name, project_versions in specified_project_description.required_projects.items():
            # maintains the proper ordering of required projects
            if project_name in required_project_names:
                required_project_names = [e for e in required_project_names if e != project_name]
            required_project_names.append(project_name)
    required_project_names.reverse()
    # print(required_project_names)
    # 2. collect all available project versions for all required projects separately
    available_project_versions = {}
    for required_project_name in required_project_names:
        project_versions = []
        for project_description in get_all_project_descriptions():
            if project_description.name == required_project_name:
                project_versions.append(project_description.version)
        available_project_versions[required_project_name] = project_versions
    # print(available_project_versions)
    # 3. iterate over all combinations of the available project versions for the different required projects
    sets = available_project_versions.values()
    keys = list(available_project_versions.keys())
    for combination in itertools.product(*sets):
        accept_combination = True
        selected_project_descriptions = []
        # 4. for each required project version combination check if it mathces all specified and required project criteria
        for i in range(len(combination)):
            selected_project_name = f"{keys[i]}-{combination[i]}"
            selected_project_description = find_project_description(ProjectReference.parse(selected_project_name))
            selected_project_descriptions.append(selected_project_description)
        # print(selected_project_descriptions)
        # 5. check if the specified project versions are included in the project version combination
        for specified_project_description in specified_project_descriptions:
            if not specified_project_description in selected_project_descriptions:
                accept_combination = False
                break
        # 6. check if one of the required project versions are included in the project version combination for all project versions
        for selected_project_description in selected_project_descriptions:
            for required_project_name, required_project_versions in selected_project_description.required_projects.items():
                accept_selected_project_description = False
                for required_project_version in required_project_versions:
                    required_project_description = find_project_description(ProjectReference.parse(required_project_name + "-" + required_project_version))
                    if required_project_description in selected_project_descriptions:
                        accept_selected_project_description = True
                if not accept_selected_project_description:
                    accept_combination = False
                    break
        if accept_combination:
            return selected_project_descriptions
    raise Exception("The specified set of project versions cannot be satisfied")

def nix_develop(workspace_directory, effective_project_descriptions, nix_packages, command, interactive=False, isolated=True, quiet=False, **kwargs):
    nix_develop_flake = """{
    inputs = {
        nixpkgs.url = "nixpkgs/nixos-22.11";
        flake-utils.url = "github:numtide/flake-utils";
    };
    outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem(system:
    let
        pkgs = import nixpkgs { inherit system; };
        in rec {
            devShells = rec {
                default = pkgs.@STDENV@.mkDerivation {
                    name = "@NAME@";
                    buildInputs = with pkgs; [ @PACKAGES@ ];
                    shellHook = ''
                        export QT_PLUGIN_PATH=${pkgs.qt5.qtbase.bin}/${pkgs.qt5.qtbase.qtPluginPrefix}:${pkgs.qt5.qtsvg.bin}/${pkgs.qt5.qtbase.qtPluginPrefix}
                        # disable GL support as NIX does not play nicely with OpenGL (except on nixOS)
                        export QT_XCB_GL_INTEGRATION=''${QT_XCB_GL_INTEGRATION:-none}

                        # modify prompt to distinguish an opp_env shell from a normal shell
                        export PS1="\\[\\e[01;33m\\]@NAME@\\[\\e[00m\\]:\[\\e[01;34m\\]\\w\[\\e[00m\\]\\$ "

                        @RESTORE_HOME@
                        @SCRIPT@
                    '';
                };
            };
        });
}"""
    flake_dir = os.path.join(workspace_directory, '.opp_env') #TODO race condition (multiple invocations write the same file)
    flake_file_name = os.path.join(flake_dir, "flake.nix")
    omnetpp_project_description = next(filter(lambda project_description: project_description.name == "omnetpp", effective_project_descriptions))
    with open(flake_file_name, "w") as f:
        name = '+'.join([str(d) for d in reversed(effective_project_descriptions)])
        nix_develop_flake = nix_develop_flake.replace("@STDENV@", omnetpp_project_description.stdenv)
        nix_develop_flake = nix_develop_flake.replace("@NAME@", name)
        nix_develop_flake = nix_develop_flake.replace("@PACKAGES@", " ".join(nix_packages))
        nix_develop_flake = nix_develop_flake.replace("@SCRIPT@", command)
        nix_develop_flake = nix_develop_flake.replace("@RESTORE_HOME@", f"export HOME={os.environ['HOME']}"  if isolated else "")
        f.write(nix_develop_flake)
    isolation_options = '-i -k HOME -k DISPLAY -k XDG_RUNTIME_DIR -k XDG_CACHE_HOME -k QT_AUTO_SCREEN_SCALE_FACTOR ' if isolated else ''
    command = '' if interactive else '-c true'
    nix_develop_command = f"nix --extra-experimental-features nix-command --extra-experimental-features flakes develop {isolation_options} {flake_dir} {command}"
    #TODO explanation: why the quirk (we don't want to source the rc and profile scripts, and bash seems to have no way to disable it, so we mislead bash by setting a dir without such files as HOME)
    run_command(nix_develop_command, quiet=not interactive and quiet, extra_env_vars={"HOME":flake_dir} if isolated else None, **kwargs)

def resolve_projects(projects=[], workspace_directory=os.getcwd(), **kwargs):
    specified_project_references = list(map(ProjectReference.parse, projects))
    specified_project_descriptions = list(map(find_project_description, specified_project_references))
    effective_project_descriptions = compute_effective_project_descriptions(specified_project_descriptions)
    _logger.info(f"Using specified projects {cyan(str(specified_project_references))} with effective projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")
    return effective_project_descriptions

def setup_environment(projects=[], workspace_directory=os.getcwd(), **kwargs):
    workspace = Workspace(workspace_directory)
    effective_project_descriptions = resolve_projects(projects=projects, workspace_directory=workspace_directory, **kwargs)
    external_nix_packages = []
    project_setenv_commands = []
    for project_description in effective_project_descriptions:
        external_nix_packages += project_description.external_nix_packages
        project_setenv_commands.append(f"cd {workspace.get_project_root_directory(project_description)} && {project_description.setenv_command}")
    return effective_project_descriptions, external_nix_packages, project_setenv_commands

def list_subcommand_main(list_mode, **kwargs):
    projects = get_all_project_descriptions()
    names = list(dict.fromkeys([p.name for p in projects]))
    if list_mode == "flat":
        for p in get_all_project_descriptions():
            print(p.get_full_name())
    elif list_mode == "grouped":
        for name in get_project_names():
            print(f"{name:<10} {'  '.join(get_project_versions(name))}")
    elif list_mode == "names":
        for name in get_project_names():
            print(name)
    else:
        raise Exception(f"invalid list mode '{list_mode}'")

def describe_subcommand_main(project, **kwargs):
    project_description = find_project_description(ProjectReference.parse(project))
    print(repr(project_description))

def download_subcommand_main(workspace_directory=os.getcwd(), **kwargs):
    workspace = Workspace(workspace_directory)
    effective_project_descriptions = resolve_projects(workspace_directory=workspace_directory, **kwargs)
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_state(project_description)
        else:
            workspace.download_project(project_description, **kwargs)

def configure_subcommand_main(workspace_directory=os.getcwd(), prepare_missing=True, **kwargs):
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(workspace_directory=workspace_directory, **kwargs)
    downloaded_project_descriptions = []
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_state(project_description)
        elif prepare_missing:
            workspace.download_project(project_description, **kwargs)
            downloaded_project_descriptions.append(project_description)
        else:
            raise Exception("Project is missing")
    for downloaded_project_description in downloaded_project_descriptions:
        if downloaded_project_description.configure_command:
            workspace.configure_project(downloaded_project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
    _logger.info(f"Configuration finished for projects {cyan(effective_project_descriptions)} in workspace {cyan(workspace_directory)}")

def build_subcommand_main(workspace_directory=os.getcwd(), prepare_missing=True, **kwargs):
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(workspace_directory=workspace_directory, **kwargs)
    downloaded_project_descriptions = []
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_state(project_description)
        elif prepare_missing:
            workspace.download_project(project_description, **kwargs)
            downloaded_project_descriptions.append(project_description)
        else:
            raise Exception("Project is missing")
    for downloaded_project_description in downloaded_project_descriptions:
        if downloaded_project_description.configure_command:
            workspace.configure_project(downloaded_project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
        if downloaded_project_description.build_command:
            workspace.build_project(downloaded_project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
    _logger.info(f"Build finished for projects {cyan(effective_project_descriptions)} in workspace {cyan(workspace_directory)}")

def clean_subcommand_main(workspace_directory=os.getcwd(), prepare_missing=True, **kwargs):
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(workspace_directory=workspace_directory, **kwargs)
    downloaded_project_descriptions = []
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_state(project_description)
        elif prepare_missing:
            workspace.download_project(project_description, **kwargs)
            downloaded_project_descriptions.append(project_description)
        else:
            raise Exception("Project is missing")
    for downloaded_project_description in downloaded_project_descriptions:
        if downloaded_project_description.configure_command:
            workspace.clean_project(downloaded_project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
    _logger.info(f"Clean finished for projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")

def shell_subcommand_main(workspace_directory=os.getcwd(), prepare_missing=True, isolated=True, **kwargs):
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(workspace_directory=workspace_directory, **kwargs)
    downloaded_project_descriptions = []
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_state(project_description)
        elif prepare_missing:
            workspace.download_project(project_description, **kwargs)
            downloaded_project_descriptions.append(project_description)
        else:
            raise Exception("Project is missing")
    for downloaded_project_description in downloaded_project_descriptions:
        if downloaded_project_description.configure_command:
            workspace.configure_project(downloaded_project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
        if downloaded_project_description.build_command:
            workspace.build_project(downloaded_project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
    _logger.info(f"Starting {green('isolated') if isolated else cyan('non-isolated')} shell for projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")
    nix_develop(workspace_directory, effective_project_descriptions, external_nix_packages, f"pushd . > /dev/null && {' && '.join(project_setenv_commands)} && popd > /dev/null", interactive=True, isolated=isolated, **kwargs)

def run_subcommand_main(command=None, workspace_directory=os.getcwd(), prepare_missing=True, **kwargs):
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(workspace_directory=workspace_directory, **kwargs)
    downloaded_project_descriptions = []
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_state(project_description)
        elif prepare_missing:
            workspace.download_project(project_description, **kwargs)
            downloaded_project_descriptions.append(project_description)
        else:
            raise Exception("Project is missing")
    for downloaded_project_description in downloaded_project_descriptions:
        if downloaded_project_description.configure_command:
            workspace.configure_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
        if downloaded_project_description.build_command:
            workspace.build_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
    _logger.info(f"Running command for projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")
    nix_develop(workspace_directory, effective_project_descriptions, external_nix_packages, f"{' && '.join(project_setenv_commands)} && cd {workspace_directory} && {command}", **dict(kwargs, quiet=False))

def main():
    kwargs = process_arguments()
    try:
        _logger.debug(f"Starting {cyan(kwargs['subcommand'])} operation")
        if (kwargs["subcommand"] == "list"):
            list_subcommand_main(**kwargs)
        elif (kwargs["subcommand"] == "describe"):
            describe_subcommand_main(**kwargs)
        elif (kwargs["subcommand"] == "download"):
            download_subcommand_main(**kwargs)
        elif (kwargs["subcommand"] == "configure"):
            configure_subcommand_main(**kwargs)
        elif (kwargs["subcommand"] == "build"):
            build_subcommand_main(**kwargs)
        elif (kwargs["subcommand"] == "clean"):
            clean_subcommand_main(**kwargs)
        elif (kwargs["subcommand"] == "shell"):
            shell_subcommand_main(**kwargs)
        elif (kwargs["subcommand"] == "run"):
            run_subcommand_main(**kwargs)
        else:
            raise Exception("Unknown subcommand")
        _logger.debug(f"The {cyan(kwargs['subcommand'])} operation completed successfully")
    except Exception as e:
        if kwargs["handle_exception"]:
            _logger.error(f"The {cyan(kwargs['subcommand'])} operation stopped with error: {str(e)}")
        else:
            raise e
    except KeyboardInterrupt:
        _logger.warning(f"The {cyan(kwargs['subcommand'])} operation was interrupted by the user")

    return 0

if __name__ == '__main__':
    sys.exit(main())