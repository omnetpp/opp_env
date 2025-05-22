import argparse
import copy
import itertools
import json
import logging
import os
import subprocess
import sys
import re
import shutil
import tempfile
import importlib
import importlib.metadata
import platform
from collections import OrderedDict

# make sure that this run-time version check is in synch with the metadata for python requirement in the project.toml file.
if sys.version_info < (3,9):
    v = sys.version_info
    print(f"Python version 3.9 or above is required, the current one is {v.major}.{v.minor}.{v.micro} ({sys.executable}).") # e.g. str.removeprefix()
    sys.exit(1)

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

def red(x): return colored(COLOR_RED, x)
def yellow(x): return colored(COLOR_YELLOW, x)
def cyan(x): return colored(COLOR_CYAN, x)
def green(x): return colored(COLOR_GREEN, x)
def gray(x): return colored(COLOR_GRAY, x)

def shell_esc(x): return x.replace("\u001b", "\\033")

SHELL_RED = shell_esc(COLOR_RED)
SHELL_YELLOW = shell_esc(COLOR_YELLOW)
SHELL_CYAN = shell_esc(COLOR_CYAN)
SHELL_GREEN = shell_esc(COLOR_GREEN)
SHELL_NOCOLOR = shell_esc(COLOR_RESET)

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
    # note: we resort to decorating each line with  "|| exit $?"
    # because "set -e" cannot be made to work reliably -- we tried!
    # see https://mywiki.wooledge.org/BashFAQ/105 for background
    return "\n".join([f"{{ {cmd}; }} || exit $?" for cmd in commands if cmd])

def topological_sort(nodes, is_edge):
    visited = set()
    stack = []

    def dfs_rec(node):
        visited.add(node)
        for neighbor in nodes:
            if neighbor not in visited and is_edge(node, neighbor):
                dfs_rec(neighbor)
        stack.append(node)

    for node in nodes:
        if node not in visited:
            dfs_rec(node)

    stack.reverse()
    return stack

def sort_by_project_dependencies(project_descriptions):
    def depends_on(project_a, project_b):
        return project_b.name in project_a.required_projects
    sorted = topological_sort(project_descriptions, depends_on)
    return sorted

def is_semver(version):
    # supported formats: "3.2", "3.2.1", "3.2p1" or "3.2.1.231125"
    # note: this only VERY loosely based on https://semver.org/ (see BNF grammar there)
    pattern = r'^(\d+)\.(\d+)(?:[.p](\d+))?(?:\.(\d+))?$'
    return re.match(pattern, version) is not None

def parse_semver(version):
    # supported formats: "3.2", "3.2.1", "3.2p1"
    pattern = r'^(\d+)\.(\d+)(?:[.p](\d+))?(?:\.(\d+))?$'
    match = re.match(pattern, version)
    if match is None:
        raise ValueError('Invalid version string: ' + version)
    major, minor, micro, nano = match.groups()
    return int(major), int(minor), int(micro) if micro is not None else 0, int(nano) if nano is not None else 0

def version_matches(wildcard_version, version):
    if not re.match(r"^[^*?]+(\.\*)?$", wildcard_version):
        raise Exception(f"Unsupported version pattern '{wildcard_version}', only '.*' is allowed at the end")
    if wildcard_version.endswith(".*"):
        truncated = wildcard_version[0:-2]
        return version == truncated or version.startswith(truncated+".") or version.startswith(truncated+"p") # "3.3.*" should match "3.3p1" too
    else:
        return wildcard_version == version

def create_arg_parser():
    def dedent(text):
        # remove the common indentation from all lines
        lines = text.split("\n")
        min_indent = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
        text = "\n".join(line[min_indent:] for line in lines)
        # join adjacent nonempty non-indented lines (i.e. join multi-line paragraphs into one line)
        text = re.sub(r"([^\n])\n(?=[^\s])", r"\1 ", text)
        return text

    parser = argparse.ArgumentParser(prog="opp_env", description=dedent(
        """
        Provides automated installation of various versions of OMNeT++ and
        simulation frameworks; enter 'opp_env list' for a list of supported
        projects. Projects are downloaded and built in dedicated directories
        called workspaces.

        The opp_env uses the Nix package manager (nixos.org) to provide a controlled
        software environment, ensuring specific versions of compilers, libraries, and
        tools are used for building and running simulations. It achieves isolation by
        modifying environment variables, mainly adjusting the PATH to prioritize the Nix
        store (a custom directory tree) over system directories. This method is not
        virtualization, so users still have access to the same file system and have the
        same permissions as they would in a regular host OS session.

        A typical session:

            $ mkdir workspace    # create and enter a workspace directory
            $ cd workspace
            $ opp_env init       # initialize the workspace
            $ opp_env install inet-latest  # download and build INET and a matching version of OMNeT++
            $ opp_env shell      # start an interactive shell for working with INET

        The above sequence may be written as a single command:

            $ opp_env shell -w workspace --init --install inet-latest

        Note: Our GitHub repository is at https://github.com/omnetpp/opp_env.
        """),
        epilog=
        "For command-specific help, type 'opp_env COMMAND -h'. For example, 'opp_env install -h' prints a "
        "detailed description and the available options of the 'install' subcommand.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--help-intro", default=False, action='store_true', help="Prints a short introduction to the opp_env tool")
    parser.add_argument("-d", "--debug", default=False, action='store_true', help="Equivalent to '--print-stacktrace --log-level DEBUG'")
    parser.add_argument("-l", "--log-level", choices=["ERROR", "WARN", "INFO", "DEBUG"], default="INFO", help="Log level of output")
    parser.add_argument("-p", "--print-stacktrace", default=False, action='store_true', help="Print stack trace on error")
    parser.add_argument("-v", "--version", action='version', version=get_version(), help="Print version information and exit")

    subparsers = parser.add_subparsers(help='', dest='subcommand', metavar='COMMAND')

    subparser = subparsers.add_parser("list", help="Lists all available projects", description=
        """
        Lists all available projects. If you want to add a new project to the database,
        send a pull request against our GitHub repository at https://github.com/omnetpp/opp_env,
        or simpler, open an issue and ask us to do it.
        """)
    subparser.add_argument("project_name_patterns", nargs="*", metavar="project-name-or-pattern", help=
                           "Project names, project names with versions, or in general, regular expressions that match "
                           "the beginning of the project names with versions to be selected. Omit to list all projects.")
    group = subparser.add_mutually_exclusive_group()
    group.add_argument("--flat", dest="list_mode", action="store_const", const="flat", help="List projects with available versions, one per line")
    group.add_argument("--grouped", dest="list_mode", action="store_const", const="grouped", help="List the available versions for each project")
    group.add_argument("--names", dest="list_mode", action="store_const", const="names", help="List project names only (without version numbers)")
    group.add_argument("--descriptions", dest="list_mode", action="store_const", const="descriptions", help="List project names with descriptions only, one per line")
    group.add_argument("--aliases", dest="list_mode", action="store_const", const="aliases", help="List version aliases for projects")
    group.add_argument("--matching", dest="list_mode", action="store_const", const="matching", help="List the version combinations in which the specified projects can be used together")
    group.add_argument("--expand", dest="list_mode", action="store_const", const="expand", help="List the default version combinations in which the specified projects can be used together, including dependencies. If no project is specified, it expands the dependency list of all projects")
    group.add_argument("--expand-all", dest="list_mode", action="store_const", const="expand-all", help="List all version combinations in which the specified projects can be used together, including dependencies. If no project is specified, it expands the dependency list of all projects.")

    subparser = subparsers.add_parser("info", help="Describes the specified project", description=
        """
        Prints the description(s) of the specified project(s). The default mode prints
        a human-readable summary; use '--raw' to get the full project description with all details.
        """)
    subparser.add_argument("projects", nargs="*", help=
        """
        The list of projects to describe. You can specify exact versions like 'inet-4.0' or project names like 'inet'.
        The latter will print info on all versions of the project. An empty list prints info on all projects.
        """)
    subparser.add_argument("--raw", action='store_true', default=False, help=
        """
        Print the full project descriptions in a raw form.
        The output includes details such as the download URL, the required projects with their acceptable versions,
        the required NIX packages, the patch / setenv / build / clean commands, the available installation options, and more.
        The output is well-formed JSON, so you can use tools like 'jq' to further query it and extract the desired data.
        """)
    subparser.add_argument("--options", action='append', metavar='[PROJECT:]NAME,...', help="Print the project description as if the given project options were selected")

    def add_argument(subparser, name):
        if name=="projects":     subparser.add_argument("projects", nargs="+", help=
            """
            List of projects with versions to work with, e.g. 'inet-4.2'.
            Abbreviated version numbers are understood as the latest minor/patchlevel version that
            matches the abbreviated version, e.g. 'inet-3' and 'inet-3.8' both refer to 'inet-3.8.3'.
            The pseudo-version 'latest' translates to the latest version of the project, e.g. 'inet-latest' stood for 'inet-4.5.0' at the time of writing.
            If the specified projects have dependencies, they will also be selected (unless the --no-deps option is present).
            When a project is installed from a git repository (for example, the "git" version of "inet" named 'inet-git'), the installed branch is
            usually the 'master' or 'main' branch. This can be overridden by specifying a branch name in the project name after an '@'
            character. For example, 'opp_env install inet-git@topic/mybranch' checks out 'topic/mybranch' from the git repo (the branch must exist),
            then patches and builds it in the same way it would with the 'master' branch. This is a convenient way to set up a work environment
            if you want to work on (or contribute to) a specific project.
            """)
        elif name=="projects-optional": subparser.add_argument("projects", nargs="*", help=
            """
            List of projects with versions to work with, e.g. 'inet-4.2'.
            Defaults to all projects in the workspace.
            Abbreviated version numbers are understood as the latest minor/patchlevel version that
            matches the abbreviated version, e.g. 'inet-3' and 'inet-3.8' both refer to 'inet-3.8.3'.
            The pseudo-version 'latest' translates to the latest version of the project, e.g. 'inet-latest' stood for 'inet-4.5.0' at the time of writing.
            If the specified projects have dependencies, they will also be selected (unless the --no-deps option is present).
            """)
        elif name=="quiet":      subparser.add_argument("-q", "--quiet", dest="suppress_stdout", default=False, action='store_true', help="Suppress the standard output of executed commands")
        elif name=="force-init": subparser.add_argument("-f", "--force", default=False, action='store_true', help="Force turning a non-empty directory into a workspace")
        elif name=="init":       subparser.add_argument("--init", default=False, action='store_true', help=
            "Turn the current directory (or the directory specified via -w/--workspace) into a workspace if it is not already one")
        elif name=="workspace":  subparser.add_argument("-w", "--workspace", metavar='DIR', dest="workspace_directory", help=
            """
            Specifies the workspace directory. When this option is missing and opp_env needs to find the workspace,
            it will do so by searching up from the current directory.
            """)
        elif name=="no-pause":   subparser.add_argument("-n", "--no-pause", dest="pause_after_warnings", default=True, action='store_false', help="Do not pause after printing warnings")
        elif name=="no-deps":    subparser.add_argument("--no-deps", "--no-dependency-resolution", dest="no_dependency_resolution", default=False, action='store_true', help=
            """
            Ignore dependencies among projects, only operate on the projects explicitly listed on the command line.
            This allows projects to be used together in previously untested or "unofficial" combinations.
            """)
        elif name=="options":    subparser.add_argument("--options", action='append', metavar='[PROJECT:]NAME,...', help=
            """
            Select project options to use; use 'opp_env info' to see what options a selected project has.
            An option applies to all effective projects that support them, unless qualified with a project name.
            """)
        elif name=="no-patch":   subparser.add_argument("--no-patch", dest="patch", default=True, action='store_false', help="Do not patch the project after download")
        elif name=="no-cleanup": subparser.add_argument("--no-cleanup", dest="cleanup", default=True, action='store_false', help=
            "Do not delete a partially downloaded project if download or patching fails or is interrupted")
        elif name=="nixless-workspace":    subparser.add_argument("--nixless-workspace", default=False, action='store_true', help=
            """
            When creating a workspace, designate the new workspace as nixless. In a nixless workspace, projects are installed and run without Nix.
            A nixless workspace requires that all packages that the projects and opp_env itself require are already installed and available in the system.
            For opp_env itself, this translates to having 'curl', 'git', 'tar', 'gzip' and other basic tools available for downloading and extracting packages.
            The packages that OMNeT++ requires, such as a C++ compiler, 'bison' and 'flex', are documented in the Installation Guide of the particular version.
            In addition to package availability, versions are also important. Nix ensures that definite versions of packages are used,
            but in nixless mode, the versions are those provided by the host OS. If they are incompatible, projects may fail to
            build or work correctly.
            """)
        elif name=="keep":       subparser.add_argument("-k", "--keep", action='append', metavar='NAME,...', help=
            "Keep the specified environment variables, i.e. pass them into shells spawned by opp_env.")
        elif name=="local":      subparser.add_argument("--local", default=False, action='store_true', help=
            """
            Replaces internet access with file access. When specified, opp_env will use a local downloads directory and
            locally cloned Git repositories as installation sources instead of network access.
            It expects the file system locations to be passed in via environment variables.
            It is primarily useful for testing purposes.
            """)
        elif name=="isolated":    subparser.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=False, help=
            """
            Run in a Nix-based isolated environment from the host operating system. The default is to run non-isolated.
            Isolated mode means that only programs (or in general, software packages) provided by Nix are accessible in the session,
            but those installed on the host OS are not. In non-isolated mode, both Nix and host OS programs are available.
            Non-isolated mode is convenient in an interactive shell session because it lets the user access all their installed software,
            such as their favorite text editor.
            However, due to the interference of various library versions in Nix and the host OS, etc, things can break in unexpected ways.
            """)
        elif name=="no-isolated": subparser.add_argument("-i", "--isolated", action=argparse.BooleanOptionalAction, default=True, help=
            """
            Run in a Nix-based isolated environment from the host operating system. The default is to run in an isolated environment.
            Isolated mode means that only programs (or in general, software packages) provided by Nix are accessible in the session,
            but those installed on the host OS are not. In non-isolated mode, both Nix and host OS programs are available.
            Non-isolated mode is convenient in an interactive shell session because it lets the user access all their installed software,
            such as their favorite text editor.
            However, due to the interference of various library versions in Nix and the host OS, etc, things can break in unexpected ways.
            """)
        elif name=="add-extra-nix-packages":  subparser.add_argument("--add-extra-nix-packages", dest='extra_nix_packages', action='append', metavar='PACKAGE,...', help=
            """
            Adds extra Nix packages to this *and* all future sessions of this workspace. The value is a comma-separated list of package names,
            e.g. 'graphviz' or 'openssh'. If a package name is bogus (no such Nix package), Nix will report it as "undefined variable",
            and the current list of extra Nix packages associated with the workspace won't be updated. The file that stores the
            current extra packages list is kept under the `.opp_env_workspace` subdirectory of the workspace, and can be edited or deleted
            by the user.
            """)
        elif name=="build-modes":  subparser.add_argument("--build-modes", metavar='MODE,...', default="release,debug",  help=
            """
            Defines the BUILD_MODES environment variable for the session, which is taken into account by many commands, e.g. `build_all`,
            `build_<projectname>`, `clean_all`, `clean_<projectname>`, and similar ones defined by opp_env.
            The value is a comma-separated list of build modes, e.g. 'release' or 'debug'.
            """)
        elif name=="install":    subparser.add_argument("--install", dest='install', default=False, action='store_true', help="Download and build missing projects")
        elif name=="build":      subparser.add_argument("--build", dest='build', default=False, action='store_true', help="Build projects")
        elif name=="no-build":   subparser.add_argument("--no-build", dest='install_without_build', default=False, action='store_true', help="Do not build the projects after download")
        elif name=="smoke-test": subparser.add_argument("--smoke-test", dest='run_smoke_test', default=False, action='store_true', help="Run a short test to ensure that the project executables are working")
        elif name=="test":       subparser.add_argument("--test", dest='run_test', default=False, action='store_true', help="Run the project's test suite to ensure it is working correctly")
        elif name=="chdir":      subparser.add_argument("--chdir", action=argparse.BooleanOptionalAction, default="convenience", help=
            """
            Whether to change into the workspace directory (--chdir), or stay in the current working directory (--no-chdir).
            If neither is given, the default action to try doing what is likely the most convenient for the user,
            which is to change into the root of the (first) project if the current working directory is outside that project's directory tree,
            and stay in the current directory (inside the project) otherwise.
            """)
        elif name=="chdir@run":  subparser.add_argument("--chdir", default=False, action='store_true', help=
            """
            Change into the workspace directory before running the command.
            (The default is to stay in the current directory.)
            """)
        elif name=="command":    subparser.add_argument("-c", "--command", help="""Specifies the command that is run in the environment""")
        else: raise Exception(f"Internal error: unrecognized option name '{name}'")

    def add_arguments(subparser, names):
        for name in names:
            add_argument(subparser, name)

    subparser = subparsers.add_parser("init", help="Designates the current working directory to be an opp_env workspace", description=dedent(
        """
        Designates the current working directory, or the directory specified via -w or --workspace,
        to be an opp_env workspace. The directory is expected to be empty.
        If the directory does not exist, it is created (only a single directory level).
        If the directory is already an opp_env workspace, an error is raised.
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_arguments(subparser, [
        "workspace",
        "force-init",
        "nixless-workspace"
    ])

    subparser = subparsers.add_parser("install", help="Downloads and builds the specified projects in their environment", description=dedent(
        """
        Downloads the specified project or projects along with their dependencies in the current workspace,
        patches or configures them as needed, and builds them.
        (The patching step is used for things like adjusting the setenv, Makefile or makefrag files
        so that dependencies are found, running the configure script, or applying minor changes
        to the source code to fix compilation errors due to compiler or library changes.)

        The download step is skipped for projects that are already downloaded.
        Any step of the process can be turned off using command-line options.
        Installation by cloning the Git repository and checking out a specific branch
        (for setting up a development environment for contributing to the project) is also supported.

        To ensure maximum reproducibility, the 'install' command runs the session in isolated mode.
        This can be changed by specifying the '--non-isolated' option.

        Examples:
            $ opp_env install inet-latest  # installs the latest version of INET, with a matching OMNeT++ version
            $ opp_env install inet-latest omnetpp-6.0.1  # like above, but with a specific OMNeT++ version
            $ opp_env install inet-latest --no-deps --no-patch --no-build  # downloads and unpacks INET only (without patching/building it)
            $ opp_env install inet-git  # installs INET by checking out the 'master' branch from its Git repository
            $ opp_env install inet-4.2.10 --options=inet:from-git  # installs INET by checking out the 'v4.2.10' tag from its Git repository
            $ opp_env install inet-git@topic/mybranch  # installs INET by checking out the 'topic/mybranch' branch from its Git repository, allowing further development
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_arguments(subparser, [
        "projects",
        "quiet",
        "init",
        "nixless-workspace",
        "workspace",
        "options",
        "add-extra-nix-packages",
        "smoke-test",
        "test",
        "no-deps",
        "no-pause",
        "no-cleanup",
        "no-patch",
        "no-build",
        "build-modes",
        "no-isolated",
        "keep",
        "local"
    ])

    subparser = subparsers.add_parser("shell", help="Opens a shell in the environment of the specified projects", description=dedent("""
        Opens a shell in the environment of the specified projects.
        If no projects are specified, all projects in the current workspace are used.
        Many options are available to request additional operations (building, testing, or
        even workspace initialization and project installation) and for controlling further details.

        The shell opens with the environment variables already set up for working with the projects,
        e.g. the 'setenv' scripts (of projects that have one) are sourced. Additionally, the location of each project
        is made available in its '<projectname>_ROOT' environment variable: 'OMNETPP_ROOT', 'INET_ROOT', etc.
        The 'BUILD_MODES' environment variable contains the build modes passed to the '--build-modes' option.

        Shortcut commands are also available in the shell for building, cleaning, checking, etc.
        each project: 'build_inet', 'build_omnetpp', 'build_all', 'clean_inet', 'clean_omnetpp', 'clean_all', etc.
        These commands accept one or more build modes, such as 'debug' or 'release'; if none is specified,
        the default is the modes in the 'BUILD_MODES' environment variable.
        The 'check_inet', check_omnetpp', 'check_all', etc. commands verify that the projects' files
        have not been changed since the download+patching step. (This is made possible by 'shasum' and 'diff'.)

        For the convenience of the user, the shell session is created in non-isolated mode, meaning that
        programs installed in the host OS are also accessible in addition to the packages provided via Nix.
        This sometimes causes things to break in unexpected ways; if that happens, use the '--isolated' option.

        Examples:
            $ opp_env shell  # opens the shell for working with all projects in the workspace
            $ opp_env shell inet-latest  # opens a shell with the existing INET installation in the workspace
            $ opp_env shell --install inet-latest  # installs INET if not yet installed, then opens a shell for working with it
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_arguments(subparser, [
        "projects-optional",
        "init",
        "nixless-workspace",
        "workspace",
        "options",
        "chdir",
        "no-deps",
        "no-pause",
        "no-cleanup",
        "no-patch",
        "add-extra-nix-packages",
        "install",
        "no-build", # with --install
        "build",
        "build-modes",
        "quiet",
        "isolated",
        "keep",
        "local"
    ])

    subparser = subparsers.add_parser("run", help="Runs a command in the environment of the specified projects", description=dedent(
        """
        Runs a command in the environment of the specified projects.
        If no projects are specified, all projects in the current workspace are used.
        Many options are available to request addition operations (building, testing, or
        even workspace initialization and project installation) and for controlling further details.

        The environment in which the command is executed is the same as for the 'shell' command.
        Unlike the 'shell' command which tries to change into the first project's directory for the user's convenience,
        'run' does NOT change the current directory before running the command.

        To ensure maximum reproducibility, the 'run' command runs the session in isolated mode.
        This can be changed by specifying the '--non-isolated' option.

        Examples :

            # Run the 'aloha' example in OMNeT++ 6.0.3 then exit
            # (expects the current directory to be a workspace with OMNeT++ already installed):
            $ opp_env run omnetpp-6.0.3 -c 'cd omnetpp-6.0.3/samples/aloha && ./aloha'

            # Install OMNeT++ and INET, then run the MANET Routing showcase simulation:
            $ opp_env run inet-4.5.0 -w inet-workspace --init --install --chdir \\
                -c 'cd inet-4.5.0/showcases/routing/manet && inet'

            # Smoke test an existing INET installation:
            $ opp_env run inet-4.5.0 --smoke-test

            # Rebuild all projects
            $ opp_env run -c "clean_all && build_all"

        """),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_arguments(subparser, [
        "projects-optional",
        "init",
        "nixless-workspace",
        "workspace",
        "command",
        "options",
        "chdir@run",
        "no-deps",
        "no-pause",
        "no-cleanup",
        "no-patch",
        "add-extra-nix-packages",
        "install",
        "no-build", # with --install
        "build",
        "smoke-test",
        "test",
        "build-modes",
        "quiet",
        "no-isolated",
        "keep",
        "local"
    ])

    subparser = subparsers.add_parser("maint", help="Maintenance functions", description="Maintenance functions for internal use.")
    subparser.add_argument("-u", "--update-catalog", metavar="download-items-dir", dest="catalog_dir", help="Update the opp_env installation commands in the model catalog of omnetpp.org. The argument should point to the `download-items/` subdir of a checked-out copy of the https://github.com/omnetpp/omnetpp.org/ repository.")

    return parser

def process_arguments():
    parser = create_arg_parser()
    args = parser.parse_args(sys.argv[1:])
    if args.help_intro:
        print_intro()
    elif args.subcommand == None:
        parser.print_help()

    if args.debug:
        args.log_level = "DEBUG"
        args.print_stacktrace = True

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
        kwargs["requested_options"] = [name.strip() for arg in args.options for name in arg.split(",") if name.strip()]
        del kwargs["options"]
    if "keep" in kwargs:
        # split up and flatten list
        kwargs["vars_to_keep"] = [name.strip() for arg in args.keep for name in arg.split(",") if name.strip()]
        del kwargs["keep"]
    if "build_modes" in kwargs:
        kwargs["build_modes"] = args.build_modes.split(",") if args.build_modes else []
    if "extra_nix_packages" in kwargs:
        # split up and flatten list
        kwargs["extra_nix_packages"] = uniq([name.strip() for arg in args.extra_nix_packages for name in re.split(r"[\s,]+",arg) if name.strip()])
    return kwargs


def print_intro():
    print("""To see all the supported simulation models, run:
  opp_env list

To create a new workspace and install the latest version of OMNeT++, run:
  mkdir workspace && cd workspace && opp_env init && opp_env install omnetpp-latest && opp_env shell omnetpp-latest

To install and use the latest version of the INET Framework with a single command, run:
  opp_env shell --install inet-latest

To run a simulation model directly with the latest version of OMNeT++, run:
  opp_env run --install omnetpp-latest -c 'cd $OMNETPP_ROOT/samples/aloha;./aloha'""")

def get_version():
    return importlib.metadata.version("opp_env")

import os
import platform
import subprocess

def get_linux_distribution():
    try:
        with open("/etc/os-release") as f:
            lines = f.readlines()
        info = {}
        for line in lines:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                info[key] = value.strip('"')
        return info.get("ID", "").lower(), info.get("PRETTY_NAME", "").lower()
    except FileNotFoundError:
        return None, None

def suggest_nix_installation():
    distro_id, distro_name = get_linux_distribution()

    unknown = False
    if distro_id in ["debian", "ubuntu"]:
        print("On Debian/Ubuntu, you can install Nix using the following command:")
        print("    sudo apt update && sudo apt install nix-setup-systemd")
    elif distro_id in ["fedora"]:
        print("On Fedora, Nix is available through a COPR repository. Install it using:")
        print("    sudo dnf copr enable petersen/nix")
        print("    sudo dnf install nix")
        print("    sudo systemctl enable --now nix-daemon")
        print("More details at: https://copr.fedorainfracloud.org/coprs/petersen/nix/")
    elif distro_id in ["arch", "manjaro"]:
        print("On Arch Linux, you can install Nix using pacman:")
        print("    sudo pacman -S nix")
        print("    sudo systemctl enable --now nix-daemon")
        print("More details at: https://wiki.archlinux.org/title/Nix")
    elif distro_id in ["opensuse", "suse"]:
        print("On OpenSUSE, you can install Nix using the following command:")
        print("    sudo zypper install nix")
    else:
        unknown = True

    print(("You" if unknown else "\nAlternatively, you") + " can install it using the official installation script from nixos.org:")
    print("    curl -L https://nixos.org/nix/install | sh")


def detect_nix():
    minimum_nix_version = "2.8"
    # check nix is installed
    try:
        _logger.debug(f"Running nix --version")
        result = subprocess.run(['nix', '--version'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        output = result.stdout.decode('utf-8')
    except Exception as ex:
        _logger.debug(f"Error: {ex}")
        print("Error: Nix does not seem to be installed (running `nix --version` failed), aborting.")
        print()
        suggest_nix_installation()
        print()
        print(f"IMPORTANT: Make sure you install Nix version {minimum_nix_version} or a later version.")
        print("See also the `--nixless-workspace` option in the help.")
        print()
        raise Exception(f"Nix not installed -- see installation hints above.")

    # check it is recent enough
    nix_version = output.strip().split()[-1]
    if not re.match("^[0-9.]+$", nix_version):
        raise Exception("Cannot parse Nix version number: Output of 'nix --version' diverges from expected format")
    if natural_less(nix_version, minimum_nix_version):
        raise Exception(f"Your Nix installation of version {nix_version} is too old, at least version {minimum_nix_version} is required. The newest version is available from https://nixos.org/download.html. See also the --nixless-workspace option in the help.")

def detect_tools():
    tools = [ "bash", "git", "curl", "grep", "find", "xargs", "shasum", "tar", "gzip", "sed", "touch" ]

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

def is_inside_git_working_tree(dir):
    try:
        result = subprocess.run(['git', '-C', dir, 'rev-parse', '--is-inside-work-tree'], capture_output=True, text=True)
        return result.returncode == 0 and result.stdout.strip() == 'true'
    except Exception as ex:
        _logger.debug(f"Could not check whether {dir} is inside a git working tree -- git not installed? Exception: {ex}")
        return None  # false-ish

class ProjectDescription:
    def __init__(self, name, version, description=None, details=None, warnings=[],
                 nixos=None, stdenv=None, folder_name=None,
                 required_projects={}, nix_packages=[], vars_to_keep=[],
                 download_url=None, git_url=None, git_branch=None, download_commands=[],
                 patch_commands=[], patch_url=None,
                 shell_hook_commands=[], setenv_commands=[],
                 build_commands=[], clean_commands=[], smoke_test_commands=[], test_commands=[],
                 potential_build_inputs=None, potential_build_outputs=None,
                 options=None, metadata=None):
        def remove_empty(list):
            return [x for x in list if x] if list else []
        self.name = name
        self.version = version
        self.description = description
        self.details = details
        self.warnings = remove_empty(warnings)
        self.nixos = nixos
        self.stdenv = stdenv
        self.folder_name = folder_name or name
        self.required_projects = required_projects
        self.nix_packages = remove_empty(nix_packages)
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
        self.smoke_test_commands = remove_empty(smoke_test_commands)
        self.test_commands = remove_empty(test_commands)
        self.potential_build_inputs = potential_build_inputs or [ "src/*", "*.cc", "*.cxx", "*.c", "*.h", "*.hpp", "*.hh", "*.msg", "Makefile", "*/Makefile", "makefrag", "*/makefrag" ]
        self.potential_build_outputs = potential_build_outputs or [ "out/*", "*.o", "*.a", "*.a.*", "*.so", "*.so.*", "*.dylib", "*.dylib.*", "*.dll", "*.exe", ":noext" ]
        self.options = options or {}
        self.metadata = metadata or {}  # examples: catalog_url, release_year, original_version

        # remove null elements from lists inside options, too
        for option_name, option_entries in self.options.items():
            for field_name, field_value in option_entries.items():
                if not re.match("option_", field_name) and not hasattr(self, field_name):
                    raise ValueError(f"Project {name}-{version} option '{option_name}' key '{field_name}': Invalid key")
                if type(field_value) is list:
                    if (field_value[0] or "") not in ["@prepend", "@append", "@replace"]:
                        raise ValueError(f"Project {name}-{version} option '{option_name}' key '{field_name}': First value of list must be '@prepend', '@append', or '@replace'")
                    field_value[:] = remove_empty(field_value)

        if self.description and "\n" in self.description:
            raise Exception(f"project {name}-{version}: description may not contain newlines -- use the details field to store additional information")
        if self.description and len(self.description) > 180:
            raise Exception(f"project {name}-{version}: description may not be longer than 180 characters (currently {len(self.description)}) -- use the details field to store additional information")

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
        return [option_name for option_name, option_entries in self.options.items() if option_entries.get("option_is_default")]

    def activate_project_options(self, requested_options, activate_default_options=True, quiet=False):
        def get_conflicting_options(the_option_name, option_names):
            return [o for o in option_names if the_option_name != o and self.options[o].get("option_category") == self.options[the_option_name].get("option_category")]

        # activate requested options, and those of the default options that don't conflict with the requested ones
        effective_options = []
        for option in requested_options or []:
            prefix,_,option = option.rpartition(":") # allows for project-specific options, e.g. "inet:from-git-repo"
            if option in self.options and (not prefix or prefix == self.name):
                conflicting_options = get_conflicting_options(option, effective_options)
                if conflicting_options:
                    raise Exception(f"Option '{option}' conflicts with option '{conflicting_options[0]}' due to both belonging in the category '{self.options[option].get('category')}' (Note that options in the same category are exclusive)")
                effective_options.append(option)
        if activate_default_options:
            for option in self.get_default_options():
                if not get_conflicting_options(option, effective_options):
                    effective_options.append(option)

        new_project_description = copy.deepcopy(self)

        def set_or_extend_attr_from_option(project_description, field_name, field_value):
            # Modify the attribute in the project description: if it's a list, extend or replace based on the first element of field_value; otherwise overwrite it
            if hasattr(project_description, field_name) and isinstance(getattr(project_description, field_name), list):
                assert isinstance(field_value, list) and field_value[0] in ["@prepend", "@append", "@replace"]
                if field_value[0] == "@prepend":
                    getattr(project_description, field_name)[:0] = field_value[1:]
                elif field_value[0] == "@append":
                    getattr(project_description, field_name).extend(field_value[1:])
                elif field_value[0] == "@replace":
                    setattr(project_description, field_name, field_value[1:])
            else:
                setattr(project_description, field_name, field_value)

        if effective_options:
            if not quiet:
                _logger.debug(f"Selecting options {cyan(requested_options)} for project {cyan(self)}")
            for option in effective_options:
                if option in self.options:
                    for field_name, field_value in self.options[option].items():
                        if not re.match("option_", field_name): # not option metadata
                            set_or_extend_attr_from_option(new_project_description, field_name, field_value)
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
        # split to name and version
        return ProjectReference(*string.rsplit("-", 1)) if "-" in string else ProjectReference(string, "")

    def get_full_name(self):
        return self.name + "-" + self.version if self.version else self.name

class ProjectRegistry:
    def __init__(self):
        self.all_project_descriptions = self.collect_project_descriptions()
        self.index = self.build_index(self.all_project_descriptions)

    def collect_project_descriptions(self):
        python_files = [
            "omnetpp",
            "inet",
            "veins",
            "simulte",
            "simu5g",
            "external",
            "testproject"
        ]

        json_files = [
            "external.json"
        ]

        all_project_descriptions = []
        for fname in python_files:
            module = importlib.import_module("opp_env.database." + fname)
            raw_project_descriptions = module.get_project_descriptions()
            project_descriptions = [ProjectDescription(**e) for e in raw_project_descriptions]
            all_project_descriptions += project_descriptions

        for fname in json_files:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "database", fname)) as f:
                all_project_descriptions += [ProjectDescription(**e) for e in json.load(f)]

        # expand to wildcard versions such as "4.2.*" to list of matching versions
        return [self.expand_wildcards_in_project_dependencies(p, all_project_descriptions) for p in all_project_descriptions]

    def get_all_project_descriptions(self):
        return self.all_project_descriptions

    def get_project_names(self, project_descriptions=None):
        return uniq([p.name for p in project_descriptions or self.get_all_project_descriptions()])

    def get_project_versions(self, project_name, project_descriptions=None):
        return [p for p in project_descriptions or self.get_all_project_descriptions() if p.name == project_name]

    def get_project_version_names(self, project_name, project_descriptions=None):
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
            semver_versions = [v for v in project_versions if is_semver(v)] # exclude weird versions, and ".x" versions like "6.0.x" (6.0 or "latest" should NOT resolve to 6.0.x)
            index[project_name]["latest"] = index[project_name][semver_versions[0]] if semver_versions else index[project_name][project_versions[0]]
            for version in semver_versions:
                truncated_version = version
                while "." in truncated_version:
                    truncated_version = truncated_version.rsplit(".",1)[0] # chop off part after last dot
                    if truncated_version not in index[project_name]:
                        index[project_name][truncated_version] = index[project_name][version]
        return index

    def get_project_version_aliases(self, project_reference):
        # collect version aliases for a given project; e.g. if project_reference is "omnetpp-6.0.2", then it may return ["6", "6.0", "latest"]
        version_to_project_dict = self.index[project_reference.name]
        return [v for v,p in version_to_project_dict.items() if p.version != v and p.version == project_reference.version]

    def get_project_description(self, project_reference):
        if type(project_reference) is str:
            project_reference = ProjectReference.parse(project_reference)
        if project_reference.name not in self.index:
            raise Exception(f"Cannot resolve '{project_reference}': " + self.get_unknown_project_message(project_reference.name))
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
            candidates = self.get_project_version_names(project_name, all_project_descriptions)
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
            project_names = [ p.name for p in specified_project_descriptions ]
            raise Exception(f"The specified project versions cannot be installed together due to incompatible dependencies. Use the `opp_env list --matching {' '.join(project_names)}` command to see the compatible version combinations.")
        return activate_project_options(selected_project_descriptions, requested_options)

    def expand_dependencies(self, specified_project_descriptions, return_all=False):
        # note: ordering is important for ensuring that the 1st match contains the highest version numbers of the specified projects
        requested_projects_versions = OrderedDict((p.name, [p.version]) for p in specified_project_descriptions)
        combinations = self._get_valid_combinations(requested_projects_versions)
        return combinations if return_all else combinations[0] if combinations else []

    def _get_valid_combinations(self, requested_projects_versions):
        # Find all valid version combinations for the requested projects and their allowed versions, including dependencies.
        # requested_projects_versions: map { project_name : possible_versions_list }
        project_names = list(requested_projects_versions.keys())

        # collect the names of all involved projects (specified + dependencies)
        expanded_project_names = self._expand_with_dependencies(project_names, requested_projects_versions)

        # collect possible versions of all involved projects
        possible_versions = { p: requested_projects_versions.get(p, self.get_project_version_names(p)) for p in expanded_project_names }

        # produce all possible combinations and filter them
        valid_combinations = []
        for version_combo in itertools.product(*possible_versions.values()):
            combination = [self.get_project_description(ProjectReference(proj, version)) for proj, version in zip(expanded_project_names, version_combo)]
            if self._is_valid_combination(combination):
                valid_combinations.append(combination)

        return valid_combinations

    def _expand_with_dependencies(self, project_names, requested_projects_versions):
        queue = list(requested_projects_versions.keys())
        result = list(project_names)
        while queue:
            project = queue.pop()
            for proj_desc in self.get_project_versions(project):
                for dep_name in proj_desc.required_projects.keys():
                    if dep_name not in result:
                        result.append(dep_name)
                        queue.append(dep_name)
        return result

    def _is_valid_combination(self, combination):
        version_map = {proj_desc.name: proj_desc for proj_desc in combination if proj_desc}

        for project_desc in combination:
            if not project_desc:
                return False
            for dep_name, compatible_versions in project_desc.required_projects.items():
                if dep_name in version_map:
                    if version_map[dep_name].version not in compatible_versions:
                        return False
                else:
                    return False  # Dependency not included in resolved set
        return True

    def expand_dependencies_old(self, specified_project_descriptions, return_all=False):
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
        available_project_versions = { name: self.get_project_version_names(name) for name in required_project_names }
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
                selected_project_descriptions = list(reversed(selected_project_descriptions))  # most derived project first, omnetpp last (usually)
                if return_all:
                    result.append(selected_project_descriptions)
                else:
                    return selected_project_descriptions
        return result

    def get_unknown_project_message(self, project_name):
        def jaccard_similarity(word1, word2):
            set1 = set(word1)
            set2 = set(word2)
            intersection = len(set1.intersection(set2))
            union = len(set1) + len(set2) - intersection
            similarity = intersection / union if union != 0 else 0
            return similarity
        names = self.get_project_names()
        most_similar =  max(names, key=lambda p: jaccard_similarity(project_name.lower(), p.lower()))
        more_candidates = [p for p in names if p!=most_similar and (p.lower() in project_name.lower() or project_name.lower() in p.lower())]
        if more_candidates:
            return f"Unknown project '{project_name}'. Did you mean one of {[most_similar] + more_candidates}?"
        else:
            return f"Unknown project '{project_name}'. Did you mean '{most_similar}'?"

def activate_project_options(project_descriptions, requested_options):
    # check requested options exist at all
    all_supported_options = []
    for desc in project_descriptions:
        all_supported_options += desc.get_supported_options()
    all_supported_options = uniq(all_supported_options)
    for option in requested_options or []:
        prefix,_,option = option.rpartition(":") # allows for project-specific options, e.g. "inet:from-git-repo"
        if prefix:
            # the project selected with the prefix (e.g. "inet:") must have such option
            targeted_projects = [p for p in project_descriptions if p.name == prefix]
            if not targeted_projects:
                raise Exception(f"Invalid option '{prefix}:{option}': There is no project named '{prefix}' among the selected projects")
            targeted_project = targeted_projects[0]  # reasonably, there can be only one matching
            if not option in targeted_project.get_supported_options():
                raise Exception(f"Invalid option '{prefix}:{option}': Project '{targeted_project}' has no option named '{option}'")
        else:
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

    def __init__(self, root_directory, default_nixos=None, default_stdenv=None):
        assert(os.path.isabs(root_directory))
        if is_inside_git_working_tree(root_directory):
            # that would lead to spurious error messages "getting status of '/nix/store/qnvxvf95a8dlfs7l88d420wxg8qcvbg0-source/<repo-relative-path>': No such file or directory"
            raise Exception(f"Workspace directory '{root_directory}' may not be under a git working tree")

        self.root_directory = root_directory
        self.default_nixos = default_nixos or "22.11"
        self.default_stdenv = default_stdenv or "llvmPackages.stdenv"

        opp_env_directory = os.path.join(self.root_directory, self.WORKSPACE_ADMIN_DIR)
        if not os.path.exists(opp_env_directory):
            raise Exception(f"'{root_directory}' is not an opp_env workspace, run 'opp_env init' to turn it into one")
        self.nixless = os.path.exists(os.path.join(self.get_workspace_admin_directory(), ".nixless"))  #TODO do it properly!!!

        extra_nix_packages_file = os.path.join(self.get_workspace_admin_directory(), "extra_nix_packages")
        extra_nix_packages_file_content = self._read_file_if_exists(extra_nix_packages_file).strip()
        self.extra_nix_packages = extra_nix_packages_file_content.split() if extra_nix_packages_file_content else []

        if self.nixless:
            detect_tools()
        else:
            detect_nix()

        _logger.debug(f"Workspace {root_directory=}, {self.nixless=}")

    @staticmethod
    def is_workspace(dir):
        return os.path.isdir(os.path.join(dir, Workspace.WORKSPACE_ADMIN_DIR))

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
    def init_workspace(dir=None, allow_existing=False, nixless=False):
        if not dir:
            dir = os.getcwd()
        if not os.path.isdir(dir):
            raise Exception(f"Directory does not exist: {dir}")
        opp_env_dir = os.path.join(dir, Workspace.WORKSPACE_ADMIN_DIR)
        if os.path.isdir(opp_env_dir):
            if allow_existing:
                _logger.debug(f"Using existing workspace in folder {cyan(dir)}")
                return
            else:
                raise Exception(f"'{dir}' is already an opp_env workspace")
        if re.search("\\s", dir):
            raise Exception(f"Whitespace characters are not allowed in the name and path of the workspace directory")
        shutil.copytree(os.path.join(os.path.dirname(__file__), "templates", "workspace"), opp_env_dir)
        if nixless:
            # write an empty file called .nixless to indicate that this is a nixless workspace
            open(os.path.join(opp_env_dir, ".nixless"), "w").close()
        _logger.info(f"Workspace created in folder {cyan(dir)}")

    def get_workspace_admin_directory(self):
        return os.path.join(self.root_directory, self.WORKSPACE_ADMIN_DIR)

    def get_installed_projects(self):
        def is_project(folder_name):
            return os.path.isdir(os.path.join(self.root_directory, folder_name, self.PROJECT_ADMIN_DIR))
        def get_project_description(folder_name):
            try:
                global project_registry
                return project_registry.get_project_description(folder_name)
            except Exception as e:
                _logger.warning(f"Failed to load project description for '{folder_name}': {e}")
                return None
        result = [get_project_description(folder) for folder in os.listdir(self.root_directory) if is_project(folder)]
        return [p for p in result if p]

    def get_project_root_directory(self, project_description):
        return os.path.join(self.root_directory, project_description.get_full_folder_name())

    def get_project_admin_directory(self, project_description, create=False):
        dir = os.path.join(self.get_project_root_directory(project_description), self.PROJECT_ADMIN_DIR)
        if create and not os.path.isdir(dir):
            os.mkdir(dir)
        return dir

    def get_project_admin_file(self, project_description, filename, create_dir=False):
        return os.path.join(self.get_project_admin_directory(project_description, create=create_dir), filename)

    def is_project_modified(self, project_description):
        postdownload_shasums = self.read_project_shasums(project_description, "postdownload")
        last_shasums = self.read_project_shasums(project_description, "last")
        new_files, disappeared_files, changed_files = self.compare_shasums(postdownload_shasums, last_shasums)
        self.print_shasums_comparison_result(new_files, disappeared_files, changed_files, label=f"File changes in {project_description} since download", root_dir=self.get_project_root_directory(project_description))
        return disappeared_files or changed_files # new files do not count  (TODO or: should count, except for build outputs?)

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

    def get_project_status(self, project_description):
        project_directory = self.get_project_root_directory(project_description)
        data = self.read_project_state_file(project_description)
        return self.ABSENT if not os.path.isdir(project_directory) else \
               self.INCOMPLETE if not data else \
               self.DOWNLOADED

    def update_project_state(self, project_description, **kwargs):
        data = self.read_project_state_file(project_description)
        data.update(kwargs)
        self.write_project_state_file(project_description, data)

    def download_project(self, project_description, effective_project_descriptions, patch=True, cleanup=True, local=False, git_branch=None, vars_to_keep=None):
        def get_env(varname, what):
            value = os.environ.get(varname)
            _logger.debug(f"Checking {cyan('$'+varname)} for {what}: {cyan(value)}")
            if not value:
                raise Exception(f"Environment variable {varname} not set, it should point to {what}")
            return value

        _logger.info(f"Downloading project {cyan(project_description.get_full_name())} in workspace {cyan(self.root_directory)}")
        project_dir = self.get_project_root_directory(project_description)
        if os.path.exists(project_dir):
            raise Exception(f"{project_dir} already exists")
        try:
            if not project_description.download_url and not project_description.git_url and not project_description.download_commands:
                raise Exception(f"project {project_description.get_full_name()}: at least one of download_url, git_url, and download_commands must be specified")

            if project_description.download_url and project_description.git_url:
                raise Exception(f"project {project_description.get_full_name()}: download_url and git_url are mutually exclusive (but either may be combined with download_commands)")

            if project_description.download_url:
                if git_branch:
                    raise Exception(f"Git branch ('@{git_branch}') may only be specified when project is installed from git")
                if not local:
                    self.download_and_unpack_tarball(project_description.download_url, project_dir)
                else:
                    downloads_dir = get_env("DOWNLOADS_DIR", "the downloads directory on the local disk")
                    fname = os.path.basename(project_description.download_url)
                    if project_description.name.lower() not in fname.lower():  # e.g. just "v1.2.0.tar.gz"
                        fname = project_description.name() + "-" + fname
                    tarball = os.path.join(downloads_dir, fname)
                    self.unpack_tarball(tarball, project_dir)
            elif project_description.git_url:
                if not local:
                    git_url = project_description.git_url
                else:
                    git_url = get_env(project_description.name.upper() + "_REPO", f"the location of the '{project_description.name}' git repository on the local disk")
                git_branch = git_branch or project_description.git_branch
                print(git_branch)
                branch_option = "-b " + git_branch if git_branch else ""
                self.run_command(f"git clone --config advice.detachedHead=false {branch_option} {git_url} {project_dir}") #TODO maybe optionally use --single-branch

            if project_description.download_commands:
                commands = [ f"export LOCAL_OPERATION={'1' if local else ''}", *project_description.download_commands ]
                self.run_commands_with_projects(effective_project_descriptions, self.root_directory, commands, run_setenv=False, vars_to_keep=vars_to_keep)

            if not os.path.exists(project_dir):
                raise Exception(f"{project_description}: Download process did not create {project_dir}")

            if project_description.patch_commands or project_description.patch_url:
                if patch:
                    _logger.info(f"Patching project {cyan(project_description.get_full_name())}")
                    self.record_project_shasums(project_description, "prepatch")
                    if project_description.patch_url:
                        self.download_and_apply_patch(project_description.patch_url, project_dir)
                    if project_description.patch_commands:
                        commands = [ f"export LOCAL_OPERATION={'1' if local else ''}", *project_description.patch_commands ]
                        self.run_commands_with_projects(effective_project_descriptions, project_dir, commands, run_setenv=False, vars_to_keep=vars_to_keep)
                else:
                    _logger.info(f"Skipping patching step of project {cyan(project_description.get_full_name())}")

            self.update_project_state(project_description, name=project_description.get_full_name())
            self.record_project_shasums(project_description, "postdownload")
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

    def record_project_shasums(self, project_description, snapshot_name):
        # exclude the Simulation IDE's directory from the shasum, because ./configure and eclipse itself modifies stuff in it
        project_root = self.get_project_root_directory(project_description)
        shasum_file = self.get_project_admin_file(project_description, snapshot_name+".sha", create_dir=True)
        # note: we chdir into project_root so that the shasum file will contain project-relative paths not absolute ones
        self.run_command(f"cd {project_root} && find . \\( -path ./{self.PROJECT_ADMIN_DIR} -o -path ./ide \\) -prune -o -type f -print0 | xargs -0 shasum > {shasum_file}")

    def read_project_shasums(self, project_description, snapshot_name, allow_missing=False):
        shasum_file = self.get_project_admin_file(project_description, snapshot_name+".sha")
        if allow_missing and not os.path.isfile(shasum_file):
            return None
        with open(shasum_file, 'r') as f:
            output = f.read()
        results = {}
        lines = output.strip().split('\n')
        for line in lines:
            shasum, filepath = line.strip().split(maxsplit=1)
            results[filepath] = shasum
        return results

    def compare_shasums(self, shasums1, shasums2, label=None, root_dir=None):
        new_files = []
        disappeared_files = []
        changed_files = []
        for filepath, shasum in shasums1.items():
            if filepath in shasums2:
                if shasums2[filepath] != shasum:
                    changed_files.append(filepath)
            else:
                disappeared_files.append(filepath)
        for filepath in shasums2.keys():
            if filepath not in shasums1:
                new_files.append(filepath)

        return new_files, disappeared_files, changed_files

    def print_shasums_comparison_result(self, new_files, disappeared_files, changed_files, label=None, root_dir=None, max_num=10):
        if _logger.isEnabledFor(logging.DEBUG):
            if root_dir and root_dir[-1] != "/":
                root_dir += "/"
            def log_list(label, list):
                if list:
                    note = f" ... and {len(list)-max_num} more" if len(list) > max_num else ""
                    _logger.debug(label + ": " + ' '.join([(f.removeprefix(root_dir or "")) for f in list[:max_num]]) + note)
            _logger.debug(f"{label or 'Files'}: {len(new_files)} new, {len(disappeared_files)} disappeared, {len(changed_files)} changed")
            log_list('New files', new_files)
            log_list('Disappeared files', disappeared_files)
            log_list('Changed files', changed_files)

    def show_warnings_before_download(self, project_descriptions, pause_after_warnings=True):
        # the ones that have warnings and are not yet downloaded
        projects_to_warn = [p for p in project_descriptions if self.get_project_status(p) ==  Workspace.ABSENT and p.warnings ]
        if projects_to_warn:
            for p in projects_to_warn:
                for warning in p.warnings:
                    _logger.warning(f"Project {cyan(p)}: {warning}")
            if pause_after_warnings and sys.stdout.isatty() and sys.stdin.isatty():
                input("Press Enter to continue, or Ctrl+C to abort ")

    @staticmethod
    def _get_unique_project_attribute(project_descriptions, attr_name, default_value):
        values = set([getattr(p, attr_name) for p in project_descriptions if getattr(p, attr_name)])
        if not values:
            _logger.debug(f"None of the projects specify the '{attr_name}' attribute, using '{default_value}' as default")
            return default_value
        elif len(values) > 1:
            raise Exception(f"The projects disagree on the choice of '{attr_name}': {values}")
        else:
            return list(values)[0]

    def download_project_if_needed(self, project_description, effective_project_descriptions, patch=True, cleanup=True, local=False, git_branch=None, vars_to_keep=None):
        project_state = self.get_project_status(project_description)
        if project_state == Workspace.ABSENT:
            self.download_project(project_description, effective_project_descriptions, patch, cleanup, local=local, git_branch=git_branch, vars_to_keep=vars_to_keep)
        elif project_state == Workspace.INCOMPLETE:
            raise Exception(f"Cannot download '{project_description}': Directory already exists")
        elif project_state == Workspace.DOWNLOADED:
            self.record_project_shasums(project_description, "last")
            if self.is_project_modified(project_description):
                _logger.warning(f"Project {project_description.get_full_name(colored=True)} has been {yellow('MODIFIED')} since download, use the check_{project_description.name} command to see what changed")
            else:
                _logger.info(f"Project {project_description.get_full_name(colored=True)} is {green('unmodified')} since download")
        else:
            assert False, f"Unknown project state '{project_state}'"

        assert self.get_project_status(project_description) == Workspace.DOWNLOADED, f"Wrong project status {self.get_project_status(project_description)} after download"

    def _read_file_if_exists(self, fname):
        try:
            with open(fname) as f:
                return f.read()
        except:
            return ""

    def download_and_unpack_tarball(self, download_url, target_folder):
        os.makedirs(target_folder)
        tar_log_file = os.path.join(target_folder, "tar.log")
        try:
            print(f"{download_url}")
            self.run_command(f"cd {target_folder} && curl -L --fail --progress-bar {download_url} | tar --strip-components=1 -xzf - 2>{tar_log_file}")
            os.remove(tar_log_file)
        except Exception as e:
            print(self._read_file_if_exists(tar_log_file).strip())
            raise e

    def unpack_tarball(self, tarball_fname, target_folder):
        os.makedirs(target_folder)
        self.run_command(f"cd {target_folder} && tar --strip-components=1 -xzf {tarball_fname}")

    def download_and_apply_patch(self, patch_url, target_folder):
        curl_log_file = os.path.join(target_folder, "curl.log")
        patching_log_file = os.path.join(target_folder, "patch.log")
        try:
            self.run_command(f"cd {target_folder} && curl -L --fail --stderr {curl_log_file} {patch_url} | git apply --whitespace=nowarn - 2>{patching_log_file}")
            os.remove(curl_log_file)
            os.remove(patching_log_file)
        except Exception as e:
            print(self._read_file_if_exists(curl_log_file).strip())
            print(self._read_file_if_exists(patching_log_file).strip())
            raise e

    @staticmethod
    def _get_dependencies(project_description, effective_project_descriptions):
        # find dependencies of the project among effective_projects
        todo = [project_description]
        processed = set()
        deps = []
        while todo:
            project = todo.pop()
            if project not in processed:
                new_deps = [p for p in effective_project_descriptions if p.name in project.required_projects and p not in processed]
                deps += new_deps
                processed.add(project)
                todo.extend(new_deps)
        return deps

    def _define_shell_functions(self, effective_project_descriptions):
        def make_build_function(function_name, directory_var, build_commands):
            return f"""
                function {function_name} ()
                {{
                    modes="$*"
                    modes=''${{modes:-$BUILD_MODES}}
                    modes=''${{modes:-release debug}}

                    (
                        for mode in $modes; do
                            echo -e "{SHELL_GREEN}Invoking {function_name} $mode:{SHELL_NOCOLOR}"
                            cd {directory_var}
                            BUILD_MODE=$mode
                            true ============== Project-specific commands: ==============
                            {build_commands}
                            true ========================================================
                        done
                    )

                    if [ "$?" == "0" ]; then
                        echo -e "{SHELL_GREEN}Done {function_name} $mode{SHELL_NOCOLOR}"
                    else
                        echo -e "{SHELL_RED}ERROR in {function_name} $mode{SHELL_NOCOLOR}";
                        return 1
                    fi
                }}
                export -f {function_name}
            """

        def make_check_function(function_name, project_name, directory_var):
            return f"""
                function {function_name} ()
                {{
                    (
                    echo -e "{SHELL_GREEN}Invoking {function_name}:{SHELL_NOCOLOR}"
                    echo 'Checking whether files have changed since download...'
                    cd {directory_var}
                    tmp=.opp_env/postdownload_changes.txt
                    if shasum --check --quiet .opp_env/postdownload.sha > $tmp 2>/dev/null; then
                        echo OK
                    else
                        cat $tmp | sed 's/FAILED open or read/MISSING/; s/FAILED$/MODIFIED/'
                        echo -e "{SHELL_YELLOW}WARNING:{SHELL_NOCOLOR} {project_name}: $(cat $tmp | wc -l) file(s) changed since download"
                    fi
                    rm $tmp
                    )
                }}
                export -f {function_name}
            """

        def make_function(function_name, commands):
            return f"""function {function_name}() {{
                {join_commands(commands)}
            }}
            export -f {function_name}"""

        project_build_function_commands = [
            make_build_function("build_" + p.name, f"${p.name.upper()}_ROOT", join_commands(p.build_commands))
            for p in effective_project_descriptions
        ]

        project_clean_function_commands = [
            make_build_function("clean_" + p.name, f"${p.name.upper()}_ROOT", join_commands(p.clean_commands))
            for p in effective_project_descriptions
        ]

        project_smoke_test_function_commands = [
            make_build_function("smoke_test_" + p.name, f"${p.name.upper()}_ROOT", join_commands(p.smoke_test_commands if p.smoke_test_commands else [ f"echo -e '{SHELL_YELLOW}SKIPPING:{SHELL_NOCOLOR} No smoke test commands were specified'"]))
            for p in effective_project_descriptions
        ]

        project_test_function_commands = [
            make_build_function("test_" + p.name, f"${p.name.upper()}_ROOT", join_commands(p.test_commands if p.test_commands else [ f"echo -e '{SHELL_YELLOW}SKIPPING:{SHELL_NOCOLOR} No test commands were specified'"]))
            for p in effective_project_descriptions
        ]

        project_check_function_commands = [
            make_check_function("check_" + p.name, p.get_full_name(), f"${p.name.upper()}_ROOT")
            for p in effective_project_descriptions
        ]

        function_definitions = [
            *project_build_function_commands,
            *project_clean_function_commands,
            *project_smoke_test_function_commands,
            *project_test_function_commands,
            *project_check_function_commands,
            make_function("build_all", [f"build_{p.name} \"$@\" || return 1" for p in reversed(effective_project_descriptions)]),
            make_function("clean_all", [f"clean_{p.name} \"$@\" || return 1" for p in effective_project_descriptions]),
            make_function("smoke_test_all", [f"smoke_test_{p.name} \"$@\"" for p in reversed(effective_project_descriptions)]),
            make_function("test_all", [f"test_{p.name} \"$@\"" for p in reversed(effective_project_descriptions)]),
            make_function("check_all", [f"check_{p.name} \"$@\"" for p in effective_project_descriptions]),
            make_function("opp_env", [ "printf 'error: Cannot run opp_env commands in an opp_env shell -- exit the shell to run it.\n' && return 1" ]),
        ]
        return function_definitions

    def run_command(self, command, suppress_stdout=False, check_exitcode=True, tracing=False):
        if not self.nixless:
            return self._nix_develop(nixos=self.default_nixos, stdenv=self.default_stdenv, session_name="run_command", script=command,
                        interactive=False, isolated=True, suppress_stdout=suppress_stdout, check_exitcode=check_exitcode, tracing=tracing)
        else:
            return self._run_command_nixless(command, suppress_stdout=suppress_stdout, check_exitcode=check_exitcode, tracing=tracing)

    def run_commands_with_projects(self, effective_project_descriptions, working_directory=None, commands=[], extra_nix_packages=None, vars_to_keep=None, run_setenv=True, interactive=False, isolated=True, check_exitcode=True, suppress_stdout=False, build_modes=None, tracing=False):

        nixful = not self.nixless

        if nixful:
            nixos = Workspace._get_unique_project_attribute(effective_project_descriptions, "nixos", self.default_nixos)
            stdenv = Workspace._get_unique_project_attribute(effective_project_descriptions, "stdenv", self.default_stdenv)

        session_name = '+'.join([str(d) for d in reversed(effective_project_descriptions)])
        project_names = [p.get_full_name() for p in effective_project_descriptions]
        project_deps = "; ".join([
            p.get_full_name() + ": " + " ".join([ dep.get_full_name() for dep in Workspace._get_dependencies(p, effective_project_descriptions) ])
            for p in effective_project_descriptions
        ])
        project_shell_hook_commands = sum([p.shell_hook_commands for p in effective_project_descriptions if p.shell_hook_commands], [])
        project_nix_packages = sum([p.nix_packages for p in effective_project_descriptions], [])
        combined_packages = project_nix_packages + (extra_nix_packages or [])
        project_nix_packages = list({pkg: None for pkg in combined_packages})  # Use a dict to maintain uniqueness
        project_vars_to_keep = sum([p.vars_to_keep for p in effective_project_descriptions], [])
        project_setenv_commands = sum([[f"cd '{self.get_project_root_directory(p)}'", *p.setenv_commands] for p in reversed(effective_project_descriptions)], [])
        project_root_environment_variable_assignments = [f"export {p.name.upper()}_ROOT={self.get_project_root_directory(p)}" for p in effective_project_descriptions]
        project_version_environment_variable_assignments = [f"export {p.name.upper()}_VERSION=\"{p.version}\"" for p in effective_project_descriptions]

        # a custom prompt spec to help users distinguish an opp_env shell from a normal terminal session
        prompt = f"\\[\\e[01;33m\\]{session_name}\\[\\e[00m\\]:\\[\\e[01;34m\\]\\w\\[\\e[00m\\]\\$ "

        is_macos = platform.system().lower() == "darwin"
        nproc_command = "nproc" if not is_macos else "sysctl -n hw.ncpu"

        shell_hook_lines = [
            'function error() { echo "$*" 1>&2; return 1; }; export -f error',
            'function ll() { ls -l $*; }; export -f ll',
            f"export BUILD_MODES=\"{' '.join(build_modes) if build_modes else ''}\"",
            f"export OPP_ENV_DIR=\"{os.path.dirname(os.path.realpath(__file__))}\"",
            f"export OPP_ENV_VERSION=\"{get_version()}\"",
            f"export OPP_ENV_PROJECTS=\"{' '.join(project_names)}\"",
            f"export OPP_ENV_PROJECT_DEPS=\"{project_deps}\"",
            *project_root_environment_variable_assignments,
            *project_version_environment_variable_assignments,
            *(project_shell_hook_commands if nixful else []),
            f"export NIX_BUILD_CORES=$({nproc_command})" if self.nixless else None, # otherwise Nix defines it
            f"export PS1='{prompt}'" if interactive and nixful else None,
            *(["pushd . > /dev/null", *project_setenv_commands, "popd > /dev/null"] if run_setenv else []),
            f"cd '{working_directory}'" if working_directory else None,
            *self._define_shell_functions(effective_project_descriptions),
            f"echo '{' '.join(extra_nix_packages)}' > {self.get_workspace_admin_directory()}/extra_nix_packages" if extra_nix_packages else None,
            *commands
        ]

        vars_to_keep = (vars_to_keep or []) + project_vars_to_keep
        script = join_lines(shell_hook_lines)

        if nixful:
            return self._nix_develop(nixos=nixos, stdenv=stdenv, nix_packages=project_nix_packages,
                        session_name=session_name, script=script, vars_to_keep=vars_to_keep, interactive=interactive,
                        isolated=isolated, check_exitcode=check_exitcode, suppress_stdout=suppress_stdout, tracing=tracing)
        else:
            if interactive:
                # launch an interactive bash session; setting PROMPT_COMMAND ensures the custom prompt
                # takes effect despite PS1 normally being overwritten by the user's profile and rc files
                script += f"\nPROMPT_COMMAND=\"PS1='{prompt}'\" bash -i"
            return self._run_command_nixless(script, suppress_stdout=suppress_stdout, check_exitcode=check_exitcode, tracing=tracing)

    def _nix_develop(self, nixos, stdenv, nix_packages=[], session_name="", script="", vars_to_keep=None, interactive=False, isolated=True, check_exitcode=True, suppress_stdout=False, tracing=False):
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
            overlay = final: prev: {
                # allow python2 to be installed despite being EOL and having known vulnerabilities
                python2 = prev.python2.overrideAttrs (oldAttrs: {
                    meta = oldAttrs.meta // { knownVulnerabilities = []; };
                });
            };
            pkgs = import nixpkgs { inherit system; overlays = [ overlay ]; };
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

        tools_nix_packages = ["bashInteractive", "gitFull", "openssh", "curl", "gzip", "which", "gnused", "gnutar", "perl", "findutils", "coreutils"]
        nix_packages = uniq(nix_packages + tools_nix_packages)

        shell_options = "-exo pipefail" if tracing else "-eo pipefail"
        flake_dir = os.path.join(self.get_workspace_admin_directory(), nixos)
        os.makedirs(flake_dir, exist_ok=True)
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

        _logger.debug(f"Using nixpkgs {cyan(nixos)} with {cyan(stdenv)}, packages: {cyan(' '.join(sorted(nix_packages)))}")
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

        result = self._run_command_nixless(nix_develop_command, env=env, suppress_stdout=not interactive and suppress_stdout, check_exitcode=check_exitcode)

        # cleanup: remove temporary home dir, as we don't want it to interfere with subsequent sessions
        if isolated:
            shutil.rmtree(temp_home)
        return result

    def _run_command_nixless(self, command, env=None, suppress_stdout=False, check_exitcode=True, tracing=False):
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

def chop_branch_names(project_names):
    # if a project name contains "@", the part after that is a git branch name
    git_branches = {}
    stripped_projects = []
    for project_name in project_names:
        if "@" in project_name:
            stripped_name, branch = project_name.split("@")
            stripped_projects.append(stripped_name)
            git_branches[stripped_name] = branch
        else:
            stripped_projects.append(project_name)
    return stripped_projects, git_branches

def resolve_projects(project_full_names, remove_trailing_slash=True):
    global project_registry
    project_descriptions = [project_registry.get_project_description(ProjectReference.parse(p.rstrip('/') if remove_trailing_slash else p)) for p in project_full_names]
    return project_descriptions

def create_or_init_workspace(workspace_directory, allow_create=True, allow_existing=False, allow_nonempty=False, nixless=False):
    workspace_directory = workspace_directory or os.getcwd()
    if os.path.isdir(workspace_directory):
        if not Workspace.is_workspace(workspace_directory):
            if os.listdir(workspace_directory) and not allow_nonempty: # dir not empty
                raise Exception(f"Refusing to turn non-empty directory '{workspace_directory}' into an opp_env workspace -- use 'opp_env init --force' if it was intentional")
    elif allow_create:
        parent_dir = os.path.dirname(os.path.abspath(workspace_directory))
        if not os.path.isdir(parent_dir):
            raise Exception(f"Cannot create workspace at '{workspace_directory}': refusing to create more than one level of directories")
        os.mkdir(workspace_directory)
    else:
        raise Exception(f"Workspace directory '{workspace_directory}' does not exist")
    Workspace.init_workspace(workspace_directory, allow_existing=allow_existing, nixless=nixless)
    return workspace_directory

def resolve_workspace(workspace_directory, init, nixless_workspace):
    if init:
        workspace_directory = create_or_init_workspace(workspace_directory, nixless=nixless_workspace, allow_existing=True)
        workspace = Workspace(workspace_directory, nixless_workspace)
    else:
        if nixless_workspace:
            raise Exception("--nixless-workspace is only supported with --init")
        workspace_directory = os.path.abspath(workspace_directory) if workspace_directory else Workspace.find_workspace(os.getcwd())
        workspace = Workspace(workspace_directory)
    return workspace

def check_project_dependencies(effective_project_descriptions, workspace, pause_after_warnings=True):
    for project_description in effective_project_descriptions:
        data = workspace.read_project_state_file(project_description)
        last_started_with = data.get("last_started_with", None)
        starting_with = [ p.get_full_name() for p in Workspace._get_dependencies(project_description, effective_project_descriptions) ]
        if last_started_with is not None and starting_with != last_started_with:
            def q(l): return "[" + ", ".join(l) + "]"
            _logger.warning(f"Project {cyan(project_description)} is now being used with a different set of dependencies "
                            f"({cyan(q(starting_with))}) than last time ({cyan(q(last_started_with))}), rebuild recommended. "
                            f"Hint: type " + green(f"clean_{project_description.name} && build_{project_description.name}") + " in the opp_env shell.")
            if pause_after_warnings and sys.stdout.isatty() and sys.stdin.isatty():
                input("Press Enter to continue, or Ctrl+C to abort ")

def update_saved_project_dependencies(effective_project_descriptions, workspace):
    for project_description in effective_project_descriptions:
        starting_with = [ p.get_full_name() for p in Workspace._get_dependencies(project_description, effective_project_descriptions) ]
        workspace.update_project_state(project_description, last_started_with=starting_with)


def list_subcommand_main(project_name_patterns=None, list_mode="grouped", **kwargs):
    def expand_pattern(project_name_pattern, projects):
        return [p for p in projects if project_name_pattern == p.name or re.match(project_name_pattern+r'\b', p.get_full_name())] # note: prefix match!

    global project_registry
    specified_projects = project_registry.get_all_project_descriptions()
    if project_name_patterns:
        tmp = []
        for project_name_pattern in project_name_patterns:
            matching_projects = expand_pattern(project_name_pattern, specified_projects)
            if not matching_projects:
                raise Exception(f"Name/pattern '{project_name_pattern}' does not match any project")
            tmp += matching_projects

        specified_projects = uniq(tmp) # NOTE: No sorting! Order of project versions is STRICTLY determined by the order they are in ProjectRegistry.
    names = uniq([p.name for p in specified_projects])

    def move_to_front(list, name):
        try:
            list.remove(name)
            list.insert(0, name)
        except ValueError:
            pass

    names.sort()
    move_to_front(names, "inet")
    move_to_front(names, "omnetpp")

    name_width = len(max(names, key=len))
    if list_mode == "flat":
        for p in specified_projects:
            print(p.get_full_name())
    elif list_mode == "grouped":
        for name in names:
            versions = [p.version for p in specified_projects if p.name == name]
            print(f"{name.ljust(name_width)} {cyan('  '.join(versions))}")
    elif list_mode == "names":
        for name in names:
            print(name)
    elif list_mode == "aliases":
        for project in specified_projects:
            alias_versions = project_registry.get_project_version_aliases(ProjectReference(project.name, project.version))
            for alias_version in natural_sorted(alias_versions):
                print(f"{project.name}-{alias_version} -> {project.get_full_name()}")
    elif list_mode == "descriptions":
        for name in names:
            descriptions = uniq([p.description for p in specified_projects if p.name == name if p.description])
            description = descriptions[0] if descriptions else "(no description)"
            print(f"{name.ljust(name_width)} {cyan(description)}")
    elif list_mode == "matching":
        if not project_name_patterns:
            raise Exception("No project name patterns specified")
        combinations_list = [expand_pattern(project_name_pattern, specified_projects) for project_name_pattern in project_name_patterns]
        for combination in itertools.product(*combinations_list):
            expanded = sort_by_project_dependencies(project_registry.expand_dependencies(combination))
            expanded = [p for p in expanded if p in specified_projects]  # drop the dependencies added by 'expand'
            if expanded:
                print(' '.join([p.get_full_name() for p in expanded]))
    elif list_mode == "expand":
        if project_name_patterns:
            # consider the projects together, not independently
            combinations_list = [expand_pattern(project_name_pattern, specified_projects) for project_name_pattern in project_name_patterns]
            for combination in itertools.product(*combinations_list):
                expanded = sort_by_project_dependencies(project_registry.expand_dependencies(combination))
                if expanded:
                    print(' '.join([p.get_full_name() for p in expanded]))
        else:
            for project in specified_projects:
                expanded = sort_by_project_dependencies(project_registry.expand_dependencies([project]))
                print(' '.join([p.get_full_name() for p in expanded]))
    elif list_mode == "expand-all":
        if project_name_patterns:
            # consider the projects together, not independently
            combinations_list = [expand_pattern(project_name_pattern, specified_projects) for project_name_pattern in project_name_patterns]
            for combination in itertools.product(*combinations_list):
                expanded_combinations = project_registry.expand_dependencies(combination, return_all=True)
                for expanded_combination in expanded_combinations:
                    print(' '.join([p.get_full_name() for p in sort_by_project_dependencies(expanded_combination)]))
        else:
            for project in specified_projects:
                combinations_list = project_registry.expand_dependencies([project], return_all=True)
                for combination in combinations_list:
                    print(' '.join([p.get_full_name() for p in sort_by_project_dependencies(combination)]))
    else:
        raise Exception(f"invalid list mode '{list_mode}'")

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
                project_descriptions += project_registry.get_project_versions(project)
            else:
                raise Exception(project_registry.get_unknown_project_message(project))

    if raw:
        serializable = [vars(p.activate_project_options(requested_options)) for p in project_descriptions]
        print(json.dumps(serializable, indent=4))
        return

    # print info for each
    for project_description in project_descriptions:
        project_description = project_description.activate_project_options(requested_options)
        print()
        print(project_description.get_full_name() + (": " + project_description.description if project_description.description else ""))
        if project_description.details:
            print("\n" + project_description.details.rstrip())
        if project_description.warnings:
            for warning in project_description.warnings:
                print(yellow("\nWARNING: ") + warning)
        if project_description.download_url:
            print(f"\nDownload URL: {cyan(project_description.download_url)}")
        if project_description.git_url:
            print(f"\nGit URL:  {cyan(project_description.git_url)}")
            if project_description.git_branch not in ['master', 'main']:
                print(f"Git Branch: {cyan(project_description.git_branch)}")
        if project_description.download_commands:
            print(f"\nDownload: {cyan('custom commands')}")
        if (project_description.required_projects):
            print(f"\nRequires:")
            for name, versions in project_description.required_projects.items():
                print(f"- {cyan(name)}: {' / '.join(versions)}")
        if project_description.nixos or project_description.stdenv or project_description.nix_packages:
            print("\nNix:")
            if project_description.nixos:
                print(f"- version:  {cyan(project_description.nixos)}")
            if project_description.stdenv:
                print(f"- stdenv:   {cyan(project_description.stdenv)}")
            if project_description.nix_packages:
                print(f"- packages: {cyan(' '.join(project_description.nix_packages))}")
        if project_description.options:
            print("\nAvailable options:")
            for option_name, option in project_description.options.items():
                option_description = option.get('option_description')
                default_mark = " (default)" if option.get('option_is_default') else "";
                if option_description:
                    print(f"- {cyan(option_name)}{default_mark}: {option_description}")
                else:
                    print(f"- {cyan(option_name)}{default_mark}")
        if len(project_descriptions) > 1:
            print("\n--------")
    print()
    print("Note: Specify `--raw` to `opp_env info` for more details.")
    print("Note: Options can be selected by adding `--options=[PROJECT:]NAME` to the opp_env command line, see e.g. `opp_env install --help`.")
    print()

def init_subcommand_main(workspace_directory=None, force=False, nixless_workspace=False, **kwargs):
    create_or_init_workspace(workspace_directory, allow_nonempty=force, nixless=nixless_workspace)

def install_subcommand_main(projects, workspace_directory=None, install_without_build=False, requested_options=None, no_dependency_resolution=False, nixless_workspace=False, extra_nix_packages=None, init=False, pause_after_warnings=True, isolated=True, vars_to_keep=None, patch=True, cleanup=True, local=False, build_modes=None, run_test=False, run_smoke_test=False, **kwargs):
    global project_registry

    workspace = resolve_workspace(workspace_directory, init, nixless_workspace)

    projects, git_branches = chop_branch_names(projects)
    if git_branches:
        _logger.info(f"Requested Git branches: {git_branches}")

    specified_project_descriptions = resolve_projects(projects)
    if no_dependency_resolution:
        effective_project_descriptions = sort_by_project_dependencies(activate_project_options(specified_project_descriptions, requested_options))
    else:
        effective_project_descriptions = sort_by_project_dependencies(project_registry.compute_effective_project_descriptions(specified_project_descriptions, requested_options))
    _logger.info(f"Using specified projects {cyan(str(specified_project_descriptions))} with effective projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace.root_directory)}")

    check_project_dependencies(effective_project_descriptions, workspace, pause_after_warnings)

    workspace.show_warnings_before_download(effective_project_descriptions, pause_after_warnings)

    for project_description in reversed(effective_project_descriptions):
        workspace.download_project_if_needed(project_description, effective_project_descriptions, patch=patch, cleanup=cleanup, local=local, git_branch=git_branches.get(project_description.get_full_name()), vars_to_keep=vars_to_keep)

    update_saved_project_dependencies(effective_project_descriptions, workspace)

    commands = [
        "build_all",
        "smoke_test_all" if run_smoke_test else None,
        "test_all" if run_test else None,
    ]

    if not install_without_build:
        extra_nix_packages = uniq(workspace.extra_nix_packages + (extra_nix_packages or []))
        workspace.run_commands_with_projects(effective_project_descriptions, commands=commands, isolated=isolated, extra_nix_packages=extra_nix_packages, build_modes=build_modes)

def is_subdirectory(child_dir, parent_dir):
    # Check if a directory is a subdirectory of another directory.
    return os.path.commonpath([child_dir, parent_dir]) == parent_dir

def check_multiple_versions(project_descriptions):
    name_versions_dict = {}
    for project_description in project_descriptions:
        name, version = project_description.name, project_description.version
        if name in name_versions_dict:
            name_versions_dict[name].append(version)
        else:
            name_versions_dict[name] = [version]
    for name, versions in name_versions_dict.items():
        if len(versions) > 1:
            def q(l): return "[" + ", ".join(l) + "]"
            raise Exception(f"Multiple versions specified for project {cyan(name)}: {cyan(q(versions))} -- only one version of a project may be active at a time")

def shell_subcommand_main(projects, workspace_directory=[], chdir=False, requested_options=None, no_dependency_resolution=False, init=False, extra_nix_packages=None, install=False, install_without_build=False, build=False, nixless_workspace=False, isolated=True, vars_to_keep=None, patch=True, cleanup=True, local=False, build_modes=None, pause_after_warnings=True, **kwargs):
    global project_registry

    workspace = resolve_workspace(workspace_directory, init, nixless_workspace)

    projects, git_branches = chop_branch_names(projects)
    if git_branches and not install:
        raise Exception("Git branch may only be specified when the project is installed")
    if git_branches:
        _logger.info(f"Requested Git branches: {git_branches}")

    specified_project_descriptions = resolve_projects(projects) if projects else workspace.get_installed_projects()
    check_multiple_versions(specified_project_descriptions)
    if no_dependency_resolution:
        effective_project_descriptions = sort_by_project_dependencies(activate_project_options(specified_project_descriptions, requested_options))
    else:
        effective_project_descriptions = sort_by_project_dependencies(project_registry.compute_effective_project_descriptions(specified_project_descriptions, requested_options))
    _logger.info(f"Using specified projects {cyan(str(specified_project_descriptions))} with effective projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace.root_directory)}")

    if not install:
        for project_description in effective_project_descriptions:
            if workspace.get_project_status(project_description) != Workspace.DOWNLOADED:
                raise Exception(f"Project {cyan(project_description.get_full_name())} is not downloaded, please run {cyan('opp_env install')} first, or use {cyan('opp_env shell --install')}")

    check_project_dependencies(effective_project_descriptions, workspace, pause_after_warnings)

    workspace.show_warnings_before_download(effective_project_descriptions, pause_after_warnings)

    if install:
        for project_description in reversed(effective_project_descriptions):
            workspace.download_project_if_needed(project_description, effective_project_descriptions, patch=patch, cleanup=cleanup, local=local, git_branch=git_branches.get(project_description.get_full_name()), vars_to_keep=vars_to_keep)

    update_saved_project_dependencies(effective_project_descriptions, workspace)

    project_names = [p.name for p in effective_project_descriptions]
    function_list = "; ".join([f"`build_{p}`, `clean_{p}`, `test_{p}`, `smoke_test_{p}`, `check_{p}`" for p in ["all"] + project_names])

    commands = [
        "build_all" if build or (install and not install_without_build) else None,
        f"echo -e '{SHELL_GREEN}HINT{SHELL_NOCOLOR} To build, clean, test or check a project or all projects, use the following commands: {function_list}. (Use `declare -f <command>` to check what they do.)'",
        f"echo -e '{SHELL_GREEN}HINT{SHELL_NOCOLOR} Type {SHELL_CYAN}omnetpp{SHELL_NOCOLOR} to start the IDE.'"
    ]

    kind = "nixless" if workspace.nixless else "isolated" if isolated else "non-isolated"
    extra_nix_packages = uniq(workspace.extra_nix_packages + (extra_nix_packages or []))
    extra_nix_packages_str = f" with extra packages: {cyan(' '.join(extra_nix_packages))}" if extra_nix_packages else ""
    _logger.info(f"Starting {cyan(kind)} shell for projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace.root_directory)}{extra_nix_packages_str}")

    if chdir and effective_project_descriptions:
        first_project_description = effective_project_descriptions[0]
        first_project_dir = workspace.get_project_root_directory(first_project_description)
        if chdir == "convenience":
            chdir = not is_subdirectory(os.getcwd(), first_project_dir)  # "is outside the project dir"
        if chdir:
            _logger.debug(f"Changing into the first project's directory {cyan(first_project_dir)}")
            os.chdir(first_project_dir)
        else:
            _logger.debug(f"No need to change directory, wd={cyan(os.getcwd())} is already under the first project's directory {cyan(first_project_dir)}")

    workspace.run_commands_with_projects(effective_project_descriptions, commands=commands, interactive=True, isolated=isolated, extra_nix_packages=extra_nix_packages, check_exitcode=False, vars_to_keep=vars_to_keep, build_modes=build_modes)

def run_subcommand_main(projects, command=None, workspace_directory=None, chdir=False, requested_options=None, no_dependency_resolution=False, init=False, extra_nix_packages=None, install=False, install_without_build=False, build=False, nixless_workspace=False, isolated=True, vars_to_keep=None, patch=True, cleanup=True, local=False, build_modes=None, pause_after_warnings=True, run_test=False, run_smoke_test=False, **kwargs):
    global project_registry

    workspace = resolve_workspace(workspace_directory, init, nixless_workspace)

    projects, git_branches = chop_branch_names(projects)
    if git_branches and not install:
        raise Exception("Git branch may only be specified when the project is installed")
    if git_branches:
        _logger.info(f"Requested Git branches: {git_branches}")

    specified_project_descriptions = resolve_projects(projects) if projects else workspace.get_installed_projects()
    check_multiple_versions(specified_project_descriptions)
    if no_dependency_resolution:
        effective_project_descriptions = sort_by_project_dependencies(activate_project_options(specified_project_descriptions, requested_options))
    else:
        effective_project_descriptions = sort_by_project_dependencies(project_registry.compute_effective_project_descriptions(specified_project_descriptions, requested_options))
    _logger.info(f"Using specified projects {cyan(str(specified_project_descriptions))} with effective projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace.root_directory)}")

    if not install:
        for project_description in effective_project_descriptions:
            if workspace.get_project_status(project_description) != Workspace.DOWNLOADED:
                raise Exception(f"Project {cyan(project_description.get_full_name())} is not downloaded, please run {cyan('opp_env install')} first, or use {cyan('opp_env run --install')}")

    check_project_dependencies(effective_project_descriptions, workspace, pause_after_warnings)

    workspace.show_warnings_before_download(effective_project_descriptions, pause_after_warnings)
    if install:
        for project_description in reversed(effective_project_descriptions):
            workspace.download_project_if_needed(project_description, effective_project_descriptions, patch=patch, cleanup=cleanup, local=local, git_branch=git_branches.get(project_description.get_full_name()), vars_to_keep=vars_to_keep)

    update_saved_project_dependencies(effective_project_descriptions, workspace)

    commands = [
        "build_all" if build or (install and not install_without_build) else None,
        "smoke_test_all" if run_smoke_test else None,
        "test_all" if run_test else None,
        command if command else None,
    ]
    kind = "nixless" if workspace.nixless else "isolated" if isolated else "non-isolated"
    working_directory = workspace_directory if chdir else None
    extra_nix_packages = uniq(workspace.extra_nix_packages + (extra_nix_packages or []))
    extra_nix_packages_str = f" with extra packages: {cyan(' '.join(extra_nix_packages))}" if extra_nix_packages else ""
    _logger.info(f"Running command for projects {cyan(str(effective_project_descriptions))} in workspace {cyan(workspace.root_directory)} in {cyan(kind)} mode{extra_nix_packages_str}")
    workspace.run_commands_with_projects(effective_project_descriptions, working_directory=working_directory, commands=commands, isolated=isolated, extra_nix_packages=extra_nix_packages, vars_to_keep=vars_to_keep, build_modes=build_modes)

def maint_subcommand_main(catalog_dir, **kwargs):
    update_catalog(catalog_dir)

def update_catalog(catalog_dir):
    # collect catalog URLs by project name
    _logger.info(f"Collecting catalog_url entries from projects")
    global project_registry
    project_catalog_urls = {}
    for project_description in project_registry.get_all_project_descriptions():
        catalog_url = project_description.metadata.get("catalog_url")
        if catalog_url:
            if project_description.name in project_catalog_urls:
                if project_catalog_urls[project_description.name] != catalog_url:
                    raise Exception(f"The 'metadata/catalog_url' field differs across versions for project '{project_description.name}'")
            else:
                project_catalog_urls[project_description.name] = catalog_url
    _logger.debug(f"Result: {project_catalog_urls=}")

    # insert them into the pages
    _logger.info(f"Updating pages in {cyan(catalog_dir)}")
    for project_name, catalog_url in project_catalog_urls.items():
        # read file
        filename = os.path.join(catalog_dir, os.path.basename(catalog_url).replace(".html", ".md"))
        with open(filename, "r") as f:
            content = f.read()

        # update content
        line = f"opp-env-command: opp_env install {project_name}-latest"
        if "opp-env-command:" in content:
            updated_content = re.sub("^opp-env-command:.*$", line, content, flags=re.MULTILINE)
        else:
            updated_content = re.sub("\n---", f"\n{line}\n---", content)
        assert f"\n{line}\n" in updated_content

        # write back change
        if content != updated_content:
            _logger.debug(f"Writing {filename}")
            with open(filename, "w") as f:
                f.write(updated_content)

def main():
    kwargs = process_arguments()
    subcommand = kwargs.get('subcommand')

    try:
        _logger.debug(f"Starting {cyan(subcommand)} operation")
        if subcommand == None:
            pass # parser.print_help() already called
        elif subcommand == "list":
            list_subcommand_main(**kwargs)
        elif subcommand == "info":
            info_subcommand_main(**kwargs)
        elif subcommand == "init":
            init_subcommand_main(**kwargs)
        elif subcommand == "install":
            install_subcommand_main(**kwargs)
        elif subcommand == "shell":
            shell_subcommand_main(**kwargs)
        elif subcommand == "run":
            run_subcommand_main(**kwargs)
        elif subcommand == "maint":
            maint_subcommand_main(**kwargs)
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
