description = "INET Framework is an open-source OMNeT++ model suite for wired, wireless and mobile networks."

def get_all_inet_4_x_versions():
    return [
        *[
            {
                "name": "inet", "version": inet_version, "description": description,
                "folder_name": "inet",
                "required_projects": {"omnetpp": omnetpp_versions},
                "external_nix_packages": ["python3", "z3"],
                "git_url": "git@github.com:inet-framework/inet.git",
                "git_branch": f"v{inet_version}",
                "setenv_command": "source setenv -f",
                "build_command": "make makefiles && make -j$NIX_BUILD_CORES MODE=release",
                "clean_command": "make clean"
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
                                                     ["4.0.0", ["5.4.1"]]]
        ],
    ]

def get_all_inet_3_x_versions():
    return [
        *[
            {
                "name": "inet", "version": inet_version, "description": description,
                "folder_name": "inet",
                "required_projects": {"omnetpp": omnetpp_versions},
                "external_nix_packages": ["python3"],
                "git_url": "git@github.com:inet-framework/inet.git",
                "git_branch": f"v{inet_version}",
                "setenv_command": "source setenv -f",
                "build_command": "make makefiles && make -j$NIX_BUILD_CORES MODE=release",
                "clean_command": "make clean"
            } for inet_version, omnetpp_versions in [["3.7.1", ["5.3"]],
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
                                                     ["3.5.0", ["5.1"]],
                                                     ["3.4.0", ["5.0"]],
                                                     ["3.3.0", ["4.6"]],
                                                     ["3.2.4", ["4.6"]],
                                                     ["3.2.3", ["4.6"]],
                                                     ["3.2.2", ["4.6"]],
                                                     ["3.2.1", ["4.6"]],
                                                     ["3.2.0", ["4.6"]],
                                                     ["3.1.1", ["4.6"]],
                                                     ["3.1.0", ["4.6"]],
                                                     ["3.0.0", ["4.6"]]]
        ]
    ]

def get_all_inet_2_x_versions():
    return [
        *[
            {
                "name": "inet", "version": inet_version, "description": description,
                "folder_name": "inet",
                "required_projects": {"omnetpp": omnetpp_versions},
                "git_url": "git@github.com:inet-framework/inet.git",
                "git_branch": f"v{inet_version}",
                "setenv_command": "",
                "build_command": "make makefiles && make -j$NIX_BUILD_CORES MODE=release",
                "clean_command": "make clean"
            } for inet_version, omnetpp_versions in [["2.6.0", ["4.4"]],
                                                     ["2.5.0", ["4.4"]],
                                                     ["2.4.0", ["4.3"]],
                                                     ["2.3.0", ["4.3"]],
                                                     ["2.2.0", ["4.2"]],
                                                     ["2.1.0", ["4.2"]],
                                                     ["2.0.0", ["4.2"]]]
        ]
    ]

def get_all_inet_versions():
    return [
        {
            "name": "inet", "version": "git", "description": description,
            "folder_name": "inet",
            "required_projects": {"omnetpp": ["git"]},
            "external_nix_packages": ["python3", "z3"],
            "git_url": "git@github.com:inet-framework/inet.git",
            "setenv_command": "source setenv",
            "build_command": "make makefiles && make -j$NIX_BUILD_CORES MODE=release",
            "clean_command": "make clean"
        },
        *get_all_inet_4_x_versions(),
        *get_all_inet_3_x_versions(),
        *get_all_inet_2_x_versions(),
    ]
