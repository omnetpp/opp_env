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

_logger = logging.getLogger(__file__)

def repr(object):
    return f"{object.__class__.__name__}({', '.join([f'{prop}={value}' for prop, value in object.__dict__.items()])})"

COLOR_GRAY = "\033[38;20m"
COLOR_RED = "\033[1;31m"
COLOR_YELLOW = "\033[1;33m"
COLOR_CYAN = "\033[0;36m"
COLOR_GREEN = "\033[0;32m"
COLOR_RESET = "\033[0;0m"

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
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-q", "--quiet", action=argparse.BooleanOptionalAction, default=False, help="Suppress the standard output of executed commands")
    parser.add_argument("-l", "--log-level", choices=["ERROR", "WARN", "INFO", "DEBUG"], default="INFO", help="Verbose output mode")
    parser.add_argument("-w", "--workspace", dest="workspace_directory", help="Workspace directory")
    parser.add_argument("-x", "--handle-exception", action=argparse.BooleanOptionalAction, default=True, help="Don't print exception stacktrace")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", required=True)

    parser_list = subparsers.add_parser("list", help="Lists all available projects")

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

def run_command(command, quiet=False, **kwargs):
    _logger.debug(f"Running command: {command}")
    result = subprocess.run(["bash", "-c", command],
                            stdout=subprocess.DEVNULL if quiet else sys.stdout,
                            stderr=subprocess.STDOUT if quiet else sys.stderr)
    assert(result.returncode==0)

class Workspace:
    def __init__(self, root_directory):
        assert(os.path.isabs(root_directory))
        self.root_directory = root_directory
        opp_env_directory = os.path.join(self.root_directory, ".opp_env")
        if not os.path.exists(opp_env_directory):
            os.mkdir(opp_env_directory)

    def get_project_root_directory(self, project_description):
        return os.path.join(self.root_directory, project_description.get_full_folder_name())

    def print_project_status(self, project_description):
        _logger.info(f"Project {project_description.get_full_name(colored=True)} is {self.check_project_status(project_description)}")

    def is_project_downloaded(self, project_description):
        return os.path.exists(self.get_project_root_directory(project_description))

    def download_project(self, project_description, **kwargs):
        _logger.info(f"Downloading project {COLOR_CYAN + project_description.get_full_name() + COLOR_RESET} in workspace {COLOR_CYAN + self.root_directory + COLOR_RESET}")
        run_command(f"cd {self.root_directory} && {project_description.download_command}", **kwargs)
        # TODO run patch_command

    def configure_project(self, project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs):
        _logger.info(f"Configuring project {COLOR_CYAN + project_description.get_full_name() + COLOR_RESET} in workspace {COLOR_CYAN + self.root_directory + COLOR_RESET}")
        nix_develop(self.root_directory, effective_project_descriptions, external_nix_packages, f"{' && '.join(project_setenv_commands)} && cd {self.get_project_root_directory(project_description)} && {project_description.configure_command}", **kwargs)

    def build_project(self, project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs):
        _logger.info(f"Building project {COLOR_CYAN + project_description.get_full_name() + COLOR_RESET} in workspace {COLOR_CYAN + self.root_directory + COLOR_RESET}")
        nix_develop(self.root_directory, effective_project_descriptions, external_nix_packages, f"{' && '.join(project_setenv_commands)} && cd {self.get_project_root_directory(project_description)} && {project_description.build_command}", **kwargs)

    def clean_project(self, project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs):
        _logger.info(f"Cleaning project {COLOR_CYAN + project_description.get_full_name() + COLOR_RESET} in workspace {COLOR_CYAN + self.root_directory + COLOR_RESET}")
        nix_develop(self.root_directory, effective_project_descriptions, external_nix_packages, f"{' && '.join(project_setenv_commands)} && cd {self.get_project_root_directory(project_description)} && {project_description.clean_command}", **kwargs)

    def check_project_status(self, project_description):
        file_list_file_name = os.path.join(self.root_directory, ".opp_env/" + project_description.get_full_folder_name() + ".txt")
        md5_file_name = os.path.join(self.root_directory, ".opp_env/" + project_description.get_full_folder_name() + ".md5")
        if not os.path.exists(file_list_file_name):
            run_command(f"find {self.get_project_root_directory(project_description)} -type f | egrep -v '(bin/|doc/|ide/|media/|out/|results/|\\.log|\\.a|\\.so|\\.metadata|\\.jar|\\.png|\\.jpg)' > {file_list_file_name}")
            run_command(f"cat {file_list_file_name} | xargs -I ARG md5sum 'ARG' | sort | md5sum > {md5_file_name}")
        run_command(f"cat {file_list_file_name} | xargs -I ARG md5sum 'ARG' | sort | md5sum > {md5_file_name}.new")
        with open(md5_file_name, "r") as old_file:
            with open(md5_file_name + ".new", "r") as new_file:
                return COLOR_GREEN + "UNMODIFIED" + COLOR_RESET if old_file.read() == new_file.read() else COLOR_RED + "MODIFIED" + COLOR_RESET

class ProjectDescription:
    def __init__(self, name, version, description=None, stdenv="llvmPackages_14.stdenv", folder_name=None, required_projects={}, external_nix_packages=[], download_command=None, patch_command=None, setenv_command=None, configure_command=None, build_command=None, clean_command=None):
        self.name = name
        self.version = version
        self.description = description
        self.stdenv = stdenv
        self.folder_name = folder_name or name
        self.required_projects = required_projects
        self.external_nix_packages = external_nix_packages
        self.download_command = download_command
        self.patch_command = patch_command
        self.setenv_command = setenv_command
        self.configure_command = configure_command
        self.build_command = build_command
        self.clean_command = clean_command

    def __repr__(self):
        return self.get_full_name()

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self, colored=False):
        return (COLOR_CYAN if colored else "") + self.name + "-" + self.version + (COLOR_RESET if colored else "")

    def get_full_folder_name(self):
        return f"{self.folder_name}-{self.version}"

def get_all_omnetpp_project_descriptions():
    import opp_env.omnetpp_versions
    return [ProjectDescription(**e) for e in opp_env.omnetpp_versions.get_all_omnetpp_versions()]

def get_all_inet_project_descriptions():
    import opp_env.inet_versions
    return [ProjectDescription(**e) for e in opp_env.inet_versions.get_all_inet_versions()]

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

def find_project_description(project_reference):
    project_descriptions = [x for x in get_all_project_descriptions() if x.name == project_reference.name and x.version == project_reference.version]
    if len(project_descriptions) == 0:
         raise Exception("Project description not found for " + str(project_reference))
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
        parts = string.split("-")
        return ProjectReference("-".join(parts[:-1]), parts[-1:][0])

    def get_full_name(self):
        return self.name + "-" + self.version

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

                        @SCRIPT@
                    '';
                };
            };
        });
}"""
    nix_develop_flake_file_name = os.path.join(workspace_directory, ".opp_env/flake.nix")
    omnetpp_project_description = next(filter(lambda project_description: project_description.name == "omnetpp", effective_project_descriptions))
    with open(nix_develop_flake_file_name, "w") as f:
        nix_develop_flake = nix_develop_flake.replace("@STDENV@", omnetpp_project_description.stdenv)
        nix_develop_flake = nix_develop_flake.replace("@NAME@", f"{'+'.join(map(str, effective_project_descriptions))}")
        nix_develop_flake = nix_develop_flake.replace("@PACKAGES@", " ".join(nix_packages))
        nix_develop_flake = nix_develop_flake.replace("@SCRIPT@", command)
        f.write(nix_develop_flake)
    nix_develop_command = f"nix --extra-experimental-features nix-command --extra-experimental-features flakes develop {'-i -k HOME -k DISPLAY -k XDG_RUNTIME_DIR -k XDG_CACHE_HOME -k QT_AUTO_SCREEN_SCALE_FACTOR ' if isolated else ''} {os.path.join(workspace_directory, '.opp_env')} {'' if interactive else '-c true'}"
    run_command(nix_develop_command, quiet=not interactive and quiet, **kwargs)

def resolve_projects(projects=[], workspace_directory=os.getcwd(), **kwargs):
    specified_project_references = list(map(ProjectReference.parse, projects))
    specified_project_descriptions = list(map(find_project_description, specified_project_references))
    effective_project_descriptions = compute_effective_project_descriptions(specified_project_descriptions)
    _logger.info(f"Using specified projects {COLOR_CYAN + str(specified_project_references) + COLOR_RESET} with effective projects {COLOR_CYAN + str(effective_project_descriptions) + COLOR_RESET} in workspace {COLOR_CYAN + workspace_directory + COLOR_RESET}")
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

def list_subcommand_main(**kwargs):
    print("\n".join(map(str, get_all_project_descriptions())))

def describe_subcommand_main(project, **kwargs):
    project_description = find_project_description(ProjectReference.parse(project))
    print(repr(project_description))

def download_subcommand_main(workspace_directory=os.getcwd(), **kwargs):
    workspace = Workspace(workspace_directory)
    effective_project_descriptions = resolve_projects(workspace_directory=workspace_directory, **kwargs)
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_status(project_description)
        else:
            workspace.download_project(project_description, **kwargs)

def configure_subcommand_main(workspace_directory=os.getcwd(), prepare_missing=True, **kwargs):
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(workspace_directory=workspace_directory, **kwargs)
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_status(project_description)
        elif prepare_missing:
            workspace.download_project(project_description, **kwargs)
        else:
            raise Exception("Project is missing")
        workspace.configure_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)

def build_subcommand_main(workspace_directory=os.getcwd(), prepare_missing=True, **kwargs):
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(workspace_directory=workspace_directory, **kwargs)
    project_build_commands = []
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_status(project_description)
        elif prepare_missing:
            workspace.download_project(project_description, **kwargs)
            if project_description.configure_command:
                workspace.configure_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
        else:
            raise Exception("Project is missing")
        project_build_commands.append(f"cd {workspace.get_project_root_directory(project_description)} && {project_description.build_command}")
    workspace.build_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)

def clean_subcommand_main(workspace_directory=os.getcwd(), prepare_missing=True, **kwargs):
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(workspace_directory=workspace_directory, **kwargs)
    project_clean_commands = []
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_status(project_description)
        elif prepare_missing:
            workspace.download_project(project_description, **kwargs)
            if project_description.configure_command:
                workspace.configure_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)
        else:
            raise Exception("Project is missing")
        project_clean_commands.append(f"cd {workspace.get_project_root_directory(project_description)} && {project_description.clean_command}")
    workspace.clean_project(project_description, effective_project_descriptions, external_nix_packages, project_setenv_commands, **kwargs)

def shell_subcommand_main(workspace_directory=os.getcwd(), prepare_missing=True, **kwargs):
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(workspace_directory=workspace_directory, **kwargs)
    downloaded_project_descriptions = []
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_status(project_description)
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
    _logger.info(f"Starting shell for projects {COLOR_CYAN + str(effective_project_descriptions) + COLOR_RESET} in workspace {COLOR_CYAN + workspace_directory + COLOR_RESET}")
    nix_develop(workspace_directory, effective_project_descriptions, external_nix_packages, f"pushd . > /dev/null && {' && '.join(project_setenv_commands)} && popd > /dev/null", interactive=True, **kwargs)

def run_subcommand_main(command=None, workspace_directory=os.getcwd(), prepare_missing=True, **kwargs):
    workspace = Workspace(workspace_directory)
    effective_project_descriptions, external_nix_packages, project_setenv_commands = setup_environment(workspace_directory=workspace_directory, **kwargs)
    downloaded_project_descriptions = []
    for project_description in effective_project_descriptions:
        if workspace.is_project_downloaded(project_description):
            workspace.print_project_status(project_description)
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
    _logger.info(f"Running command for projects {COLOR_CYAN + str(effective_project_descriptions) + COLOR_RESET} in workspace {COLOR_CYAN + workspace_directory + COLOR_RESET}")
    nix_develop(workspace_directory, effective_project_descriptions, external_nix_packages, f"{' && '.join(project_setenv_commands)} && cd {workspace_directory} && {command}", **dict(kwargs, quiet=False))

def main():
    kwargs = process_arguments()
    try:
        _logger.debug(f"Starting {COLOR_CYAN + kwargs['subcommand'] + COLOR_RESET} operation")
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
        _logger.debug(f"The {COLOR_CYAN + kwargs['subcommand'] + COLOR_RESET} operation completed succesfully")
    except Exception as e:
        if kwargs["handle_exception"]:
            _logger.error(f"The {COLOR_CYAN + kwargs['subcommand'] + COLOR_RESET} operation stopped with error: {str(e)}")
        else:
            raise e
    except KeyboardInterrupt:
        _logger.warning(f"The {COLOR_CYAN + kwargs['subcommand'] + COLOR_RESET} operation was interrupted by the user")

main()
