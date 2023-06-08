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
import importlib
import importlib.util
import platform


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

def project_natural_sort_key(project_description):
    return natural_sort_key(project_description.get_full_name())

def sorted_projects(project_description_list):
    return sorted(project_description_list, key=project_natural_sort_key)

def uniq(l):
    return list(dict.fromkeys(l))

def indent(txt, indent="    "):
    return indent + txt.replace("\n", "\n" + indent)

def join_lines(lines):
    assert type(lines) is list
    return "\n".join([li for li in lines if li])

def join_commands(commands):
    assert type(commands) is list
    return "\n".join([cmd for cmd in commands if cmd])  # using ";" as separator also works, " && " should too (script runs on 'set -e' anyway) but doesn't

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

def version_matches(wildcard_version, version):
    if not re.match(r"^[^*?]+(\.\*)?$", wildcard_version):
        raise Exception(f"Unsupported version pattern '{wildcard_version}', only '.*' is allowed at the end")
    if wildcard_version.endswith(".*"):
        truncated = wildcard_version[0:-2]
        return version == truncated or version.startswith(truncated+".") or version.startswith(truncated+"p") # "3.3.*" should match "3.3p1" too
    else:
        return wildcard_version == version

def parse_arguments():
    description = "Sets up the development environment for OMNeT++ projects"
    parser = argparse.ArgumentParser(prog="opp_env", description=description)
    parser.add_argument("-q", "--quiet", dest="suppress_stdout", action=argparse.BooleanOptionalAction, default=False, help="Suppress the standard output of executed commands")
    parser.add_argument("-l", "--log-level", choices=["ERROR", "WARN", "INFO", "DEBUG"], default="INFO", help="Verbose output mode")
    parser.add_argument("-w", "--workspace", dest="workspace_directory", help="Workspace directory")
    parser.add_argument("-p", "--print-stacktrace", default=False, action='store_true', help="Print stack trace on error")
    parser.add_argument("-n", "--no-pause", dest="pause_after_warnings", default=True, action='store_false', help="Do not pause after printing warnings")
    parser.add_argument("-v", "--version", action='version', version=get_version(), help="Print version information and exit")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", required=True)

    subparser = subparsers.add_parser("list", help="Lists all available projects")
    subparser.add_argument("project_name_patterns", nargs="*", metavar="project-name-or-pattern", help="Names of projects to list (omit to list all)")
    subparser.add_argument("-m", "--mode", dest="list_mode", choices=["flat", "grouped", "names", "expand", "combinations"], default="grouped", help="Listing mode")

    subparser = subparsers.add_parser("info", help="Describes the specified project")
    subparser.add_argument("projects", nargs="*", help="The list of projects to describe. You can specify exact versions like 'inet-4.0' or project names like 'inet'. The latter will print info on all versions of the project. An empty list prints info on all projects.")
    subparser.add_argument("--raw", action=argparse.BooleanOptionalAction, default=False, help="Print the project descriptions in a raw form. The output is well-formed JSON, so you can use tools like 'jq' to further query it and extract the desired data.")
    subparser.add_argument("--options", action='append', metavar='name1,name2,...', help="Print the project description as if the given project options were selected")

    subparser = subparsers.add_parser("init", help="Designates the current working directory to be an opp_env workspace")

    help_nixless = re.sub(r"\s+", " ", """Run without Nix. This mode assumes that all packages that the projects and opp_env itself require are already installed in the system.
        For opp_env itself, this translates to having 'wget' and/or 'git', and basic tools like 'tar' and 'gzip' available for downloading packages.
        The packages that OMNeT++ requires are documented in the Installation Guide of the particular version.""")

    subparser = subparsers.add_parser("download", help="Downloads the specified projects into the workspace")
    subparser.add_argument("projects", nargs="+", help="List of projects")
    subparser.add_argument("-j", "--skip-dependencies", default=False, action='store_true', help="Download just the specified projects, skip downloading the projects they depend on")
    subparser.add_argument("--options", action='append', metavar='name1,name2,...', help="Project options to use; use 'opp_env info' to see what options a selected project has")
    subparser.add_argument("--patch", action=argparse.BooleanOptionalAction, default=True, help="Patch/do not patch the project after download")
    subparser.add_argument("--cleanup", action=argparse.BooleanOptionalAction, default=True, help="Specifies whether to delete partially downloaded project if download fails or is interrupted")
    subparser.add_argument("--nixless", default=False, action='store_true', help=help_nixless)
    subparser.add_argument("-k", "--keep", action='append', metavar='name1,name2,...', help="Keep the specified environment variables, i.e. pass them into shells spawned by opp_env")

    subparser = subparsers.add_parser("build", help="Builds the specified projects in their environment")
    subparser.add_argument("projects", nargs="+", help="List of projects")
    subparser.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=True, help="Run in isolated environment from the host operating system")
    subparser.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading and configuring them")
    subparser.add_argument("--patch", action=argparse.BooleanOptionalAction, default=True, help="Patch/do not patch the project after download")
    subparser.add_argument("--mode", action='append', metavar='debug,release,...', help="Build mode(s)")
    subparser.add_argument("--options", action='append', metavar='name1,name2,...', help="Project options to use; use 'opp_env info' to see what options a selected project has")
    subparser.add_argument("--nixless", default=False, action='store_true', help=help_nixless)
    subparser.add_argument("-k", "--keep", action='append', metavar='name1,name2,...', help="Keep the specified environment variables, i.e. pass them into shells spawned by opp_env")

    subparser = subparsers.add_parser("clean", help="Cleans the specified projects in their environment")
    subparser.add_argument("projects", nargs="+", help="List of projects")
    subparser.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=True, help="Run in isolated environment from the host operating system")
    subparser.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading and configuring them")
    subparser.add_argument("--mode", action='append', metavar='debug,release,...', help="Build mode(s)")
    subparser.add_argument("--options", action='append', metavar='name1,name2,...', help="Project options to use; use 'opp_env info' to see what options a selected project has")
    subparser.add_argument("--nixless", default=False, action='store_true', help=help_nixless)
    subparser.add_argument("-k", "--keep", action='append', metavar='name1,name2,...', help="Keep the specified environment variables, i.e. pass them into shells spawned by opp_env")

    subparser = subparsers.add_parser("shell", help="Runs a shell in the environment of the specified projects")
    subparser.add_argument("projects", nargs="+", help="List of projects")
    subparser.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=False, help="Run in isolated environment from the host operating system")
    subparser.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading, configuring, and building them")
    subparser.add_argument("--options", action='append', metavar='name1,name2,...', help="Project options to use; use 'opp_env info' to see what options a selected project has")
    subparser.add_argument("--build", action=argparse.BooleanOptionalAction, default=True, help="Build project if not already built")
    subparser.add_argument("--mode", action='append', metavar='debug,release,...', help="Build mode(s)")
    subparser.add_argument("--patch", action=argparse.BooleanOptionalAction, default=True, help="Patch/do not patch the project after download")
    subparser.add_argument("--chdir", action=argparse.BooleanOptionalAction, default="if-outside", help="Whether to change into the directory of the project. The default action is to change into the project root only if the current working directory is outside the project")
    subparser.add_argument("--nixless", default=False, action='store_true', help=help_nixless)
    subparser.add_argument("-k", "--keep", action='append', metavar='name1,name2,...', help="Keep the specified environment variables, i.e. pass them into shells spawned by opp_env")

    subparser = subparsers.add_parser("run", help="Runs a command in the environment of the specified projects")
    subparser.add_argument("projects", nargs="+", help="List of projects")
    subparser.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=True, help="Run in isolated environment from the host operating system")
    subparser.add_argument("-p", "--prepare-missing", action=argparse.BooleanOptionalAction, default=True, help="Automatically prepare missing projects by downloading, configuring, and building them")
    subparser.add_argument("--options", action='append', metavar='name1,name2,...', help="Project options to use; use 'opp_env info' to see what options a selected project has")
    subparser.add_argument("--build", action=argparse.BooleanOptionalAction, default=True, help="Build project before running the command if not already built")
    subparser.add_argument("--mode", action='append', metavar='debug,release,...', help="Build mode(s)")
    subparser.add_argument("--patch", action=argparse.BooleanOptionalAction, default=True, help="Patch/do not patch the project after download")
    subparser.add_argument("-c", "--command", help="Specifies the command that is run in the environment")
    subparser.add_argument("--nixless", default=False, action='store_true', help=help_nixless)
    subparser.add_argument("-k", "--keep", action='append', metavar='name1,name2,...', help="Keep the specified environment variables, i.e. pass them into shells spawned by opp_env")

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
        # split up and flatten list
        kwargs["requested_options"] = [name for arg in args.options for name in arg.split(",")]
        del kwargs["options"]
    if "keep" in kwargs:
        # split up and flatten list
        kwargs["vars_to_keep"] = [name for arg in args.keep for name in arg.split(",")]
        del kwargs["keep"]
    return kwargs

def get_version():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    version_file_path = os.path.join(current_dir, "_version.py")

    version_module = importlib.util.spec_from_file_location("_version", version_file_path)
    version = importlib.util.module_from_spec(version_module) # type: ignore
    version_module.loader.exec_module(version) # type: ignore
    return version.version

def detect_nix():
    minimum_nix_version = "2.4"  # Nix flakes were introduced in version 2.4
    # check nix is installed
    try:
        _logger.debug(f"Running nix --version")
        result = subprocess.run(['nix', '--version'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        output = result.stdout.decode('utf-8')
    except Exception as ex:
        _logger.debug(f"Error: {ex}")
        raise Exception("Nix does not seem to be installed. You can install it from https://nixos.org/download.html or using your system's package manager (important: at least version {minimum_nix_version} is required). See also the --nixless option in the help.")

    # check it is recent enough
    nix_version = output.strip().split()[-1]
    if not re.match("^[0-9.]+$", nix_version):
        raise Exception("Cannot parse Nix version number: Output of 'nix --version' diverges from expected format")
    if natural_less(nix_version, minimum_nix_version):
        raise Exception(f"Your Nix installation of version {nix_version} is too old, at least version {minimum_nix_version} is required. The newest version is available from https://nixos.org/download.html. See also the --nixless option in the help.")

def detect_tools():
    tools = [ "bash", "git", "wget", "grep", "find", "xargs", "md5sum", "tar", "gzip", "sed", "touch" ]

    is_macos = platform.system().lower() == "darwin"
    if not is_macos:
        tools.append("nproc")

    errors = []
    for tool in tools:
        try:
            result = subprocess.run([tool, '--version'], capture_output=True)
        except Exception as ex:
            errors.append(tool)
    if errors:
        raise Exception(f"The following programs were not found: {', '.join(errors)}.")


class ProjectDescription:
    def __init__(self, name, version, description=None, warnings=[],
                 nixos=None, stdenv=None, folder_name=None,
                 required_projects={}, external_nix_packages=[], vars_to_keep=[],
                 download_url=None, git_url=None, git_branch=None, download_commands=None,
                 patch_commands=[], patch_url=None,
                 shell_hook_commands=[], setenv_commands=[],
                 build_commands=[], clean_commands=[],
                 options=None):
        def remove_empty(list):
            return [x for x in list if x] if list else []
        self.name = name
        self.version = version
        self.description = description
        self.warnings = remove_empty(warnings)
        self.nixos = nixos
        self.stdenv = stdenv
        self.folder_name = folder_name or name
        self.required_projects = required_projects
        self.external_nix_packages = remove_empty(external_nix_packages)
        self.vars_to_keep = remove_empty(vars_to_keep)
        self.download_url = download_url
        self.git_url = git_url
        self.git_branch = git_branch
        self.download_commands = remove_empty(download_commands)
        self.patch_commands = remove_empty(patch_commands)
        self.patch_url = patch_url
        self.shell_hook_commands = remove_empty(shell_hook_commands)
        self.setenv_commands = remove_empty(setenv_commands)
        self.build_commands = remove_empty(build_commands)
        self.clean_commands = remove_empty(clean_commands)
        self.options = options or {}

        # remove null elements from lists inside options, too
        for option_name, option_entries in self.options.items():
            for field_name, field_value in option_entries.items():
                if type(field_value) is list:
                    field_value[:] = remove_empty(field_value)

        if bool(download_url) + bool(git_url) + bool(download_commands) > 1:
            raise Exception(f"project {name}-{version}: download_url, git_url, and download_commands are mutually exclusive")

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

    def get_default_options(self):
        return [option_name for option_name, option_entries in self.options.items() if option_entries.get("is_default")]

    def activate_project_options(self, requested_options, activate_default_options=True, quiet=False):
        def get_conflicting_options(the_option_name, option_names):
            return [o for o in option_names if the_option_name != o and self.options[o].get("category") == self.options[the_option_name].get("category")]

        # activate requested options, and those of the default options that don't conflict with the requested ones
        effective_options = []
        for option in requested_options or []:
            if option in self.options:
                conflicting_options = get_conflicting_options(option, effective_options)
                if conflicting_options:
                    raise Exception(f"Option '{option}' conflicts with option '{conflicting_options[0]}' due to both belonging in the category '{self.options[option].get('category')}' (Note that options in the same category are exclusive)")
                effective_options.append(option)
        if activate_default_options:
            for option in self.get_default_options():
                if not get_conflicting_options(option, effective_options):
                    effective_options.append(option)

        new_project_description = copy.deepcopy(self)

        if effective_options:
            if not quiet:
                _logger.debug(f"Selecting options {cyan(requested_options)} for project {cyan(self)}")
            for option in effective_options:
                if option in self.options:
                    for field_name, field_value in self.options[option].items():
                        if field_name not in ["option_description", "category", "is_default"]: # option metadata fields
                            setattr(new_project_description, field_name, field_value)
                else:
                    _logger.warning(f"Project {cyan(self)} does not support option {cyan(option)}")
        return new_project_description

class ProjectReference:
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def __repr__(self):
        return self.get_full_name()

    def __str__(self):
        return self.get_full_name()

    @staticmethod
    def parse(string):
        return ProjectReference(*string.rsplit("-", 1)) if "-" in string else ProjectReference(string, "")

    def get_full_name(self):
        return self.name + "-" + self.version if self.version else self.name

class ProjectRegistry:
    def __init__(self):
        self.all_project_descriptions = self.collect_project_descriptions()
        self.index = self.build_index(self.all_project_descriptions)

    def collect_project_descriptions(self):
        python_files = [
            "omnetpp_versions",
            "inet_versions",
            "veins_versions",
            "simulte_versions",
            "simu5g_versions",
        ]

        json_files = [
            "external_versions.json"
        ]

        all_project_descriptions = []
        for fname in python_files:
            module = importlib.import_module("opp_env." + fname)
            raw_project_descriptions = module.get_project_descriptions()
            project_descriptions = [ProjectDescription(**e) for e in raw_project_descriptions]
            all_project_descriptions += project_descriptions

        for fname in json_files:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), fname)) as f:
                all_project_descriptions += [ProjectDescription(**e) for e in json.load(f)]

        # expand to wildcard versions such as "4.2.*" to list of matching versions
        return [self.expand_wildcards_in_project_dependencies(p, all_project_descriptions) for p in all_project_descriptions]

    def get_all_project_descriptions(self):
        return self.all_project_descriptions

    def get_project_names(self, project_descriptions=None):
        return uniq([p.name for p in project_descriptions or self.get_all_project_descriptions()])

    def get_project_versions(self, project_name, project_descriptions=None):
        # Note: this does not include "pseudo" versions like "latest", or "omnetpp-4" that means "omnetpp-4.6.1"
        return [p.version for p in project_descriptions or self.get_all_project_descriptions() if p.name == project_name]

    def build_index(self, project_descriptions):
        # index structure: { name: {version: description}}
        index = {}
        versions = {}
        for project in project_descriptions:
            project_name = project.name
            project_version = project.version
            if project_name not in index:
                index[project_name] = {}
                versions[project_name] = []
            index[project_name][project_version] = project
            versions[project_name].append(project_version)

        # add meta entries: "latest"; "3", "3.8" -> 3.8.2 (latest minor/patch version)
        # ordering is determined by order of items in the project_descriptions array.
        for project_name, project_versions in versions.items():
            index[project_name]["latest"] = index[project_name][project_versions[0]]
            for version in project_versions:
                truncated_version = version
                while "." in truncated_version:
                    truncated_version = truncated_version.rsplit(".",1)[0] # chop off part after last dot
                    if truncated_version not in index[project_name]:
                        index[project_name][truncated_version] = index[project_name][version]
        return index

    def get_project_description(self, project_reference):
        if type(project_reference) is str:
            project_reference = ProjectReference.parse(project_reference)
        if project_reference.name not in self.index:
            raise Exception(f"Cannot resolve '{project_reference}': Unknown project '{project_reference.name}'")
        if not project_reference.version:
            raise Exception(f"Which version of '{project_reference.name}' do you mean? (Use '{project_reference.name}-latest' for latest version)")
        project_description = self.index[project_reference.name].get(project_reference.version)
        if not project_description:
            raise Exception(f"Project '{project_reference.name}' has no version '{project_reference.version}'")
        if project_reference.version != project_description.version:
            _logger.debug(f"Resolved {cyan(project_reference)} as {cyan(project_description)}")
        return project_description

    def expand_wildcards_in_project_dependencies(self, project_description, all_project_descriptions):
        def expand(project_name, version, all_project_descriptions):
            if not '*' in version:
                return [ version ]
            candidates = self.get_project_versions(project_name, all_project_descriptions)
            return [ candidate for candidate in candidates if version_matches(version, candidate) ]

        def expand_all(project_name, versions, all_project_descriptions):
            result = []
            for version in versions:
                result += expand(project_name, version, all_project_descriptions)
            return result

        project_description.required_projects = { project_name: expand_all(project_name, versions, all_project_descriptions)
            for project_name, versions in project_description.required_projects.items() }

        return project_description

    def compute_effective_project_descriptions(self, specified_project_descriptions, requested_options=None):
        selected_project_descriptions = self.expand_dependencies(specified_project_descriptions)
        if not selected_project_descriptions:
            raise Exception("The specified set of project versions cannot be satisfied")
        return activate_project_options(selected_project_descriptions, requested_options)

    def expand_dependencies(self, specified_project_descriptions, return_all=False):
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
                    todo_list.append(self.get_project_description(ProjectReference.parse(project_name + "-" + project_versions[0])))
                required_project_names.append(project_name)
        required_project_names.reverse()
        # _logger.debug(f"{required_project_names=}")

        # 2. collect all available project versions for all required projects separately
        available_project_versions = { name: self.get_project_versions(name) for name in required_project_names }
        # _logger.debug(f"{available_project_versions=}")

        # 3. iterate over all combinations of the available project versions for the different required projects
        result = []
        sets = available_project_versions.values()
        keys = list(available_project_versions.keys())
        for combination in itertools.product(*sets):
            # _logger.debug(f"checking combination: {combination=}")
            accept_combination = True
            selected_project_descriptions = []
            # 4. turn the combination of version numbers (a tuple of strings) into a tuple of project descriptions
            for i in range(len(combination)):
                selected_project_name = f"{keys[i]}-{combination[i]}"
                selected_project_description = self.get_project_description(ProjectReference.parse(selected_project_name))
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
                        required_project_description = self.get_project_description(ProjectReference.parse(required_project_name + "-" + required_project_version))
                        if required_project_description in selected_project_descriptions:
                            accept_selected_project_description = True
                    if not accept_selected_project_description:
                        # _logger.debug(f"  rejecting {required_project_name} {required_project_versions}")
                        accept_combination = False
                        break
            if accept_combination:
                if return_all:
                    result.append(selected_project_descriptions)
                else:
                    return selected_project_descriptions
        return result

def activate_project_options(project_descriptions, requested_options):
    # check requested options exist at all
    all_supported_options = []
    for desc in project_descriptions:
        all_supported_options += desc.get_supported_options()
    all_supported_options = list(set(all_supported_options))
    for option in requested_options or []:
        if option not in all_supported_options:
            raise Exception(f"None of the selected projects supports option '{option}'")
    # create and return updated project descriptions
    return [desc.activate_project_options(requested_options) for desc in project_descriptions]

class Workspace:
    # project states
    ABSENT = "ABSENT"
    INCOMPLETE = "INCOMPLETE"
    DOWNLOADED = "DOWNLOADED"

    WORKSPACE_ADMIN_DIR = ".opp_env_workspace"
    PROJECT_ADMIN_DIR = ".opp_env"

    def __init__(self, root_directory, nixless=False):
        assert(os.path.isabs(root_directory))
        self.root_directory = root_directory
        self.nixless = nixless
        if nixless:
            detect_tools()
        else:
            detect_nix()
        opp_env_directory = os.path.join(self.root_directory, self.WORKSPACE_ADMIN_DIR)
        if not os.path.exists(opp_env_directory):
            raise Exception(f"'{root_directory}' is not an opp_env workspace, run 'opp_env init' to turn in into one")
        _logger.debug(f"Workspace created, {root_directory=}, {nixless=}")

    @staticmethod
    def find_workspace(from_dir=None):
        dir = os.path.abspath(from_dir) if from_dir else os.getcwd()
        while True:
            if os.path.isdir(os.path.join(dir, Workspace.WORKSPACE_ADMIN_DIR)):
                return dir
            parent_dir = os.path.dirname(dir)
            if parent_dir == dir:
                break
            dir = parent_dir
        raise Exception(f"No opp_env workspace found in '{from_dir}' or its parent directories, run 'opp_env init' to create one")
        #return None

    @staticmethod
    def init_workspace(dir=None):
        if not dir:
            dir = os.getcwd()
        if not os.path.isdir(dir):
            raise Exception(f"Directory does not exist: {dir}")
        opp_env_dir = os.path.join(dir, Workspace.WORKSPACE_ADMIN_DIR)
        if os.path.isdir(opp_env_dir):
            raise Exception(f"'{dir}' is already an opp_env workspace")
        if re.search("\\s", dir):
            raise Exception(f"Whitespace characters are not allowed in the name and path of the workspace directory")
        os.mkdir(opp_env_dir)

    def get_workspace_admin_directory(self):
        return os.path.join(self.root_directory, self.WORKSPACE_ADMIN_DIR)

    def get_project_root_directory(self, project_description):
        return os.path.join(self.root_directory, project_description.get_full_folder_name())

    def get_project_admin_directory(self, project_description, create=False):
        dir = os.path.join(self.get_project_root_directory(project_description), self.PROJECT_ADMIN_DIR)
        if create and not os.path.isdir(dir):
            os.mkdir(dir)
        return dir

    def get_project_admin_file(self, project_description, filename, create_dir=False):
        return os.path.join(self.get_project_admin_directory(project_description, create=create_dir), filename)

    def print_project_state(self, project_description):
        _logger.info(f"Project {project_description.get_full_name(colored=True)} is {green(self.get_project_state(project_description))}, {self.check_project_state(project_description)}")

    def read_project_state_file(self, project_description):
        state_file_name = self.get_project_admin_file(project_description, "state")
        if not os.path.isfile(state_file_name):
            return {}
        with open(state_file_name) as f:
            return json.load(f)

    def write_project_state_file(self, project_description, data):
        state_file_name = self.get_project_admin_file(project_description, "state", create_dir=True)
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

    def download_project(self, project_description, effective_project_descriptions, patch=True, cleanup=True, **kwargs):
        _logger.info(f"Downloading project {cyan(project_description.get_full_name())} in workspace {cyan(self.root_directory)}")
        project_dir = self.get_project_root_directory(project_description)
        if os.path.exists(project_dir):
            raise Exception("f{project_dir} already exists")
        try:
            if project_description.download_commands:
                self.nix_develop(effective_project_descriptions, self.root_directory, project_description.download_commands, run_setenv=False, **kwargs)
            elif project_description.download_url:
                self.download_and_unpack_tarball(project_description.download_url, project_dir)
            elif project_description.git_url:
                branch_option = "-b " + project_description.git_branch if project_description.git_branch else ""
                #TODO maybe optionally use --single-branch
                self.run_command(f"git clone --config advice.detachedHead=false {branch_option} {project_description.git_url} {project_dir}")
            else:
                raise Exception(f"{project_description}: No download_url or download_commands in project description -- check project options for alternative download means (enter 'opp_env info {project_description}')")
            if not os.path.exists(project_dir):
                raise Exception(f"{project_description}: Download process did not create {project_dir}")

            if project_description.patch_commands or project_description.patch_url:
                if patch:
                    _logger.info(f"Patching project {cyan(project_description.get_full_name())}")
                    if project_description.patch_commands:
                        self.nix_develop(effective_project_descriptions, project_dir, project_description.patch_commands, run_setenv=False, **kwargs)
                    if project_description.patch_url:
                        self.download_and_apply_patch(project_description.patch_url, project_dir)
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

    def build_project(self, project_description, effective_project_descriptions, build_modes, **kwargs):
        assert(project_description.build_commands)
        for build_mode in build_modes:
            _logger.info(f"Building project {cyan(project_description.get_full_name())} in {cyan(build_mode)} mode in workspace {cyan(self.root_directory)}")
            project_dir = self.get_project_root_directory(project_description)
            self.nix_develop(effective_project_descriptions, project_dir, project_description.build_commands, build_mode=build_mode, **kwargs)

    def clean_project(self, project_description, effective_project_descriptions, build_modes, **kwargs):
        assert(project_description.clean_commands)
        for build_mode in build_modes:
            _logger.info(f"Cleaning project {cyan(project_description.get_full_name())} in {cyan(build_mode)} in workspace {cyan(self.root_directory)}")
            project_dir = self.get_project_root_directory(project_description)
            self.nix_develop(effective_project_descriptions, project_dir, project_description.clean_commands, build_mode=build_mode, **kwargs)

    def mark_project_state(self, project_description):
        # exclude the Simulation IDE's directory from the md5sum, because ./configure and eclipse itself modifies stuff in it
        dir = self.get_project_root_directory(project_description)
        admin_dir = self.get_project_admin_directory(project_description)
        ide_dir = os.path.join(dir, "ide")
        file_list_file_name = self.get_project_admin_file(project_description, "filelist.md5", create_dir=True)
        self.run_command(f"find {dir} \\( -path {admin_dir} -o -path {ide_dir} \\) -prune -o -type f -print0 | xargs -0 md5sum > {file_list_file_name}")

    def check_project_state(self, project_description):
        file_list_file_name = self.get_project_admin_file(project_description, "filelist.md5")
        if not os.path.exists(file_list_file_name):
            return red('UNKNOWN -- project state not yet marked')
        # note: this won't detect if extra files were added to the project
        result = self.run_command(f"md5sum -c --quiet {file_list_file_name} > {file_list_file_name + '.out'}", suppress_stdout=True, check_exitcode=False)
        return green("UNMODIFIED") if result.returncode == 0 else f"{red('MODIFIED')} -- see {file_list_file_name + '.out'} for details"

    def setup_environment(self, projects, requested_options=None, pause_after_warnings=True, **kwargs):
        global project_registry
        specified_project_descriptions = resolve_projects(projects)
        effective_project_descriptions = project_registry.compute_effective_project_descriptions(specified_project_descriptions, requested_options)
        _logger.info(f"Using specified projects {cyan(str(specified_project_descriptions))} with effective projects {cyan(str(effective_project_descriptions))} in workspace {cyan(self.root_directory)}")
        self._print_project_warnings(effective_project_descriptions, pause_after_warnings)
        return effective_project_descriptions

    def _print_project_warnings(self, project_descriptions, pause_after_warnings=True):
        have_warnings = False
        for p in project_descriptions:
            if p.warnings:
                for warning in p.warnings:
                    have_warnings = True
                    _logger.warning(f"Project {cyan(p)}: {warning}")
        if pause_after_warnings and have_warnings and sys.stdin.isatty():
            input("Press Enter to continue, or Ctrl+C to abort ")

    @staticmethod
    def _get_unique_project_attribute(project_descriptions, attr_name):
        values = set([getattr(p, attr_name) for p in project_descriptions if getattr(p, attr_name)])
        if not values:
            raise Exception(f"None of the projects specify the '{attr_name}' attribute")
        elif len(values) > 1:
            raise Exception(f"The projects disagree on the choice of '{attr_name}': {values}")
        else:
            return list(values)[0]

    def download_project_if_needed(self, project_description, effective_project_descriptions, prepare_missing=True, patch=True, cleanup=True, **kwargs):
        project_state = self.get_project_state(project_description)
        if not prepare_missing and project_state in [Workspace.ABSENT, Workspace.INCOMPLETE]:
            raise Exception(f"Project '{project_description}' is missing or incomplete")
        elif project_state == Workspace.ABSENT:
            self.download_project(project_description, effective_project_descriptions, patch, cleanup, **kwargs)
        elif project_state == Workspace.INCOMPLETE:
            raise Exception(f"Cannot download '{project_description}': Directory already exists")
        else:
            self.print_project_state(project_description)
        assert self.get_project_state(project_description) == Workspace.DOWNLOADED

    def _read_file_if_exists(self, fname):
        try:
            with open(fname) as f:
                return f.read()
        except:
            return ""

    def download_and_unpack_tarball(self, download_url, target_folder):
        os.makedirs(target_folder)
        wget_log_file = os.path.join(target_folder, "wget.log")
        tar_log_file = os.path.join(target_folder, "tar.log")
        try:
            self.run_command(f"cd {target_folder} && wget -O - -nv -o {wget_log_file} --show-progress {download_url} | tar --strip-components=1 -xzf - 2>{tar_log_file}")
            os.remove(wget_log_file)
            os.remove(tar_log_file)
        except Exception as e:
            print(self._read_file_if_exists(wget_log_file).strip())
            print(self._read_file_if_exists(tar_log_file).strip())
            raise e

    def download_and_apply_patch(self, patch_url, target_folder):
        wget_log_file = os.path.join(target_folder, "wget.log")
        patching_log_file = os.path.join(target_folder, "patch.log")
        try:
            self.run_command(f"cd {target_folder} && wget -O - -nv -o {wget_log_file} --show-progress {patch_url} | git apply --whitespace=nowarn - 2>{patching_log_file}")
            os.remove(wget_log_file)
            os.remove(patching_log_file)
        except Exception as e:
            print(self._read_file_if_exists(wget_log_file).strip())
            print(self._read_file_if_exists(patching_log_file).strip())
            raise e

    def nix_develop(self, effective_project_descriptions, working_directory=None, commands=[], vars_to_keep=None, run_setenv=True, interactive=False, isolated=True, check_exitcode=True, suppress_stdout=False, build_mode=None, tracing=False, **kwargs):
        nixos = Workspace._get_unique_project_attribute(effective_project_descriptions, "nixos")
        stdenv = Workspace._get_unique_project_attribute(effective_project_descriptions, "stdenv")

        session_name = '+'.join([str(d) for d in reversed(effective_project_descriptions)])
        project_shell_hook_commands = sum([p.shell_hook_commands for p in effective_project_descriptions if p.shell_hook_commands], [])
        project_nix_packages = sum([p.external_nix_packages for p in effective_project_descriptions], [])
        project_vars_to_keep = sum([p.vars_to_keep for p in effective_project_descriptions], [])
        project_setenv_commands = sum([[f"cd '{self.get_project_root_directory(p)}'", *p.setenv_commands] for p in effective_project_descriptions], [])
        project_root_environment_variable_assignments = [f"export {p.name.upper()}_ROOT={self.get_project_root_directory(p)}" for p in effective_project_descriptions]

        # a custom prompt spec to help users distinguish an opp_env shell from a normal terminal session
        prompt = f"\\[\\e[01;33m\\]{session_name}\\[\\e[00m\\]:\[\\e[01;34m\\]\\w\[\\e[00m\\]\\$ "

        nixful = not self.nixless

        is_macos = platform.system().lower() == "darwin"
        nproc_command = "nproc" if not is_macos else "sysctl -n hw.ncpu"

        shell_hook_lines = [
            'error() { echo "$*" 1>&2; return 1; }; export -f error',
            f"export BUILD_MODE={build_mode or ''}",
            *project_root_environment_variable_assignments,
            *(project_shell_hook_commands if nixful else []),
            f"export NIX_BUILD_CORES=$({nproc_command})" if self.nixless else None, # otherwise Nix defines it
            f"export PS1='{prompt}'" if interactive and nixful else None,
            *(["pushd . > /dev/null", *project_setenv_commands, "popd > /dev/null"] if run_setenv else []),
            f"cd '{working_directory}'" if working_directory else None,
            *commands
        ]

        vars_to_keep = (vars_to_keep or []) + project_vars_to_keep
        script = join_lines(shell_hook_lines)

        if nixful:
            return self._do_nix_develop(nixos=nixos, stdenv=stdenv, nix_packages=project_nix_packages,
                        session_name=session_name, script=script, vars_to_keep=vars_to_keep, interactive=interactive,
                        isolated=isolated, check_exitcode=check_exitcode, suppress_stdout=suppress_stdout, tracing=tracing)
        else:
            if interactive:
                # launch an interactive bash session; setting PROMPT_COMMAND ensures the custom prompt
                # takes effect despite PS1 normally being overwritten by the user's profile and rc files
                script += f"\nPROMPT_COMMAND=\"PS1='{prompt}'\" bash -i"
            return self._do_run_command(script, suppress_stdout=suppress_stdout, check_exitcode=check_exitcode, tracing=tracing)

    def _do_nix_develop(self, nixos, stdenv, nix_packages=[], session_name="", script="", vars_to_keep=None, interactive=False, isolated=True, check_exitcode=True, suppress_stdout=False, tracing=False):
        if not nixos or not stdenv:
            raise Exception(f"The nixos or stdenv field is not defined in any of the effective projects! {nixos=} {stdenv=}")

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
                        name = "@SESSION_NAME@";
                        hardeningDisable = [ "all" ];
                        buildInputs = with pkgs; [ @PACKAGES@ bashInteractive ];
                        shellHook = ''
                            set @SHELL_OPTIONS@
                            @SCRIPT@
                        '';
                    };
                };
            });
        }"""

        tools_nix_packages = ["bashInteractive", "git", "openssh", "wget", "gzip", "which", "gnused", "gnutar", "findutils", "coreutils"]
        nix_packages = uniq(nix_packages + tools_nix_packages)

        shell_options = "-exo pipefail" if tracing else "-eo pipefail"
        flake_dir = self.get_workspace_admin_directory()
        flake_file_name = os.path.join(flake_dir, "flake.nix")
        with open(flake_file_name, "w") as f:
            nix_develop_flake = (nix_develop_flake
                .replace("@NIXOS@", nixos)
                .replace("@STDENV@", stdenv)
                .replace("@SESSION_NAME@", session_name)
                .replace("@PACKAGES@", " ".join(nix_packages))
                .replace("@SHELL_OPTIONS@", shell_options)
                .replace("@SCRIPT@", script)
            )
            f.write(nix_develop_flake)

        _logger.debug(f"Using {nixos}, {stdenv}, packages: {' '.join(nix_packages)}")
        _logger.debug(f"Nix flake shellHook script:\n{indent(script)}")
        #_logger.debug(f"Nix flake file {cyan(flake_file_name)}:\n{yellow(nix_develop_flake)}")
        vars_to_keep = (vars_to_keep or []) + ['HOME', 'TERM', 'COLORTERM', 'DISPLAY', 'XAUTHORITY', 'XDG_RUNTIME_DIR', 'XDG_DATA_DIRS', 'XDG_CACHE_HOME', 'QT_AUTO_SCREEN_SCALE_FACTOR']
        isolation_options = ('-i ' + ' '.join(['-k ' + varname for varname in vars_to_keep])) if isolated else ''
        command = '-c bash --norc' if interactive else '-c true'
        nix_develop_command = f"nix --extra-experimental-features nix-command --extra-experimental-features flakes develop {isolation_options} {flake_dir} {command}"

        env = dict(os.environ)

        if isolated:
            # some programs prefer the home directory to exist and be writable
            temp_home = tempfile.mkdtemp()
            env["HOME"] = temp_home

        # This is a workaround for an error message that is printed multiple times when the "shell" command starts e.g. with Ubuntu 22.04 Unity desktop:
        # ERROR: ld.so: object 'libgtk3-nocsd.so.0' from LD_PRELOAD cannot be preloaded (cannot open shared object file): ignored.
        # The reason is that under NIX, the lib's directory is not in the default linker path. Workaround: use full path for lib.
        gtk3_lib_fname = "libgtk3-nocsd.so.0"
        gtk3_lib_dir = "/usr/lib/x86_64-linux-gnu/"
        if "LD_PRELOAD" in env and gtk3_lib_fname in env["LD_PRELOAD"].split(":") and os.path.isfile(gtk3_lib_dir + gtk3_lib_fname):
            def replace_in_list(list, old_value, new_value):
                return [new_value if x == old_value else x for x in list]
            env["LD_PRELOAD"] = ":".join(replace_in_list(env["LD_PRELOAD"].split(":"), gtk3_lib_fname, gtk3_lib_dir + gtk3_lib_fname))

        # This is a workaround for the following warning printed by Perl:
        # perl: warning: Setting locale failed. / Please check that your locale settings: / LANGUAGE = (unset), / LC_ALL = (unset), ... / Falling back to the standard locale ("C").
        env["LC_ALL"] = "C"

        result = self._do_run_command(nix_develop_command, env=env, suppress_stdout=not interactive and suppress_stdout, check_exitcode=check_exitcode)

        # cleanup: remove temporary home dir, as we don't want it to interfere with subsequent sessions
        if isolated:
            shutil.rmtree(temp_home)
        return result

    def run_command(self, command, suppress_stdout=False, check_exitcode=True, tracing=False):
        global project_registry
        if not self.nixless:
            reference_project_description = project_registry.get_project_description("omnetpp-latest").activate_project_options([], quiet=True)
            return self._do_nix_develop(nixos=reference_project_description.nixos,
                        stdenv=reference_project_description.stdenv,
                        session_name="run_command", script=command,
                        interactive=False, isolated=True, suppress_stdout=suppress_stdout, check_exitcode=check_exitcode, tracing=tracing)
        else:
            return self._do_run_command(command, suppress_stdout=suppress_stdout, check_exitcode=check_exitcode, tracing=tracing)

    def _do_run_command(self, command, env=None, suppress_stdout=False, check_exitcode=True, tracing=False):
        if "\n" not in command:
            _logger.debug(f"Running command: {command}")
        else:
            _logger.debug(f"Running command:\n{indent(command)}")

        # make the script exit on first error, and also on errors in piped commands
        options = "-exo pipefail" if tracing else "-eo pipefail"
        command = f"set {options}; {command}"

        result = subprocess.run(["bash", "-c", command],
                                env=env,
                                stdout=subprocess.DEVNULL if suppress_stdout else sys.stdout,
                                stderr=subprocess.STDOUT if suppress_stdout else sys.stderr)
        _logger.debug(f"Exit code: {result.returncode}")
        if check_exitcode and result.returncode != 0:
            raise Exception(f"Child process exit code {result.returncode}")
        return result

def resolve_projects(project_full_names):
    global project_registry
    project_descriptions = [project_registry.get_project_description(ProjectReference.parse(p)) for p in project_full_names]
    return project_descriptions

def resolve_workspace(workspace_directory):
    workspace_directory = os.path.abspath(workspace_directory) if workspace_directory else Workspace.find_workspace(os.getcwd())
    return workspace_directory

def list_subcommand_main(project_name_patterns=None, list_mode="grouped", **kwargs):
    global project_registry
    projects = project_registry.get_all_project_descriptions()
    if project_name_patterns:
        tmp = []
        for project_name_pattern in project_name_patterns:
            matching_projects = [p for p in projects if re.match(project_name_pattern, p.get_full_name())]
            if not matching_projects:
                raise Exception(f"Name/pattern '{project_name_pattern}' does not match any project")
            tmp += matching_projects
        projects = tmp # NOTE: No sorting! Order of project versions is STRICTLY determined by the order they are in ProjectRegistry.

    names = uniq([p.name for p in projects])
    if list_mode == "flat":
        for p in projects:
            print(p.get_full_name())
    elif list_mode == "grouped":
        for name in names:
            versions = [p.version for p in projects if p.name == name]
            print(f"{name:<10} {cyan('  '.join(versions))}")
    elif list_mode == "names":
        for name in names:
            print(name)
    elif list_mode == "expand":
        for project in projects:
            expanded = project_registry.expand_dependencies([project])
            print(project, "-->", expanded)
    elif list_mode == "combinations":
        grouped = False #TODO
        if grouped:
            for project in projects:
                combinations_list = project_registry.expand_dependencies([project], return_all=True)
                print(project, "-->", combinations_list)
        else:
            for project in projects:
                combinations_list = project_registry.expand_dependencies([project], return_all=True)
                for combination in combinations_list:
                    print(" ".join([p.get_full_name() for p in reversed(combination)]))

    else:
        raise Exception(f"invalid list mode '{list_mode}'")

def init_subcommand_main(workspace_directory=None, **kwargs):
    workspace_directory = workspace_directory or os.getcwd()
    Workspace.init_workspace(workspace_directory)
    _logger.info(f"Workspace created in folder {cyan(workspace_directory)}")

def info_subcommand_main(projects, raw=False, requested_options=None, **kwargs):
    # resolve project list
    global project_registry
    if not projects:
        project_descriptions = project_registry.get_all_project_descriptions()
    else:
        project_descriptions = []
        for project in projects:
            if '-' in project:
                project_descriptions += [project_registry.get_project_description(ProjectReference.parse(project))]
            elif project in project_registry.get_project_names():
                project_descriptions += [project_registry.get_project_description(ProjectReference(project, version)) for version in project_registry.get_project_versions(project)]
            else:
                raise Exception(f"Unknown project name '{project}'")

    if raw:
        serializable = [vars(p.activate_project_options(requested_options)) for p in project_descriptions]
        print(json.dumps(serializable, indent=4))
        return

    # print info for each
    for project_description in project_descriptions:
        project_description = project_description.activate_project_options(requested_options)
        print()
        print(project_description.get_full_name() + (": " + project_description.description if project_description.description else ""))
        if project_description.warnings:
            for warning in project_description.warnings:
                print(yellow("\nWARNING: ") + warning)
        if (project_description.options):
            print("\nAvailable options:")
            for option_name, option in project_description.options.items():
                option_description = option.get('option_description')
                default_mark = "*" if option.get('is_default') else "";
                if option_description:
                    print(f"- {cyan(option_name)}{default_mark}: {option_description}")
                else:
                    print(f"- {cyan(option_name)}{default_mark}")
        if (project_description.required_projects):
            print(f"\nRequires:")
            for name, versions in project_description.required_projects.items():
                print(f"- {cyan(name)}: {' / '.join(versions)}")
        if len(project_descriptions) > 1:
            print("\n--------")
    print()
    print("Note: Specify `--raw` to `opp_env info` for more details.")
    print("Note: Options can be selected by adding `--options <optionname>` to the opp_env command line, see help. Options active by default are marked with '*'.")

def download_subcommand_main(projects, workspace_directory=None, requested_options=None, skip_dependencies=True, nixless=False, **kwargs):
    global project_registry
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory, nixless)
    specified_project_descriptions = resolve_projects(projects)
    if skip_dependencies:
        effective_project_descriptions = activate_project_options(specified_project_descriptions, requested_options)
    else:
        effective_project_descriptions = project_registry.compute_effective_project_descriptions(specified_project_descriptions, requested_options)
        _logger.info(f"Using specified projects {cyan(str(specified_project_descriptions))} with effective projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")
    for project_description in effective_project_descriptions:
        workspace.download_project_if_needed(project_description, effective_project_descriptions, **kwargs)

def build_subcommand_main(projects, workspace_directory=None, prepare_missing=True, requested_options=None, mode=None, nixless=False, **kwargs):
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory, nixless)
    effective_project_descriptions = workspace.setup_environment(projects, requested_options, **kwargs)
    build_modes = mode if mode else ["debug", "release"]
    for project_description in effective_project_descriptions:
        workspace.download_project_if_needed(project_description, effective_project_descriptions, prepare_missing, **kwargs)
    for project_description in effective_project_descriptions:
        assert workspace.get_project_state(project_description) == Workspace.DOWNLOADED
        if project_description.build_commands:
            workspace.build_project(project_description, effective_project_descriptions, build_modes, **kwargs)
    _logger.info(f"Build finished for projects {cyan(effective_project_descriptions)} in workspace {cyan(workspace_directory)}")

def clean_subcommand_main(projects, workspace_directory=None, prepare_missing=True, requested_options=None, mode=None, nixless=False, **kwargs):
    #TODO shouldn't there be a "realclean" command that deletes all files NOT in the file list??
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory, nixless)
    effective_project_descriptions = workspace.setup_environment(projects, requested_options, **kwargs)
    build_modes = mode if mode else ["debug", "release"]
    for project_description in effective_project_descriptions:
        workspace.download_project_if_needed(project_description, effective_project_descriptions, prepare_missing, **kwargs)
    for project_description in reversed(effective_project_descriptions):
        if project_description.clean_commands:
            workspace.clean_project(project_description, effective_project_descriptions, build_modes, **kwargs)
    _logger.info(f"Clean finished for projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")

def is_subdirectory(child_dir, parent_dir):
    # Check if a directory is a subdirectory of another directory.
    return os.path.commonpath([child_dir, parent_dir]) == parent_dir

def shell_subcommand_main(projects, workspace_directory=[], prepare_missing=True, chdir=False, requested_options=None, build=True, mode=None, nixless=False, isolated=True, **kwargs):
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory, nixless)
    effective_project_descriptions = workspace.setup_environment(projects, requested_options, **kwargs)
    for project_description in effective_project_descriptions:
        workspace.download_project_if_needed(project_description, effective_project_descriptions, prepare_missing, **kwargs)
    if build:
        try:
            build_modes = mode if mode else ["debug", "release"]
            for project_description in effective_project_descriptions:
                assert workspace.get_project_state(project_description) == Workspace.DOWNLOADED
                if project_description.build_commands:
                    workspace.build_project(project_description, effective_project_descriptions, build_modes, **kwargs)
        except Exception as e:
            # print error but continue bringing up the shell to give user a chance to fix the problem
            _logger.error(f"An error occurred while building affected projects: {red(e)}")

    kind = "nixless" if nixless else "isolated" if isolated else "non-isolated"
    _logger.info(f"Starting {cyan(kind)} shell for projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)}")

    if chdir and projects:
        first_project_description = resolve_projects(projects)[0]
        first_project_dir = workspace.get_project_root_directory(first_project_description)
        if chdir == "if-outside":
            chdir = not is_subdirectory(os.getcwd(), first_project_dir)  # "is outside the project dir"
        if chdir:
            _logger.debug(f"Changing into the first project's directory {cyan(first_project_dir)}")
            os.chdir(first_project_dir)
        else:
            _logger.debug(f"No need to change directory, wd={cyan(os.getcwd())} is already under the first project's directory {cyan(first_project_dir)}")

    workspace.nix_develop(effective_project_descriptions, interactive=True, isolated=isolated, check_exitcode=False, **kwargs)

def run_subcommand_main(projects, command=None, workspace_directory=None, prepare_missing=True,requested_options=None, build=True, mode=None, nixless=False,  isolated=True, **kwargs):
    workspace_directory = resolve_workspace(workspace_directory)
    workspace = Workspace(workspace_directory, nixless)
    effective_project_descriptions = workspace.setup_environment(projects, requested_options, **kwargs)
    for project_description in effective_project_descriptions:
        workspace.download_project_if_needed(project_description, effective_project_descriptions, prepare_missing, **kwargs)
    if build:
        build_modes = mode if mode else ["debug", "release"]
        for project_description in effective_project_descriptions:
            assert workspace.get_project_state(project_description) == Workspace.DOWNLOADED
            if project_description.build_commands:
                workspace.build_project(project_description, effective_project_descriptions, build_modes, **kwargs)
    kind = "nixless" if nixless else "isolated" if isolated else "non-isolated"
    _logger.info(f"Running command for projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace_directory)} in {cyan(kind)} mode")
    workspace.nix_develop(effective_project_descriptions, workspace_directory, [command], **dict(kwargs, suppress_stdout=False))

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

project_registry = ProjectRegistry()


if __name__ == '__main__':
    sys.exit(main())
