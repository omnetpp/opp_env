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
import re
import shutil

# project states: downloaded, configured, built
# NEW ---download--> DOWNLOADED
# DOWNLOADED ---configure--> CONFIGURED
# CONFIGURED ---build--> BUILT
# CONFIGURED/BUILT ---clean--> CONFIGURED  ("clean" doesn't undo the result of "configure")
# DOWNLOADED ---clean--> DOWNLOADED
#

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

COLOR_GRAY = "\033[38;20m"
COLOR_RED = "\033[1;31m"
COLOR_YELLOW = "\033[1;33m"
COLOR_CYAN = "\033[0;36m"
COLOR_GREEN = "\033[0;32m"
COLOR_RESET = "\033[0;0m"

coloring_enabled = sys.stdout.isatty() and sys.stderr.isatty()

def colored(color, x):
    global coloring_enabled
    return color + str(x) + COLOR_RESET if coloring_enabled else str(x)

def gray(x): return colored(COLOR_GRAY, x)
def red(x): return colored(COLOR_RED, x)
def yellow(x): return colored(COLOR_YELLOW, x)
def cyan(x): return colored(COLOR_CYAN, x)
def green(x): return colored(COLOR_GREEN, x)

class ColoredLoggingFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: COLOR_GREEN,
        logging.INFO: COLOR_GREEN,
        logging.WARNING: COLOR_YELLOW,
        logging.ERROR: COLOR_RED,
        logging.CRITICAL: COLOR_RED
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno)
        format = colored(color, "%(levelname)s") + " %(message)s"
        formatter = logging.Formatter(format)
        return formatter.format(record)

def parse_arguments():
    description = "Sets up the development environment for OMNeT++ projects"
    parser = argparse.ArgumentParser(prog="opp_env", description=description)
    parser.add_argument("-q", "--quiet", action=argparse.BooleanOptionalAction, default=False, help="Suppress the standard output of executed commands")
    parser.add_argument("-l", "--log-level", choices=["ERROR", "WARN", "INFO", "DEBUG"], default="INFO", help="Verbose output mode")
    parser.add_argument("-w", "--workspace", dest="workspace_directory", help="Workspace directory")
    parser.add_argument("-p", "--print-stacktrace", default=False, action='store_true', help="Print stack trace on error")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", required=True)

    subparser = subparsers.add_parser("list", help="Lists all available projects")
    subparser.add_argument("-m", "--mode", dest="list_mode", choices=["flat", "grouped", "names"], default="grouped", help="Listing mode")

    subparser = subparsers.add_parser("describe", help="Describes the specified project")
    subparser.add_argument("project", help="The project name")

    subparser = subparsers.add_parser("init", help="Designates the current working directory to be an opp_env workspace")

    subparser = subparsers.add_parser("download", help="Downloads the specified projects into the workspace")
    subparser.add_argument("projects", nargs="+", help="List of projects")

    subparser = subparsers.add_parser("configure", help="Configures the specified projects for their environment")
    subparser.add_argument("projects", nargs="+", help="List of projects")
    subparser.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading them")
    subparser.add_argument("-v", "--variant", action='append', metavar='name1,name2,...', help="Project variants to use; use 'opp_env describe' to see what variants a selected project has")

    subparser = subparsers.add_parser("build", help="Builds the specified projects in their environment")
    subparser.add_argument("projects", nargs="+", help="List of projects")
    subparser.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=True, help="Run in isolated environment from the host operating system")
    subparser.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading and configuring them")

    subparser = subparsers.add_parser("clean", help="Cleans the specified projects in their environment")
    subparser.add_argument("projects", nargs="+", help="List of projects")
    subparser.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=True, help="Run in isolated environment from the host operating system")
    subparser.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading and configuring them")

    subparser = subparsers.add_parser("shell", help="Runs a shell in the environment of the specified projects")
    subparser.add_argument("projects", nargs="+", help="List of projects")
    subparser.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=False, help="Run in isolated environment from the host operating system")
    subparser.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading, configuring, and building them")
    subparser.add_argument("--chdir", default=False, action='store_true', help="Change into the directory of the project")

    subparser = subparsers.add_parser("run", help="Runs a command in the environment of the specified projects")
    subparser.add_argument("projects", nargs="+", help="List of projects")
    subparser.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=True, help="Run in isolated environment from the host operating system")
    subparser.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading, configuring, and building them")
    subparser.add_argument("-c", "--command", help="Specifies the command that is run in the environment")

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

def run_command(command, quiet=False, check_exitcode=True, tweak_env_for_nix=True, extra_env_vars=None):
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
    _logger.debug(f"Exit code: {result.returncode}")
    if check_exitcode and result.returncode != 0:
        raise Exception(f"Child process exit code {result.returncode}")
    return result

def read_file_if_exists(fname):
    try:
        with open(fname) as f:
            return f.read()
    except:
        return ""

def download_and_unpack_tarball(download_url, target_folder):
    os.makedirs(target_folder)
    wget_log_file = os.path.join(target_folder, "wget.log")
    tar_log_file = os.path.join(target_folder, "tar.log")
    try:
        run_command(f"cd {target_folder} && wget -O - -nv -o {wget_log_file} --show-progress {download_url} | tar --strip-components=1 -xzf - 2>{tar_log_file}")
        os.remove(wget_log_file)
        os.remove(tar_log_file)
    except KeyboardInterrupt as e:
        _logger.debug("Download and unpacking interrupted by user, cleaning up")
        shutil.rmtree(target_folder)
        raise e
    except Exception as e:
        print(read_file_if_exists(wget_log_file).strip())
        print(read_file_if_exists(tar_log_file).strip())
        shutil.rmtree(target_folder)  # clean up partial download
        raise e

class Workspace:
    # project states
    ABSENT = "ABSENT"
    DOWNLOADED = "DOWNLOADED"
    CONFIGURED = "CONFIGURED"
    BUILT = "BUILT"

    def __init__(self, root_directory):
        assert(os.path.isabs(root_directory))
        self.root_directory = root_directory
        opp_env_directory = os.path.join(self.root_directory, ".opp_env")
        if not os.path.exists(opp_env_directory):
            raise Exception(f"'{root_directory}' is not an opp_env workspace, run 'opp_env init' to turn in into one")

    @staticmethod
    def find_workspace(from_dir=None):
        dir = os.path.abspath(from_dir) if from_dir else os.getcwd()
        while True:
            if os.path.isdir(os.path.join(dir, ".opp_env")):
                return dir
            parent_dir = os.path.dirname(dir)
            if parent_dir == dir:
                break
            dir = parent_dir
        raise Exception(f"No opp_env workspace found in '{from_dir}' or its parent directories, run 'opp_env init' to create one")
        #return None

    @staticmethod
    def init_workspace(dir=None):
        opp_env_dir = os.path.join(dir, ".opp_env")
        if os.path.isdir(opp_env_dir):
            raise Exception(f"'{dir}' is already an opp_env workspace")
        os.mkdir(opp_env_dir)

    def get_project_root_directory(self, project_description):
        return os.path.join(self.root_directory, project_description.get_full_folder_name())

    def print_project_state(self, project_description):
        _logger.info(f"Project {project_description.get_full_name(colored=True)} is {green(self.get_project_state(project_description))}, {self.check_project_state(project_description)}")

    def is_project_downloaded(self, project_description):
        return os.path.exists(self.get_project_root_directory(project_description))

    def read_project_state_file(self, project_description):
        state_file_name = os.path.join(self.root_directory, ".opp_env", project_description.get_full_folder_name() + ".state")
        if not os.path.isfile(state_file_name):
            return {}
        with open(state_file_name) as f:
            return json.load(f)

    def write_project_state_file(self, project_description, data):
        state_file_name = os.path.join(self.root_directory, ".opp_env", project_description.get_full_folder_name() + ".state")
        with open(state_file_name, "w") as f:
            json.dump(data, f)

    def get_project_state(self, project_description):
        data = self.read_project_state_file(project_description)
        return self.ABSENT if not self.is_project_downloaded(project_description) else data['state'] if 'state' in data else self.DOWNLOADED

    def set_project_state(self, project_description, state):
        data = self.read_project_state_file(project_description)
        data['state'] = state
        self.write_project_state_file(project_description, data)

    def download_project(self, project_description, **kwargs):
        _logger.info(f"Downloading project {cyan(project_description.get_full_name())} in workspace {cyan(self.root_directory)}")
        project_dir = self.root_directory + "/" + project_description.get_full_name()
        if os.path.exists(project_dir):
            raise Exception("f{project_dir} already exists")
        if project_description.download_command:
            run_command(f"cd {self.root_directory} && {project_description.download_command}")
        elif project_description.download_url:
            download_and_unpack_tarball(project_description.download_url, project_dir)
        elif project_description.git_url:
            branch_option = "-b " + project_description.git_branch if project_description.git_branch else ""
            run_command(f"git clone --config advice.detachedHead=false {branch_option} {project_description.git_url} {project_dir}")
        else:
            raise Exception("no download_url or download_command in project description")
        if not os.path.exists(project_dir):
            raise Exception(f"download process did not create {project_dir}")

        if project_description.patch_command:
            run_command(f"cd {project_dir} && {project_description.patch_command}")

        self.mark_project_state(project_description)
        self.set_project_state(project_description, self.DOWNLOADED)

    def configure_project(self, project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs):
        assert(project_description.configure_command)
        _logger.info(f"Configuring project {cyan(project_description.get_full_name())} in workspace {cyan(self.root_directory)}")
        nix_develop(self.root_directory, effective_project_descriptions, external_nix_packages, f"{' && '.join(project_setenv_commands)} && cd {self.get_project_root_directory(project_description)} && {project_description.configure_command}", **kwargs)
        self.set_project_state(project_description, self.CONFIGURED)

    def build_project(self, project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs):
        assert(project_description.build_command)
        _logger.info(f"Building project {cyan(project_description.get_full_name())} in workspace {cyan(self.root_directory)}")
        nix_develop(self.root_directory, effective_project_descriptions, external_nix_packages, f"{' && '.join(project_setenv_commands)} && cd {self.get_project_root_directory(project_description)} && {project_description.build_command}", **kwargs)
        self.set_project_state(project_description, self.BUILT)

    def clean_project(self, project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs):
        assert(project_description.clean_command)
        _logger.info(f"Cleaning project {cyan(project_description.get_full_name())} in workspace {cyan(self.root_directory)}")
        # A BUILT project becomes CONFIGURED, other states remain unchanged. Update the state *before* running the command,
        # because even if it only does part of its job before running into an error, the project cannot be considered BUILT any more.
        if self.get_project_state(project_description) == self.BUILT:
            self.set_project_state(project_description, self.CONFIGURED)
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
    def __init__(self, name, version, description=None, stdenv="llvmPackages_14.stdenv", folder_name=None, required_projects={}, external_nix_packages=[], download_url=None, git_url=None, git_branch=None, download_command=None, patch_command=None, setenv_command=None, configure_command=None, build_command=None, clean_command=None):
        self.name = name
        self.version = version
        self.description = description
        self.stdenv = stdenv
        self.folder_name = folder_name or name
        self.required_projects = required_projects
        self.external_nix_packages = external_nix_packages
        self.download_url = download_url
        self.git_url = git_url
        self.git_branch = git_branch
        self.download_command = download_command
        self.patch_command = patch_command
        self.setenv_command = setenv_command
        self.configure_command = configure_command
        self.build_command = build_command
        self.clean_command = clean_command
        if bool(download_url) + bool(git_url) + bool(download_command) > 1:
            raise Exception(f"project {name}-{version}: download_url, git_url, and download_command are mutually exclusive")

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

def natsorted(l): # from https://stackoverflow.com/questions/4836710/is-there-a-built-in-function-for-string-natural-sort
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

def get_project_latest_version(project_name):
    versions = get_project_versions(project_name)
    numbered_versions = [v for v in versions if v and v[0] in '0123456789']  # exclude versions named "git", etc.
    return natsorted(numbered_versions)[-1] if numbered_versions else None  # almost as good as semantic version sorting

def find_project_description(project_reference):
    if project_reference.name not in get_project_names():
         raise Exception(f"Cannot resolve '{project_reference}': Unknown project '{project_reference.name}'")
    if not project_reference.version:
         raise Exception(f"Which version of '{project_reference.name}' do you mean? (Use '{project_reference.name}-latest' for latest version)")
    if project_reference.version == "latest":
        project_reference.version = get_project_latest_version(project_reference.name)

    project_descriptions = [x for x in get_all_project_descriptions() if x.name == project_reference.name and x.version == project_reference.version]
    if len(project_descriptions) == 0:
         raise Exception(f"Project '{project_reference.name}' has no version '{project_reference.version}'")
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
        # 4. for each required project version combination check if it matches all specified and required project criteria
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

def nix_develop(workspace_directory, effective_project_descriptions, nix_packages, shell_hook_script, interactive=False, isolated=True, check_exitcode=True, quiet=False, **kwargs):
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
                    hardeningDisable = [ "all" ];
                    buildInputs = with pkgs; [ @PACKAGES@ ];
                    shellHook = ''
                        export QT_PLUGIN_PATH=${pkgs.qt5.qtbase.bin}/${pkgs.qt5.qtbase.qtPluginPrefix}:${pkgs.qt5.qtsvg.bin}/${pkgs.qt5.qtbase.qtPluginPrefix}
                        export NIX_CFLAGS_COMPILE="$NIX_CFLAGS_COMPILE -isystem ${pkgs.libxml2.dev}/include/libxml2"
                        # disable GL support as NIX does not play nicely with OpenGL (except on nixOS)
                        export QT_XCB_GL_INTEGRATION=''${QT_XCB_GL_INTEGRATION:-none}

                        # modify prompt to distinguish an opp_env shell from a normal shell
                        export PS1="\\[\\e[01;33m\\]@NAME@\\[\\e[00m\\]:\[\\e[01;34m\\]\\w\[\\e[00m\\]\\$ "

                        @RESTORE_HOME@
                        @SCRIPT@ || exit 1
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
        nix_develop_flake = nix_develop_flake.replace("@SCRIPT@", shell_hook_script)
        nix_develop_flake = nix_develop_flake.replace("@RESTORE_HOME@", f"export HOME={os.environ['HOME']}"  if isolated else "")
        f.write(nix_develop_flake)

    _logger.debug(f"Nix flake shellHook script: {yellow(shell_hook_script)}")
    #_logger.debug(f"Nix flake file {cyan(flake_file_name)}:\n{yellow(nix_develop_flake)}")
    isolation_options = '-i -k HOME -k DISPLAY -k XDG_RUNTIME_DIR -k XDG_CACHE_HOME -k QT_AUTO_SCREEN_SCALE_FACTOR ' if isolated else ''
    command = '' if interactive else '-c true'
    nix_develop_command = f"nix --extra-experimental-features nix-command --extra-experimental-features flakes develop {isolation_options} {flake_dir} {command}"
    # Note: Why do we set HOME=<flake_dir> in isolated mode? We want the bash shell to only execute the system-wide startup and
    # initialization files (/etc/profile, /etc/bash.bashrc, etc) but skip the personal startup and initialization files such as
    # ~/.bashrc, ~/.bash_profile, ~/.bash_login, or ~/.profile. bash does not offer such an option, so the workaround is to set
    # HOME to a directory that doesn't contain such files (such as <flake_dir>) for the time bash starts up, and restore it
    # after bash has already started. The latter is what @RESTORE_HOME@ above is for.
    run_command(nix_develop_command, quiet=not interactive and quiet, extra_env_vars={"HOME":flake_dir} if isolated else None, check_exitcode=check_exitcode)

def resolve_projects(projects):
    project_descriptions = [find_project_description(ProjectReference.parse(p)) for p in projects]
    return project_descriptions

def resolve_workspace(workspace_directory):
    workspace_directory = os.path.abspath(workspace_directory) if workspace_directory else Workspace.find_workspace(os.getcwd())
    return workspace_directory

def setup_environment(projects, workspace_directory=None, **kwargs):
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory)
    specified_project_descriptions = resolve_projects(projects)
    effective_project_descriptions = compute_effective_project_descriptions(specified_project_descriptions)
    _logger.info(f"Using specified projects {cyan(str(specified_project_descriptions))} with effective projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")
    external_nix_packages = []
    project_setenv_commands = []
    for project_description in effective_project_descriptions:
        external_nix_packages += project_description.external_nix_packages
        project_setenv_commands.append(f"cd {workspace.get_project_root_directory(project_description)} && {project_description.setenv_command or 'true'}")
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

def init_subcommand_main(**kwargs):
    dir = os.getcwd()
    Workspace.init_workspace(dir)
    _logger.info(f"Workspace created in folder {cyan(dir)}")

def describe_subcommand_main(project, **kwargs):
    project_description = find_project_description(ProjectReference.parse(project))
    for prop, value in vars(project_description).items():
        print(cyan(prop) + " = " + repr(value))

def download_subcommand_main(projects, workspace_directory=None, **kwargs):
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory)
    specified_project_descriptions = resolve_projects(projects)
    effective_project_descriptions = compute_effective_project_descriptions(specified_project_descriptions)
    _logger.info(f"Using specified projects {cyan(str(specified_project_descriptions))} with effective projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_state(project_description)
        else:
            workspace.download_project(project_description, **kwargs)

def configure_subcommand_main(projects, workspace_directory=None, prepare_missing=True, **kwargs):
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(projects, workspace_directory=workspace_directory, **kwargs)
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_state(project_description)
        elif prepare_missing:
            workspace.download_project(project_description, **kwargs)
        else:
            raise Exception(f"Project {project_description} is missing")
    for project_description in effective_project_descriptions:
        if project_description.configure_command:
            workspace.configure_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
    _logger.info(f"Configuration finished for projects {cyan(effective_project_descriptions)} in workspace {cyan(workspace_directory)}")

def build_subcommand_main(projects, workspace_directory=None, prepare_missing=True, **kwargs):
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(projects, workspace_directory=workspace_directory, **kwargs)
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_state(project_description)
        elif prepare_missing:
            workspace.download_project(project_description, **kwargs)
        else:
            raise Exception(f"Project {project_description} is missing")
    for project_description in effective_project_descriptions:
        if project_description.configure_command and workspace.get_project_state(project_description) == Workspace.DOWNLOADED:
            workspace.configure_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
    for project_description in effective_project_descriptions:
        if project_description.build_command and workspace.get_project_state(project_description) in [Workspace.DOWNLOADED, Workspace.CONFIGURED]:
            workspace.build_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
    _logger.info(f"Build finished for projects {cyan(effective_project_descriptions)} in workspace {cyan(workspace_directory)}")

def clean_subcommand_main(projects, workspace_directory=None, prepare_missing=True, **kwargs):
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(projects, workspace_directory=workspace_directory, **kwargs)
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_state(project_description)
        elif prepare_missing:
            workspace.download_project(project_description, **kwargs)
        else:
            raise Exception(f"Project {project_description} is missing")
    for project_description in reversed(effective_project_descriptions):
        if project_description.clean_command:
            workspace.clean_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
    _logger.info(f"Clean finished for projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")

def shell_subcommand_main(projects, workspace_directory=[], prepare_missing=True, isolated=True, chdir=False, **kwargs):
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(projects, workspace_directory=workspace_directory, **kwargs)
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_state(project_description)
        elif prepare_missing:
            workspace.download_project(project_description, **kwargs)
        else:
            raise Exception(f"Project {project_description} is missing")
    try:
        for project_description in effective_project_descriptions:
            if project_description.configure_command and workspace.get_project_state(project_description) == Workspace.DOWNLOADED:
                workspace.configure_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
        for project_description in effective_project_descriptions:
            if project_description.build_command and workspace.get_project_state(project_description) in [Workspace.DOWNLOADED, Workspace.CONFIGURED]:
                workspace.build_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
    except Exception as e:
        # print error but continue bringing up the shell to give user a chance to fix the problem
        _logger.error(f"An error occurred while building affected projects: {red(e)}")

    _logger.info(f"Starting {green('isolated') if isolated else cyan('non-isolated')} shell for projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")
    if chdir and projects:
        first_project_description = resolve_projects(projects)[0]
        first_project_dir = os.path.join(workspace_directory, first_project_description.get_full_name())
        _logger.debug(f"Changing into the first project's directory {cyan(first_project_dir)}")
        os.chdir(first_project_dir)

    nix_develop(workspace_directory, effective_project_descriptions, external_nix_packages, f"pushd . > /dev/null && {' && '.join(project_setenv_commands)} && popd > /dev/null", interactive=True, isolated=isolated, check_exitcode=False, **kwargs)

def run_subcommand_main(projects, command=None, workspace_directory=None, prepare_missing=True, **kwargs):
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(projects, workspace_directory=workspace_directory, **kwargs)
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_state(project_description)
        elif prepare_missing:
            workspace.download_project(project_description, **kwargs)
        else:
            raise Exception(f"Project {project_description} is missing")
    for project_description in effective_project_descriptions:
        if project_description.configure_command and workspace.get_project_state(project_description) == Workspace.DOWNLOADED:
            workspace.configure_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
    for project_description in effective_project_descriptions:
        if project_description.build_command and workspace.get_project_state(project_description) in [Workspace.DOWNLOADED, Workspace.CONFIGURED]:
            workspace.build_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
    _logger.info(f"Running command for projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")
    nix_develop(workspace_directory, effective_project_descriptions, external_nix_packages, f"{' && '.join(project_setenv_commands)} && cd {workspace_directory} && {command}", **dict(kwargs, quiet=False))

def main():
    kwargs = process_arguments()
    subcommand = kwargs['subcommand']
    try:
        _logger.debug(f"Starting {cyan(subcommand)} operation")
        if subcommand == "list":
            list_subcommand_main(**kwargs)
        elif subcommand == "describe":
            describe_subcommand_main(**kwargs)
        elif subcommand == "init":
            init_subcommand_main(**kwargs)
        elif subcommand == "download":
            download_subcommand_main(**kwargs)
        elif subcommand == "configure":
            configure_subcommand_main(**kwargs)
        elif subcommand == "build":
            build_subcommand_main(**kwargs)
        elif subcommand == "clean":
            clean_subcommand_main(**kwargs)
        elif subcommand == "shell":
            shell_subcommand_main(**kwargs)
        elif subcommand == "run":
            run_subcommand_main(**kwargs)
        else:
            raise Exception(f"Unknown subcommand '{subcommand}'")
        _logger.debug(f"The {cyan(subcommand)} operation completed successfully")
    except Exception as e:
        if not kwargs["print_stacktrace"]:
            _logger.error(f"The {cyan(subcommand)} operation stopped with error: {str(e)}")
        else:
            raise e
    except KeyboardInterrupt:
        _logger.error(f"The {cyan(subcommand)} operation was interrupted by the user")

    return 0

if __name__ == '__main__':
    sys.exit(main())
