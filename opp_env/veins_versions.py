import re

def dotx(version):
    # 4.2, 4.2.1, 4.2p1 -> 4.2.x
    return re.sub("(\\d\\.\\d)[\\.p]\\d", "\\1", version) + ".x"

def get_all_veins_released_versions():
    local_veins_git_repo = "../veins"

    return [
            {
                "name": "veins", "version": veins_version,
                "description": "The open source vehicular network simulation framework.",
                "required_projects": {"omnetpp": omnetpp_versions},  #list(set([dotx(v) for v in omnetpp_versions]))},
                "external_nix_packages": ["sumo"] if veins_version >= "5.1" else ["sumo", "python2"],
                # currently unused: "download_command": "wget  -q -nv --show-progress https://veins.car2x.org/download/veins-5.2.zip && unzip veins-5.2.zip && rm veins-5.2.zip && mv veins-veins-5.2 veins-5.2",
                "git_url": "git@github.com:sommer/veins.git",
                "git_branch": f"veins-{veins_version}",
                "patch_command": "sed -i 's|^#!/usr/bin/env python$|#!/usr/bin/env python2|' configure" if veins_version<="4.6" else "",
                "setenv_command": "source setenv" if veins_version >= "5.1" else "",
                "build_command": "./configure && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
                "clean_command": "[ ! -f src/Makefile ] || make clean",
                # "options": {
                #     "local": {
                #         "download_command": f"git clone -l {local_veins_git_repo} veins-{veins_version} --branch veins-{veins_version}",
                #         "download_url": "",
                #         "git_url": ""
                #     }
                # }
            } for veins_version, omnetpp_versions in [
                # Notes:
                # - alpha and 2.x versions are omitted from this list: 5a2, 5a1, 5a2, 4a1, 3a2, 3a2, 3a1, 2.2, 2.1, 2.0.
                # - many Veins versions may actually compile/work with more omnetpp versions than listed -- this is to be checked
                #
                ["5.2", ["6.0", "5.7", "5.6.2", "5.6.1", "5.6", "5.5.1", "5.4.1", "5.3"]],
                ["5.1", ["5.5.1", "5.4.1", "5.3"]],
                ["5.0", ["5.5.1", "5.4.1", "5.3"]],
                ["4.7.1", ["5.3", "5.2.1", "5.2", "5.1.1"]],
                ["4.7", ["5.3", "5.2.1", "5.2", "5.1.1"]],
                ["4.6", ["5.3", "5.2.1", "5.2", "5.1.1", "5.0"]],
                ["4.5", ["5.0"]],  # note: with  omnetpp-4.6, compilation error is c++ language related -- maybe just requires newer c++ standard, e.g. c++11?
                ["4.4", ["5.0","4.6", "4.5", "4.4.1"]],
                ["4.3", ["4.6", "4.5", "4.4.1", "4.3", "4.2.2"]],
                ["3.0", ["4.4.1", "4.3", "4.2.2"]],
            ]
    ]

def get_all_veins_versions():
    return [
        # {
        #     "name": "veins", "version": "git", "description": description,
        #     "folder_name": "veins",
        #     "required_projects": {"omnetpp": ["master"]},
        #     "external_nix_packages": ["python3", "z3"],
        #     "git_url": "git@github.com:veins-framework/veins.git",
        #     "setenv_command": "source setenv",
        #     "build_command": "make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
        #     "clean_command": "[ ! -f src/Makefile ] || make clean"
        # },
        *get_all_veins_released_versions()
    ]
