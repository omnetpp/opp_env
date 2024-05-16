# Changes

## dev branch

### opp_env

### Frameworks and models

## 0.29.1.240516

### opp_env

- add nix package and a flake file (use `nix shell` to start an opp_env enabled shell)
- change into project directory when using 'opp_env shell' command without any project arguments

### Frameworks and models

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

### Frameworks and models

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
