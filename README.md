![smoke tests](https://github.com/omnetpp/opp_env/actions/workflows/smoketest.yml/badge.svg)

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

<a name="supported-simulation-frameworks"></a>
## Available packages

The output from `opp_env list` from October 1, 2024:

    omnetpp                     6.0.3  6.0.2  6.0.1  6.0.0  5.7.1  5.7.0  5.6.3
                                5.6.2  5.6.1  5.6.0  5.5.2  5.5.1  5.5.0  5.4.2
                                5.4.1  5.4.0  5.3.1  5.3.0  5.2.2  5.2.1  5.2.0
                                5.1.2  5.1.1  5.1.0  5.0.1  5.0.0  4.6.1  4.6.0
                                4.5.1  4.5.0  4.4.2  4.4.1  4.4.0  4.3.2  4.3.1
                                4.3.0  4.2.3  4.2.2  4.2.1  4.2.0  4.1.1  4.1.0
                                4.0.2  4.0.1  3.3.2  3.3.1  git
    inet                        4.5.2  4.5.1  4.5.0  4.4.1  4.4.0  4.3.9  4.3.8
                                4.3.7  4.2.10  4.2.9  4.2.8  4.2.7  4.2.6  4.2.5
                                4.2.4  4.2.3  4.2.2  4.2.1  4.2.0  4.1.2  4.1.1
                                4.1.0  4.0.0  3.8.3  3.8.2  3.8.1  3.8.0  3.7.1
                                3.7.0  3.6.8  3.6.7  3.6.6  3.6.5  3.6.4  3.6.3
                                3.6.2  3.6.1  3.6.0  3.5.x  3.5.0  3.4.0  3.3.0
                                3.2.4  3.2.3  3.2.2  3.2.1  3.2.0  3.1.x  3.1.1
                                3.1.0  3.0.x  3.0.0  2.6.x  2.6.0  2.5.x  2.5.0
                                2.4.x  2.4.0  2.3.x  2.3.0  2.2.x  2.2.0  2.1.x
                                2.1.0  2.0.x  2.0.0  20100323  20061020  git
    afdx                        20220904
    ansa                        3.4.0
    artery_allinone             20230820
    can_allinone                0.1.0
    castalia                    3.3pr16  3.3  3.2
    cell                        20140729
    chaosmanager                20221210
    cmm_orbit_mobility_allinone 20220815
    core4inet                   240124  221109
    crsimulator                 20140204
    dctrafficgen                20181016
    dns                         20150911
    fico4omnet                  20210113
    flora                       1.1.0
    gptp                        20200311
    gradys                      0.5
    hnocs                       20221212
    icancloud                   1.0
    ieee802154standalone        20180310
    inet_hnrl                   20170217  20100723
    inetgpl                     1.0
    inetmanet3                  3.8.2
    inetmanet4                  4.0.0
    libara_allinone             20150402
    lora_icn                    paper
    lre_omnet                   1.0.1
    mixim                       2.3
    ndnomnet                    20200914
    nesting                     0.9.1
    neta_allinone               1.0
    obs                         20130114
    omnet_tdma                  1.0.2
    opencv2x_artery             1.4.1
    opencv2x_veins              1.4.1
    opendsme_allinone           20201110
    openflow                    20231017
    oppbsd                      4.0
    ops_allinone                20230331
    os3                         1.0
    plexe                       3.1.2
    processbus_allinone         20180926
    quagga                      20090803
    quisp                       20230807
    rease                       20130819
    rimfading_allinone          20171123
    rinasim                     20200903
    rpl_allinone                6tisch_paper
    rspsim                      6.1.3  6.1.2
    seapp                       20191230
    sedencontroller_allinone    20230305
    simcan                      1.2
    simproctc                   2.0.2
    simu5g                      1.2.2  1.2.1  1.1.0  git
    simulte                     1.2.0  1.1.0  0.9.1
    solarleach                  1.01
    space_veins                 0.3
    stochasticbattery           20170224
    streetlightsim              1.0
    swim_allinone               20180221
    tcp_fit_illinois            20150828
    tsch_allinone               6tisch_paper
    veins                       5.2  5.1  5.0  4.7.1  4.7  4.6  4.4  4.3  3.0  git
    veins_vlc                   1.0
    wifidirect_allinone         3.4
