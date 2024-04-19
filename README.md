# opp_env: Automated Installation of OMNeT++ Simulation Frameworks

`opp_env` is a powerful tool that allows for the easy and automated installation
of OMNeT++ simulation frameworks and models, including dependencies like INET
Framework and OMNeT++ itself. It can install any version of OMNeT++ and INET, as
well as currently selected versions of Veins, SimuLTE, Simu5G and other models.
We are working towards expanding its database with more models, and we are open
to suggestions and contributions.

`opp_env` supports Linux and macOS systems. On Windows 10 & 11, `opp_env` can be 
run on the Windows Subsystem for Linux (WSL2).

> [!NOTE]
> `opp_env` relies on [Nix](https://nixos.org/), a powerful package manager that
> provides isolation between different versions of dependencies and allows for
> reproducible builds. By leveraging the power of Nix, `opp_env` ensures that each
> installation is consistent and can be easily replicated on different machines.

## Features

`opp_env` provides a number of powerful features that make it a valuable tool for
any researcher or developer working with OMNeT++ simulation frameworks:

- Automated installation of OMNeT++ simulation frameworks and models, including
  dependencies like INET Framework and OMNeT++ itself.
- Support for any version of OMNeT++ and INET, as well as select
  versions of Veins, SimuLTE, Simu5G and other 3rd party models.
- Reproducible builds thanks to the powerful isolation provided by Nix.
- Easy to use shell command that sets up an environment for working with the
  selected simulation framework.
- Customizable configuration options that allow for advanced control over the
  installation process.

## Usage

Using `opp_env` is simple. To install a specific version of a simulation framework
and its dependencies, first create a workspace and initialize it:

    mkdir workspace && cd workspace && opp_env init

Then run the following command:

    opp_env install <framework-version>

For example, to install Simu5G version 1.2.1, run the following command:

    opp_env install simu5g-1.2.1

This will download Simu5G, the matching INET and OMNeT++ packages and compile
them.

> [!TIP]
> To install the latest version of a package, use the `latest` pseudo-version
> e.g. to install the latest version of OMNeT++ use `opp_env install omnetpp-latest`

To open a shell prompt where you can use the recently installed Simu5G model, type:

    opp_env shell simu5g-1.2.1

> [!IMPORTANT]
> You cannot use the packages you installed via `opp_env` outside of `opp_env shell` or `opp_env run`. 

> [!TIP]
> To see the list of available packages, type: `opp_env list`.
> [Scroll down](#supported-simulation-frameworks) for the output from a recently released version.

## Installation

### Installing opp_env on Linux and macOS

`opp_env` requires Python3, pip and Nix installed on your machine. Everything else will be installed by Nix. 

#### Installing Python3 and pip

Use your operating system's package manager to install Python3 and pip.

#### Installing Nix

You can download and install Nix from [here](https://nixos.org/download). All other
`opp_env` dependencies are automatically installed using the Nix package manager.

> [!NOTE] 
> For macOS users, it is recommended to add 
>    ```
>    if [ -e '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh' ]; then
>      . '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh'
>    fi
>   ```
> to your `~/.zshrc` or `~/.bashrc` file after a successful Nix installation. 
> The Nix installer adds these lines to your global `/etc/bashrc` and `/etc/zshrc`
> files, but macOS system upgrades regularly overwrite these system files rendering
> the Nix installation unavailable.

#### Installing opp_env with pip

Once you have the prerequisites, you can install `opp_env` using `pip`:

First, make sure that `pip` is the latest version:

    pip install --upgrade pip

You can now install `opp_env`:

    pip3 install opp-env

> [!IMPORTANT]
> On some system, namely recent versions of Ubuntu / Debian, this
> command stops with an error message: `error: externally-managed-environment`
>
> To work around the error, follow the instructions in the printed message, which
> boils down to either adding the `--break-system-packages` option to the
> `pip install` commands, or setting up a Python virtual environment
> ([venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/))
> and working from there.

When you install `opp_env` using pip, it installs the `opp_env` Python module,
as well as a small script into your system's path (e.g. `~/.local/bin` or the
virtual environment's bin directory) that allows you to invoke it from the shell.
The `opp_env` command is equivalent to running `python -m opp_env`, which also
runs the `opp_env` Python module. (Make sure that `~/.local/bin` is in
your `PATH` environment variable. Acivating the python virtual environment 
does this for you automatically.)

### Installing opp_env on Windows 10 & 11 (with WSL2)

`opp_env` requires the Nix package manager which is available only on Linux and macOS,
but you can still use `opp_env` on Windows running it in a WSL2 (Windows Subsystem 
for Linux) container.

For Windows 10 and 11, we provide a pre-packaged, Ubuntu 22.04 based WSL2
container with all the necessary dependencies (Python3, pip, Nix, etc.) already installed.

To install the `opp_env` WSL distro image, open a command prompt and run the
following command:

    curl.exe -L https://github.com/omnetpp/opp_env/releases/download/wsl/opp_env-wsl.tar.gz | wsl --import opp_env .\opp_env-wsl -

The above command will download and install a WSL2 container image for `opp_env` and
place it into the `opp_env-wsl` folder. The shell can be started with:

    wsl -d opp_env --cd ~

Once you are inside the container, you can run the `opp_env` command as
suggested in the previous section.

### Installing opp_env with Docker

We provide docker images for `opp_env` that can be installed with the following
command:

    docker pull ghcr.io/omnetpp/opp_env

You can try it interactively with:

    docker run -it ghcr.io/omnetpp/opp_env

This image is the same as the one used for generating the WSL2 image.

## Developing or changing opp_env

If you want to contribute to the development of `opp_env` or need to modify the
source code for any reason, you can install the package in editable mode by
cloning the git repo, changing to its root directory and using
the following command:

    pip install --editable .

This will install the Python module and the `opp_env` command, but with the
added ability to make local modifications that will take effect immediately.

If you get the `error: externally-managed-environment` message, see the note
marked IMPORTANT above.

In case of other errors, try upgrading pip to the latest version first by
running `python3 -m pip install --upgrade pip`.

### Building the Python Package

To build the Python package, you first need to install the `build` package by
running the following command:

    pip install --upgrade build

Once you have `build` installed, you can build the package by running:

    python3 -m build

If you have any issues or questions, feel free to open an issue on the GitHub
repository. We are always happy to help!
