import re

def make_veins_project_description(version, omnetpp_versions):
    is_git_branch = (version == "master")
    git_branch_or_tag_name = version if is_git_branch else f"veins-{version}"
    heads_or_tags = 'heads' if is_git_branch else 'tags'

    return {
        "name": "veins", "version": version,
        "description": "The open source vehicular network simulation framework.",
        "required_projects": {"omnetpp": omnetpp_versions},
        "external_nix_packages": ["sumo"] if version >= "5.1" else ["sumo", "python2"],
        "patch_commands": [
            "sed -i 's|^#!/usr/bin/env python$|#!/usr/bin/env python2|' configure" if version<="4.6" else ""
        ],
        "setenv_commands": [
            'export OMNETPP_IMAGE_PATH="$OMNETPP_IMAGE_PATH:$VEINS_ROOT/images"',
            "source setenv" if version >= "5.1" else ""
        ],
        "build_commands": [ "./configure && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE" ],
        "clean_commands": [ "[ ! -f src/Makefile ] || make clean" ],
        "options": {
            "from-source-archive": {
                "option_description": "Install from source archive on GitHub",
                "category": "download",
                "is_default": version != "master",
                # currently unused: "download_commands": [ "wget  -q -nv --show-progress https://veins.car2x.org/download/veins-5.2.zip && unzip veins-5.2.zip && rm veins-5.2.zip && mv veins-veins-5.2 veins-5.2" ],
                "download_url": f"https://github.com/sommer/veins/archive/refs/{heads_or_tags}/{git_branch_or_tag_name}.tar.gz",
            },
            "from-git": {
                "option_description": "Install from git repo on GitHub",
                "category": "download",
                "is_default": version == "master",
                "git_url": "git@github.com:sommer/veins.git",
                "git_branch": git_branch_or_tag_name,
            },
        }
    }

def get_project_descriptions():
    return [ make_veins_project_description(veins_version, omnetpp_versions) for veins_version, omnetpp_versions in [
        # Notes:
        # - alpha and 2.x versions are omitted from this list: 5a2, 5a1, 5a2, 4a1, 3a2, 3a2, 3a1, 2.2, 2.1, 2.0.
        # - many Veins versions may actually compile/work with more omnetpp versions than listed -- this is to be checked
        #
        ["5.2", ["6.0.0", "5.7.0", "5.6.2", "5.6.1", "5.6.0", "5.5.1", "5.4.1", "5.3.0"]],
        ["5.1", ["5.5.1", "5.4.1", "5.3.0"]],
        ["5.0", ["5.5.1", "5.4.1", "5.3.0"]],
        ["4.7.1", ["5.3.0", "5.2.1", "5.2.0", "5.1.1"]],
        ["4.7", ["5.3.0", "5.2.1", "5.2.0", "5.1.1"]],
        ["4.6", ["5.3.0", "5.2.1", "5.2.0", "5.1.1", "5.0.0"]],
        ["4.5", ["5.0.0"]],  # note: does not compile with omnetpp-4.6 -- missing type cRandom
        ["4.4", ["5.0.0","4.6.0", "4.5.0", "4.4.1"]],
        ["4.3", ["4.6.0", "4.5.0", "4.4.1", "4.3.0", "4.2.2"]],
        ["3.0", ["4.4.1", "4.3.0", "4.2.2"]],
        ["master", ["6.0.0", "5.7.0", "5.6.2", "5.6.1", "5.6.0", "5.5.1", "5.4.1", "5.3.0"]],
    ]]
