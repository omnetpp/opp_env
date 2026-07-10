## 0.37.0.260609

### opp_env

- Read-only Nix store dependencies: appending `@` to a version
  (e.g. `opp_env install inet-latest omnetpp-latest@`) builds the project as a
  real Nix package in the read-only `/nix/store` instead of the workspace.
  The `@` automatically extends to all dependencies of the marked project.
  Note that a trailing `@` is the read-only marker, while `@<branch>` still means
  a git branch; the two cannot be combined.
  Store packages are shared between workspaces (identical requests are instant
  cache hits), are picked up by a later `shell`/`run` that names no projects at
  all, and their `build_*`/`clean_*`/`check_*` shell functions become no-ops. Source archive checksums are obtained trust-on-first-use and
  cached under `~/.cache/opp_env/`; use `--refresh-source-hashes` if an archive
  changes upstream. Currently omnetpp >= 6.0 (modernized releases) and
  inet >= 4.4 releases support this.
  Every store package, whether named on the command line or pulled in as a
  dependency, is symlinked into the workspace under its usual directory name plus
  a `@` suffix, e.g. `omnetpp-6.4.0@`. Thanks to the suffix a mutable and a
  read-only copy of the same project version can coexist in one workspace; a bare
  project name then selects the mutable copy, and `<name>@` the read-only one.
  The symlink is what Nix created as the package's out-link, so it doubles as its
  garbage collection root; deleting it exposes the package to the next
  `nix store gc`, and a later `install` relinks it (a cache hit unless the store
  path is already gone). Nothing else depends on the symlink: the shell
  environment (`<NAME>_ROOT`, `PATH`, `NEDPATH`, ...) is set up from the
  `/nix/store` path, and the package metadata lives in the workspace admin
  directory. `shell --chdir` does start the shell in the `<name>@` symlink
  though, so the working directory stays inside the workspace.
  Store packages no longer contain the `out/` build output tree; the finished
  libraries and executables in `lib/`, `bin/` and `src/` are unaffected. This
  cuts the installed size of INET by about 75% and of OMNeT++ by about 40%.
  Note that it also changes the derivations, so store packages installed by an
  earlier opp_env are rebuilt on the next `install`.
  The shell prompt marks read-only projects with the same `@` suffix, e.g.
  `omnetpp-6.4.0@+inet-4.6.0@+simu5g-1.5.0:~/w/x/simu5g-1.5.0$`.
  Naming a project without the `@` always means the regular one, even if only the
  store package happens to be installed -- `--install` then installs the regular
  one alongside it. A store package in the workspace is picked up only when no
  projects are named on the command line at all, or for a dependency an already
  installed project was recorded as using that way. So installing a new mutable
  project never drags its dependencies into the store silently; opp_env points out
  the store package that could have been reused instead.
- New `export-flake` subcommand: exports the Nix flake(s) that build a project
  and its dependencies as Nix packages, independently of opp_env. The default
  layout is one flake per project (dependencies wired up as flake inputs);
  `--bundle` produces a single self-contained flake. Exports include a dev
  shell, a README, and a `push-to-cachix.sh` helper for publishing the packages
  to a binary cache (see `docs/binary-cache.md`).
- Add `--run-install-commands` option and `install_commands` list to
  project descriptions to support limited automatic installation of
  external dependencies in nixless workspaces.
- inet: added version 4.7.0

### Database (Frameworks and Models)

- omnetpp: new `no-ide` option (>= 6.0): excludes the graphical IDE from the
  installation; mainly useful for read-only Nix store packages, where it
  removes the Eclipse/webkitgtk dependencies from the package closure.
- omnetpp: added support calling `./install.sh` after downloading and
  patching, if `--run-install-commands` is specified (for nixless workspaces).


## 0.36.2.260805

### Database (Frameworks and Models)

- nasctime: added nasctime-1.0.1, a 5G-TSN bridge model implementing 3GPP
  Release 16 TSN integration
- simu5g_nasctime: added version 1.0, the patched Simu5G fork that nascTime's
  IEEE 802.1CB FRER features require


## 0.36.2.260713

### Database (Frameworks and Models)

- simu5g: added versions 1.4.5 and 1.5.0

## 0.36.2.260707

### Database (Frameworks and Models)

- inet: added version 4.7.0

## 0.36.2.260606

### opp_env

- Fixed incorrect version number used in timestamp. Should be YYMMDD.

### Database (Frameworks and Models)

- omnetpp: added 6.4.0 AI preview version
- omnetpp: 6.4.0 and 6.4.0 ai preview is now using stable nixos 26.05
- inet: added omnetpp-6.4.0aipre2 as a supported dependency got INET 4.6
- mm1k: added a dummy model for `opp_ci` testing


## 0.36.1.20260524

### Database (Frameworks and Models)

- inet: added the inet-4.5.4 + omnetpp-6.4.0 combination
- simu5g: added version 1.4.4
- flora: added flora-1.3


## 0.36.1.20260515

### Database (Frameworks and Models)

- omnetpp: fix missing python3Packages.posix-ipc nix dependency name for
  omnetpp-6.* (follow name change posix-ipx -> posix_ipc, and now only
  omnetpp-6.0.* depends on it)
- omnetpp: added version 6.4.0
- omnetpp: fixed non-working internal browser on NixOS
- add omnetpp-6.4 support to the following projects: inet-4.6.0, inet-3.8.5,
  inet-git, simu5g-1.4.*, simu5g-git, inetgpl-4.6.0, openflow-20250717,
  inbaversim-0.3.0, inbaversim-0.1.0, inbaversim-git (note: inet-git now
  requires with omnetpp-6.4)
- simu5g: added specialized releases 1.4.1_sdap_2, 1.3.1_rlcam, 1.4.0_rlcam

### opp_env:

- fix python error on using `--init` with `--nixless-workspace`
- raise error when `--nixless-workspace` is specified on existing nixful workspace


## 0.36.0.260422

### Database (Frameworks and Models)

- inet: added the omnetpp-aipre version as a dependency for INET 4.6.0

## 0.36.0.260421

### opp_env

- added `upgrade` subcommand that allows upgrading `opp_env` itself

### Database (Frameworks and Models)

- omnetpp: added missing `bubblewrap` package for running simulations using `opp_sandbox`

## 0.35.0.260420

### Database (Frameworks and Models)

- flora: added flora 1.2.0
- omnetpp: added the omnetpp AI preview version for easier testing

## 0.35.0.260320

### Database (Frameworks and Models)

- added pileach and wifi_mlo_omnet
- plexe: added 3.2
- veins: fixed sumo version for 5.3.1
- veins: added inet-4.6 compatibility to veins-git
- inetgpl: added 4.6.0
- inetgpl: added omnetpp-6.3 compatibility to inetgpl 1.0

## 0.35.0.260224

### Database (Frameworks and Models)

- veins: added patch for inet-4.6 compatibility
- openflow: added inet-4.6 and omnetpp-6.3 compatibility

## 0.35.0.260220

### Database (Frameworks and Models)

- inet: added 4.6.0 version
- simu5g: added patch commands for 1.4.x versions to work with inet 4.6.0
- inbaversim: added inet-4.6 and omnetpp-6.3 compatibility

## 0.35.0.260218

### Database (Frameworks and Models)

- simu5g: added 1.4.2, 1.4.3


## 0.35.0.251114

### Database (Frameworks and Models)

- omnetpp: fix debugger not working on macOS
- omnetpp: add libdwarf and elfutils for better crash stack trace on linux
- omnetpp: added omnetpp 6.3.0
- inetgpl: use 1.0 release instead of commit hash
- lre_omnet: use 1.0.1 tag; use git_branch instead of git reset in download commands
- rpl_allinone and tsch_allinone 6tisch_paper versions: use release instead of commit hash
- fix inet-gpl and swim_allinone: use fix git commits instead of branches that may change over time
- swim_allinone: fix: move download from patch phase to download phase

## 0.35.0.251007

### Database (Frameworks and Models)

- added simu5g-1.4.1 and 1.4.1-sdap
- added sixgdetcom_allinone-20250910 (https://github.com/DETERMINISTIC6G/6GDetCom_Simulator/commit/7d3a08ba2eeab687e135f60f27f1bc79dacff153)
- added quisp-0.3.0

## 0.35.0.250919

### Database (Frameworks and Models)

- omnetpp: added missing lldb package for omnetpp 6.2+
- simu5g: added 1.3.1 and 1.4.0
- added inbaversim-0.3.0; removed inbaversim-0.2.0 as it was not a release tag
- added gptp_howhangliu2024_paper
- added new version of quisp

## 0.35.0.250718

### Database (Frameworks and Models)

- omnetpp: fixed a build error on macOS when brew and nix packages of qt got mixed up
- omnetpp: fixed build error on macOS with Qt6 frameworks
- omnetpp: fixed missing package error on macOS
- omnetpp: fixed MPI detection patch
- added openflow-20250717

## 0.35.0.250716

### Database (Frameworks and Models)

- omnetpp: fixed missing SVG icons in Qtenv (in 6.2.0)
- omnetpp: added the `qt6ct` tool to the shell (in 6.2.0 only) so it is possible
  to set and configure the themeing of Qtenv.
- omnetpp: projects not installed by opp_env are no longer closed when the IDE is started.
- omnetpp: on 6.0 and later, the PARSIM support is enabled 
- added inbaversim 0.2.0

## 0.34.0.250714

### Database (Frameworks and Models)

- omnetpp: added omnetpp-6.2.0 (also updated all models to use it if it was supported)

## 0.34.0.250623

### Database (Frameworks and Models)

- added inbaverSim, from https://github.com/ComNets-Bremen/inbaverSim

## 0.34.0.250617

### Database (Frameworks and Models)

- omnetpp: installation of omnetpp-6.1.0 on macOS was failing because of a broken
  numpy package in nixos 24.05. Moved omnetpp-6.1.0 to use nixos 24.11 instead
- omnetpp: the 6.2.1pre1 version is now using nixos 25.05

## 0.34.0.250608

### Database (Frameworks and Models)

- omnetpp: added omnetpp 6.2.0pre1 (omnetpp-latest is still omnetpp-6.1.0)
- inet: added 4.4.2
- added versions of semi-official openflow; refined project descriptions for openflow4core

## 0.34.0.250529

### Database (Frameworks and Models)

- added 5GTQ from https://github.com/tum-esi/5GTQ as simu5g_5gtq

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
