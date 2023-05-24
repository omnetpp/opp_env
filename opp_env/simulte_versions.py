
def get_simulte_project_description(simulte_version, inet_versions, omnetpp_versions):
    return {
        "name": "simulte", "version": simulte_version,
        "description": "LTE and LTE Advanced (3GPP Release 8 and beyond) user plane simulation model",
        "required_projects": {"inet": inet_versions, "omnetpp": omnetpp_versions},
        "download_url":
            f"https://github.com/inet-framework/simulte/releases/download/v{simulte_version}/simulte-{simulte_version}-src.tgz" if simulte_version == "1.2.0" else
            f"https://github.com/inet-framework/simulte/archive/refs/tags/v{simulte_version}.tar.gz",
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
        "clean_commands": [ "make clean" ]
    }

def get_project_descriptions():
    return [ get_simulte_project_description(simulte_version, inet_versions, omnetpp_versions) for simulte_version, inet_versions, omnetpp_versions in [
        ["1.2.0", ["4.2.10", "4.2.5"], ["5.7.*"]], # Contains the integration code required to work with Veins.
        ["1.1.0", ["3.6.6"], ["5.5.*"]], # Contains the integration code required to work with Veins. Tested on Ubuntu 18.04. It is NOT compatible with INET 4.x.
        ["0.9.1", ["3.4.0"], ["5.1.*"]], # It DOES NOT contain support for the Veins simulator. Note: Release notes lists omnetpp-5.0 as dependency, but inet-3.4.0 requires omnetpp-5.1.
    ]]
