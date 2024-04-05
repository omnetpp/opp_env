import re

def make_veins_project_description(version, inet_versions, sumo_version, omnetpp_versions):
    is_git_branch = (version == "master")
    git_branch_or_tag_name = version if is_git_branch else f"veins-{version}"
    heads_or_tags = 'heads' if is_git_branch else 'tags'

    return {
        "name": "veins", "version": version,
        "description": "The open source vehicular network simulation framework.",
        "metadata": {
            "catalog_url": "https://omnetpp.org/download-items/Veins.html",
        },
        "required_projects": {"omnetpp": omnetpp_versions, "inet": inet_versions},
        "nix_packages": ["sumo" if version >= "5.0" else None, "python2" if version < "5.2" else None],
        "patch_commands": [
            "sed -i 's|^#!/usr/bin/env python$|#!/usr/bin/env python2|' configure" if version<="4.6" else "",
        ],
        "setenv_commands": [
            'export OMNETPP_IMAGE_PATH="$OMNETPP_IMAGE_PATH:$VEINS_ROOT/images"',
            "export SUMO_ROOT=${pkgs.sumo}",
            "source setenv" if version >= "5.1" else "",
            "if [[ ! ($INET_VERSION < '4.0.0') ]]; then cd subprojects/veins_inet && source setenv; else cd subprojects/veins_inet3 && source setenv; fi" if version >= "5.1" else "",
        ],
        "smoke_test_commands": [
            # can't test 4.7.1 -> no sumo before 5.0
            """if [ "$BUILD_MODE" = "debug" ]; then DEBUG_POSTFIX="-d"; fi""",
            """if [ "$BUILD_MODE" = "release" ]; then DEBUG_POSTFIX=""; fi""",
            "./sumo-launchd.py &> /dev/null & bg_pid=$! &> /dev/null",
            "cd examples/veins && ./run $DEBUG_POSTFIX -c Default -u Cmdenv > /dev/null",
            "export VEINS_INET_INI_CONFIG='-c plain'" if version >= "5.1" else "",
            "if [[ ! ($INET_VERSION < '4.0.0') ]]; then cd ../../subprojects/veins_inet/examples/veins_inet && ./run $DEBUG_POSTFIX $VEINS_INET_INI_CONFIG -u Cmdenv > /dev/null; else cd ../../subprojects/veins_inet3/examples/veins_inet && ./run $DEBUG_POSTFIX -u Cmdenv > /dev/null; fi",
            "kill $bg_pid &> /dev/null",
        ] if version >= "5.0" else ["echo 'Skipping test because required sumo version is not available as a nix package.'"],
        "build_commands": [ 
            "./configure && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE" if version >= "4.5" else "./configure --with-inet=$INET_ROOT && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
            # this is a hack so that the veins_inet subproject's configure can query the inet version
            "cd $INET_ROOT && mkdir -p _scripts && echo 'echo $INET_VERSION' > _scripts/get_version && chmod +x _scripts/get_version && cd -" if version == "5.0" else "cd $INET_ROOT && mkdir -p _scripts && echo '#!/usr/bin/env sh\n\necho $INET_VERSION' > _scripts/get_version && chmod +x _scripts/get_version && cd -",
            "if [[ ! ($INET_VERSION < '4.0.0') ]]; then cd subprojects/veins_inet && ./configure --with-inet=$INET_ROOT --with-veins=$VEINS_ROOT && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE; else cd subprojects/veins_inet3 && ./configure --with-inet=$INET_ROOT --with-veins=$VEINS_ROOT && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE; fi" if version >= "5.0" else "",
            "cd subprojects/veins_inet && ./configure --with-inet=$INET_ROOT --with-veins=$VEINS_ROOT && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE" if version >= "4.5" and version < "5.0" else "",
            ],
        "warnings": [
            f"This version requires an older version of SUMO, which is not available in opp_env. Please install the appropriate SUMO version ({''.join(sumo_version)}) manually." if version < "5.0" else "",
        ],
        "clean_commands": [ "[ ! -f src/Makefile ] || make clean" ],
        "options": {
            "from-source-archive": {
                "option_description": "Install from source archive on GitHub",
                "option_category": "download",
                "option_is_default": version != "master",
                # currently unused: "download_commands": [ "curl -LO https://veins.car2x.org/download/veins-5.2.zip && unzip veins-5.2.zip && rm veins-5.2.zip && mv veins-veins-5.2 veins-5.2" ],
                "download_url": f"https://github.com/sommer/veins/archive/refs/{heads_or_tags}/{git_branch_or_tag_name}.tar.gz",
            },
            "from-git": {
                "option_description": "Install from git repo on GitHub",
                "option_category": "download",
                "option_is_default": version == "master",
                "git_url": "https://github.com/sommer/veins.git",
                "git_branch": git_branch_or_tag_name,
            },
        }
    }

def get_project_descriptions():
    return [ make_veins_project_description(veins_version, inet_versions, sumo_version, omnetpp_versions) for veins_version, inet_versions, sumo_version, omnetpp_versions in [
        # Notes:
        # - alpha and 2.x versions are omitted from this list: 5a2, 5a1, 5a2, 4a1, 3a2, 3a2, 3a1, 2.2, 2.1, 2.0.
        # - many Veins versions may actually compile/work with more omnetpp versions than listed -- this is to be checked
        # - versions before 5.0 need older versions of SUMO, which are currently not available as nix packages
        #
        ["5.2", ["4.2.8", "4.2.5", "4.2.4", "4.2.3", "4.2.2", "4.2.1", "4.2.0", "3.8.1", "3.7.1", "3.7.0", "3.6.8", "3.6.7", "3.6.6", "3.6.5"], ["1.9.2"], ["6.0.*", "5.7.*", "5.6.*", "5.5.*", "5.4.*", "5.3.*"]],
        ["5.1", ["4.2.1", "4.2.0", "3.6.5", "3.6.6", "3.6.7", "3.6.8"], ["1.9.2"], ["5.5.*", "5.4.*", "5.3.*"]],
        ["5.0", ["4.1.1", "4.1.0", "3.6.5"], ["1.9.2"], ["5.5.*", "5.4.*", "5.3.*"]],      # this is the first one that works with sumo 1.9.2
        ["4.7.1", ["3.6.0", "3.5.0", "3.4.0"], ["0.30.0"], ["5.3.*", "5.2.*", "5.1.*"]],    # needs SUMO 0.30.0
        ["4.7", ["3.6.0", "3.5.0", "3.4.0"], ["0.30.0"], ["5.3.*", "5.2.*", "5.1.*"]],          # needs SUMO 0.30.0
        ["4.6", ["3.6.0", "3.5.0", "3.4.0"], ["0.30.0"], ["5.3.*", "5.2.*", "5.1.*", "5.0.*"]],         # needs SUMO 0.30.0
        # ["4.5", ["3.4.0"], ["0.29.0"], ["5.0.*"]],  # note: does not compile with omnetpp-4.6 -- missing type cRandom   # inet 3.4 needs omnetpp 5.1, but veins doesnt build with that     # needs sumo 0.29.0
        ["4.4", ["2.3.0"], ["0.25.0"], ["5.0.*","4.6.*", "4.5.*", "4.4.*"]],    # needs SUMO 0.25.0
        ["4.3", ["2.3.0"], ["0.25.0"], ["4.6.*", "4.5.*", "4.4.*", "4.3.*", "4.2.*"]],  # needs SUMO 0.25.0
        ["3.0", ["2.3.0"], ["0.21.0"], ["4.4.*", "4.3.*", "4.2.*"]],        # needs SUMO 0.21.0
        ["master", ["4.2.8", "4.2.5", "4.2.4", "4.2.3", "4.2.2", "4.2.1", "4.2.0", "3.8.2", "3.8.1", "3.7.1", "3.7.0", "3.6.8", "3.6.7", "3.6.6", "3.6.5"], ["1.9.2"], ["6.0.*", "5.7.*", "5.6.*", "5.5.*", "5.4.*", "5.3.*"]], # actually inet 4.2. 0 1 2 3 4 5 8, 3.6. 5 6 7 8, 3.7. 0 1, 3.8. 1 2
    ]]
