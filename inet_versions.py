#!/usr/bin/env python3

def get_all_inet_4_x_versions():
    return [
        {
            "name":"INET","version":"4.4",
            "folder_name":"inet",
            "required_projects":{"omnetpp": ["6.0", "5.7"]},
            "external_nix_packages":["z3"],
            "download_command":"git clone -b v4.4.0 git@github.com:inet-framework/inet.git INET-4.4",
            "setenv_command":"source setenv",
            "build_command":"make makefiles && make -j16 MODE:release",
            "clean_command":"make clean"
        },
        {
            "name":"INET","version":"4.3.5",
            "folder_name":"inet",
            "required_projects":{"omnetpp": ["6.0", "5.7"]},
            "external_nix_packages":["z3"],
            "download_command":"git clone -b v4.3.5 git@github.com:inet-framework/inet.git INET-4.3.5",
            "setenv_command":"source setenv",
            "configure_command":"make makefiles",
            "build_command":"make -j16 MODE:release",
            "clean_command":"make clean"
        },
        {
            "name":"INET","version":"4.2.2",
            "folder_name":"inet",
            "required_projects":{"omnetpp": ["5.6.2"]},
            "external_nix_packages":["z3"],
            "download_command":"git clone -b v4.2.2 git@github.com:inet-framework/inet.git INET-4.2.2",
            "setenv_command":"source setenv -f",
            "configure_command":"make makefiles",
            "build_command":"make -j16 MODE:release",
            "clean_command":"make clean"
        },
        {
            "name":"INET","version":"4.2",
            "folder_name":"inet",
            "required_projects":{"omnetpp": ["5.7"]},
            "external_nix_packages":["z3"],
            "download_command":"git clone -b v4.2.0 git@github.com:inet-framework/inet.git INET-4.2",
            "setenv_command":"source setenv -f",
            "configure_command":"make makefiles",
            "build_command":"make -j16 MODE:release",
            "clean_command":"make clean"
        },
    ]

def get_all_inet_3_x_versions():
    return [
    ]

def get_all_inet_versions():
    return [
        {
            "name":"INET","version":"git",
            "folder_name":"inet",
            "required_projects":{"omnetpp": ["git"]},
            "external_nix_packages":["z3"],
            "download_command":"git git@github.com:inet-framework/inet.git inet",
            "setenv_command":"source setenv",
            "build_command":"make makefiles && make -j16 MODE:release",
            "clean_command":"make clean"
        },
        *get_all_inet_4_x_versions(),
        *get_all_inet_3_x_versions(),
    ]
