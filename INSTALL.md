# Installing opp_env

## Linux

`opp_env` requires Python3, pip and Nix installed on your machine.
Use your operating system's package manager to install Python3 and pip if they are not already installed.

### Installing opp_env with pip

You can install `opp_env` using `pip`. First, make sure that `pip` is the latest version:

    pip install --upgrade pip

You can now install `opp_env`:

    pip install opp-env

> [!IMPORTANT]
> On some system, namely recent versions of Ubuntu / Debian, this
> command stops with an error message: `error: externally-managed-environment`
>
> To work around the error, set up a Python virtual environment
> ([venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/))
> and start working from there, or follow the instructions in the printed message, which
> boils down to adding the `--break-system-packages --user` option to the
> `pip install` commands.

When you install `opp_env` using pip, it installs the `opp_env` Python module,
as well as a small script into your system's path (e.g. `~/.local/bin` or the
virtual environment's bin directory) that allows you to invoke it from the shell.
The `opp_env` command is equivalent to running `python -m opp_env`, which also
runs the `opp_env` Python module. (Make sure that `~/.local/bin` is in
your `PATH` environment variable. Activating the Python virtual environment
does this for you automatically.)

### Installing Nix

`opp_env` requires a relatively recent version of Nix, so we recommend that
you install Nix from the  [project's web site](https://nixos.org/download)
instead of using the package manager of your OS.


## macOS

We do not provide precise installation instructions at the moment, but by-and-large
the procedure is the same as on Linux.

> [!IMPORTANT]
> On a Mac with Apple Silicon, only OMNeT++ 6.x works, earlier versions cannot
> be installed with `opp_env`. This severely limits the selection of models you can install.

[!TIP]
> The Nix installer adds a few lines to the global `/etc/bashrc` and `/etc/zshrc`
> system files. However, macOS system upgrades regularly overwrite these files,
> rendering the Nix installation unavailable. To prevent this from happening,
> we recommend that you add the following lines to the `~/.zshrc` and/or `~/.bashrc` file:
>
>    ```
>    if [ -e '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh' ]; then
>      . '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh'
>    fi
>   ```


## Windows 10/11, using WSL2

`opp_env` cannot be installed on Windows directly because Nix is not available on that platform.
However, you can use it inside a WSL2 (Windows Subsystem for Linux) container.

For Windows, we provide a pre-packaged WSL2 container image based on Ubuntu 24.04
that includes all necessary dependencies (Python3, pip, Nix, etc.).

To install the `opp_env` WSL2 image, open a command prompt and run the following command:

    curl.exe -L https://github.com/omnetpp/opp_env/releases/download/wsl/opp_env.wsl | wsl --import opp_env -

Alternatively, if you have [WSL 2.4.4](https://github.com/microsoft/WSL/releases) or later (recommended),
you can just download the `opp_env.wsl` file and open it by either double-clicking it in
the file explorer or opening it directly in the browser's download folder. 

Once the image is imported, the shell can be started with:

    wsl -d opp_env --cd ~

or just start opp_env from the start menu.

Once you are inside the container, you can run the `opp_env` command as
suggested in the previous section.


## In Docker

We provide docker images for `opp_env` that can be installed with the following
command:

    docker pull ghcr.io/omnetpp/opp_env

You can try it interactively with:

    docker run -it ghcr.io/omnetpp/opp_env

This image is the same as the one we use for generating the WSL2 image.

