def get_all_omnetpp_6_x_versions():
    return [
        {
            "name": "omnetpp", "version": "6.0.1",
            "external_nix_packages": ["bison", "flex", "perl", "xdg-utils", "openscenegraph", "python3", "python3Packages.numpy", "python3Packages.scipy", "python3Packages.pandas", "python3Packages.matplotlib", "python3Packages.posix_ipc"],
            "download_command": "wget http://github.com/omnetpp/omnetpp/releases/download/omnetpp-6.0.1/omnetpp-6.0.1-linux-x86_64.tgz && tar xzf omnetpp-6.0.1-linux-x86_64.tgz && rm omnetpp-6.0.1-linux-x86_64.tgz",
            "setenv_command": "source setenv",
            "configure_command": "./configure WITH_OSG=no WITH_QTENV=no",
            "build_command": "make -j16 MODE=release",
            "clean_command": "make clean"
        },
        {
            "name": "omnetpp", "version": "6.0",
            "external_nix_packages": ["bison", "flex", "perl", "xdg-utils", "openscenegraph", "python3", "python3Packages.numpy", "python3Packages.scipy", "python3Packages.pandas", "python3Packages.matplotlib", "python3Packages.posix_ipc"],
            "download_command": "wget http://github.com/omnetpp/omnetpp/releases/download/omnetpp-6.0/omnetpp-6.0-linux-x86_64.tgz && tar xzf omnetpp-6.0-linux-x86_64.tgz && rm omnetpp-6.0-linux-x86_64.tgz",
            "setenv_command": "source setenv",
            "configure_command": "./configure WITH_OSG=no WITH_QTENV=no",
            "build_command": "make -j16 MODE=release",
            "clean_command": "make clean"
        },
    ]

def get_all_omnetpp_5_x_versions():
    return [
        {
            "name": "omnetpp", "version": "5.7",
            "external_nix_packages": ["bison", "flex", "perl", "xdg-utils", "openscenegraph", "python3", "python3Packages.numpy", "python3Packages.scipy", "python3Packages.pandas", "python3Packages.matplotlib", "python3Packages.posix_ipc"],
            "download_command": "wget http://github.com/omnetpp/omnetpp/releases/download/omnetpp-5.7/omnetpp-5.7-linux-x86_64.tgz && tar xzf omnetpp-5.7-linux-x86_64.tgz && rm omnetpp-5.7-linux-x86_64.tgz &&",
            "setenv_command": "source setenv",
            "configure_command": "./configure WITH_OSG=no WITH_QTENV=no",
            "build_command": "make -j16 MODE=release",
            "clean_command": "make clean"
        },
        {
            "name": "omnetpp", "version": "5.6.2",
            "external_nix_packages": ["bison", "flex", "perl", "xdg-utils", "openscenegraph", "python3", "python3Packages.numpy", "python3Packages.scipy", "python3Packages.pandas", "python3Packages.matplotlib", "python3Packages.posix_ipc"],
            "download_command": "wget http://github.com/omnetpp/omnetpp/releases/download/omnetpp-5.6.2/omnetpp-5.6.2-src-linux.tgz && tar xzf omnetpp-5.6.2-src-linux.tgz && rm omnetpp-5.6.2-src-linux.tgz",
            "setenv_command": "source setenv",
            "configure_command": "./configure WITH_OSG=no WITH_QTENV=no",
            "build_command": "make -j16 MODE=release",
            "clean_command": "make clean"
        },
        {
            "name": "omnetpp", "version": "5.6.1",
            "external_nix_packages": ["bison", "flex", "perl", "xdg-utils", "openscenegraph", "python3", "python3Packages.numpy", "python3Packages.scipy", "python3Packages.pandas", "python3Packages.matplotlib", "python3Packages.posix_ipc"],
            "download_command": "wget http://github.com/omnetpp/omnetpp/releases/download/omnetpp-5.6.1/omnetpp-5.6.1-src-linux.tgz && tar xzf omnetpp-5.6.1-src-linux.tgz && rm omnetpp-5.6.1-src-linux.tgz",
            "setenv_command": "source setenv",
            "configure_command": "./configure WITH_OSG=no WITH_QTENV=no",
            "build_command": "make -j16 MODE=release",
            "clean_command": "make clean"
        },
        {
            "name": "omnetpp", "version": "5.6",
            "external_nix_packages": ["bison", "flex", "perl", "xdg-utils", "openscenegraph", "python3", "python3Packages.numpy", "python3Packages.scipy", "python3Packages.pandas", "python3Packages.matplotlib", "python3Packages.posix_ipc"],
            "download_command": "wget http://github.com/omnetpp/omnetpp/releases/download/omnetpp-5.6/omnetpp-5.6-src-linux.tgz && tar xzf omnetpp-5.6-src-linux.tgz && rm omnetpp-5.6-src-linux.tgz",
            "setenv_command": "source setenv",
            "configure_command": "./configure WITH_OSG=no WITH_QTENV=no",
            "build_command": "make -j16 MODE=release",
            "clean_command": "make clean"
        },
    ]

def get_all_omnetpp_4_x_versions():
    return [
        {
            "name": "omnetpp", "version": "4.6",
            "external_nix_packages": ["bison", "flex", "perl", "xdg-utils", "openscenegraph", "python3", "python3Packages.numpy", "python3Packages.scipy", "python3Packages.pandas", "python3Packages.matplotlib", "python3Packages.posix_ipc"],
            "download_command": "wget http://github.com/omnetpp/omnetpp/releases/download/omnetpp-4.6/omnetpp-4.6-src.tgz && tar xzf omnetpp-4.6-src.tgz && rm omnetpp-4.6-src.tgz",
            "setenv_command": "source setenv",
            "configure_command": "./configure WITH_TKENV=no",
            "build_command": "make -j16 MODE=release",
            "clean_command": "make clean"
        },
    ]

def get_all_omnetpp_3_x_versions():
    return [
        {
            "name": "omnetpp", "version": "3.3p1",
            "stdenv": "gcc7Stdenv",
            "external_nix_packages": ["bison", "flex", "perl", "tk", "tcl", "xdg-utils", "openscenegraph", "python3", "python3Packages.numpy", "python3Packages.scipy", "python3Packages.pandas", "python3Packages.matplotlib", "python3Packages.posix_ipc"],
            "download_command": "wget http://github.com/omnetpp/omnetpp/releases/download/omnetpp-3.3-ubuntu18.04/omnetpp-3.3-src-gcc73.tgz && tar xzf omnetpp-3.3-src-gcc73.tgz && rm omnetpp-3.3-src-gcc73.tgz && mv omnetpp-omnetpp-3.3-ubuntu18.04 omnetpp-3.3p1",
            "setenv_command": "export PATH=$PATH:/home/levy/workspace/test/omnetpp-3.3p1/bin && export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/levy/workspace/test/omnetpp-3.3p1/lib", # TODO hardcoded folder
            "configure_command": "./configure",
            "build_command": "make MODE=release",
            "clean_command": "make clean"
        },
    ]

def get_all_omnetpp_git_versions():
    return [
        {
            "name": "omnetpp", "version": "git",
            "external_nix_packages": ["bison", "flex", "perl", "xdg-utils", "openscenegraph", "python3", "python3Packages.numpy", "python3Packages.scipy", "python3Packages.pandas", "python3Packages.matplotlib", "python3Packages.posix_ipc"],
            "download_command": "git clone git@github.com:omnetpp/omnetpp.git",
            "setenv_command": "source setenv",
            "configure_command": "./configure WITH_OSG=no WITH_QTENV=no",
            "build_command": "make -j16 MODE=release",
            "clean_command": "make clean"
        },
    ]

def get_all_omnetpp_versions():
    return [
        *get_all_omnetpp_git_versions(),
        *get_all_omnetpp_6_x_versions(),
        *get_all_omnetpp_5_x_versions(),
        *get_all_omnetpp_4_x_versions(),
        *get_all_omnetpp_3_x_versions(),
    ]
