import re

#TODO make version="master" work

def dotx(base_version):
    return re.sub("(\\d\\.\\d)[\\.p]\\d", "\\1", base_version) + ".x"  # 4.2, 4.2.1, 4.2p1 -> 4.2.x

def join_nonempty_items(sep, list):
    return sep.join([x for x in list if x])

def remove_blanks(list):
    return [x for x in list if x]

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

    # Packages required by the IDE to work. The IDE can be started and is usable for most versions.
    # It doesn't work in omnetpp-4.0 and 4.1, because it would require an older JRE version that is not present in the Nix repo.
    # A problem component is the embedded Webkit library, used as HTML widget in Eclipse (help, some tooltips, etc.)
    # It doesn't work for version 5.7 and 6.0 (due to some incompatible change in Webkit), but other versions should work.
    ide_packages = [
        "temurin-jre-bin-8" if version < "5.7" else None,  # 5.7, 6.0 and up have bundled JREs (JustJ)
        "gtk2", # SWT
        "xorg.libXtst",
        "stdenv.cc.cc.lib" if version < "4.6" else None  # for libstdc++.so used by our nativelibs; in 4.6 and up, it's statically linked
    ] if version >= "4.0" else []

    # Qtenv was added in omnetpp-5.0 (and coexisted with Tkenv throughout the 5.x series).
    # Note that omnetpp-5.0 searches for Qt4 by default, but also accepts Qt5.
    qt_packages = ["qt5.qtbase", "qt5.qtsvg"] if version >= "5.0" else []

    # The default Tcl/Tk version in Nix is 8.6, and that's OK with most of our releases.
    # However, early 4.x versions don't compile with Tcl 8.6 because no longer supports "interp->result" in the C API, so they need version 8.5.
    # Tkenv was updated for Tcl 8.6 in version omnetpp-4.3. omnetpp-3.3p1 has no problem with 8.6, as it was updated for Tcl 8.6 earlier.
    # Cairo is required for the Tkpath plugin bundled with omnetpp in 5.x versions (those with cCanvas support).
    # Tkenv was removed in 6.0, Tcl/Tk is not required above that.
    tcltk_packages = [] if version >= "6.0" else ["tk", "tcl", "cairo"] if version >= "5.0" else ["tk", "tcl"] if is_modernized or version >= "4.3" else ["tk-8_5", "tcl-8_5"]

    # Various tools and libs required by / for building omnetpp. Note that we only started using Python in version 5.0.
    other_packages = ["bison", "flex", "perl", "libxml2", "expat", "which", "xdg-utils", "ccache", "vim", ("python3" if version > "5.0" else None)]

    # Python packages required for the Analysis Tool and the omnetpp.scave package. Version 6.0 and up.
    python3package_packages = ["python3Packages.numpy", "python3Packages.scipy", "python3Packages.pandas", "python3Packages.matplotlib", "python3Packages.posix_ipc"] if version >= "6.0" else []

    # Unreleased patch versions are produced by downloading the preceding release, then applying the diff downloaded from github.
    apply_release_patch_from_github_commands = [
        f"""# apply diff between omnetpp-{base_version} and omnetpp-{version}
        wget -O configure {github_url}/raw/omnetpp-{base_version}/configure &&
        wget -O configure.in {github_url}/raw/omnetpp-{base_version}/configure.in &&
        wget -O patchfile.diff {github_url}/compare/omnetpp-{base_version}...omnetpp-{version}.patch &&
        git apply --whitespace=nowarn --exclude 'ui/*' --exclude '**/Makefile.vc' patchfile.diff
        """ if version != base_version else None,
    ]

    apply_release_patch_from_local_repo_commands = [
        f"""# apply diff between omnetpp-{base_version} and omnetpp-{version}
        git --git-dir={local_omnetpp_git_repo}/.git show omnetpp-{base_version}:configure >configure &&
        git --git-dir={local_omnetpp_git_repo}/.git show omnetpp-{base_version}:configure.in >configure.in &&
        git --git-dir={local_omnetpp_git_repo}/.git diff omnetpp-{base_version}..omnetpp-{version} --patch > patchfile.diff &&
        git apply --whitespace=nowarn --exclude 'ui/*' --exclude '**/Makefile.vc' patchfile.diff
        """ if version != base_version else None,
    ]

    # Vanilla 4.x releases need to be patched to compile under Nix.
    # Compiling with '-std=c++03 -fpermissive' helps, but is not enough.
    source_patch_commands = [
        "sed -i 's|exit 1|# exit 1|' setenv" if not is_modernized and version.startswith("4.") else None, # otherwise setenv complains and exits
        "sed -i 's|echo \"Error: not a login shell|# echo \"Error: not a login shell|' setenv" if not is_modernized and version.startswith("4.") else None, # otherwise setenv complains and exits

        "sed -i '1s|.*|#!/bin/env perl|;2s|.*||' src/nedc/opp_msgc" if version == "3.3p1" else None, # otherwise calling msgc from a Makefile fails

        "sed -i 's/\\$(QMAKE)/$(QMAKE) -spec linux-clang' src/qtenv/Makefile" if version == "5.0" else None,

        "sed -i '/#include <stdlib.h>/a #include <unistd.h> // added by opp_env' src/utils/abspath.cc" if not is_modernized and version >= "4.0" and version < "4.3" else None, # add missing include in unpatched 4.0/4.1/4.2
        "sed -i 's|static inline int64 abs(int64 x)|//static inline int64 abs(int64 x)|' src/common/bigdecimal.cc" if not is_modernized and version >= "4.0" and version < "4.2" else None,
        "sed -i 's|int64 val = abs(this->intVal);|int64 val = this->intVal < 0 ? -this->intVal : this->intVal;|' src/common/bigdecimal.cc" if not is_modernized and version >= "4.0" and version < "4.2" else None,
        "sed -i 's/(state)<<1/((state)<0 ? -((-(state))<<1) : (state)<<1)/' include/cfsm.h" if not is_modernized and version >= "4.0" and version < "4.4" else None,
        "sed -i 's/va_copy/__va_copy/' src/tkenv/tkenv.cc" if not is_modernized and version.startswith("4.") and version >= "4.1" else None,

        # Early 4.x versions were written for Bison 2.x, but Nix only has Bison 3.x, so the grammar needs to be patched.
        "sed -i '/%pure_parser/a %lex-param {void *statePtr}' src/common/matchexpression.y" if not is_modernized and version >= "4.0" and version < "4.4" else None,
        "sed -i '/%pure_parser/a %parse-param {void *statePtr}' src/common/matchexpression.y" if not is_modernized and version >= "4.0" and version < "4.4" else None,
        "sed -i '/void yyerror (const char \\*s);/a void yyerror (void *statePtr, const char *s) {yyerror(s);}' src/common/matchexpression.y" if not is_modernized and version >= "4.0" and version < "4.4" else None,
    ]

    # Adjust settings in configure.user so that a simple ./configure will do in the configuration phase.
    # Note the CFLAGS can only be specified in a convenient way by patching Makefile.inc.
    configuration_patch_commands = [
        "mkdir -p bin",
        "[ ! -f configure.user ] && [ -f configure.user.dist ] && cp configure.user.dist configure.user", # create default configure.user from configure.user.dist unless already exists
        "sed -i 's|^WITH_OSG=yes|WITH_OSG=no|' configure.user",  # we currently don't support OSG and osgEarth in opp_env
        "sed -i 's|^WITH_OSGEARTH=yes|WITH_OSGEARTH=no|' configure.user",
        "sed -i 's|^QT_VERSION=4|QT_VERSION=5|' configure.user" if version.startswith("5.0") else None, # 5.0.x too!
        "sed -i '/^PERL =/i CFLAGS += -std=c++03 -fpermissive -Wno-c++11-compat -Wno-deprecated-declarations' Makefile.inc.in" if not is_modernized and version.startswith("4.") else None,
    ]

    # More recent releases can handle parallel build
    allow_parallel_build = version.startswith("5.") or version.startswith("6.") or is_modernized
    num_build_cores = '$NIX_BUILD_CORES' if allow_parallel_build else '1'

    return {
        "name": "omnetpp",
        "version": version,
        "description": "OMNeT++ base system",
        "warnings": remove_blanks([
            f"INSTALLATION: This version cannot be installed in the standard way, because the release tarball is no longer available. To install it from a source archive (which doesn't include the pre-built IDE), specify '--options=source-archive' on the command line." if version in missing_releases else None,
            join_nonempty_items(" ", [
                f"BETTER VERSION EXISTS: This version is likely to compile with lots of warnings, not compile at all, or work incorrectly due to bit rotting (changes in the software environment) -- use the corresponding patch branch 'omnetpp-{dotx(version)}' for better results." if not is_modernized else None,
                "Specifically, most simulation models won't work, because they use activity(), and the coroutine library in this release has become broken due to changes in the standard C library implementation of setjmp()/longjmp(). This issue has been resolved in the modernized patch branch and release.)" if not is_modernized and version.startswith("3.") else None,
                "Specifically, this version could only be made to compile with the combination of compiler options (C++03, permissiveness, warning suppression, etc.), patching (e.g. due to changes in Bison), and using an older Tcl/Tk library." if not is_modernized and version >= "4.0" and version < "4.3" else None,
                "Specifically, Qtenv in this version will not build in isolated mode due to a qmake problem (g++ not found error)." if not is_modernized and version.startswith("5.0.") else None
            ])
        ]),
        "nixos": "nixos-22.11",
        "stdenv":
            "gcc7Stdenv" if not is_modernized and (version.startswith("3.") or version.startswith("4.")) else
            "llvmPackages_14.stdenv",
        "external_nix_packages":
            remove_blanks([*ide_packages, *qt_packages, *tcltk_packages, *other_packages, *python3package_packages]),
        "download_url":
            "" if version in missing_releases else
            f"{github_url}/releases/download/omnetpp-{base_version}/omnetpp-{base_version}-linux-x86_64.tgz" if base_version.startswith("6.") or base_version == "5.7" else
            f"{github_url}/releases/download/omnetpp-{base_version}/omnetpp-{base_version}-src.tgz" if base_version == "5.0" else
            f"{github_url}/releases/download/omnetpp-{base_version}/omnetpp-{base_version}-src-linux.tgz" if base_version.startswith("5.") else
            f"{github_url}/releases/download/omnetpp-4.0/omnetpp-4.0p1-src.tgz" if base_version == '4.0p1' else
            f"{github_url}/releases/download/omnetpp-{base_version}/omnetpp-{base_version}-src.tgz" if base_version.startswith("4.") else
            f"{github_url}/releases/download/omnetpp-3.3-ubuntu18.04/omnetpp-3.3-src-gcc73.tgz" if base_version == "3.3p1" else "",
        "patch_command": join_nonempty_items("\n", [
            *apply_release_patch_from_github_commands,
            *source_patch_commands,
            *configuration_patch_commands
        ]),
        "shell_hook_command": join_nonempty_items("\n", [
            "export QT_PLUGIN_PATH=${pkgs.qt5.qtbase.bin}/${pkgs.qt5.qtbase.qtPluginPrefix}:${pkgs.qt5.qtsvg.bin}/${pkgs.qt5.qtbase.qtPluginPrefix}" if qt_packages else None,
            "export QT_XCB_GL_INTEGRATION=''${QT_XCB_GL_INTEGRATION:-none}  # disable GL support as NIX does not play nicely with OpenGL (except on nixOS)" if qt_packages else None,
            "export NIX_CFLAGS_COMPILE=\"$NIX_CFLAGS_COMPILE -isystem ${pkgs.libxml2.dev}/include/libxml2\"" if "libxml2.dev" in other_packages else None,
            "export LD_LIBRARY_PATH=\"$LD_LIBRARY_PATH:${pkgs.cairo}/lib\"" if "cairo" in tcltk_packages else None,
            "export LD_LIBRARY_PATH=\"$LD_LIBRARY_PATH:${pkgs.gtk2}/lib\"" if "gtk2" in ide_packages else None,
            "export LD_LIBRARY_PATH=\"$LD_LIBRARY_PATH:${pkgs.xorg.libXtst}/lib\"" if "xorg.libXtst" in ide_packages else None,
            "export LD_LIBRARY_PATH=\"$LD_LIBRARY_PATH:${pkgs.stdenv.cc.cc.lib}/lib\"" if "stdenv.cc.cc.lib" in ide_packages else None,
            "export TK_LIBRARY=\"${pkgs.tk-8_5}/lib/tk8.5\"" if "tcl-8_5" in tcltk_packages else None,
            "export AR=    # Older/unpatched omnetpp versions require AR to be defined as 'ar rs' (not just 'ar'), so rather undefine it" if not is_modernized else None,
            # alternative: "AR=\"${AR:-ar} cr\""
        ]),
        "setenv_command":
            "export PATH=$(pwd)/bin:$PATH && export LD_LIBRARY_PATH=$(pwd)/lib:$LD_LIBRARY_PATH && export TCL_LIBRARY=$(echo 'puts [info library]; exit' | wish)" if version == "3.3p1" else
            "source setenv -f" if base_version.startswith("5.") else  # -f allows setenv to be called from scripts
            "source setenv",
        "build_command": f"[ -f config.status ] || ./configure && make -j{num_build_cores}",
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
                "build_command": f"[ -f config.status ] || ./configure && make -j{num_build_cores} MODE=debug",
            },
            "release": {
                "option_description": "Build release mode binaries",
                "conflicts_with": ["debug"],
                "build_command": f"[ -f config.status ] || ./configure && make -j{num_build_cores} MODE=release",
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
                    *apply_release_patch_from_local_repo_commands,
                    *source_patch_commands,
                    *configuration_patch_commands
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
