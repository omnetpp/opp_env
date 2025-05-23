# Changes

## 0.34.0.250523

### opp_env

- allow download_commands to coexist with git_url/download_url in project descriptions

### Database (Frameworks and Models)

- added libptp and its required projects libpln and omnet_utils

## 0.33.1.250429

### opp_env

- opp_ide is no longer forced to run with X11 backend on WSL

## 0.33.0.250429

### opp_env

- reduced NIX version requirement from 2.9 to 2.8 which is available in debian bookworm or later
- fix #28 "... --add-extra-nix-packages --gcc,gcc should not add duplicates"

### Database (Frameworks and Models)

- eclipse_mosaic: added as a new model
- veins: added 5.3.1

## 0.32.1.250228

### opp_env

- added distro specific NIX installation hints when nix command is not detected

### Database (Frameworks and Models)

- veins: wider range of dependencies are supported (i.e. more INET versions)
- veins_vlc: added a more up to date version
- artery_allinone: fixes to dependencies, build anbd test commands

## 0.32.0.250219

### opp_env

- added "list --matching" option, expanded "--expand" and  "--expand-all"

### Database (Frameworks and Models)

- veins: added 5.3 version
- veins: added inet 4.5.4 and updated sumo version for veins-git
- veins: updated omnetpp-6.* dependencies
- veins: removed omnetpp-5.5.0 from all veins versions due to segfault in smoke test
- veins: fixed smoke test command for veins-5.3 and omnetpp-6.0.*
- veins: removed non-working dependencies from veins-5.3
- veins: updated clean command to also clean subprojects
- veins: added patch command to remove --no-deep-includes from configure because it's deprecated
- openflow: renamed to openflow4core
- simu5g: added simu5g v1.3.0
- inet: fixed smoke test command

## 0.31.2.250122

### opp_env

### Database (Frameworks and Models)

- omnetpp: added a `nixos-recent` option so any older version of omnetpp
  can be forced to use the latest tested nixos version as an environment
  (corrent latest is 24.05)
- simu5g: added v1.2.3 (for omnetpp 6.1)

## 0.31.2.241127

### opp_env

- `shell` to print "Type omnetpp to start the IDE."
- fix: do not add omnetpp as referenced project when importing projects into the IDE

### Database (Frameworks and Models)

- omnetpp: on WSL, force IDE and Qtenv to use the X11 backend instead of Wayland
- inet: enable lwIP feature by default
- inet: remove redundant osudp example
- inet: added "full" option to inet_versions
- inet: make "test_commands" depend on INET version
- inet: added 3.8.5

## 0.31.1.241031

### opp_env

- fix: `-k` option not being effective in the `install` subcommand
- fix: errors during build and test were not properly detected and reported by `opp_env`
- fix: with `run`, the `--smoke-test` and `--test` options were ineffective
- various refactorings

### Database (Frameworks and Models)

- omnetpp: report error for unsupported platforms (versions earlier than 6.0 on Apple Silicon)
- inet: added version 4.5.4
- inet: smoke test works now in both debug and release 
- inet: adjusted smoke test command
- inet: use lower case inet lib name before 3.0 in smoke tests
- veins-5.2: removed omnetpp-6 and corresponding inet versions as it didn't work
- veins: removed `/dev/null` redirection and added echo statements
- lora_icn: fixed smoke test command
- oppbsd: use release build instead of debug
- opencv2x_artery: fixed build command
- gradys: fixed smoke test commands
- libara: fixed patch command
- mixim: smoke test works now in both debug and release 

## 0.31.0.241018

### opp_env

- `install`, `shell` and `run`: added `--add-extra-nix-packages`
- improved parsing for `--options`, `--vars-to-keep`, `--build-modes`
- make sure workspace is not under a git working tree
- record a `prepatch.sha` too, so it's possible to find out which files were patched

### Database (Frameworks and Models)

- omnetpp: removed optional `bear` package as it was causing build issues on macOS/x86_64
- omnetpp: fixed a qtenv issue for omnetpp 6.0.3 on macOS/x86_64 - `QT_PLUGIN_PATH` was overwritten by `setenv`
- oppbsd: only build in debug (it was built in debug twice) 
- obs: only build in debug (it was built in both but only tested in debug)
- updated sim-time-limit for some smoke tests

## 0.30.3.241016

### opp_env

- more detailed/helpful help text for subcommands, with examples
- `info` subcommand: Include the download/git URL in the output
- `info` subcommand: fix: default option was not marked with `*`
- `run` subcommand: do not chdir by default; added `--chdir` option to change into ws root
- `shell` subcommand: print an expanded list of commands available on startup
- `install` subcommand: added `--test` and `--smoke-test`
- `install` subcommand: did not correctly take and pass on build modes
- `install` and `run` subcommands: fix: `--no-isolated` flag did not take effect
- define `OPP_ENV_DIR`, `OPP_ENV_PROJECTS`, `OPP_ENV_PROJECT_DEPS` env vars
- fix up escaping in shell prompt
- the `--mode` command line option became `--build-modes`
- adjusted the order in which the projects are downloaded (dependencies first)
- `--init` option: do not complain if workspace is already initialized
- fix: `build_all` etc. did not pass on mode args
- added the possibility to install any branch directly from a git repository
  by specifying `@branchname` after the project name (e.g. `inet-git@mybranch`)

### Database (Frameworks and Models)

- omnetpp: above version 6.1, IDE now auto-imports projects into its workspace
- omnetpp: added omnetpp-6.1.0 and added omnetpp-6.1.* compatibility everywhere 6.0.* is listed
- omnetpp: remove possibility to install patch branches (.x) which are no longer relevant
- omnetpp: added `bear` nix package as dependency
- inet: use fingerprint testing for `--test`
- inet: fix: INET project was modified right after build
- renamed versions `<projectname>-master` to `<projectname>-git`
- added ecmp_allinone
- added signals_and_gateways
- added sdn4core
- added soa4core
- added new version of openflow
- added new version of fico4omnet which is compatible with omnetpp-6.0.*
- added new version of artery_allinone
- veins: added inet 4.4.1, 4.3.8 and 4.3.7 to master version dependencies
- updated project descriptions
- fixed patch command for tsch_allinone
- fixed patch command in rpl_allinone
- space_veins: renamed to space_veins_allinone
- space_veins: fixed build command
- fix "clean" commands: they ignored `$BUILD_MODE`
- smoke test fixes for all projects


## 0.29.3.240918

### opp_env

- fix: use gitFull nix package instead of git (so that we have git gui in opp_env)

### Database (Frameworks and Models)

- fix: certain programs that were executed from the host environment (like midnight commander)
       failed to load because opp_env was modifying the LD_LIBRARY_PATH.
- veins: added new inet versions needed for omnetpp-6; fixed image path
- added artery, neta, space_veins, plexe, rimfading, opencv2x_artery, cmm_solar_mobility
- inet: disabled smoke test commands for inet_20100323
- plexe: added omnetpp-6

## 0.29.1.240516

### opp_env

- add nix package and a flake file (use `nix shell` to start an opp_env enabled shell)
- change into project directory when using 'opp_env shell' command without any project arguments

### Database (Frameworks and Models)

- obs: build properly in both release and debug (still only tested in debug due to segfault)
- dns, tcp_fit_illinois: build and test properly in both release and debug
- rspsim: build tools in toolchain directory
- streetlightsim: build and test in release and debug
- added rspsim-6.1.3
- solarleach: only build in release, because omnetpp 3.3 has no distinct debug/release
- added castalia-3.3pr16. This is the 3.3 version ported to omnetpp-5
- inet-3.4.0: removed omnetpp-5.0.* from dependencies due to build error
- inet: use another example for smoke test; also properly test release and debug
- added from-git-option to simu5g, simulte, fico4omnet, ansa, core4inet, simproctc, rspsim, ops and rina
- added newer version for core4inet (240124)

## 0.29.0.240422

### opp_env2

- removed the `upgrade` subcommand

### Database (Frameworks and Models)

- oppbsd: fixed incorrect download URL
- inet-2010323, rease, quagga: build only debug version, because inet-20100323 can only support one build at a time

Supported simulation models and frameworks:

```
$ opp_env list

omnetpp                  6.0.3  6.0.2  6.0.1  6.0.0  5.7.1  5.7.0  5.6.3  5.6.2  5.6.1  5.6.0  5.5.2  5.5.1  5.5.0  5.4.2  5.4.1  5.4.0  5.3.1  5.3.0  5.2.2  5.2.1  5.2.0  5.1.2  5.1.1  5.1.0  5.0.1  5.0.0  4.6.1  4.6.0  4.5.1  4.5.0  4.4.2  4.4.1  4.4.0  4.3.2  4.3.1  4.3.0  4.2.3  4.2.2  4.2.1  4.2.0  4.1.1  4.1.0  4.0.2  4.0.1  3.3.2  3.3.1  6.0.x  5.7.x  5.6.x  5.5.x  5.4.x  5.3.x  5.2.x  5.1.x  5.0.x  4.6.x  4.5.x  4.4.x  4.3.x  4.2.x  4.1.x  4.0.x  3.3.x  master
inet                     4.5.2  4.5.1  4.5.0  4.4.1  4.4.0  4.3.9  4.3.8  4.3.7  4.2.10  4.2.9  4.2.8  4.2.7  4.2.6  4.2.5  4.2.4  4.2.3  4.2.2  4.2.1  4.2.0  4.1.2  4.1.1  4.1.0  4.0.0  3.8.3  3.8.2  3.8.1  3.8.0  3.7.1  3.7.0  3.6.8  3.6.7  3.6.6  3.6.5  3.6.4  3.6.3  3.6.2  3.6.1  3.6.0  3.5.x  3.5.0  3.4.0  3.3.0  3.2.4  3.2.3  3.2.2  3.2.1  3.2.0  3.1.x  3.1.1  3.1.0  3.0.x  3.0.0  2.6.x  2.6.0  2.5.x  2.5.0  2.4.x  2.4.0  2.3.x  2.3.0  2.2.x  2.2.0  2.1.x  2.1.0  2.0.x  2.0.0  20100323  20061020  master
afdx                     20220904
ansa                     3.4.0
can_allinone             0.1.0
castalia                 3.3  3.2
cell                     20140729
chaosmanager             20221210
core4inet                221109
crsimulator              20140204
dctrafficgen             20181016
dns                      20150911
fico4omnet               20210113
flora                    1.1.0
gptp                     20200311
gradys                   0.5
hnocs                    20221212
icancloud                1.0
ieee802154standalone     20180310
inet_hnrl                20170217  20100723
inetgpl                  1.0
inetmanet3               3.8.2
inetmanet4               4.0.0
libara_allinone          20150402
lora_icn                 paper
lre_omnet                1.0.1
mixim                    2.3
ndnomnet                 20200914
nesting                  0.9.1
obs                      20130114
omnet_tdma               1.0.2
opencv2x_veins           1.4.1
opendsme_allinone        20201110
openflow                 20231017
oppbsd                   4.0
ops_allinone             20230331
os3                      1.0
processbus_allinone      20180926
quagga                   20090803
quisp                    20230807
rease                    20130819
rinasim                  20200903
rpl_allinone             6tisch_paper
rspsim                   6.1.2
seapp                    20191230
sedencontroller_allinone 20230305
simcan                   1.2
simproctc                2.0.2
simu5g                   1.2.2  1.2.1  1.1.0
simulte                  1.2.0  1.1.0  0.9.1
solarleach               1.01
stochasticbattery        20170224
streetlightsim           1.0
swim_allinone            20180221
tcp_fit_illinois         20150828
tsch_allinone            6tisch_paper
veins                    5.2  5.1  5.0  4.7.1  4.7  4.6  4.4  4.3  3.0  master
veins_vlc                1.0
wifidirect_allinone      3.4
```

## 0.28.1.240417

### opp_env

The first version of `opp_env` published on pypi.org
