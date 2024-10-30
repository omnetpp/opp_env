# Contributing to opp_env

If you want to contribute to the development of `opp_env` or need to modify the
source code for any reason, you can install the package in editable mode by
cloning the git repo, changing to its root directory and using
the following command:

    pip install --editable .

This will install the Python module and the `opp_env` command, but with the
added ability to make local modifications that will take effect immediately.

In case of other errors, try upgrading pip to the latest version first by
running `python3 -m pip install --upgrade pip`.

## Building the Python Package

To build the Python package, you first need to install the `build` package by
running the following command:

    pip install --upgrade build

Once you have `build` installed, you can build the package by running:

    python3 -m build

If you have any issues or questions, feel free to open an issue on the GitHub
repository. We are always happy to help!

