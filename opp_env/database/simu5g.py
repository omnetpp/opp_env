
def get_simu5g_project_description(simu5g_version, inet_versions, omnetpp_versions):
    return {
        "name": "simu5g", "version": simu5g_version,
        "description": "5G NR and LTE/LTE-A user-plane simulation model",
        "metadata": {
            "catalog_url": "https://omnetpp.org/download-items/Simu5G.html",
        },
        "required_projects": {"inet": inet_versions, "omnetpp": omnetpp_versions},
        "download_url": f"https://github.com/Unipisa/Simu5G/archive/refs/tags/v{simu5g_version}.tar.gz",
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
        "clean_commands": [ "make clean" ]
    }

def get_project_descriptions():
    return [ get_simu5g_project_description(simu5g_version, inet_versions, omnetpp_versions) for simu5g_version, inet_versions, omnetpp_versions in [
        ["1.2.2", ["4.5.*"], ["6.0.*"]],
        ["1.2.1", ["4.4.*"], ["6.0.*"]],
        # ["1.2.0", ["4.3.2"], ["6.0pre10"]], -- unavailable because OMNeT++ prereleases are not kept
        ["1.1.0", ["4.2.*"], ["5.6.*", "5.7.*"]],
    ]]
