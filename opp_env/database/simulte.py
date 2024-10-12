
def get_simulte_project_description(simulte_version, inet_versions, omnetpp_versions):
    is_git_branch = simulte_version == "master"
    git_branch_or_tag_name = f"v{simulte_version}" if simulte_version[0].isdigit() else simulte_version
    return {
        "name": "simulte", "version": simulte_version,
        "description": "LTE and LTE Advanced (3GPP Release 8 and beyond) user plane simulation model",
        "metadata": {
            "catalog_url": "https://omnetpp.org/download-items/SimuLTE.html",
        },
        "required_projects": {"inet": inet_versions, "omnetpp": omnetpp_versions},
        "smoke_test_commands": [
            "cd simulations/demo",
            """if [ "$BUILD_MODE" = "debug" ]; then SIMULTE_LIB=$(echo $SIMULTE_ROOT/out/*-debug/src/*lte*); fi""",
            """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""" if simulte_version >= "1.1.0" else """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX=""; fi""",
            """if [ "$BUILD_MODE" = "release" ]; then SIMULTE_LIB=$(echo $SIMULTE_ROOT/out/*-release/src/*lte*); BUILD_MODE_SUFFIX=""; fi""",
            """if [ "$BUILD_MODE" = "release" ]; then BUILD_MODE_SUFFIX=""; fi""" if simulte_version >= "1.1.0" else """if [ "$BUILD_MODE" = "release" ]; then BUILD_MODE_SUFFIX="_release"; fi""",
            "opp_run$BUILD_MODE_SUFFIX -l $SIMULTE_LIB -n $SIMULTE_ROOT/simulations:$SIMULTE_ROOT/src:$INET_ROOT/src -c VideoStreaming -r 0 -u Cmdenv --sim-time-limit=10s"
        ],
        "patch_commands": [
            "sed -i -E 's|-KINET_PROJ=[^ ]+|-KINET_PROJ=$(INET_ROOT)|' Makefile",
            "sed -i -E 's|^INET_DIR=.*|INET_DIR=$INET_ROOT/src|' src/run_lte",
            "find . -name omnetpp.ini | xargs -n1 sed -i -E 's|^image-path|#image-path|'", # we use OMNETPP_IMAGE_PATH instead
        ],
        "setenv_commands": [
            'export OMNETPP_IMAGE_PATH="$OMNETPP_IMAGE_PATH:$SIMULTE_ROOT/images"',
            # Note: no setenv script in SimuLTE
        ],
        "build_commands": [ "make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE" ],
        "clean_commands": [ "make clean MODE=$BUILD_MODE" ],
        "options": {
            "from-release": {
                "option_description": "Install from release tarball on GitHub",
                "option_category": "download",
                "option_is_default": not is_git_branch,
                "download_url":
                    f"https://github.com/inet-framework/simulte/releases/download/v{simulte_version}/simulte-{simulte_version}-src.tgz" if simulte_version == "1.2.0" else
                    f"https://github.com/inet-framework/simulte/archive/refs/tags/v{simulte_version}.tar.gz",
            },
            "from-git": {
                "option_description": "Install from git repo on GitHub",
                "option_category": "download",
                "option_is_default": is_git_branch,
                "git_url": "https://github.com/inet-framework/simulte.git",
                "git_branch": git_branch_or_tag_name,
            },
        },
    }

def get_project_descriptions():
    return [ get_simulte_project_description(simulte_version, inet_versions, omnetpp_versions) for simulte_version, inet_versions, omnetpp_versions in [
        ["1.2.0", ["4.2.10", "4.2.5"], ["5.7.*"]], # Contains the integration code required to work with Veins.
        ["1.1.0", ["3.6.6"], ["5.5.*"]], # Contains the integration code required to work with Veins. Tested on Ubuntu 18.04. It is NOT compatible with INET 4.x.
        ["0.9.1", ["3.4.0"], ["5.1.*"]], # It DOES NOT contain support for the Veins simulator. Note: Release notes lists omnetpp-5.0 as dependency, but inet-3.4.0 requires omnetpp-5.1.
        # ["master", ["4.3.2"], ["6.0.*"]],   # current master needs omnetpp-6.0pre10 and inet-4.3.2 which are not available in opp_env; doesn't build with inet-4.3.7 and omnetpp-6.0.*
    ]]
