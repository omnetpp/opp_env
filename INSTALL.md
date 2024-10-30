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

