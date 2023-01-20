description = "INET Framework is an open-source OMNeT++ model suite for wired, wireless and mobile networks."

def get_all_inet_4_x_versions():
    return [
        *[
            {
                "name": "inet", "version": version, "description": description,
                "folder_name": "inet",
                "required_projects": {"omnetpp":  [ "6.0.1", "6.0" ]},
                "external_nix_packages": [ "python3", "z3"],
                "download_command": f"git clone -b v{version} git@github.com:inet-framework/inet.git inet-{version}",
                "setenv_command": "source setenv",
                "build_command": "make makefiles && make -j$NIX_BUILD_CORES MODE=release",
                "clean_command": "make clean"
            } for version in ["4.4", "4.4.1"]
        ],
        {
            "name": "inet", "version": "4.3.9", "description": description,
            "folder_name": "inet",
            "required_projects": {"omnetpp":  [ "6.0.1" ]},
            "external_nix_packages": [ "python3", "z3"],
            "download_command": "git clone -b v4.3.9 git@github.com:inet-framework/inet.git inet-4.3.9",
            "setenv_command": "source setenv",
            "configure_command": "make makefiles",
            "build_command": "make -j$NIX_BUILD_CORES MODE=release",
            "clean_command": "make clean"
        },
        {
            "name": "inet", "version": "4.2.10", "description": description,
            "folder_name": "inet",
            "required_projects": {"omnetpp":  [ "6.0.1", "5.7" ]},
            "external_nix_packages": [ "python3", "z3"],
            "download_command": "git clone -b v4.2.10 git@github.com:inet-framework/inet.git inet-4.2.10",
            "setenv_command": "source setenv -f",
            "configure_command": "make makefiles",
            "build_command": "make -j$NIX_BUILD_CORES MODE=release",
            "clean_command": "make clean"
        },
        *[
            {
                "name": "inet", "version": version, "description": description,
                "folder_name": "inet",
                "required_projects": {"omnetpp":  [ "5.6.2", "5.5.1", "5.4.1" ]},
                "external_nix_packages": [ "python3", "z3"],
                "download_command": f"git clone -b v{version} git@github.com:inet-framework/inet.git inet-{version}",
                "setenv_command": "source setenv -f",
                "configure_command": "make makefiles",
                "build_command": "make -j$NIX_BUILD_CORES MODE=release",
                "clean_command": "make clean"
            } for version in ["4.2", "4.2.1", "4.2.2", "4.2.3", "4.2.4", "4.2.5"]
        ],
    ]

def get_all_inet_3_x_versions():
    return [
        {
            "name": "inet", "version": "3.8.3", "description": description,
            "folder_name": "inet",
            "required_projects": {"omnetpp":  [ "6.0.1", "5.7" ]},
            "external_nix_packages": [ "python3" ],
            "download_command": "git clone -b v3.8.3 git@github.com:inet-framework/inet.git inet-3.8.3",
            "setenv_command": "source setenv -f",
            "configure_command": "make makefiles",
            "build_command": "make -j$NIX_BUILD_CORES MODE=release",
            "clean_command": "make clean"
        },
        {
            "name": "inet", "version": "3.7.1", "description": description,
            "folder_name": "inet",
            "required_projects": {"omnetpp":  [ "5.7", "5.6.2", "5.5.1", "5.4.1", "5.3" ]},
            "external_nix_packages": [ "python3" ],
            "download_command": "git clone -b v3.7.1 git@github.com:inet-framework/inet.git inet-3.7.1",
            "setenv_command": "source setenv -f",
            "configure_command": "make makefiles",
            "build_command": "make -j$NIX_BUILD_CORES MODE=release",
            "clean_command": "make clean"
        },
        {
            "name": "inet", "version": "3.3.0", "description": description,
            "folder_name": "inet",
            "required_projects": {"omnetpp":  [ "4.6" ]},
            "external_nix_packages": [ "python3" ],
            "download_command": "git clone -b v3.3.0 git@github.com:inet-framework/inet.git inet-3.3.0",
            "setenv_command": "true",
            "configure_command": "make makefiles",
            "build_command": "make -j$NIX_BUILD_CORES MODE=release",
            "clean_command": "make clean"
        },
        {
            "name": "inet", "version": "2.6.0", "description": description,
            "folder_name": "inet",
            "required_projects": {"omnetpp":  [ "4.4.1" ]},
            "external_nix_packages": [ ],
            "download_command": "git clone -b v2.6.0 git@github.com:inet-framework/inet.git inet-2.6.0",
            "setenv_command": "",
            "configure_command": "make makefiles",
            "build_command": "make -j$NIX_BUILD_CORES MODE=release",
            "clean_command": "make clean"
        },
    ]

def get_all_inet_versions():
    return [
        {
            "name": "inet", "version": "git", "description": description,
            "folder_name": "inet",
            "required_projects": {"omnetpp":  ["git"]},
            "external_nix_packages": [ "python3", "z3"],
            "download_command": "git git@github.com:inet-framework/inet.git inet",
            "setenv_command": "source setenv",
            "build_command": "make makefiles && make -j$NIX_BUILD_CORES MODE=release",
            "clean_command": "make clean"
        },
        *get_all_inet_4_x_versions(),
        *get_all_inet_3_x_versions(),
    ]
