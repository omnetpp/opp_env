def get_project_descriptions():
    return [
        {
            "name": "opp_env_testproject", "version": "0.1",
            "description": "Dummy project for testing opp_env",
            "patch_commands": ["echo hello from patch command"],
            "setenv_commands": ["echo hello from setenv command", "export SETENV_VAR=hello-from-setenv", "echo BUILD_MODES=$BUILD_MODES"],
            "build_commands": ["make MODE=$BUILD_MODE"],
            "clean_commands": ["make clean MODE=$BUILD_MODE"],
            "test_commands":  ["make test"],
            "smoke_test_commands": ["make smoketest"],
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
