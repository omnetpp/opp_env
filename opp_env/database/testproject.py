def get_project_descriptions():
    return [
        {
            "name": "opp_env_testproject", "version": "0.1",
            "description": "Dummy project for testing opp_env",
            "metadata": {"store_buildable": True},
            "install_commands": ["$TEST_PRE_INSTALL_COMMAND", "echo hello from install command"],
            "patch_commands": ["$TEST_PRE_PATCH_COMMAND", "echo hello from patch command"],
            "setenv_commands": ["$TEST_PRE_SETENV_COMMAND", "echo hello from setenv command", "export SETENV_VAR=hello-from-setenv", "export SETENV_PWD=$(pwd)", "echo BUILD_MODES=$BUILD_MODES"],
            # the two 'out' folders exercise the store package's build output pruning: the first
            # looks like an opp_makemake build tree and must be pruned, the second must be kept
            "build_commands": ["$TEST_PRE_BUILD_COMMAND", "make MODE=$BUILD_MODE",
                               "mkdir -p out/gcc-$BUILD_MODE && touch out/gcc-$BUILD_MODE/objectfile.o",
                               "mkdir -p tools/out && touch tools/out/notabuildtree"],
            "clean_commands": ["$TEST_PRE_CLEAN_COMMAND", "make clean MODE=$BUILD_MODE"],
            "test_commands":  ["$TEST_PRE_TEST_COMMAND", "make test"],
            "smoke_test_commands": ["$TEST_PRE_SMOKETEST_COMMAND", "make smoketest"],
            "options": {
                "from-release": {
                    "option_description": "Install from release tarball on GitHub",
                    "option_category": "download",
                    "option_is_default": True,
                    "download_url": "https://github.com/omnetpp/opp_env_testproject/archive/refs/heads/main.tar.gz",
                },
                "from-git": {
                    "option_description": "Install from git repo on GitHub",
                    "option_category": "download",
                    "option_is_default": False,
                    "git_url": "https://github.com/omnetpp/opp_env_testproject.git",
                    "git_branch": "main",
                },
                "extra-install": {
                    "option_description": "Append extra install commands",
                    "install_commands": ["@append", "echo hello from extra install command"],
                },
            },
        },
        {
            # dummy project depending on opp_env_testproject, for testing the propagation of
            # the '@' (Nix store package) marker to dependencies
            "name": "opp_env_teststoreapp", "version": "0.1",
            "description": "Dummy dependent project for testing opp_env's Nix store package ('@') installs",
            "metadata": {"store_buildable": True},
            "required_projects": {"opp_env_testproject": ["0.1"]},
            "download_url": "https://github.com/omnetpp/opp_env_testproject/archive/refs/heads/main.tar.gz",
            "setenv_commands": ["echo hello from teststoreapp setenv", "echo TESTPROJECT_ROOT=$OPP_ENV_TESTPROJECT_ROOT"],
            "build_commands": ["make MODE=$BUILD_MODE"],
            "clean_commands": ["make clean MODE=$BUILD_MODE"],
        },
        {
            "name": "mm1k", "version": "git",
            "description": "Dummy project for testing opp_repl and its own build system",
            "required_projects": {"omnetpp": ["6.*"]},
            "git_url": "https://github.com/omnetpp/mm1k.git",
        },
    ]
