import re
description = "INET Framework is an open-source OMNeT++ model suite for wired, wireless and mobile networks."

def dotx(version):
    # 4.2, 4.2.1, 4.2p1 -> 4.2.x
    return re.sub("(\\d\\.\\d)[\\.p]\\d", "\\1", version) + ".x"

def get_all_inet_released_versions():
    local_inet_git_repo = "/home/andras/projects/inet"
    return [
            {
                "name": "inet", "version": inet_version, "description": description,
                "folder_name": "inet",
                "required_projects": {"omnetpp": list(set([dotx(v) for v in omnetpp_versions]))},
                "external_nix_packages": ["python3", "z3"] if inet_version.startswith("4.") else
                                         ["python3"]  if inet_version.startswith("3.") else [],
                "git_url": "git@github.com:inet-framework/inet.git",
                "git_branch": f"v{inet_version}",
                "setenv_command": "source setenv -f" if inet_version.startswith("4.") else "",
                "patch_command": "touch tutorials/package.ned" if inet_version <= "4.2.1" and inet_version >= "3.6.0" else "",
                "build_command": "make makefiles && make -j$NIX_BUILD_CORES MODE=release",
                "clean_command": "[ ! -f src/Makefile ] || make clean",
                "options": {
                    "local": {
                        "download_command": f"git clone -l {local_inet_git_repo} inet-{inet_version} --branch v{inet_version}",
                        "download_url": "",
                        "git_url": ""
                    }
                }
            } for inet_version, omnetpp_versions in [["4.4.1", ["6.0.1", "6.0"]],
                                                     ["4.4.0", ["6.0.1", "6.0"]],
                                                     ["4.3.9", ["6.0.1", "6.0"]],
                                                     ["4.3.8", ["6.0.1", "6.0"]],
                                                     ["4.3.7", ["6.0.1", "6.0"]],
                                                     ["4.3.6", ["6.0.1", "6.0"]],
                                                     ["4.3.5", ["6.0.1", "6.0"]],
                                                     ["4.3.4", ["6.0.1", "6.0"]],
                                                     ["4.3.3", ["6.0.1", "6.0"]],
                                                     ["4.3.2", ["6.0.1", "6.0"]],
                                                     ["4.3.1", ["6.0.1", "6.0"]],
                                                     ["4.3.0", ["6.0.1", "6.0"]],
                                                     ["4.2.10", ["6.0.1", "6.0"]],
                                                     ["4.2.9", ["6.0.1", "6.0"]],
                                                     ["4.2.8", ["5.7"]],
                                                     ["4.2.7", ["5.7"]],
                                                     ["4.2.6", ["5.6.2"]],
                                                     ["4.2.5", ["5.6.2"]],
                                                     ["4.2.4", ["5.4.1"]],
                                                     ["4.2.3", ["5.4.1"]],
                                                     ["4.2.2", ["5.4.1"]],
                                                     ["4.2.1", ["5.4.1"]],
                                                     ["4.2.0", ["5.4.1"]],
                                                     ["4.1.2", ["5.4.1"]],
                                                     ["4.1.1", ["5.4.1"]],
                                                     ["4.1.0", ["5.4.1"]],
                                                     ["4.0.0", ["5.4.1"]],

                                                     ["3.8.3", ["5.3"]],
                                                     ["3.8.2", ["5.3"]],
                                                     ["3.8.1", ["5.3"]],
                                                     ["3.8.0", ["5.3"]],
                                                     ["3.7.1", ["5.3"]],
                                                     ["3.7.0", ["5.3"]],
                                                     ["3.6.8", ["5.3"]],
                                                     ["3.6.7", ["5.3"]],
                                                     ["3.6.6", ["5.3"]],
                                                     ["3.6.5", ["5.3"]],
                                                     ["3.6.4", ["5.3"]],
                                                     ["3.6.3", ["5.3"]],
                                                     ["3.6.2", ["5.3"]],
                                                     ["3.6.1", ["5.3"]],
                                                     ["3.6.0", ["5.3"]],
                                                     ["3.5.x", ["5.1"]],
                                                     ["3.5.0", ["5.1"]],
                                                     ["3.4.0", ["5.0"]],
                                                     ["3.3.0", ["4.6"]],
                                                     ["3.2.x", ["4.6"]],
                                                     ["3.2.4", ["4.6"]],
                                                     ["3.2.3", ["4.6"]],
                                                     ["3.2.2", ["4.6"]],
                                                     ["3.2.1", ["4.6"]],
                                                     ["3.2.0", ["4.6"]],
                                                     ["3.1.x", ["4.6"]],
                                                     ["3.1.1", ["4.6"]],
                                                     ["3.1.0", ["4.6"]],
                                                     ["3.0.x", ["4.6"]],
                                                     ["3.0.0", ["4.6"]],

                                                     ["2.6.0", ["4.4"]],
                                                     ["2.5.0", ["4.4"]],
                                                     ["2.4.0", ["4.3"]],
                                                     ["2.3.0", ["4.3"]],
                                                     ["2.2.0", ["4.2"]],
                                                     ["2.1.0", ["4.2"]],
                                                     ["2.0.0", ["4.2"]],

                                                     ["2.6.x", ["4.4"]],
                                                     ["2.5.x", ["4.4"]],
                                                     ["2.4.x", ["4.3"]],
                                                     ["2.3.x", ["4.3"]],
                                                     ["2.2.x", ["4.2"]],
                                                     ["2.1.x", ["4.2"]],
                                                     ["2.0.x", ["4.2"]]]

    ]

def get_all_inet_versions():
    return [
        {
            "name": "inet", "version": "git", "description": description,
            "folder_name": "inet",
            "required_projects": {"omnetpp": ["master"]},
            "external_nix_packages": ["python3", "z3"],
            "git_url": "git@github.com:inet-framework/inet.git",
            "setenv_command": "source setenv",
            "build_command": "make makefiles && make -j$NIX_BUILD_CORES MODE=release",
            "clean_command": "[ ! -f src/Makefile ] || make clean"
        },
        *get_all_inet_released_versions()
    ]
