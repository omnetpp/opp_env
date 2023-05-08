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
import tempfile


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

try:
    from opp_env.veins_versions import get_all_veins_versions
except ImportError:
    from veins_versions import get_all_veins_versions

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

def natural_sort_key(text):
    return [int(part) if part.isdigit() else part.lower() for part in re.split('([0-9]+)', text)]

def natural_less(a, b):
    return natural_sort_key(a) < natural_sort_key(b)

def natural_sorted(list):
    return sorted(list, key=natural_sort_key)

def parse_arguments():
    description = "Sets up the development environment for OMNeT++ projects"
    parser = argparse.ArgumentParser(prog="opp_env", description=description)
    parser.add_argument("-q", "--quiet", action=argparse.BooleanOptionalAction, default=False, help="Suppress the standard output of executed commands")
    parser.add_argument("-l", "--log-level", choices=["ERROR", "WARN", "INFO", "DEBUG"], default="INFO", help="Verbose output mode")
    parser.add_argument("-w", "--workspace", dest="workspace_directory", help="Workspace directory")
    parser.add_argument("-p", "--print-stacktrace", default=False, action='store_true', help="Print stack trace on error")
    parser.add_argument("-n", "--no-pause", dest="pause_after_warnings", default=True, action='store_false', help="Do not pause after printing warnings")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", required=True)

    subparser = subparsers.add_parser("list", help="Lists all available projects")
    subparser.add_argument("project_names", nargs="*", metavar="project-name", help="Names of projects to list (omit to list all)")
    subparser.add_argument("-l", "--latest-patchlevels", default=False, action='store_true', help="Print the latest patchlevels of each major/minor version only")
    subparser.add_argument("-m", "--mode", dest="list_mode", choices=["flat", "grouped", "names"], default="grouped", help="Listing mode")

    subparser = subparsers.add_parser("info", help="Describes the specified project")
    subparser.add_argument("projects", nargs="*", help="The list of projects to describe. You can specify exact versions like 'inet-4.0' or project names like 'inet'. The latter will print info on all versions of the project. An empty list prints info on all projects.")
    subparser.add_argument("--raw", action=argparse.BooleanOptionalAction, default=False, help="Print the project description in JSON format")
    subparser.add_argument("--options", action='append', metavar='name1,name2,...', help="Print the project description as if the given project options were selected")

    subparser = subparsers.add_parser("init", help="Designates the current working directory to be an opp_env workspace")

    subparser = subparsers.add_parser("download", help="Downloads the specified projects into the workspace")
    subparser.add_argument("projects", nargs="+", help="List of projects")
    subparser.add_argument("-j", "--skip-dependencies", default=False, action='store_true', help="Download just the specified projects, skip downloading the projects they depend on")
    subparser.add_argument("--options", action='append', metavar='name1,name2,...', help="Project options to use; use 'opp_env info' to see what options a selected project has")
    subparser.add_argument("--patch", action=argparse.BooleanOptionalAction, default=True, help="Patch/do not patch the project after download")
    subparser.add_argument("--cleanup", action=argparse.BooleanOptionalAction, default=True, help="Specifies whether to delete partially downloaded project if download fails or is interrupted")

    subparser = subparsers.add_parser("build", help="Builds the specified projects in their environment")
    subparser.add_argument("projects", nargs="+", help="List of projects")
    subparser.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=True, help="Run in isolated environment from the host operating system")
    subparser.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading and configuring them")
    subparser.add_argument("--patch", action=argparse.BooleanOptionalAction, default=True, help="Patch/do not patch the project after download")
    subparser.add_argument("--mode", action='append', metavar='debug,release,...', help="Build mode(s)")
    subparser.add_argument("--options", action='append', metavar='name1,name2,...', help="Project options to use; use 'opp_env info' to see what options a selected project has")

    subparser = subparsers.add_parser("clean", help="Cleans the specified projects in their environment")
    subparser.add_argument("projects", nargs="+", help="List of projects")
    subparser.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=True, help="Run in isolated environment from the host operating system")
    subparser.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading and configuring them")
    subparser.add_argument("--mode", action='append', metavar='debug,release,...', help="Build mode(s)")
    subparser.add_argument("--options", action='append', metavar='name1,name2,...', help="Project options to use; use 'opp_env info' to see what options a selected project has")

    subparser = subparsers.add_parser("shell", help="Runs a shell in the environment of the specified projects")
    subparser.add_argument("projects", nargs="+", help="List of projects")
    subparser.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=False, help="Run in isolated environment from the host operating system")
    subparser.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading, configuring, and building them")
    subparser.add_argument("--options", action='append', metavar='name1,name2,...', help="Project options to use; use 'opp_env info' to see what options a selected project has")
    subparser.add_argument("--build", action=argparse.BooleanOptionalAction, default=True, help="Build project if not already built")
    subparser.add_argument("--mode", action='append', metavar='debug,release,...', help="Build mode(s)")
    subparser.add_argument("--patch", action=argparse.BooleanOptionalAction, default=True, help="Patch/do not patch the project after download")
    subparser.add_argument("--chdir", action=argparse.BooleanOptionalAction, default="if-outside", help="Whether to change into the directory of the project. The default action is to change into the project root only if the current working directory is outside the project")

    subparser = subparsers.add_parser("run", help="Runs a command in the environment of the specified projects")
    subparser.add_argument("projects", nargs="+", help="List of projects")
    subparser.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=True, help="Run in isolated environment from the host operating system")
    subparser.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading, configuring, and building them")
    subparser.add_argument("--options", action='append', metavar='name1,name2,...', help="Project options to use; use 'opp_env info' to see what options a selected project has")
    subparser.add_argument("--build", action=argparse.BooleanOptionalAction, default=True, help="Build project before running the command if not already built")
    subparser.add_argument("--mode", action='append', metavar='debug,release,...', help="Build mode(s)")
    subparser.add_argument("--patch", action=argparse.BooleanOptionalAction, default=True, help="Patch/do not patch the project after download")
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
    if "options" in kwargs:
        options = []
        for arg in args.options:
            options += arg.split(",")
        kwargs["requested_options"] = options
        del kwargs["options"]
    return kwargs

def detect_nix():
    # check nix is installed
    try:
        _logger.debug(f"Running nix --version")
        result = subprocess.run(['nix', '--version'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        output = result.stdout.decode('utf-8')
    except Exception as ex:
        _logger.debug(f"Error: {ex}")
        raise Exception("Nix does not seem to be installed. You can install it from https://nixos.org/download.html, or using your system's package manager.")
    # check it is recent enough
    nix_version = output.strip().split()[-1]
    if not re.match("^[0-9.]+$", nix_version):
        raise Exception("Cannot parse Nix version number: Output of 'nix --version' diverges from expected format")
    minimum_nix_version = "2.4"  # Nix flakes were introduced in version 2.4
    if natural_less(nix_version, minimum_nix_version):
        raise Exception(f"Your Nix installation of version {nix_version} is too old! At least version {minimum_nix_version} is required.")

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
    except Exception as e:
        print(read_file_if_exists(wget_log_file).strip())
        print(read_file_if_exists(tar_log_file).strip())
        raise e

def download_and_apply_patch(patch_url, target_folder):
    wget_log_file = os.path.join(target_folder, "wget.log")
    patching_log_file = os.path.join(target_folder, "patch.log")
    try:
        run_command(f"cd {target_folder} && wget -O - -nv -o {wget_log_file} --show-progress {patch_url} | git apply --whitespace=nowarn - 2>{patching_log_file}")
        os.remove(wget_log_file)
        os.remove(patching_log_file)
    except Exception as e:
        print(read_file_if_exists(wget_log_file).strip())
        print(read_file_if_exists(patching_log_file).strip())
        raise e

class Workspace:
    # project states
    ABSENT = "ABSENT"
    INCOMPLETE = "INCOMPLETE"
    DOWNLOADED = "DOWNLOADED"

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
        if not os.path.isdir(dir):
            raise Exception(f"Directory does not exist: {dir}")
        opp_env_dir = os.path.join(dir, ".opp_env")
        if os.path.isdir(opp_env_dir):
            raise Exception(f"'{dir}' is already an opp_env workspace")
        os.mkdir(opp_env_dir)

    def get_project_root_directory(self, project_description):
        return os.path.join(self.root_directory, project_description.get_full_folder_name())

    def print_project_state(self, project_description):
        _logger.info(f"Project {project_description.get_full_name(colored=True)} is {green(self.get_project_state(project_description))}, {self.check_project_state(project_description)}")

    def read_project_state_file(self, project_description):
        state_file_name = os.path.join(self.get_project_root_directory(project_description), ".opp_env_state")
        if not os.path.isfile(state_file_name):
            return {}
        with open(state_file_name) as f:
            return json.load(f)

    def write_project_state_file(self, project_description, data):
        state_file_name = os.path.join(self.get_project_root_directory(project_description), ".opp_env_state")
        with open(state_file_name, "w") as f:
            json.dump(data, f)

    def get_project_state(self, project_description):
        project_directory = self.get_project_root_directory(project_description)
        data = self.read_project_state_file(project_description)
        return self.ABSENT if not os.path.isdir(project_directory) else \
               self.INCOMPLETE if not data or 'state' not in data else \
               data['state']

    def set_project_state(self, project_description, state):
        _logger.debug(f"Setting project {cyan(project_description.get_full_name())} state to {cyan(state)}")
        data = self.read_project_state_file(project_description)
        data['state'] = state
        self.write_project_state_file(project_description, data)

    def download_project(self, project_description, patch, cleanup, **kwargs):
        _logger.info(f"Downloading project {cyan(project_description.get_full_name())} in workspace {cyan(self.root_directory)}")
        project_dir = self.root_directory + "/" + project_description.get_full_name()
        if os.path.exists(project_dir):
            raise Exception("f{project_dir} already exists")
        try:
            if project_description.download_command:
                run_command(f"cd {self.root_directory} && {project_description.download_command}")
            elif project_description.download_url:
                download_and_unpack_tarball(project_description.download_url, project_dir)
            elif project_description.git_url:
                branch_option = "-b " + project_description.git_branch if project_description.git_branch else ""
                #TODO maybe optionally use --single-branch
                run_command(f"git clone --config advice.detachedHead=false {branch_option} {project_description.git_url} {project_dir}")
            else:
                raise Exception(f"{project_description}: No download_url or download_command in project description -- check project options for alternative download means (enter 'opp_env info {project_description}')")
            if not os.path.exists(project_dir):
                raise Exception(f"{project_description}: Download process did not create {project_dir}")

            if project_description.patch_command or project_description.patch_url:
                if patch:
                    _logger.info(f"Patching project {cyan(project_description.get_full_name())}")
                    if project_description.patch_command:
                        run_command(f"cd {project_dir} && {project_description.patch_command}")
                    if project_description.patch_url:
                        download_and_apply_patch(project_description.patch_url, project_dir)
                else:
                    _logger.info(f"Skipping patching step of project {cyan(project_description.get_full_name())}")

            self.mark_project_state(project_description)
            self.set_project_state(project_description, self.DOWNLOADED)
        except KeyboardInterrupt as e:
            if cleanup:
                _logger.info("Download interrupted by user, cleaning up")
                if os.path.isdir(project_dir):
                    shutil.rmtree(project_dir)
            raise e
        except Exception as e:
            if cleanup:
                _logger.info("Error during download, cleaning up")
                if os.path.isdir(project_dir):
                    shutil.rmtree(project_dir)
            raise e

    def build_project(self, project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, build_modes, **kwargs):
        assert(project_description.build_command)
        for build_mode in build_modes:
            _logger.info(f"Building project {cyan(project_description.get_full_name())} in {cyan(build_mode)} mode in workspace {cyan(self.root_directory)}")
            nix_develop(self.root_directory, effective_project_descriptions, external_nix_packages, f"{' && '.join(project_setenv_commands)} && cd {self.get_project_root_directory(project_description)} && {project_description.build_command}", build_mode=build_mode, **kwargs)

    def clean_project(self, project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, build_modes, **kwargs):
        assert(project_description.clean_command)
        for build_mode in build_modes:
            _logger.info(f"Cleaning project {cyan(project_description.get_full_name())} in {cyan(build_mode)} in workspace {cyan(self.root_directory)}")
            nix_develop(self.root_directory, effective_project_descriptions, external_nix_packages, f"{' && '.join(project_setenv_commands)} && cd {self.get_project_root_directory(project_description)} && {project_description.clean_command}", build_mode=build_mode, **kwargs)

    def mark_project_state(self, project_description):
        # exclude the Simulation IDE's directory from the md5sum, because ./configure and eclipse itself modifies stuff in it
        file_list_file_name = os.path.join(self.root_directory, ".opp_env/" + project_description.get_full_folder_name() + ".md5")
        run_command(f"find {self.get_project_root_directory(project_description)} -type f -a -not -path './ide/*' -print0 | xargs -0 md5sum > {file_list_file_name}")

    def check_project_state(self, project_description):
        file_list_file_name = os.path.join(self.root_directory, ".opp_env/" + project_description.get_full_folder_name() + ".md5")
        if not os.path.exists(file_list_file_name):
            return red('UNKNOWN -- project state not yet marked')
        # note: this won't detect if extra files were added to the project
        result = run_command(f"md5sum -c --quiet {file_list_file_name} > {file_list_file_name + '.out'}", quiet=True, check_exitcode=False)
        return green("UNMODIFIED") if result.returncode == 0 else f"{red('MODIFIED')} -- see {file_list_file_name + '.out'} for details"

class ProjectDescription:
    def __init__(self, name, version, description=None, warnings=[],
                 nixos=None, stdenv=None, folder_name=None,
                 required_projects={}, external_nix_packages=[],
                 download_url=None, git_url=None, git_branch=None, download_command=None,
                 patch_command=None, patch_url=None,
                 shell_hook_command = None, setenv_command=None,
                 build_command=None, clean_command=None,
                 options=None):
        self.name = name
        self.version = version
        self.description = description
        self.warnings = warnings
        self.nixos = nixos
        self.stdenv = stdenv
        self.folder_name = folder_name or name
        self.required_projects = required_projects
        self.external_nix_packages = external_nix_packages
        self.download_url = download_url
        self.git_url = git_url
        self.git_branch = git_branch
        self.download_command = download_command
        self.patch_command = patch_command
        self.patch_url = patch_url
        self.shell_hook_command = shell_hook_command
        self.setenv_command = setenv_command
        self.build_command = build_command
        self.clean_command = clean_command
        self.options = options or {}
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

    def get_supported_options(self):
        return list(self.options.keys())

    def get_with_options(self, requested_options):
        fields = dict(vars(self))
        if requested_options:
            _logger.debug(f"Selecting options {cyan(requested_options)} for project {cyan(self)}")
            category_to_option = dict()
            for option in requested_options:
                if option in self.options:
                    # check for conflicts by "conflicts_with"
                    option_fields = self.options[option]
                    conflicts_with = option_fields.get("conflicts_with", [])
                    if conflicts_with is str:
                        conflicts_with = [conflicts_with]
                    conflicting_options = list(set(conflicts_with).intersection(set(requested_options)))
                    if conflicting_options:
                        raise Exception(f"Option '{option}' conflicts with the following option(s): {conflicting_options}")
                    # check for conflicts by the "category" field
                    option_category = option_fields.get("category")
                    if option_category in category_to_option:
                        raise Exception(f"Option '{option}' conflicts with option '{category_to_option[option_category]}' due to both belonging in the category '{option_category}' (Note that options in the same category are exclusive)")
                    category_to_option[option_category] = option
                    # update project description with entries in the option
                    _logger.debug(f"option {option} has the following fields: {list(option_fields.keys())}")
                    fields.update(option_fields)
                else:
                    _logger.warning(f"Project {cyan(self)} does not support option {cyan(option)}")
        fields.pop("option_description", None)
        fields.pop("conflicts_with", None)
        fields.pop("category", None)
        fields.pop("options", None)
        return ProjectDescription(**fields)

def get_all_omnetpp_project_descriptions():
    return [ProjectDescription(**e) for e in get_all_omnetpp_versions()]

def get_all_inet_project_descriptions():
    return [ProjectDescription(**e) for e in get_all_inet_versions()]


def get_all_veins_project_descriptions():
    return [ProjectDescription(**e) for e in get_all_veins_versions()]

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
            *get_all_veins_project_descriptions(),
            *get_all_external_project_descriptions(),
        ]
    return all_project_descriptions

def get_project_names(project_descriptions=None):
    return list(dict.fromkeys([p.name for p in project_descriptions or get_all_project_descriptions()]))

def get_project_versions(project_name):
    return [p.version for p in get_all_project_descriptions() if p.name == project_name]

def get_project_latest_version(project_name):
    versions = get_project_versions(project_name)
    numbered_versions = [v for v in versions if v and v[0] in '0123456789']  # exclude versions named "git", etc.
    return natural_sorted(numbered_versions)[-1] if numbered_versions else None  # almost as good as semantic version sorting

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

def compute_effective_project_descriptions(specified_project_descriptions, requested_options=None):
    _logger.debug(f"Computing list of effective projects for {specified_project_descriptions}")
    # 1. collect all required projects ignoring the project versions
    required_project_names = []
    todo_list = specified_project_descriptions.copy()
    while todo_list:
        project_description = todo_list.pop(0)
        required_project_names.append(project_description.name)
        for project_name, project_versions in project_description.required_projects.items():
            # maintains the proper ordering of required projects
            if project_name in required_project_names:
                required_project_names = [e for e in required_project_names if e != project_name]
            else:
                todo_list.append(find_project_description(ProjectReference.parse(project_name + "-" + project_versions[0])))
            required_project_names.append(project_name)
    required_project_names.reverse()
    # _logger.debug(f"{required_project_names=}")

    # 2. collect all available project versions for all required projects separately
    available_project_versions = {}
    for required_project_name in required_project_names:
        project_versions = []
        for project_description in get_all_project_descriptions():
            if project_description.name == required_project_name:
                project_versions.append(project_description.version)
        available_project_versions[required_project_name] = project_versions
    # _logger.debug(f"{available_project_versions=}")

    # 3. iterate over all combinations of the available project versions for the different required projects
    sets = available_project_versions.values()
    keys = list(available_project_versions.keys())
    for combination in itertools.product(*sets):
        # _logger.debug(f"checking combination: {combination=}")
        accept_combination = True
        selected_project_descriptions = []
        # 4. for each required project version combination check if it matches all specified and required project criteria
        for i in range(len(combination)):
            selected_project_name = f"{keys[i]}-{combination[i]}"
            selected_project_description = find_project_description(ProjectReference.parse(selected_project_name))
            selected_project_descriptions.append(selected_project_description)
        # _logger.debug(f"checking combination: {selected_project_descriptions=}")
        # 5. check if the specified project versions are included in the project version combination
        for specified_project_description in specified_project_descriptions:
            if not specified_project_description in selected_project_descriptions:
                # _logger.debug(f"  rejecting because {specified_project_description} is not in {selected_project_descriptions}")
                accept_combination = False
                break
        # 6. check if one of the required project versions are included in the project version combination for all project versions
        for selected_project_description in selected_project_descriptions:
            # _logger.debug(f"  checking {selected_project_description}")
            for required_project_name, required_project_versions in selected_project_description.required_projects.items():
                accept_selected_project_description = False
                for required_project_version in required_project_versions:
                    required_project_description = find_project_description(ProjectReference.parse(required_project_name + "-" + required_project_version))
                    if required_project_description in selected_project_descriptions:
                        accept_selected_project_description = True
                if not accept_selected_project_description:
                    # _logger.debug(f"  rejecting {required_project_name} {required_project_versions}")
                    accept_combination = False
                    break
        if accept_combination:
            # return selected_project_descriptions with the requested options activated
            return get_projects_with_options(selected_project_descriptions, requested_options)
    raise Exception("The specified set of project versions cannot be satisfied")

def get_projects_with_options(project_descriptions, requested_options):
    if not requested_options:
        return project_descriptions
    # check requested options exist at all
    all_supported_options = []
    for desc in project_descriptions:
        all_supported_options += desc.get_supported_options()
    all_supported_options = list(set(all_supported_options))
    for option in requested_options:
        if option not in all_supported_options:
            raise Exception(f"None of the selected projects supports option '{option}'")
    # create and return updated project descriptions
    return [desc.get_with_options(requested_options) for desc in project_descriptions]

def print_project_warnings(project_descriptions, pause_after_warnings=True):
    have_warnings = False
    for p in project_descriptions:
        if p.warnings:
            for warning in p.warnings:
                have_warnings = True
                _logger.warning(f"Project {cyan(p)}: {warning}")
    if pause_after_warnings and have_warnings and sys.stdin.isatty():
        input("Press Enter to continue, or Ctrl+C to abort ")

def get_unique_project_attribute(project_descriptions, attr_name):
    values = set([getattr(p, attr_name) for p in project_descriptions if getattr(p, attr_name)])
    if not values:
        raise Exception(f"None of the projects specify the '{attr_name}' attribute")
    elif len(values) > 1:
        raise Exception(f"The projects disagree on the choice of '{attr_name}': {values}")
    else:
        return list(values)[0]

def nix_develop(workspace_directory, effective_project_descriptions, nix_packages, shell_hook_script, interactive=False, isolated=True, check_exitcode=True, quiet=False, build_mode=None, **kwargs):
    nix_develop_flake = """{
    inputs = {
        nixpkgs.url = "nixpkgs/@NIXOS@";
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
                    buildInputs = with pkgs; [ @PACKAGES@ bashInteractive vim ];
                    shellHook = ''
                        BUILD_MODE=@BUILD_MODE@
                        @PROJECTDIR_VARS@

                        @SHELL_HOOK_COMMANDS@

                        # modify prompt to distinguish an opp_env shell from a normal shell
                        export PS1="\\[\\e[01;33m\\]@NAME@\\[\\e[00m\\]:\[\\e[01;34m\\]\\w\[\\e[00m\\]\\$ "

                        @SCRIPT@ || exit 1
                    '';
                };
            };
        });
}"""

    nixos = get_unique_project_attribute(effective_project_descriptions, "nixos")
    stdenv = get_unique_project_attribute(effective_project_descriptions, "stdenv")
    shell_hook_commands = "\n".join([p.shell_hook_command for p in effective_project_descriptions if p.shell_hook_command])
    projectdir_var_assignments = "\n".join([f"export {p.name.upper()}_ROOT={os.path.join(workspace_directory, p.get_full_name())}" for p in effective_project_descriptions])

    flake_dir = os.path.join(workspace_directory, '.opp_env') #TODO race condition (multiple invocations write the same file)
    flake_file_name = os.path.join(flake_dir, "flake.nix")
    with open(flake_file_name, "w") as f:
        name = '+'.join([str(d) for d in reversed(effective_project_descriptions)])
        nix_develop_flake = nix_develop_flake.replace("@NIXOS@", nixos)
        nix_develop_flake = nix_develop_flake.replace("@STDENV@", stdenv)
        nix_develop_flake = nix_develop_flake.replace("@NAME@", name)
        nix_develop_flake = nix_develop_flake.replace("@PACKAGES@", " ".join(nix_packages))
        nix_develop_flake = nix_develop_flake.replace("@BUILD_MODE@", build_mode or "")
        nix_develop_flake = nix_develop_flake.replace("@PROJECTDIR_VARS@", projectdir_var_assignments)
        nix_develop_flake = nix_develop_flake.replace("@SHELL_HOOK_COMMANDS@", shell_hook_commands)
        nix_develop_flake = nix_develop_flake.replace("@SCRIPT@", shell_hook_script)
        f.write(nix_develop_flake)

    _logger.debug(f"Nix flake shellHook script: {yellow(shell_hook_script)}")
    #_logger.debug(f"Nix flake file {cyan(flake_file_name)}:\n{yellow(nix_develop_flake)}")
    temp_home = tempfile.mkdtemp() if isolated else None
    isolation_options = '-i -k HOME -k TERM -k COLORTERM -k DISPLAY -k XAUTHORITY -k XDG_RUNTIME_DIR -k XDG_DATA_DIRS -k XDG_CACHE_HOME -k QT_AUTO_SCREEN_SCALE_FACTOR ' if isolated else ''
    command = '-c bash --norc' if interactive else '-c true'
    nix_develop_command = f"nix --extra-experimental-features nix-command --extra-experimental-features flakes develop {isolation_options} {flake_dir} {command}"
    run_command(nix_develop_command, quiet=not interactive and quiet, extra_env_vars={"HOME":temp_home} if isolated else None, check_exitcode=check_exitcode)
    if temp_home:
        shutil.rmtree(temp_home)

def resolve_projects(projects):
    project_descriptions = [find_project_description(ProjectReference.parse(p)) for p in projects]
    return project_descriptions

def resolve_workspace(workspace_directory):
    workspace_directory = os.path.abspath(workspace_directory) if workspace_directory else Workspace.find_workspace(os.getcwd())
    return workspace_directory

def setup_environment(projects, workspace_directory=None, requested_options=None, pause_after_warnings=True, **kwargs):
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory)
    specified_project_descriptions = resolve_projects(projects)
    effective_project_descriptions = compute_effective_project_descriptions(specified_project_descriptions, requested_options)
    _logger.info(f"Using specified projects {cyan(str(specified_project_descriptions))} with effective projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")
    print_project_warnings(effective_project_descriptions, pause_after_warnings)
    external_nix_packages = []
    project_setenv_commands = []
    for project_description in effective_project_descriptions:
        external_nix_packages += project_description.external_nix_packages
        project_setenv_commands.append(f"cd {workspace.get_project_root_directory(project_description)} && {project_description.setenv_command or 'true'}")
    return effective_project_descriptions, external_nix_packages, project_setenv_commands

def download_project_if_needed(workspace, project_description, prepare_missing=True, patch=True, cleanup=True, **kwargs):
    project_state = workspace.get_project_state(project_description)
    if not prepare_missing and project_state in [Workspace.ABSENT, Workspace.INCOMPLETE]:
        raise Exception(f"Project '{project_description}' is missing or incomplete")
    elif project_state == Workspace.ABSENT:
        workspace.download_project(project_description, patch, cleanup, **kwargs)
    elif project_state == Workspace.INCOMPLETE:
        raise Exception(f"Cannot download '{project_description}': Directory already exists")
    else:
        workspace.print_project_state(project_description)
    assert workspace.get_project_state(project_description) == Workspace.DOWNLOADED

def is_semver(version):
    # supported formats: "3.2", "3.2.1", "3.2p1"
    pattern = r'^(\d+)\.(\d+)(?:[.p](\d+))?$'
    return re.match(pattern, version) is not None

def parse_semver(version):
    # supported formats: "3.2", "3.2.1", "3.2p1"
    pattern = r'^(\d+)\.(\d+)(?:[.p](\d+))?$'
    match = re.match(pattern, version)
    if match is None:
        raise ValueError('Invalid version string: ' + version)
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch) if patch is not None else 0

def is_latest_patchlevel(project_description, among_project_descriptions):
    name = project_description.name
    if is_semver(project_description.version):
        major, minor, patch = parse_semver(project_description.version)
    else:
        return True

    for p in among_project_descriptions:
        if is_semver(p.version):
            p_major, p_minor, p_patch = parse_semver(p.version)
            if name == p.name and major == p_major and minor == p_minor and patch < p_patch:
                return False
    return True

def list_subcommand_main(project_names=None, list_mode="grouped", latest_patchlevels=False, **kwargs):
    projects = get_all_project_descriptions()
    if project_names:
        projects = [p for p in projects if p.name in project_names]
    if latest_patchlevels:
        projects = [p for p in projects if is_latest_patchlevel(p,projects)]
    names = list(dict.fromkeys([p.name for p in projects]))
    if list_mode == "flat":
        for p in projects:
            print(p.get_full_name())
    elif list_mode == "grouped":
        for name in names:
            versions = [p.version for p in projects if p.name == name]
            print(f"{name:<10} {'  '.join(versions)}")
    elif list_mode == "names":
        for name in names:
            print(name)
    else:
        raise Exception(f"invalid list mode '{list_mode}'")

def init_subcommand_main(workspace_directory=None, **kwargs):
    workspace_directory = workspace_directory or os.getcwd()
    Workspace.init_workspace(workspace_directory)
    _logger.info(f"Workspace created in folder {cyan(workspace_directory)}")

def info_subcommand_main(projects, raw=False, requested_options=None, **kwargs):
    # resolve project list
    if not projects:
        project_descriptions = get_all_project_descriptions()
    else:
        project_descriptions = []
        for project in projects:
            if '-' in project:
                project_descriptions += [find_project_description(ProjectReference.parse(project))]
            elif project in get_project_names():
                project_descriptions += [find_project_description(ProjectReference(project, version)) for version in get_project_versions(project)]
            else:
                raise Exception(f"Unknown project name '{project}'")

    # print info for each
    first = True
    for project_description in project_descriptions:
        if first:
            first = False
        else:
            print()
        if requested_options:
            project_description = project_description.get_with_options(requested_options)
        if raw:
            print(json.dumps(vars(project_description), indent=4))
        else:
            print(cyan(project_description.get_full_name()) + (" - " + project_description.description if project_description.description else ""))
            if project_description.warnings:
                for warning in project_description.warnings:
                    print(yellow("\nWARNING: ") + warning)
            if (project_description.options):
                print("\nAvailable options:")
                for option_name, option in project_description.options.items():
                    option_description = option.get('option_description')
                    if option_description:
                        print(f"- {cyan(option_name)}: {option.get('option_description', 'n/a')}")
                    else:
                        print(f"- {cyan(option_name)}")
            if (project_description.required_projects):
                print(f"\nRequires:")
                for name, versions in project_description.required_projects.items():
                    print(f"- {cyan(name)}: {versions}")

def download_subcommand_main(projects, workspace_directory=None, requested_options=None, skip_dependencies=True, **kwargs):
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory)
    specified_project_descriptions = resolve_projects(projects)
    if skip_dependencies:
        effective_project_descriptions = get_projects_with_options(specified_project_descriptions, requested_options)
    else:
        effective_project_descriptions = compute_effective_project_descriptions(specified_project_descriptions, requested_options)
        _logger.info(f"Using specified projects {cyan(str(specified_project_descriptions))} with effective projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")
    for project_description in effective_project_descriptions:
        download_project_if_needed(workspace, project_description, **kwargs)

def build_subcommand_main(projects, workspace_directory=None, prepare_missing=True, requested_options=None, mode=None, **kwargs):
    detect_nix()
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(projects, workspace_directory, requested_options, **kwargs)
    build_modes = mode if mode else ["debug", "release"]
    for project_description in effective_project_descriptions:
        download_project_if_needed(workspace, project_description, prepare_missing, **kwargs)
    for project_description in effective_project_descriptions:
        assert workspace.get_project_state(project_description) == Workspace.DOWNLOADED
        if project_description.build_command:
            workspace.build_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, build_modes, **kwargs)
    _logger.info(f"Build finished for projects {cyan(effective_project_descriptions)} in workspace {cyan(workspace_directory)}")

def clean_subcommand_main(projects, workspace_directory=None, prepare_missing=True, requested_options=None, mode=None, **kwargs):
    #TODO shouldn't there be a "realclean" command that deletes all files NOT in the file list??
    detect_nix()
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(projects, workspace_directory, requested_options, **kwargs)
    build_modes = mode if mode else ["debug", "release"]
    for project_description in effective_project_descriptions:
        download_project_if_needed(workspace, project_description, prepare_missing, **kwargs)
    for project_description in reversed(effective_project_descriptions):
        if project_description.clean_command:
            workspace.clean_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, build_modes, **kwargs)
    _logger.info(f"Clean finished for projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")

def is_subdirectory(child_dir, parent_dir):
    # Check if a directory is a subdirectory of another directory.
    return os.path.commonpath([child_dir, parent_dir]) == parent_dir

def shell_subcommand_main(projects, workspace_directory=[], prepare_missing=True, isolated=True, chdir=False, requested_options=None, build=True, mode=None, **kwargs):
    detect_nix()
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(projects, workspace_directory, requested_options, **kwargs)
    for project_description in effective_project_descriptions:
        download_project_if_needed(workspace, project_description, prepare_missing, **kwargs)
    if build:
        try:
            build_modes = mode if mode else ["debug", "release"]
            for project_description in effective_project_descriptions:
                assert workspace.get_project_state(project_description) == Workspace.DOWNLOADED
                if project_description.build_command:
                    workspace.build_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, build_modes, **kwargs)
        except Exception as e:
            # print error but continue bringing up the shell to give user a chance to fix the problem
            _logger.error(f"An error occurred while building affected projects: {red(e)}")

    _logger.info(f"Starting {green('isolated') if isolated else cyan('non-isolated')} shell for projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")

    if chdir and projects:
        first_project_description = resolve_projects(projects)[0]
        first_project_dir = os.path.join(workspace_directory, first_project_description.get_full_name())
        if chdir == "if-outside":
            chdir = not is_subdirectory(os.getcwd(), first_project_dir)  # "is outside the project dir"
        if chdir:
            _logger.debug(f"Changing into the first project's directory {cyan(first_project_dir)}")
            os.chdir(first_project_dir)
        else:
            _logger.debug(f"No need to change directory, wd={cyan(os.getcwd())} is already under the first project's directory {cyan(first_project_dir)}")

    nix_develop(workspace_directory, effective_project_descriptions, external_nix_packages, f"pushd . > /dev/null && {' && '.join(project_setenv_commands)} && popd > /dev/null", interactive=True, isolated=isolated, check_exitcode=False, **kwargs)

def run_subcommand_main(projects, command=None, workspace_directory=None, prepare_missing=True, requested_options=None, build=True, mode=None, **kwargs):
    detect_nix()
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(projects, workspace_directory, requested_options, **kwargs)
    for project_description in effective_project_descriptions:
        download_project_if_needed(workspace, project_description, prepare_missing, **kwargs)
    if build:
        build_modes = mode if mode else ["debug", "release"]
        for project_description in effective_project_descriptions:
            assert workspace.get_project_state(project_description) == Workspace.DOWNLOADED
            if project_description.build_command:
                workspace.build_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, build_modes, **kwargs)
    _logger.info(f"Running command for projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")
    nix_develop(workspace_directory, effective_project_descriptions, external_nix_packages, f"{' && '.join(project_setenv_commands)} && cd {workspace_directory} && {command}", **dict(kwargs, quiet=False))

def main():
    kwargs = process_arguments()
    subcommand = kwargs['subcommand']
    try:
        _logger.debug(f"Starting {cyan(subcommand)} operation")
        if subcommand == "list":
            list_subcommand_main(**kwargs)
        elif subcommand == "info":
            info_subcommand_main(**kwargs)
        elif subcommand == "init":
            init_subcommand_main(**kwargs)
        elif subcommand == "download":
            download_subcommand_main(**kwargs)
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
        return 0
    except Exception as e:
        if not kwargs["print_stacktrace"]:
            _logger.error(f"The {cyan(subcommand)} operation stopped with error: {str(e)}")
            return 1
        else:
            raise e
    except KeyboardInterrupt:
        _logger.error(f"The {cyan(subcommand)} operation was interrupted by the user")
        return 130 # = 128 + SIGINT


if __name__ == '__main__':
    sys.exit(main())
