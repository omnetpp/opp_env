import re
import platform

def join_nonempty_items(sep, list):
    return sep.join([x for x in list if x])

def remove_blanks(list):
    return [x for x in list if x]

def trim_lines(text):
    trimmed_lines = [line.trim() for line in text.splitlines()]
    return '\n'.join(trimmed_lines)

def make_omnetpp_project_description(version, base_version=None, is_modernized=False):
    canonical_version = version.replace("p", ".") if re.match(r"\d+\.\d+p\d+", version) else version+".0" if version.count('.') == 1 else version

    # Some patch releases are installed by downloading the preceding release ("base version"),
    # and patching them from the repo.
    base_version = base_version or version
    github_url = "https://github.com/omnetpp/omnetpp"

    # Github automatically makes source archives available under a different URL for tags and branches.
    is_git_branch = version.endswith(".x") or version=="git"

    git_branch_or_tag_name = f"omnetpp-{version}" if version[0].isdigit() else "master" if version == "git" else version

    # Some versions have no release tarballs on github, some don't even have an entry on the Releases page (5.4, 5.5).
    # Source tarballs that github automatically makes are still available at URLs of the form
    # https://github.com/omnetpp/omnetpp/archive/refs/tags/omnetpp-<version>.tar.gz
    missing_releases = ["5.4", "5.5"]

    # Some downloads have the OS (Linux or macOS) in the file name; we only care about these two, because Windows doesn't have Nix
    is_macos = platform.system().lower() == "darwin"
    is_linux = platform.system().lower() == "linux"
    os_name = "macos" if is_macos else "linux" if is_linux else "unsupported"
    os_name_x = "macosx" if is_macos else "linux" if is_linux else "unsupported"  # alternative name used in some URLs for 5.x versions

    # some versions have machine architecture specific versions (aarch64, x86_64, etc.)
    is_x86_64 = platform.machine().lower() == "x86_64"
    is_aarch64 = platform.machine().lower() == "arm64" or platform.machine().lower() == "aarch64"
    arch_name = "x86_64" if is_x86_64 else "aarch64" if is_aarch64 else "unsupported"

    # old versions don't support Apple Silicon, although they could be made to work via emulation
    is_unsupported_apple_silicon = version < "6.0" and is_macos and is_aarch64

    # whether we can support the IDE considering the required JRE on the OS and architecture
    # we do not support the IDE below 4.2 because of incompatibilities with JRE 8
    is_ide_supported = (version >= "5.7") or (version >= "4.2" and is_x86_64)

    # 5.7, 6.0 and up have bundled JREs (JustJ) so we don't depend on a JRE package
    jre_package = "temurin-jre-bin-8" if is_ide_supported and version < "5.7" else None

    # Packages required by the IDE to work. The IDE can be started and is usable for most versions.
    # It doesn't work in omnetpp-4.0 and 4.1, because it would require an older JRE version that is not present in the Nix repo.
    # A problem component is the embedded Webkit library, used as HTML widget in Eclipse (help, some tooltips, etc.)
    # It doesn't work for version 5.6 and below (due to some incompatible change in Webkit), but newer versions should work.
    linux_ide_packages = [
        "graphviz", "doxygen", # required for NED doc builder
        "gtk2" if version < "5.2" else "gtk3", # SWT (eclipse 4.7 and up is using gtk3)
        "glib", "glib-networking", "libsecret",
        "cairo", "freetype", "fontconfig", "xorg.libXtst", "xorg.libX11", "xorg.libXrender",
        "adw-gtk3", "gsettings-desktop-schemas", "zlib",
        "webkitgtk" if version < "6.2" else "webkitgtk_4_1",
        "stdenv.cc", # required for the CDT discovery mechanism (as it is hardcoded to use gcc/g++)
        "stdenv.cc.cc.lib" if version < "5.2" else None  # for libstdc++.so used by our nativelibs; in 5.2 and up, it's statically linked
    ] if is_ide_supported else []

    ide_packages = [jre_package] + (linux_ide_packages if is_linux else [])

    # Qtenv was added in omnetpp-5.0 (and coexisted with Tkenv throughout the 5.x series).
    # Note that omnetpp-5.0 searches for Qt4 by default, but also accepts Qt5.
    qt_packages = [] if version < "5.0" else  ["qt5.qtbase", "qt5.qtsvg", "qt5.qtwayland" if is_linux else None] if version < "6.2" \
                  else ["qt6ct", "adwaita-qt6", "kdePackages.breeze", "qt6.qtbase", "qt6.qtsvg", "qt6.qtwayland" if is_linux else None]

    # The default Tcl/Tk version in Nix is 8.6, and that's OK with most of our releases.
    # However, early 4.x versions don't compile with Tcl 8.6 because no longer supports "interp->result" in the C API, so they need version 8.5.
    # Tkenv was updated for Tcl 8.6 in version omnetpp-4.3. omnetpp-3.3.1 has no problem with 8.6, as it was updated for Tcl 8.6 earlier.
    # Cairo is required for the Tkpath plugin bundled with omnetpp in 5.x versions (those with cCanvas support).
    # Tkenv was removed in 6.0, Tcl/Tk is not required above that.
    tcltk_packages = [] if version >= "6.0" else ["tk-8_6", "tcl-8_6", "cairo"] if version >= "5.0" else ["tk-8_6", "tcl-8_6"] if is_modernized or version >= "4.3" else ["tk-8_5", "tcl-8_5"]
    tcltk_packages += ["darwin.apple_sdk.frameworks.Carbon"] if is_macos and version >= "4.0" and version < "5.1" else []
    tcltk_libs = "-ltcl8.5 -ltk8.5" if ("tcl-8_5" in tcltk_packages) else "-ltcl8.6 -ltk8.6" if ("tcl-8_6" in tcltk_packages) else ""

    # Various tools and libs required by / for building omnetpp. Note that we only started using Python in version 5.0.
    # NOTE: We have to explicitly specify and use gnumake 4.2 (instead of relying on the version bundled in the stdenv).
    # Later versions (especially >= 4.4) have introduced backward-incompatible changes with pattern rules that are incompatible
    # with older OMNeT++ releases. These issues can even cause mysterious compiler crashes on subsequent builds because of
    # concurrency issues between the message compiler and the compiler.
    other_packages = ["llvmPackages.bintools", "bison", "flex", "perl", "libxml2", "expat", "which", "xdg-utils", "pkg-config", "ccache", "gnumake42", ("gdb" if not is_macos else None), "vim", ("python3" if version > "5.0" else None)]

    # Python packages required for the Analysis Tool and the omnetpp.scave package. Version 6.0 and up.
    # note: "python3Packages.pyqt*" are needed by matplotlib in opp_charttool
    python3package_packages = ["python3Packages.numpy", "python3Packages.scipy", "python3Packages.pandas", "python3Packages.matplotlib", "python3Packages.posix_ipc"] if version >= "6.0" else []

    python3package_packages += [] if version < "6.0" else ["python3Packages.pyqt5"] if version < "6.2" else ["python3Packages.pyqt6"]

    python3package_packages += [] if version < "6.0" else ["python3Packages.setuptools"] if version < "6.2" else ["python3Packages.packaging", "python3Packages.ipython"]

    # Unreleased patch versions are produced by downloading the preceding release, then applying the diff downloaded from github.
    base_release_to_actual_version_patch_commands = [] if version == base_version else [
        f"echo 'Patching vanilla omnetpp-{base_version} to {git_branch_or_tag_name} from git...'",
        'if [ "$LOCAL_OPERATION" == "" ]; then',
        f"  curl -L -sS -o configure {github_url}/raw/omnetpp-{base_version}/configure",
        f"  curl -L -sS -o configure.in {github_url}/raw/omnetpp-{base_version}/configure.in",
        f"  curl -L -sS -o patchfile.diff {github_url}/compare/omnetpp-{base_version}...omnetpp-{version}.patch",
        f"  git apply --whitespace=nowarn --allow-empty --exclude .gitignore --exclude 'ui/*' --exclude 'releng/*' --exclude '**/Makefile.vc' patchfile.diff",
        'else',
        f'  [ -d $OMNETPP_REPO/.git ] || error "Error: OMNETPP_REPO=$OMNETPP_REPO is not set or does not point to a git repository on the local disk (required for obtaining patch to upgrade base release omnetpp-{base_version} to requested version omnetpp-{version})"',
        f"  git --git-dir=$OMNETPP_REPO/.git show omnetpp-{base_version}:configure >configure",
        f"  git --git-dir=$OMNETPP_REPO/.git show omnetpp-{base_version}:configure.in >configure.in",
        f"  git --git-dir=$OMNETPP_REPO/.git diff omnetpp-{base_version}..origin/{git_branch_or_tag_name} --patch > patchfile.diff",
        f"  git apply --whitespace=nowarn --allow-empty --exclude .gitignore --exclude 'ui/*' --exclude 'releng/*' --exclude '**/Makefile.vc' patchfile.diff",
        'fi',
    ]

    # Vanilla 4.x releases need to be patched to compile under Nix.
    # Compiling with '-std=c++03 -fpermissive' helps, but is not enough.
    source_patch_commands = [
        # patch the simulator executables/IDE/build system if we are in an opp_env shell so later it does not allow running outside of an opp_env shell
        """[ -n "$OPP_ENV_VERSION" ] && sed -i 's/cStaticFlag dummy;/cStaticFlag dummy;\\n    if (!getenv("OPP_ENV_VERSION") || !getenv("OMNETPP_ROOT")) { std::cerr << "<!> Error: This OMNeT++ installation cannot be used outside an opp_env shell." << std::endl; return 1; }/' """ + ("src/envir/evmain.cc" if version >= "4.2" else "src/envir/main.cc"),
        # set the LD_LIBRARY_PATH in opp_ide (or omnetpp/omnest) so the IDE will be able properly access the required dependencies
        f"""[ -n "$OPP_ENV_VERSION" ] && sed -i -E 's|#!/bin/(.*)|#!/bin/\\1\\nexport LD_LIBRARY_PATH="$LD_LIBRARY_PATH{":${pkgs.zlib}/lib" if "zlib" in ide_packages else ""}{":${pkgs.cairo}/lib" if "cairo" in (tcltk_packages + ide_packages) else ""}{":${pkgs.gtk2}/lib" if "gtk2" in ide_packages else ""}{":${pkgs.gtk3}/lib" if "gtk3" in ide_packages else ""}{":${pkgs.glib.out}/lib" if "glib" in ide_packages else ""}{":${pkgs.libsecret}/lib" if "libsecret" in ide_packages else ""}{":${pkgs.webkitgtk}/lib" if "webkitgtk" in ide_packages else ""}{":${pkgs.xorg.libXtst}/lib" if "xorg.libXtst" in ide_packages else ""}{":${pkgs.stdenv.cc.cc.lib}/lib" if "stdenv.cc.cc.lib" in ide_packages else ""}" |' """ + (" src/utils/opp_ide" if version >= "6.0" else " src/utils/omnetpp src/utils/omnest" ) if version >= "4.0" else None,
        """[ -n "$OPP_ENV_VERSION" ] && sed -i -E 's|#!/bin/(.*)|#!/bin/\\1\\n[ -z $OPP_ENV_VERSION ] \\&\\& echo "<!> Error: This OMNeT++ installation cannot be used outside an opp_env shell." \\&\\& exit 1|' """ + ("src/utils/opp_ide" if version >= "6.0" else "src/utils/omnetpp src/utils/omnest" ) if version >= "4.0" else None,
        """[ -n "$OPP_ENV_VERSION" ] && sed -i 's/OMNETPP_PRODUCT = @OMNETPP_PRODUCT@/ifndef OPP_ENV_VERSION\\n  $(error This OMNeT++ installation cannot be used outside an opp_env shell.)\\nendif\\nOMNETPP_PRODUCT = @OMNETPP_PRODUCT@/' Makefile.inc.in""" if version >= "4.0" else None,

        # disable the IDE launcher scripts on unsupported os/arch
        "sed -i 's/echo Starting the.*/echo The IDE is not supported on this OS and platform ; exit 1/' src/utils/omnetpp src/utils/omnest" if (not is_ide_supported) and version >= "4.0" else None,

        # binary patch the IDE so proper glibc and interpreter is used by the eclipse launcher and the JRE executables under the Nix environment
        # Only do it in nix environment. Using glob patterns and enabling nullglob are important because theses file may or may not be present in a distro (depending on the distro version)
        "[ -n $OPP_ENV_VERSION -a -n $NIX_BINTOOLS ] && (shopt -s nullglob && patchelf --set-interpreter $(cat $NIX_BINTOOLS/nix-support/dynamic-linker) ide/*opp_ide ide/*omnetpp ide/*omnetpp64 ide/linux64/*omnetpp ide/plugins/org.eclipse.justj.*/jre/bin/* ; shopt -u nullglob) || true" if is_linux and is_ide_supported else None,

        # adhoc code signature is required for the IDE native lib on aarch64/macOS systems
        # absolute path required otherwise codesign is not reachable in isolated shells (i.e. durinb install/build)
        "/usr/bin/codesign --force -s - ide/opp_ide.app/Contents/Eclipse/plugins/org.omnetpp.ide.nativelibs.macosx*/libopplibs.jnilib" if version >= "6.0" and is_macos and is_aarch64 else None,

        # remove deprecated GetCurrentProcess() and TransformProcessType() calls from qtenv.cc (not present on aarch64)
        "sed -i 's|GetCurrentProcess.*;||' src/qtenv/qtenv.cc" if version.startswith("6.0") and is_macos and is_aarch64 else None,
        "sed -i 's|TransformProcessType.*;||' src/qtenv/qtenv.cc" if version.startswith("6.0") and is_macos and is_aarch64 else None,

        # delete and disable most bundled tools on macOS/x86_64 as they are not required when compiling under Nix (except the debugger helper)
        """find tools/macos.x86_64/bin -mindepth 1 -not -name 'lldbmi2' -delete && (cd tools/macos.x86_64 && rm -rf doc include lib mkspecs plugins share) ;
        sed -i -e 's|export QT_PLUGIN_PATH|#export QT_PLUGIN_PATH|' -e 's|export BISON_PKGDATADIR|#export export BISON_PKGDATADIR|' setenv ;
        sed -i -e 's|export PIP_PREFIX|#export PIP_PREFIX|' -e 's|export PYTHONNOUSERSITE|#export PYTHONNOUSERSITE|' setenv
        """ if version < "6.1" and is_macos and is_x86_64 else None,

        "sed -i 's|exit 1|# exit 1|' setenv" if not is_modernized and version.startswith("4.") else None, # otherwise setenv complains and exits
        "sed -i 's|echo \"Error: not a login shell|# echo \"Error: not a login shell|' setenv" if not is_modernized and version.startswith("4.") else None, # otherwise setenv complains and exits

        "sed -i '1s|.*|#!/bin/env perl|;2s|.*||' src/nedc/opp_msgc" if version == "3.3.1" else None, # otherwise calling msgc from a Makefile fails
        "sed -i 's/#build_shared_libs=no/build_shared_libs=no/' configure.user.dist" if version < "4.0" and is_macos else None, # on macOS only static builds were properly supported

        # fix Qtenv build error in isolated mode ("g++ not found") due to a qmake issue
        "sed -i 's/\\$(QMAKE)/$(QMAKE) -spec linux-clang/' src/qtenv/Makefile" if version.startswith("5.0") else None,

        "sed -i '/#include/a #include <stdio.h> // added by opp_env' src/common/commondefs.h" if version == "4.0" else None, # add missing include in vanilla 4.0 release
        "sed -i '/#include <stdlib.h>/a #include <unistd.h> // added by opp_env' src/utils/abspath.cc" if not is_modernized and version >= "4.0" and version < "4.3" else None, # add missing include in unpatched 4.0/4.1/4.2
        "sed -i 's|static inline int64 abs(int64 x)|//static inline int64 abs(int64 x)|' src/common/bigdecimal.cc" if not is_modernized and version >= "4.0" and version < "4.2" else None,
        "sed -i 's|int64 val = abs(this->intVal);|int64 val = this->intVal < 0 ? -this->intVal : this->intVal;|' src/common/bigdecimal.cc" if not is_modernized and version >= "4.0" and version < "4.2" else None,
        "sed -i 's/(state)<<1/((state)<0 ? -((-(state))<<1) : (state)<<1)/' include/cfsm.h" if not is_modernized and version >= "4.0" and version < "4.4" else None,
        "sed -i 's/va_copy/__va_copy/' src/tkenv/tkenv.cc" if not is_modernized and version.startswith("4.") and version >= "4.1" else None,

        # Early 4.x versions were written for Bison 2.x, but Nix only has Bison 3.x, so the grammar needs to be patched.
        "sed -i '/%pure_parser/a %lex-param {void *statePtr}' src/common/matchexpression.y" if not is_modernized and version >= "4.0" and version < "4.4" else None,
        "sed -i '/%pure_parser/a %parse-param {void *statePtr}' src/common/matchexpression.y" if not is_modernized and version >= "4.0" and version < "4.4" else None,
        "sed -i '/void yyerror (const char \\*s);/a void yyerror (void *statePtr, const char *s) {yyerror(s);}' src/common/matchexpression.y" if not is_modernized and version >= "4.0" and version < "4.4" else None,

        # 5.x versions assumed python2 but now we have python3 only and a little patching is needed
        # for the opp_featuretool to work with python3
        "sed -i 's/raw_input()/input()/' src/utils/opp_featuretool" if version.startswith("5.") else None,

        # to avoid "error: invalid argument '-std=c++03' not allowed with 'C'" with tkImgPNG.c
        "sed -i 's/\\$(CC) -c \\$(COPTS)/\\$(CC) -c /' src/tkenv/Makefile" if not is_modernized and version == "4.0" else None,

        # some versions detect system-wide Tcl/Tk at fixed paths if TK_CFLAGS is empty, prevent that by giving a dummy include path (Nix will supply the actual one)
        f"sed -i '/# Compiler and linker options for/a TK_LIBS=\"{tcltk_libs}\"' configure.user" if not is_modernized and version >= "4.0" and version < "4.6" else None,
        f"sed -i '/# Compiler and linker options for/a TK_CFLAGS=\"-Idummy\"' configure.user" if not is_modernized and version >= "4.0" and version < "4.6" else None,

        # to disable tkdock calls which is not available on macOS / aarch64
        "sed -i 's|tkdock::switchIcon|# tkdock::switchIcon|' src/tkenv/startup.tcl" if not is_modernized and version >= "4.5" and version < "5.0" and is_macos and is_aarch64 else None, # on macos aarch64, tkdock is not supported
    ]

    # for older versions we use gcc7 (although a recent compiler with -std=c++03 -fpermissive would also do? -- TODO check)
    use_gcc7 = not is_modernized and (version.startswith("3.") or version.startswith("4.")) and not is_macos

    # Early 4.x versions need flags such as -std=c++03 -fpermissive to compile.
    # Note: technically, omnetpp itself would not need "-std=c++03" from version 4.3 on,
    # but inet versions from that time period (early 2.x) don't compile without it.
    # Note: -Wno-string-plus-int is for silencing tons of warnings in INET emitted for CASE() macros that
    # expand to expressions like ("TCP_I_TIMED_OUT"+6) where +6 serves to remove the "TCP_I_" prefix.
    # TODO -Wno-string-plus-int should probably be moved into INET.
    extra_cflags = (
        "-Wno-string-plus-int" if is_modernized else
        "-std=c++03 -fpermissive -Wno-c++11-compat -Wno-deprecated-declarations -Wno-string-plus-int -Wno-address-of-temporary" if version < "4.6" else
        "-Wno-deprecated-declarations -Wno-string-plus-int" if version >= "4.6" and version < "5.7" else "")
    extra_cflags += " -D_XOPEN_SOURCE" if is_macos and version >= "4.0" else "" # use _XOPEN_SOURCE on all macOS versions

    # Adjust settings in configure.user so that a simple ./configure will do in the configuration phase.
    # Note the CFLAGS can only be specified in a convenient way by patching Makefile.inc.
    configuration_patch_commands = [
        "mkdir -p bin",
        f"echo 'omnetpp-{version}' > Version",
        "[ -f configure.user.dist ] && cp configure.user.dist configure.user", # create default configure.user from configure.user.dist
        "sed -i 's|^WITH_LIBXML=no|WITH_LIBXML=yes|' configure.user",  # we can use LIBXML even on later version of OMNeT++ where it is optional
        "sed -i 's|^WITH_OSG=yes|WITH_OSG=no|' configure.user",  # we currently don't support OSG and osgEarth in opp_env
        "sed -i 's|^WITH_OSGEARTH=yes|WITH_OSGEARTH=no|' configure.user",
        "sed -i 's|^WITH_PARSIM=no|WITH_PARSIM=yes|' configure.user" if version >= "6.0" else None, # NOTE: we need WITH_PARSIM (but not MPI) for the "d" fingerprint ingredient to work
        """sed -i 's|#MPI_LIBS="-lmpi++ -lmpi"   #SGI|#MPI_LIBS="-lmpi++ -lmpi"   #SGI\\nMPI_LIBS="-ldisabled"|' src/sim/cfingerprint.cc""" if version.startswith("5.0") else None,
        """sed -i 's|#include "parsim/cmemcommbuffer.h"|#ifdef WITH_PARSIM\\n#include "parsim/cmemcommbuffer.h"\\n#endif|' src/sim/cfingerprint.cc""" if version.startswith("5.0") else None,
        """sed -i 's|cMemCommBuffer buffer;|#ifdef WITH_PARSIM\\ncMemCommBuffer buffer;|' src/sim/cfingerprint.cc""" if version.startswith("5.0") else None,
        """sed -i 's|delete copy;|delete copy;\\n#else\\nthrow cRuntimeError("Fingerprint is configured to contain MESSAGE_DATA (d),"\\n" but parallel simulation support is disabled (WITH_PARSIM=no)"\\n" which is required for serialization.");\\n#endif|' src/sim/cfingerprint.cc""" if version.startswith("5.0") else None,
        "sed -i 's|^QT_VERSION=4|QT_VERSION=5|' configure.user" if version.startswith("5.0") else None, # 5.0.x too!
        "sed -i 's|^WITH_TKENV=yes|WITH_TKENV=no|' configure.user" if version >= "5.0" and version < "6.0" and is_macos and is_aarch64 else None, # on macos aarch64, tkenv is not supported
        f"sed -i '/^PERL =/i CFLAGS += {extra_cflags}' Makefile.inc.in" if extra_cflags and version >= "4.0" else  # no Makefile.inc.in in 3.x yet
        f"sed -i 's/^CFLAGS=.*/CFLAGS=\\\"-O2 -DNDEBUG=1 {extra_cflags}\\\"/' configure.user" if extra_cflags and version < "4.0" else None,  # no Makefile.inc.in in 3.x yet

        # use the opp_env workspace as the default IDE workspace (on 6.1 or later, where auto importing of projects are supported)
        # and copy IDE startup script into it (auto-imports projects)
        "sed -i 's|../samples|../..|' src/utils/opp_ide""" if version >= "6.1" else None,
        "mkdir -p ../.metadata && cp \"$OPP_ENV_DIR/templates/metadata/startup.bsh\" ../.metadata" if version >= "6.1" else None,
    ]

    # More recent releases can handle parallel build
    allow_parallel_build = version.startswith("5.") or version.startswith("6.") or (is_modernized and version >= "4.1")
    num_build_cores = '$NIX_BUILD_CORES' if allow_parallel_build else '1'

    return {
        "name": "omnetpp",
        "version": canonical_version,
        "description": "OMNeT++ base system",
        "warnings": ["This version (versions <6.0) is not supported on Apple Silicon."] if is_unsupported_apple_silicon else remove_blanks([
            join_nonempty_items(" ", [
                f"This is not a modernized version of OMNeT++. Consider using a later patchlevel for a cleaner compilation and bug fixes." if not is_modernized and version >= "5.0" else None,
                f"This is not a modernized version of OMNeT++. Consider using a later patchlevel for a cleaner compilation, bug fixes, and compatibility with modern C++ compilers and libraries." if not is_modernized and version < "5.0" else None,
                "Specifically, most simulation models won't work, because they use activity(), and the coroutine library in this release has become broken due to changes in the standard C library implementation of setjmp()/longjmp(). This issue has been resolved in modernized patchlevel releases.)" if not is_modernized and version.startswith("3.") else None,
                "Specifically, this version could only be made to compile with the combination of compiler options (C++03, permissiveness, warning suppression, etc.), patching (e.g. due to changes in Bison), and using an older Tcl/Tk library." if not is_modernized and version >= "4.0" and version < "4.3" else None,
            ]),
            "The OMNeT++ IDE will not be available because this version is installed from source instead of a release tarball." if version in missing_releases or version == "git" else None,
            "The OMNeT++ IDE will not be available because a matching JRE is not available." if (version < "4.2" or (is_macos and is_aarch64 and version < "5.7")) and version >= "4.0" else None,
        ]),
        "metadata": {
            "modernized": is_modernized,
            "base_version": base_version,
        },

        # Default NIX version used by OMNeT++ 5.7.x and earlier: https://github.com/NixOS/nixpkgs/commits/22.11
        # TO ENSURE REPRODUCIBILITY, IT MUST NOT BE CHANGED FOR EXISTING VERSIONS.
        # IT MUST BE A TAG (i.e 22.11) AND NOT A BRANCH (nixos-22.11)
        "nixos": "22.11" if version < "6.0.0" else "23.05" if version < "6.1.0" else "24.11" if version < "6.2.0" else "25.05",
        "stdenv": None, # defined as default option
        "nix_packages":
            remove_blanks([*ide_packages, *qt_packages, *tcltk_packages, *other_packages, *python3package_packages]),
        "shell_hook_commands": [
            "echo 'Error: This OMNeT++ version (versions <6.0) is not supported on Apple Silicon.' && exit 1 " if is_unsupported_apple_silicon else None,

            "export QT_PLUGIN_PATH=${pkgs.qt5.qtbase.bin}/${pkgs.qt5.qtbase.qtPluginPrefix}:${pkgs.qt5.qtsvg.bin}/${pkgs.qt5.qtbase.qtPluginPrefix}" if "qt5.qtbase" in qt_packages else None,
            "export QT_PLUGIN_PATH=${pkgs.qt6.qtbase}/${pkgs.qt6.qtbase.qtPluginPrefix}:${pkgs.qt6.qtsvg}/${pkgs.qt6.qtbase.qtPluginPrefix}" if "qt6.qtbase" in qt_packages else None,

            "export QT_PLUGIN_PATH=$QT_PLUGIN_PATH:${pkgs.qt5.qtwayland.bin}/${pkgs.qt5.qtbase.qtPluginPrefix}" if "qt5.qtwayland" in qt_packages else None,
            "export QT_PLUGIN_PATH=$QT_PLUGIN_PATH:${pkgs.qt6.qtwayland}/${pkgs.qt6.qtbase.qtPluginPrefix}" if "qt6.qtwayland" in qt_packages else None,

            "export QT_PLUGIN_PATH=$QT_PLUGIN_PATH:${pkgs.kdePackages.breeze}/lib/qt-6/plugins" if "kdePackages.breeze" in qt_packages else None,
            "export QT_PLUGIN_PATH=$QT_PLUGIN_PATH:${pkgs.adwaita-qt6}/lib/qt-6/plugins" if "adwaita-qt6" in qt_packages else None,
            "export QT_QPA_PLATFORMTHEME=qt6ct" if "qt6ct" in qt_packages else None,

            "export GTK_THEME=Adwaita" if "adw-gtk3" in linux_ide_packages else None,

            "export QT_XCB_GL_INTEGRATION=''${QT_XCB_GL_INTEGRATION:-none}  # disable GL support as NIX does not play nicely with OpenGL (except on nixOS)" if qt_packages else None,

            "export NIX_CFLAGS_COMPILE=\"$NIX_CFLAGS_COMPILE -isystem ${pkgs.libxml2.dev}/include/libxml2\"" if "libxml2" in other_packages else None,
            "export XDG_DATA_DIRS=$XDG_DATA_DIRS:$GSETTINGS_SCHEMAS_PATH" if not is_macos else None,
            "export GIO_EXTRA_MODULES=${pkgs.glib-networking}/lib/gio/modules" if "gtk3" in ide_packages else None,
            "export TK_LIBRARY=\"${pkgs.tk-8_5}/lib/tk8.5\"" if "tcl-8_5" in tcltk_packages else None,
            "export AR=    # Older/unpatched omnetpp versions require AR to be defined as 'ar rs' (not just 'ar'), so rather undefine it" if not is_modernized else None,
            # alternative: "AR=\"${AR:-ar} cr\""
        ],
        "patch_commands": [
            *source_patch_commands,
            *configuration_patch_commands
        ],
        "setenv_commands": [
            # need to set OMNETPP_IMAGE_PATH explicitly, otherwise any model that sets it will silently make stock omnetpp images inaccessible;
            # unfortunately omnetpp setenv scripts don't set OMNETPP_IMAGE_PATH, so do it here
            "export OMNETPP_IMAGE_PATH=$OMNETPP_IMAGE_PATH:$(pwd)/images" if not is_modernized else None,

            "export PATH=$(pwd)/bin:$PATH && export LD_LIBRARY_PATH=$(pwd)/lib:$LD_LIBRARY_PATH && export TCL_LIBRARY=$(echo 'puts [info library]; exit' | wish)" if version == "3.3.1" else
            "source setenv" + (" -f" if base_version.startswith("5.") else ""), # -f allows setenv to be called from scripts

            # export which opp_run bin to use depending on omnetpp version
            # before 5.2.0, opp_run was debug, and opp_run_release was release
            # INET versions before 4.0 need the opp_run bin for running smoke tests; some INET versions work (e.g. 3.6.1) work with both omnetpp 5.2.0 and 5.1.2
            # which use differently named opp_run bins
            "export OPP_RUN_DBG_BIN=$OMNETPP_ROOT/bin/opp_run_dbg; export OPP_RUN_RELEASE_BIN=$OMNETPP_ROOT/bin/opp_run_release" if base_version >= "5.2" else "export OPP_RUN_DBG_BIN=$OMNETPP_ROOT/bin/opp_run; export OPP_RUN_RELEASE_BIN=$OMNETPP_ROOT/bin/opp_run_release" if base_version > "4.2" else "",
        ],
        "build_commands": [
            # "./configure && make" on steroids: magic "[" command ensures that ./configure is run whenever config.status is missing or is older than configure.user
            f"[ config.status -nt configure.user ] || ./configure && make -j{num_build_cores} MODE=$BUILD_MODE"
        ],
        "smoke_test_commands": [
            """if [ "$BUILD_MODE" = "debug" ]; then DEBUG_SUFFIX="_dbg"; fi """ if base_version >= "5.2" else None,
            "nedtool -h" if base_version.startswith("3.") else
            "cd samples/dyna; ./dyna$DEBUG_SUFFIX -u Cmdenv"
        ],
        "test_commands": [
            None if base_version < "6.0" else
            "cd test/core; MODE=$BUILD_MODE ./runtest"
        ],
        "clean_commands": [
            "make clean MODE=$BUILD_MODE"  #TODO plain "make clean" in early versions?
        ],
        "options": {  # note: git master doesn't have all these download options
            "nixos-recent": {
                "option_description": "Force using the latest (tested) version of NixOS",
                "option_category": "nixos",
                "nixos": "24.05",
            },
            "gcc7": {
                "option_description": "Use an older version of the gcc compiler toolchain for the build",
                "option_category": "compiler",
                "option_is_default": use_gcc7,
                "stdenv": "gcc7Stdenv",
            },
            "clang": {
                "option_description": "Use a recent version of the clang toolchain for the build",
                "option_category": "compiler",
                "option_is_default": not use_gcc7,
                "stdenv": "llvmPackages.stdenv",
            },
            "from-release": {
                "option_description": "Install from release tarball on GitHub",
                "option_category": "download",
                "option_is_default": version not in missing_releases and version != "git",
                "download_url":
                    "" if version in missing_releases or version == "git" else
                    f"{github_url}/releases/download/omnetpp-{base_version}/omnetpp-{base_version}-src.tgz" if base_version.startswith("3.") else
                    f"{github_url}/releases/download/omnetpp-4.0/omnetpp-4.0p1-src.tgz" if base_version == '4.0p1' else # special name for v4.0
                    f"{github_url}/releases/download/omnetpp-{base_version}/omnetpp-{base_version}-src.tgz" if base_version.startswith("4.") else # for versions 4.1 - 4.6 there is a single tarball for all OSes
                    f"{github_url}/releases/download/omnetpp-{base_version}/omnetpp-{base_version}-src{'-'+os_name_x if is_macos else ''}.tgz" if base_version.startswith("5.0") else # macOS has an OS-specific download for 5.0
                    f"{github_url}/releases/download/omnetpp-{base_version}/omnetpp-{base_version}-src-{os_name_x}.tgz" if base_version.startswith("5.") else # for versions 5.1 - 5.7 there are separate tarballs for each OS (linux or macosx)
                    f"{github_url}/releases/download/omnetpp-{base_version}/omnetpp-{base_version}-{os_name}-{'x86_64' if is_macos else arch_name}.tgz" if base_version == "6.0.0" or base_version == "6.0.1" else # for 6.0.0 and 6.0.1 there are separate tarballs for each architecture on Linux (x86_64, aarch64), but not on macOS (only x86_64)
                    f"{github_url}/releases/download/omnetpp-{base_version}/omnetpp-{base_version}-{os_name}-{arch_name}.tgz", # for later versions (6.0.2+) there are separate tarballs for each architecture on both Linux and macOS
                "patch_commands": [
                    "@prepend",
                    *base_release_to_actual_version_patch_commands,
                ],
                "vars_to_keep": [
                    "@append",
                    "OMNETPP_REPO"
                ],
            },
            "from-source-archive": {
                "option_description": "Install from source archive on GitHub (IDE will not be available)",
                "option_category": "download",
                "option_is_default": version in missing_releases,
                "download_url": f"https://github.com/omnetpp/omnetpp/archive/refs/{'heads' if is_git_branch else 'tags'}/{git_branch_or_tag_name}.tar.gz",
            },
            "from-git": {
                "option_description": "Install from git repo on GitHub (IDE will not be available)",
                "option_category": "download",
                "option_is_default": version == "git",
                "git_url": "https://github.com/omnetpp/omnetpp.git",
                "git_branch": git_branch_or_tag_name,
            },
        }
    }

def get_project_descriptions():
    # Modernized versions are marked with a "*" suffix.
    # Modernized versions build/work with modern a C++ compiler, bison/flex
    # and other tools and libraries, and also to have similar setenv scripts.
    released_versions = [
        "6.2.0*",
        "6.1.0*",
        "6.0.3*", "6.0.2*", "6.0.1", "6.0",
        "5.7.1*", "5.7",
        "5.6.3*", "5.6.2", "5.6.1", "5.6",
        "5.5.2*", "5.5.1", "5.5",
        "5.4.2*", "5.4.1", "5.4",
        "5.3.1*", "5.3",
        "5.2.2*", "5.2.1", "5.2",
        "5.1.2*", "5.1.1", "5.1",
        "5.0.1*", "5.0",
        "4.6.1*", "4.6",
        "4.5.1*", "4.5",
        "4.4.2*", "4.4.1", "4.4",
        "4.3.2*", "4.3.1", "4.3",
        "4.2.3*", "4.2.2", "4.2.1", "4.2",
        "4.1.1*", "4.1",
        "4.0.2*", "4.0p1",
        "3.3.2*", "3.3.1",
        # branches
        #"6.0.x:6.0.3",
        #"5.7.x:5.7.1", "5.6.x:5.6.3", "5.5.x:5.5.2", "5.4.x:5.4.2", "5.3.x:5.3.1", "5.2.x:5.2.2", "5.1.x:5.1.2", "5.0.x:5.0.1",
        #"4.6.x:4.6.1", "4.5.x:4.5.1", "4.4.x:4.4.2", "4.3.x:4.3.2", "4.2.x:4.2.3", "4.1.x:4.1.1", "4.0.x:4.0.2",
        #"3.3.x:3.3.2",
    ]
    descriptions = []
    for version in released_versions:
        version_name = version.split(":")[0].replace("*", "")
        base_version = version.split(":")[1] if ":" in version else None
        is_modernized = base_version is not None or "*" in version
        descriptions.append(make_omnetpp_project_description(version_name, base_version, is_modernized))
    master_description = make_omnetpp_project_description("git", None, True)

    return descriptions + [ master_description ]
