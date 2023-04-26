import re

def dotx(base_version):
    return re.sub("(\\d\\.\\d)[\\.p]\\d", "\\1", base_version) + ".x"  # 4.2, 4.2.1, 4.2p1 -> 4.2.x

def join_nonempty_items(sep, list):
    return sep.join([x for x in list if x])

def trim_lines(text):
    trimmed_lines = [line.trim() for line in text.splitlines()]
    return '\n'.join(trimmed_lines)

def make_omnetpp_project_description(version, base_version=None):
    # Some patch releases are installed by downloading the preceding release ("base version"),
    # and patching them from the repo.
    base_version = base_version or version
    github_url = "https://github.com/omnetpp/omnetpp"

    # All major and minor releases have been patched to work with modern a C++ compiler, tools like
    # bison/flex, and libraries, and also to have similar setenv scripts.
    # Patch branches in the repo are in the form "omnetpp-<major>.<minor>.x", and are based off
    # the last patch release of that major/minor release. E.g. "omnetpp-4.2.x" is based off "omnetpp-4.2.2".
    # Those modernized versions require much fewer quirks to set up and compile.
    is_modernized = version.endswith(".x") or version=="master" #TODO and new patch releases from the .x branches, and releases after 6.0.1

    # Github automatically makes source archives available under a different URL for tags and branches.
    is_git_branch = version.endswith(".x") or version=="master"

    # It is possible to install from locally downloaded tarballs and repo, using the  "local" or "local-git" options.
    # This is used mainly for testing. The following are the locations of the local files.
    downloads_dir = "~/projects/opp_env_downloads"
    local_omnetpp_git_repo = "~/projects/omnetpp-dev"

    # Some versions have no release tarballs on github, some don't even have an entry on the Releases page (5.4, 5.5, 5.7).
    # Source tarballs that github automatically makes are still available at URLs of the form
    # https://github.com/omnetpp/omnetpp/archive/refs/tags/omnetpp-<version>.tar.gz
    missing_releases = ["4.0", "4.2", "4.2.1", "4.4", "5.1", "5.2", "5.4", "5.5"]

    return {
        "name": "omnetpp",
        "version": version,
        "description": "OMNeT++ base system",
        "warning": join_nonempty_items(" ", [
            f"This version cannot be installed in the standard way, because the release tarball is no longer available. To install it from a source archive (which doesn't include the pre-built IDE), specify `--options=source-archive` on the command line." if version in missing_releases else None,
            f"This version is likely to compile with lots of warnings, not compile at all, or work incorrectly due to bit rotting (changes in the software environment)-- use the corresponding patch branch 'omnetpp-{dotx(version)}' for better results." if not is_modernized else None,
            "Specifically, this version compiles, but most simulation models won't work due to the original coroutine library being broken due to changes in the standard setjmp()/longjmp() implementation. (This has been resolved in the modernized patch branch and release.)" if not is_modernized and version.startswith("3.") else None,
            "Specifically, this version will not build due to various issues: incompatible changes from Bison 2.x to 3.x, changes in the Tcl/Tk C API from version 8.5 to 8.6 (interp->result), etc." if not is_modernized and version >= "4.0" and version < "4.3" else None,
            "Specifically, Qtenv in this version will not build in isolated mode due to a qmake problem (g++ not found error)." if not is_modernized and version.startswith("5.0.") else None,
        ]),
        "nixos": "nixos-22.11",
        "stdenv":
            "gcc7Stdenv" if version.startswith("3.") or version.startswith("4.") else
            "llvmPackages_14.stdenv",
        "external_nix_packages":
            ["ccache", "which", "bison", "flex", "perl", "xdg-utils", "qt5.qtbase", "qt5.qtsvg", "python3", "python3Packages.numpy", "python3Packages.scipy", "python3Packages.pandas", "python3Packages.matplotlib", "python3Packages.posix_ipc"] if version.startswith("6.") else
            ["temurin-jre-bin-8", "gtk2", "xorg.libXtst", "ccache", "which", "bison", "flex", "perl", "xdg-utils", "qt5.qtbase", "qt5.qtsvg", "python3", "tk", "tcl", "cairo" ] if version.startswith("5.") else
            ["temurin-jre-bin-8", "gtk2", "xorg.libXtst", "ccache", "which", "bison", "flex", "perl", "xdg-utils", "tk-8_5", "tcl-8_5", "libxml2", "expat" ] if version.startswith("4.") else
            ["ccache", "which", "bison", "flex", "perl", "xdg-utils", "tk", "tcl", "libxml2", "expat" ] if version.startswith("3.") else [],
        "download_url":
            "" if version in missing_releases else
            f"{github_url}/releases/download/omnetpp-{base_version}/omnetpp-{base_version}-linux-x86_64.tgz" if base_version.startswith("6.") or base_version == "5.7" else
            f"{github_url}/releases/download/omnetpp-{base_version}/omnetpp-{base_version}-src.tgz" if base_version == "5.0" else
            f"{github_url}/releases/download/omnetpp-{base_version}/omnetpp-{base_version}-src-linux.tgz" if base_version.startswith("5.") else
            f"{github_url}/releases/download/omnetpp-4.0/omnetpp-4.0p1-src.tgz" if base_version == '4.0p1' else
            f"{github_url}/releases/download/omnetpp-{base_version}/omnetpp-{base_version}-src.tgz" if base_version.startswith("4.") else
            f"{github_url}/releases/download/omnetpp-3.3-ubuntu18.04/omnetpp-3.3-src-gcc73.tgz" if base_version == "3.3p1" else "",
        "patch_command": join_nonempty_items("\n", [
            f"""# apply diff between omnetpp-{base_version} and omnetpp-{version}
            wget -O configure {github_url}/raw/omnetpp-{base_version}/configure &&
            wget -O configure.in {github_url}/raw/omnetpp-{base_version}/configure.in &&
            wget -O patchfile.diff {github_url}/compare/omnetpp-{base_version}...omnetpp-{version}.patch &&
            git apply --whitespace=nowarn --exclude 'ui/*' --exclude '**/Makefile.vc' patchfile.diff
            """ if version != base_version else None,

            # Note: the following should be consistent with the similar commands in the option="local" version
            "sed -i 's|exit 1|# exit 1|' setenv" if not is_modernized and version.startswith("4.") else None, # otherwise setenv complains and exits
            "sed -i 's|echo \"Error: not a login shell|# echo \"Error: not a login shell|' setenv" if not is_modernized and version.startswith("4.") else None, # otherwise setenv complains and exits

            "sed -i '/#include <stdlib.h>/a #include <unistd.h> // added by opp_env' src/utils/abspath.cc" if not is_modernized and version >= "4.0" and version < "4.3" else None, # add missing include in unpatched 4.0/4.1/4.2

            "sed -i '/%pure_parser/a %lex-param {void *statePtr}' src/common/matchexpression.y" if not is_modernized and version >= "4.0" and version < "4.4" else None,
            "sed -i '/%pure_parser/a %parse-param {void *statePtr}' src/common/matchexpression.y" if not is_modernized and version >= "4.0" and version < "4.4" else None,
            "sed -i '/void yyerror (const char \\*s);/a void yyerror (void *statePtr, const char *s) {yyerror(s);}' src/common/matchexpression.y" if not is_modernized and version >= "4.0" and version < "4.4" else None,

            "sed -i 's|static inline int64 abs(int64 x)|//static inline int64 abs(int64 x)|' src/common/bigdecimal.cc" if not is_modernized and version >= "4.0" and version < "4.2" else None,
            "sed -i 's|int64 val = abs(this->intVal);|int64 val = this->intVal < 0 ? -this->intVal : this->intVal;|' src/common/bigdecimal.cc" if not is_modernized and version >= "4.0" and version < "4.2" else None,
            "sed -i 's/(state)<<1/((state)<0 ? -((-(state))<<1) : (state)<<1)/' include/cfsm.h" if not is_modernized and version >= "4.0" and version < "4.4" else None,

            "sed -i '1s|.*|#!/bin/env perl|;2s|.*||' src/nedc/opp_msgc" if version == "3.3p1" else None, # otherwise calling msgc from a Makefile fails

            "mkdir -p bin",
            "[ ! -f configure.user ] && [ -f configure.user.dist ] && cp configure.user.dist configure.user", # create default configure.user from configure.user.dist unless already exists
            "sed -i 's|^WITH_OSG=yes|WITH_OSG=no|' configure.user",  # we currently don't support OSG and osgEarth in opp_env
            "sed -i 's|^WITH_OSGEARTH=yes|WITH_OSGEARTH=no|' configure.user",
            "sed -i 's|^QT_VERSION=4|QT_VERSION=5|' configure.user" if version=="5.0" else None,

            "sed -i '/^PERL =/i CFLAGS += -std=c++03 -fpermissive -Wno-c++11-compat -Wno-deprecated-declarations' Makefile.inc.in" if not is_modernized and version >= "4.0" and version < "4.4" else None,
        ]),
        "shell_hook_command": join_nonempty_items("\n", [
            """export QT_PLUGIN_PATH=${pkgs.qt5.qtbase.bin}/${pkgs.qt5.qtbase.qtPluginPrefix}:${pkgs.qt5.qtsvg.bin}/${pkgs.qt5.qtbase.qtPluginPrefix}
            export QT_XCB_GL_INTEGRATION=''${QT_XCB_GL_INTEGRATION:-none}  # disable GL support as NIX does not play nicely with OpenGL (except on nixOS)
            """ if version.startswith("5.") or version.startswith("6.") else None,
            "export NIX_CFLAGS_COMPILE=\"$NIX_CFLAGS_COMPILE -isystem ${pkgs.libxml2.dev}/include/libxml2\"",
            "export LD_LIBRARY_PATH=\"$LD_LIBRARY_PATH:${pkgs.cairo}/lib\"" if version.startswith("5.") else None, # for tkpath in omnetpp-5.x Tkenv
            "export LD_LIBRARY_PATH=\"$LD_LIBRARY_PATH:${pkgs.gtk2}/lib\"" if version.startswith("5.") or version.startswith("4.") else None,
            "export LD_LIBRARY_PATH=\"$LD_LIBRARY_PATH:${pkgs.xorg.libXtst}/lib\"" if version.startswith("5.") or version.startswith("4.") else None,
            "export TK_LIBRARY=\"${pkgs.tk-8_5}/lib/tk8.5\"", #TODO whenever tk8.5 is used
            "export AR=    # due to the 'ar rs' problem" if not is_modernized else None,
        ]),
        "setenv_command":
            "export PATH=$(pwd)/bin:$PATH && export LD_LIBRARY_PATH=$(pwd)/lib:$LD_LIBRARY_PATH && export TCL_LIBRARY=$(echo 'puts [info library]; exit' | wish)" if version == "3.3p1" else
            "source setenv -f" if base_version.startswith("5.") else  # -f allows setenv to be called from scripts
            "source setenv",
        "configure_command":
            # "NO_TCL=1 ./configure" if not is_modernized and version >= "4.0" and version < "4.3" else  # Tkenv doesn't compile due to interp->result being removed in Tcl 8.6
            "./configure",
        "build_command":
            "make -j$NIX_BUILD_CORES" if version.startswith("5.") or version.startswith("6.") or is_modernized else # these can handle parallel build
            "make -j1", # use sequential build
        "clean_command": "make clean",
        "options": {
            "gcc7": {
                "option_description": "Use the GCC 7.5 compiler toolchain for the build",
                "conflicts_with": ["clang14"],
                "stdenv": "gcc7Stdenv",
            },
            "clang14": {
                "option_description": "Use the Clang 14 compiler toolchain for the build",
                "conflicts_with": ["gcc7"],
                "stdenv": "llvmPackages_14.stdenv",
            },
            "debug": {
                "option_description": "Build debug mode binaries",
                "conflicts_with": ["release"],
                "build_command":
                    "make -j$NIX_BUILD_CORES MODE=debug" if version.startswith("5.") or version.startswith("6.") or is_modernized else # these can handle parallel build
                    "make -j1 MODE=debug",
            },
            "release": {
                "option_description": "Build release mode binaries",
                "conflicts_with": ["debug"],
                "build_command":
                        "make -j$NIX_BUILD_CORES MODE=release" if version.startswith("5.") or version.startswith("6.") or is_modernized else # these can handle parallel build
                        "make -j1 MODE=release",
            },
            "source-archive": {
                "option_description": "Install from source archive on github",
                "conflicts_with": ["git", "local", "local-git"],
                "download_url": f"https://github.com/omnetpp/omnetpp/archive/refs/{'heads' if is_git_branch else 'tags'}/omnetpp-{version}.tar.gz", #TODO fix branch name
                "download_command": ""
            },
            "git": {
                "option_description": "Install from git repo on github",
                "conflicts_with": ["source-archive", "local", "local-git"],
                "git_url": "https://github.com/omnetpp/omnetpp.git",
                "git_branch": f"omnetpp-{version}" if version[0].isdigit() else version, # TODO branch names like "master" don't need to be prefixed
                "download_command": "",
                "download_url": "",
            },
            "local": {
                "option_description": "Install from tarballs (and potentially, git repo) on local disk",
                "conflicts_with": ["source-archive", "git", "local-git"],
                "download_command": f"mkdir omnetpp-{version} && cd omnetpp-{version} && tar --strip-components=1 -xzf {downloads_dir}/omnetpp-{base_version}-linux-x86_64.tgz" if base_version.startswith("6.") or base_version == "5.7" else
                                    f"mkdir omnetpp-{version} && cd omnetpp-{version} && tar --strip-components=1 -xzf {downloads_dir}/omnetpp-{base_version}-src.tgz" if base_version == "5.0" else
                                    f"mkdir omnetpp-{version} && cd omnetpp-{version} && tar --strip-components=1 -xzf {downloads_dir}/omnetpp-{base_version}-src-linux.tgz" if base_version.startswith("5.") else
                                    f"mkdir omnetpp-{version} && cd omnetpp-{version} && tar --strip-components=1 -xzf {downloads_dir}/omnetpp-{base_version}-src.tgz" if base_version.startswith("4.") else
                                    f"mkdir omnetpp-{version} && cd omnetpp-{version} && tar --strip-components=1 -xzf {downloads_dir}/omnetpp-3.3-src-gcc73.tgz" if base_version == "3.3p1" else "",
                "download_url": "",
                "patch_command": join_nonempty_items("\n", [
                    f"""# apply diff between omnetpp-{base_version} and omnetpp-{version}
                    git --git-dir={local_omnetpp_git_repo}/.git show omnetpp-{base_version}:configure >configure &&
                    git --git-dir={local_omnetpp_git_repo}/.git show omnetpp-{base_version}:configure.in >configure.in &&
                    git --git-dir={local_omnetpp_git_repo}/.git diff omnetpp-{base_version}..omnetpp-{version} --patch > patchfile.diff &&
                    git apply --whitespace=nowarn --exclude 'ui/*' --exclude '**/Makefile.vc' patchfile.diff
                    """ if version != base_version else None,
                    # NOTE: the following should be the same as the default (non-option) version
                    "sed -i 's|exit 1|# exit 1|' setenv" if not is_modernized and version.startswith("4.") else None, # otherwise setenv complains and exits
                    "sed -i 's|echo \"Error: not a login shell|# echo \"Error: not a login shell|' setenv" if not is_modernized and version.startswith("4.") else None, # otherwise setenv complains and exits

                    "sed -i '/#include <stdlib.h>/a #include <unistd.h> // added by opp_env' src/utils/abspath.cc" if not is_modernized and version >= "4.0" and version < "4.3" else None, # add missing include in unpatched 4.0/4.1/4.2

                    "sed -i '/%pure_parser/a %lex-param {void *statePtr}' src/common/matchexpression.y" if not is_modernized and version >= "4.0" and version < "4.4" else None,
                    "sed -i '/%pure_parser/a %parse-param {void *statePtr}' src/common/matchexpression.y" if not is_modernized and version >= "4.0" and version < "4.4" else None,
                    "sed -i '/void yyerror (const char \\*s);/a void yyerror (void *statePtr, const char *s) {yyerror(s);}' src/common/matchexpression.y" if not is_modernized and version >= "4.0" and version < "4.4" else None,

                    "sed -i 's|static inline int64 abs(int64 x)|//static inline int64 abs(int64 x)|' src/common/bigdecimal.cc" if not is_modernized and version >= "4.0" and version < "4.2" else None,
                    "sed -i 's|int64 val = abs(this->intVal);|int64 val = this->intVal < 0 ? -this->intVal : this->intVal;|' src/common/bigdecimal.cc" if not is_modernized and version >= "4.0" and version < "4.2" else None,
                    "sed -i 's/(state)<<1/((state)<0 ? -((-(state))<<1) : (state)<<1)/' include/cfsm.h" if not is_modernized and version >= "4.0" and version < "4.4" else None,

                    "sed -i '1s|.*|#!/bin/env perl|;2s|.*||' src/nedc/opp_msgc" if version == "3.3p1" else None, # otherwise calling msgc from a Makefile fails
                    "mkdir -p bin",
                    "[ ! -f configure.user ] && [ -f configure.user.dist ] && cp configure.user.dist configure.user", # create default configure.user from configure.user.dist unless already exists
                    "sed -i 's|^WITH_OSG=yes|WITH_OSG=no|' configure.user",  # we currently don't support OSG and osgEarth in opp_env
                    "sed -i 's|^WITH_OSGEARTH=yes|WITH_OSGEARTH=no|' configure.user",
                    "sed -i 's|^QT_VERSION=4|QT_VERSION=5|' configure.user" if version=="5.0" else None,

                    #"sed -i 's|^#CFLAGS_DEBUG=|CFLAGS_DEBUG=\"-std=c++03 -fpermissive \"|' configure.user" if not is_modernized and version >= "4.0" and version < "4.4" else None,
                    #"sed -i 's|^#CFLAGS_RELEASE=|CFLAGS_RELEASE=\"-std=c++03 -fpermissive \"|' configure.user" if not is_modernized and version >= "4.0" and version < "4.4" else None,
                    "sed -i '/^PERL =/i CFLAGS += -std=c++03 -fpermissive -Wno-c++11-compat -Wno-deprecated-declarations' Makefile.inc.in" if not is_modernized and version >= "4.0" and version < "4.4" else None,
                ]),
            },
            "local-git": {
                "option_description": "Install from git repo on local disk",
                "conflicts_with": ["source-archive", "git", "local"],
                "download_command": f"git clone -l {local_omnetpp_git_repo} omnetpp-{version} --branch omnetpp-{version}", #TODO unless version="master"
                "download_url": "",
            }
        }
    }

def get_all_omnetpp_released_versions():
    released_versions = [
        "6.0.1", "6.0",
        "5.7", "5.6.2", "5.6.1", "5.6", "5.5.1", "5.4.1", "5.3", "5.2.1", "5.2", "5.1.1", "5.1", "5.0", # note: no linux tarball on github for: 5.1, 5.2, etc
        "4.6", "4.5", "4.4.1", "4.4", "4.3.1", "4.3", "4.2.2", "4.2.1", "4.2", "4.1", "4.0p1", "4.0", # note: no linux tarball on github for: 4.0, 4.2, 4.2.1, 4.4
        "3.3p1"
    ]
    return [make_omnetpp_project_description(version) for version in released_versions]

def get_all_omnetpp_patch_branches():
    base_versions_for_patch_branches = [
        "6.0.1",
        "5.7", "5.6.2", "5.5.1", "5.4.1", "5.3", "5.2.1", "5.1.1", "5.0",
        "4.6", "4.5", "4.4.1", "4.3.1", "4.2.2", "4.1", "4.0p1",
        "3.3p1"
    ]

    return [make_omnetpp_project_description(dotx(base_version), base_version) for base_version in base_versions_for_patch_branches]

def get_all_omnetpp_versions():
    return [
        *get_all_omnetpp_released_versions(),
        *get_all_omnetpp_patch_branches(),
        make_omnetpp_project_description("master", "omnetpp-6.0.1")

    ]
