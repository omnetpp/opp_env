![smoke tests](https://github.com/omnetpp/opp_env/actions/workflows/smoketest.yml/badge.svg)

# opp_env: Simplifying OMNeT++ Model Installations

`opp_env` is a powerful tool that allows for the easy and automated installation
of OMNeT++ simulation frameworks and models, including dependencies like INET
Framework and OMNeT++ itself. It can install any version of OMNeT++ and INET, as
well as currently selected versions of Veins, SimuLTE, Simu5G and other models.
We are working towards expanding its database with more models, and we are open
to suggestions and contributions.

`opp_env` supports Linux and macOS systems. On Windows 11, `opp_env` can be
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

## Installation

See the [INSTALL](INSTALL.md) page.

## Usage

To install a specific version of a simulation framework
and its dependencies, first create a workspace and initialize it:

    mkdir workspace && cd workspace && opp_env init

Then run the following command:

    opp_env install <framework-version>

For example, to install Simu5G version 1.3.0, run the following command:

    opp_env install simu5g-1.3.0

This will download Simu5G, the matching INET and OMNeT++ packages and compile
them.

> [!TIP]
> To install the latest version of a package, use the `latest` pseudo-version
> e.g. to install the latest version of OMNeT++ use `opp_env install omnetpp-latest`

To open a shell prompt where you can use the recently installed Simu5G model, type:

    opp_env shell simu5g-1.3.0

> [!IMPORTANT]
> You cannot use the packages you installed via `opp_env` outside of `opp_env shell` or `opp_env run`.

> [!TIP]
> If you frequently install new versions of OMNeT++ and/or simulation models, it's recommended to
> run `nix store gc` periodically to reclaim disk space occupied by older, unused dependencies.

## Available Packages

To see the list of available packages, type: `opp_env list`. The output from `opp_env list` from October 31, 2024:

    omnetpp                     6.1.0  6.0.3  6.0.2  6.0.1  6.0.0  5.7.1  5.7.0  5.6.3  
                                5.6.2  5.6.1  5.6.0  5.5.2  5.5.1  5.5.0  5.4.2  5.4.1  
                                5.4.0  5.3.1  5.3.0  5.2.2  5.2.1  5.2.0  5.1.2  5.1.1  
                                5.1.0  5.0.1  5.0.0  4.6.1  4.6.0  4.5.1  4.5.0  4.4.2  
                                4.4.1  4.4.0  4.3.2  4.3.1  4.3.0  4.2.3  4.2.2  4.2.1  
                                4.2.0  4.1.1  4.1.0  4.0.2  4.0.1  3.3.2  3.3.1  git
    inet                        4.5.4  4.5.2  4.5.1  4.5.0  4.4.1  4.4.0  4.3.9  4.3.8  
                                4.3.7  4.2.10  4.2.9  4.2.8  4.2.7  4.2.6  4.2.5  4.2.4  
                                4.2.3  4.2.2  4.2.1  4.2.0  4.1.2  4.1.1  4.1.0  4.0.0  
                                3.8.5  3.8.3  3.8.2  3.8.1  3.8.0  3.7.1  3.7.0  3.6.8  
                                3.6.7  3.6.6  3.6.5  3.6.4  3.6.3  3.6.2  3.6.1  3.6.0  
                                3.5.x  3.5.0  3.4.0  3.3.0  3.2.4  3.2.3  3.2.2  3.2.1  
                                3.2.0  3.1.x  3.1.1  3.1.0  3.0.x  3.0.0  2.6.x  2.6.0  
                                2.5.x  2.5.0  2.4.x  2.4.0  2.3.x  2.3.0  2.2.x  2.2.0  
                                2.1.x  2.1.0  2.0.x  2.0.0  20100323  20061020  git
    afdx                        20220904
    ansa                        3.4.0
    artery_allinone             20240807  20230820
    can_allinone                0.1.0
    castalia                    3.3pr16  3.3  3.2
    cell                        20140729
    chaosmanager                20221210
    cmm_orbit_mobility_allinone 20220815
    core4inet                   20240124  221109
    crsimulator                 20140204
    dctrafficgen                20181016
    dns                         20150911
    ecmp_allinone               20230713
    fico4omnet                  20240124  20210113
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
    openflow4core               20240124  20231017
    opp_env_testproject         0.1
    oppbsd                      4.0
    ops_allinone                20230331
    os3                         1.0
    plexe                       3.1.2  3.1.0  3.0
    processbus_allinone         20180926
    quagga                      20090803
    quisp                       20230807
    rease                       20130819
    rimfading_allinone          20171123
    rinasim                     20200903
    rpl_allinone                6tisch_paper
    rspsim                      6.1.3  6.1.2
    sdn4core                    20240124
    seapp                       20191230
    sedencontroller_allinone    20230305
    signals_and_gateways        20240124
    simcan                      1.2
    simproctc                   2.0.2
    simu5g                      1.3.0  1.2.3  1.2.2  1.2.1  1.1.0  git
    simulte                     1.2.0  1.1.0  0.9.1
    soa4core                    20240124
    solarleach                  1.01
    space_veins_allinone        0.3
    stochasticbattery           20170224
    streetlightsim              1.0
    swim_allinone               20180221
    tcp_fit_illinois            20150828
    tsch_allinone               6tisch_paper
    veins                       5.3  5.2  5.1  5.0  4.7.1  4.7  4.6  4.4  4.3  3.0  git
    veins_vlc                   1.0.20210526  1.0
    wifidirect_allinone         3.4

## Modifying opp_env

If you want to modify `opp_env`, see the [DEVELOP](DEVELOP.md) page.
