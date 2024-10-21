def get_project_descriptions():
    return [
        {
            "name": "opp_env_testproject", "version": "0.1",
            "description": "Dummy project for testing opp_env",
            "patch_commands": ["$TEST_PRE_PATCH_COMMAND", "echo hello from patch command"],
            "setenv_commands": ["$TEST_PRE_SETENV_COMMAND", "echo hello from setenv command", "export SETENV_VAR=hello-from-setenv", "echo BUILD_MODES=$BUILD_MODES"],
            "build_commands": ["$TEST_PRE_BUILD_COMMAND", "make MODE=$BUILD_MODE"],
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
            },
        },
    ]
