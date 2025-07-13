
def get_simu5g_project_description(simu5g_version, inet_versions, omnetpp_versions):
    is_git_branch = simu5g_version == "git"
    git_branch_or_tag_name = f"v{simu5g_version}" if simu5g_version[0].isdigit() else "master" if simu5g_version == "git" else simu5g_version
    return {
        "name": "simu5g", "version": simu5g_version,
        "description": "5G NR and LTE/LTE-A user-plane simulation model",
        "metadata": {
            "catalog_url": "https://omnetpp.org/download-items/Simu5G.html",
        },
        "required_projects": {"inet": inet_versions, "omnetpp": omnetpp_versions},
        "smoke_test_commands": [
            "cd simulations/LTE/demo" if simu5g_version >= "1.2.1" else "cd simulations/demo",
            "SIMU5G_EMULATION_ROOT=$SIMU5G_ROOT/emulation" if simu5g_version >= "1.2.1" else "",
            """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
            """if [ "$BUILD_MODE" = "release" ]; then BUILD_MODE_SUFFIX=""; fi""",
            "opp_run$BUILD_MODE_SUFFIX -l $SIMU5G_ROOT/src/simu5g -l $INET_ROOT/src/INET -n $SIMU5G_ROOT/simulations:$SIMU5G_EMULATION_ROOT:$SIMU5G_ROOT/src:$INET_ROOT/src -c VideoStreaming -r 0 -u Cmdenv --sim-time-limit=10s",
        ],
        "patch_commands": [
            "sed -i -E 's|-KINET_PROJ=[^ ]+|-KINET_PROJ=$(INET_ROOT)|' Makefile",
            "sed -i -E 's|^INET_SRC=.*|INET_SRC=$INET_ROOT/src|' bin/simu5g",
            "find . -name omnetpp.ini | xargs -n1 sed -i -E 's|^image-path|#image-path|'", # we use OMNETPP_IMAGE_PATH instead
        ],
        "setenv_commands": [
            'export OMNETPP_IMAGE_PATH="$OMNETPP_IMAGE_PATH:$SIMU5G_ROOT/images"',
            "source setenv -f"
        ],
        "build_commands": [ "make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE" ],
        "clean_commands": [ "make clean MODE=$BUILD_MODE" ],
        "options": {
            "from-release": {
                "option_description": "Install from release tarball on GitHub",
                "option_category": "download",
                "option_is_default": not is_git_branch,
                "download_url": None if is_git_branch else
                    f"https://github.com/Unipisa/Simu5G/archive/refs/tags/v{simu5g_version}.tar.gz" if simu5g_version < "1.3.0" else
                    f"https://github.com/Unipisa/Simu5G/releases/download/v{simu5g_version}/simu5g-{simu5g_version}-src.tgz",
            },
            "from-git": {
                "option_description": "Install from git repo on GitHub",
                "option_category": "download",
                "option_is_default": is_git_branch,
                "git_url": "https://github.com/Unipisa/Simu5G.git",
                "git_branch": git_branch_or_tag_name,
            },
        },
    }

def get_project_descriptions():
    return [ get_simu5g_project_description(simu5g_version, inet_versions, omnetpp_versions) for simu5g_version, inet_versions, omnetpp_versions in [
        ["1.3.0", ["4.5.*"], ["6.2.*", "6.1.*"]],
        ["1.2.3", ["4.5.*"], ["6.2.*", "6.1.*"]],
        ["1.2.2", ["4.5.*"], ["6.0.*"]],
        ["1.2.1", ["4.4.*"], ["6.0.*"]],
        # ["1.2.0", ["4.3.2"], ["6.0pre10"]], -- unavailable because OMNeT++ prereleases are not kept
        ["1.1.0", ["4.2.*"], ["5.6.*", "5.7.*"]],
        ["git", ["4.5.*"], ["6.2.*", "6.1.*", "6.0.*"]],
    ]]
