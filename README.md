## opp_env: Automated Installation of OMNeT++ Simulation Frameworks

`opp_env` is a powerful tool that allows for the easy and automated installation
of OMNeT++ simulation frameworks and models, including dependencies like INET
Framework and OMNeT++ itself. It can install any version of OMNeT++ and INET, as
well as currently selected versions of Veins, SimuLTE, and Simu5G. We are working
towards expanding its database with more models, and we are open to suggestions
and contributions.

`opp_env` relies on Nix, a powerful package manager that provides isolation
between different versions of dependencies and allows for reproducible builds.
By leveraging the power of Nix, `opp_env` ensures that each installation is
consistent and can be easily replicated on different machines.

`opp_env` currently supports Linux systems.

### Usage

Using `opp_env` is simple. To install a specific version of a simulation framework
and its dependencies, first create a workspace:

```
mkdir workspace
cd workspace
opp_env init
```

Then run the following command:

```
opp_env shell <framework-version>
```

For example, to install Simu5G version 1.2.1, run the following command:

```
opp_env shell simu5g-1.2.1
```

This will download Simu5G, the matching INET and OMNeT++ packages, compile
them, and open a shell prompt set up to work with them.

To see the list of available packages, type the following:

```
opp_env list
```

### Features

`opp_env` provides a number of powerful features that make it a valuable tool for
any researcher or developer working with OMNeT++ simulation frameworks:

- Automated installation of OMNeT++ simulation frameworks and models, including
  dependencies like INET Framework and OMNeT++ itself.
- Support for any version of OMNeT++ and INET, as well as currently selected
  versions of Veins, SimuLTE, and Simu5G.
- Reproducible builds thanks to the powerful isolation provided by Nix.
- Easy to use shell command that sets up an environment for working with the
  selected simulation framework.
- Customizable configuration options that allow for advanced control over the
  installation process.

### Installation

To get started with `opp_env`, you first need to have Nix installed on your
machine. You can download and install Nix from
[here](https://nixos.org/download). `opp_env` also needs several smaller utility
programs like `wget`, `tar`, `gzip`, and also `git` for the installation of certain packages or package versions.

Once you have the prerequisites, you can install `opp_env` using `pip`.

#### Installing opp_env with pip

In the future, end users will be able to install `opp_env` using the following command:

```
pip install --user opp_env
```

For now, clone the git repo, change into its root directory, and run the
following command:

```
pip install --user .
```

Or you can install directly from GitHub:

```
pip3 install --user git+https://github.com/omnetpp/opp_env.git
```

When you install `opp_env` using pip, it installs the `opp_env` Python module,
as well as a small script into your system's path (e.g. `~/.local/bin`) that
allows you to invoke it from the shell. The `opp_env` command is equivalent to
running `python -m opp_env`, which also runs the `opp_env` Python module.

#### Installing opp_env for Development

If you want to contribute to the development of opp_env or need to modify the
source code for any reason, you can install the package in editable mode using
the following command:

```
pip install --user --editable .
```

This will install the Python module and the `opp_env` command, but with the
added ability to make local modifications that will take effect immediately.

If the above command results in any errors, try upgrading pip to the latest
version first by running `python3 -m pip install --upgrade pip`.

#### Building the Python Package

To build the Python package, you first need to install the `build` package by
running the following command:

```
pip install --upgrade build
```

Once you have `build` installed, you can build the package by running:

```
python3 -m build
```

If you have any issues or questions, feel free to open an issue on the GitHub
repository. We are always happy to help!
