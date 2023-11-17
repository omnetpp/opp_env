def get_project_descriptions():
    return [
        {
            # DONE - ok
            "name": "fico4omnet", "version": "20210113",        # last commit of master branch as of time of writing
            "description": "Fieldbus Communication (CAN and FlexRay)",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/FiCo4OMNeT.html",
                "test_command": "cd fico4omnet-20210113/examples/flexray/dynamic && run_fico4omnet -u Cmdenv --sim-time-limit=1s",
            },
            "required_projects": {"omnetpp": ["5.5.*", "5.6.*", "5.7.*"]},
            # "git_url": "https://github.com/CoRE-RG/FiCo4OMNeT.git",
            "download_url": "https://github.com/CoRE-RG/FiCo4OMNeT/archive/refs/tags/nightly/2021-01-13_00-00-25.tar.gz",       # there are no releases available, so we download the latest nightly
            "patch_commands": [
                "mkdir bin",
                "rm src/run_fico4omnet.cmd",
                "mv src/run_fico4omnet bin",
                "sed -i 's|DIR=`dirname $0`|DIR=`dirname \\$0`/../src|' bin/run_fico4omnet",
                "sed -i 's|MAKEMAKE_OPTIONS .* -I.|& -o FiCo4OMNeT|' Makefile"
            ],
            "setenv_commands": [
                "export NEDPATH=$NEDPATH:$FICO4OMNET_ROOT/src:$FICO4OMNET_ROOT/examples:$FICO4OMNET_ROOT/examples_andl:$FICO4OMNET_ROOT/simulations",
                "export PATH=$PATH:$FICO4OMNET_ROOT/bin",
                "echo 'Hint: use the `run_fico4omnet` command to run the simulations in the examples folder.'"
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE - ok
            "name": "ansa", "version": "inet3.4.0",
            "description": "Automated Network Simulation and Analysis",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/ANSA.html",
                "test_command": "cd ansa-inet3.4.0/examples/ansa/eigrp/basic && ls -a && run_inet -c EIGRP_unequal_cost_lb -u Cmdenv",
            },
            "required_projects": {"omnetpp": ["5.1.*"]},
            "git_url": "https://github.com/kvetak/ANSA.git",
            "git_branch": "ansainet-3.4.0",
            "patch_commands": [
                "chmod +x inet_featuretool",
                "chmod +x src/run_inet",
                "sed -i 's|getClassName() > 0)|getCount() > 0)|' src/ansa/routing/babel/BabelDef.cc",
                "sed -i 's|cResultFilterDescriptor|cResultFilterType|' src/inet/common/figures/DelegateSignalConfigurator.cc",
                "sed -i 's/if (vector_cost<=nullptr)/if (vector_cost == nullptr)/' src/inet/routing/extras/dsr/dsr-uu/path-cache.cc",
                "rm src/run_inet.cmd",
                "mkdir bin",
                "mv src/run_inet bin",
                "sed -i 's|DIR=`dirname $0`|DIR=`dirname \\$0`/../src|' bin/run_inet"
            ],
            "setenv_commands": [
                "echo 'Hint: use the `run_inet` command to run the simulations in the examples/ansa folder.'",
                "export PATH=$PATH:$ANSA_ROOT/bin"
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE - ok
            "name": "flora", "version": "1.1.0",
            "description": "Framework for LoRa",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/FLoRA.html",
                "test_command": "cd flora-1.1.0/simulations && ./run -u Cmdenv --sim-time-limit=10s",
            },
            "required_projects": {"omnetpp": ["6.0.*"], "inet": ["4.4.0"]},
            "download_url": "https://github.com/florasim/flora/releases/download/v1.1.0/flora-1.1.0.tgz",
            "patch_commands": [
                "sed -i -E 's|INET_DIR = [^ ]+|INET_DIR = $(INET_ROOT)|' Makefile",
                "sed -i -E 's|-KINET_PROJ=[^ ]+|-KINET_PROJ=$(INET_DIR)|' Makefile"
            ],
            "setenv_commands": [
                "echo 'Hint: use the `./run` command to run the example in the simulations folder.'",
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE - ok
            "name": "core4inet", "version": "221109",       # last commit of master branch as of time of writing
            "description": "Real-Time Ethernet protocols for INET",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/Core4INET.html",
                "test_commands": "cd core4inet-221109/examples/IEEE8021Q/small_network && ./run -u Cmdenv --sim-time-limit=1s",
            },
            "required_projects": {"omnetpp": ["5.5.*"], "inet": ["3.6.6"]},
            "download_url": "https://github.com/CoRE-RG/CoRE4INET/archive/refs/tags/nightly/2022-11-09_00-01-11.tar.gz",
            "patch_commands": [
                "sed -i -E 's|INET_PROJ=[^ ]+|INET_PROJ=$(INET_ROOT)|' Makefile",
                "sed -i -E 's|-L.*/src|-L$$\\\\(INET_PROJ\\\\)/src|' Makefile",
                "sed -i -E 's|-O out |-O out -o CoRE4INET |' Makefile"
            ],
            "setenv_commands": [
                "echo 'Hint: use the `./rundemo` command in the examples folder or the `./run` command in any of the example subfolders.'",
                "export INETPATH=$INET_ROOT",
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE - ok
            "name": "simproctc", "version": "2.0.2",
            "description": "Simulation Processing Tool-Chain",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/SimProcTC.html",
                "test_command": "cd simproctc-2.0.2/example-simulation && ./example-simulation -u Cmdenv --sim-time-limit=10s",
            },
            "required_projects": {"omnetpp": ["6.0.*"]},
            "download_url": "https://github.com/dreibh/simproctc/archive/refs/tags/simproctc-2.0.2.tar.gz",
            "setenv_commands": [
                "export OPPMAIN_LIB=$OMNETPP_ROOT/lib",
                "echo 'Hint: use the `./example_simulation` command in the example-simulation folder.'",
                ],
            "build_commands": ["cd example-simulation && opp_makemake -f && make"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE - ok
            "name": "hnocs", "version": "20221212",     # last commit of master branch as of time of writing
            "description": "Network on Chip Simulation Framework",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/HNOCS.html",
                "test_command": "cd hnocs-20221212/examples/async/4x4 && ./run -u Cmdenv --sim-time-limit=0.01ms",
            },
            "required_projects": {"omnetpp": ["5.5.*"]},
            # "git_url": "https://github.com/yanivbi/HNOCS.git",
            "download_url": "https://github.com/yanivbi/HNOCS/archive/465754c28977a397e8ea4aef9296ca9987eb4f51.tar.gz",     # there are no releases, so we use a commit from the master branch
            "setenv_commands": [
                "echo 'Hint: use the `./run_nocs` command in the examples folder.'",
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE - ok
            "name": "gptp", "version": "20200311",      # last commit of master branch as of time of writing
            "description": "IEEE 802.1AS gPTP for Clock Synchronization",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/gPTP.html",
                "test_command": "cd gptp-20200311/IEEE8021AS/simulations && ./run -c Network_with_cross_traffic -u Cmdenv --sim-time-limit=10s",
            },
            "required_projects": {"omnetpp": ["5.2.*"], "inet": ["3.6.3"]},
            # "git_url": "https://gitlab.amd.e-technik.uni-rostock.de/peter.danielis/gptp-implementation.git",
            # there are no releases, so we use a commit from the master branch
            "download_url": "https://gitlab.amd.e-technik.uni-rostock.de/peter.danielis/gptp-implementation/-/archive/c498af56431d45b71ab5732cb352d03774344b6c/gptp-implementation-c498af56431d45b71ab5732cb352d03774344b6c.tar.gz",
            "patch_commands": [
                "sed -i -E 's|ieee8021as|IEEE8021AS|' IEEE8021AS/simulations/run",
                "sed -i -E 's|-n.*|-n $INET_ROOT/src:.:../src $*|' IEEE8021AS/simulations/run",
                "chmod +x IEEE8021AS/simulations/run",
            ],
            "setenv_commands": [
                "export INET_PROJ=$INET_ROOT",
                "echo 'Hint: use the `./run` command in the simulations folder.'",
            ],
            "build_commands": ["cd IEEE8021AS/src && opp_makemake -f --deep -KINET_PROJ=$INET_PROJ -DINET_IMPORT -I$INET_PROJ/src -L$INET_PROJ/src -lINET\$D && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE - ok
            "name": "nesting", "version": "0.9.1",
            "description": "Network Simulator for Time-Sensitive Networking (TSN)",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/NeSTiNg.html",
                "test_command": "cd nesting-0.9.1/simulations/examples && ../runsim 01_example_strict_priority.ini --sim-time-limit=10s",
            },
            "required_projects": {"omnetpp": ["5.4.*"], "inet": ["4.1.0"]},
            # "git_url": "https://gitlab.com/ipvs/nesting.git",
            "download_url": "https://gitlab.com/ipvs/nesting/-/archive/v0.9.1/nesting-v0.9.1.tar.gz",
            "patch_commands": [
                "sed -i -E 's|-KINET_PROJ=[^ ]+|-KINET_PROJ=$(INET_ROOT)|' Makefile",
                "sed -i 's|NESTING=.*|#NESTING=|' simulations/runsim-qt",
                "sed -i -E 's|INET=.*|INET=$INET_ROOT|' simulations/runsim-qt",
                "sed -i 's|./nesting$D|$NESTING/simulations/nesting$D|' simulations/runsim-qt",
                "sed -i 's|-n .:|-n $NESTING/simulations:|' simulations/runsim-qt",
                "sed -i 's|NESTING=.*|#NESTING=|' simulations/runsim",
                "sed -i -E 's|INET=.*|INET=$INET_ROOT|' simulations/runsim",
                "sed -i 's|./nesting$D|$NESTING/simulations/nesting$D|' simulations/runsim",
                "sed -i 's|-n .:|-n $NESTING/simulations:|' simulations/runsim",
            ],
            "setenv_commands": ["export INET_PROJ=$INET_ROOT",
                                "export NESTING=$NESTING_ROOT",
                                "echo 'Hint: use the `../runsim-qt` command to run the examples in the simulations/examples folder.'"],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE - ok
            "name": "castalia", "version": "3.3",
            "description": "Simulator for Wireless Sensor Networks (WSN), Body Area Networks (BAN) and generally networks of low-power embedded devices",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/Castalia.html",
                "test_command": "cd castalia-3.3/Castalia/Simulations/BANtest && Castalia -c TMAC",
            },
            "nix_packages": ["python2"],
            "required_projects": {"omnetpp": ["4.1.*"]},
            # "git_url": "https://github.com/boulis/Castalia.git",  # for master branch version
            # "required_projects": {"omnetpp": ["4.4"]},
            "download_url": "https://github.com/boulis/Castalia/archive/refs/tags/3.3.tar.gz",
            "patch_commands": [
                "sed -i 's|bin/python|bin/env python2|' Castalia/bin/Castalia",
                "sed -i 's|bin/python|bin/env python2|' Castalia/bin/CastaliaResults",
                "sed -i 's|bin/python|bin/env python2|' Castalia/bin/extractOmnetppINI",
                """sed -i 's|traceFile.open(par("traceFile"));|traceFile.open((const char *)par("traceFile"));|' Castalia/src/wirelessChannel/traceChannel/TraceChannel.cc""",
            ],
            "setenv_commands": [
                "export PATH=$PATH:$CASTALIA_ROOT/Castalia/bin",
                "echo 'Hint: Use the `Castalia` command to run the examples in the Simulations folder.'"
            ],
            "build_commands": ["cd Castalia && ./makemake && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE
            "name": "castalia", "version": "3.2",
            "description": "Simulator for Wireless Sensor Networks (WSN), Body Area Networks (BAN) and generally networks of low-power embedded devices",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/Castalia.html",
                "test_command": "cd castalia-3.2/Castalia/Simulations/BANtest && Castalia -c TMAC",
            },
            "nix_packages": ["python2"],
            "required_projects": {"omnetpp": ["4.1.0"]},
            "download_url": "https://github.com/boulis/Castalia/archive/refs/tags/3.2.tar.gz",
            "patch_commands": [
                "sed -i 's|bin/python|bin/env python2|' Castalia/bin/Castalia",
                "sed -i 's|bin/python|bin/env python2|' Castalia/bin/CastaliaResults",
                "sed -i 's|bin/python|bin/env python2|' Castalia/bin/extractOmnetppINI",
            ],
            "setenv_commands": [
                "export PATH=$PATH:$CASTALIA_ROOT/Castalia/bin",
                "echo 'Hint: Use the `Castalia` command to run the examples in the Simulations folder.'"
            ],
            "build_commands": ["cd Castalia && ./makemake && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE - ok
            "name": "mixim", "version": "2.3",
            "description": "Framework for modeling and simulation of wireless and mobile networks (deprecated in favor of INET)",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/MiXiM.html",
                "test_command": "cd mixim-2.3/examples/bmac && ./run -u Cmdenv",
            },
            "required_projects": {"omnetpp": ["4.6.*", "4.5.*", "4.4.*", "4.3.*", "4.2.*"], "inet": ["2.1.0"]},
            "download_url": "https://github.com/omnetpp-models/mixim/archive/refs/tags/2.3.tar.gz",
            "patch_commands": ["sed -i -E 's|INET_PROJECT_DIR=.*|INET_PROJECT_DIR=$(INET_ROOT)|' Makefile"],
            "setenv_commands": [
                "export PATH=$MIXIM_ROOT/src:$PATH",
                "echo 'Hint: Use `./run` command in the examples and examples-inet subfolders.'"
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE - ok
            # TODO: catalog
            "name": "inetgpl", "version": "1.0",
            "description": "GPL licensed models for INET",
            "metadata": {
                "test_command": "cd inetgpl-1.0/examples/hls && inetgpl -c Experiment1 -u Cmdenv --sim-time-limit=1s",
            },
            "required_projects": {"inet": ["4.5.*"], "omnetpp": ["6.0.*"]},
            "download_commands": ["git clone https://github.com/inet-framework/inet-gpl.git inetgpl-1.0"],
            "setenv_commands": ["source setenv",
                                "echo 'Hint: Use `inetgpl` command in any of the example simulation folders.'"],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE - ok
            # TODO: build tools in toolchain dir
            "name": "rspsim", "version": "6.1.2",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/RSPSIM.html",
                "test_command": "cd rspsim-6.1.2/model && ./model test1.ini -u Cmdenv",
            },
            "required_projects": {"omnetpp": ["6.0.*", "5.7.*"]},
            "download_url": "https://github.com/dreibh/rspsim/archive/refs/tags/rspsim-6.1.2.tar.gz",
            "patch_commands": [
                "sed -i -E 's|<ext_socket.h>|\"ext_socket.h\"|' model/poolelementnode-template.h",
                "sed -i -E 's|<ext_socket.h>|\"ext_socket.h\"|' model/transportaddressblock.c",
            ],
            "build_commands": ["cd model && opp_makemake -f && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "setenv_commands": ["echo 'Hint: Use `./model` command in the model folder. For example: ./model test1.ini'"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE - ok
            "name": "rinasim", "version": "20200903",       # last commit of master branch as of time of writing
            "description": "Recursive InterNetwork Architecture Simulator",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/RINASim.html",
                "test_command": "cd rinasim-20200903 && ./simulate.sh examples/Demos/UseCase1/ -u Cmdenv -G -c Ping",
            },
            "required_projects": {"omnetpp": ["5.2.*"]},
            # "git_url": "https://github.com/kvetak/RINA.git",
            "download_url": "https://github.com/kvetak/RINA/archive/eb6baaf1034319245fa9e4b846a61094445c8d8a.tar.gz",
            "patch_commands": [
                "sed -i -E 's|-O out|-O out -I. -I../src|g' makemakefiles",
            ],
            "setenv_commands": [
                "echo 'Hint: use `./simulate.sh examples/Demos/UseCase1/ -G -c Ping`'",
            ],
            "build_commands": ["make -f makemakefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE - builds and starts, simulations run, but segfault after some time (tested with inet 2.6, 2.4)
            "name": "ieee802154standalone", "version": "20180310",      # last commit of master branch as of time of writing
            "description": "IEEE 802.15.4-2006 simulation model for OMNeT++ / INET",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/IEEE802154INET-Standalone.html",
                "test_command": "cd ieee802154standalone-20180310/simulations && ./run -c StartWPAN-1Node_Starting_WPAN -u Cmdenv",
            },
            "required_projects": {"omnetpp": ["4.6.*"], "inet": ["2.6.0"]},
            # "git_url": "https://github.com/michaelkirsche/IEEE802154INET-Standalone.git",     # master branch
            "download_url": "https://github.com/michaelkirsche/IEEE802154INET-Standalone/archive/28add1dd6a208f9f410f7c5c34631550edd2f371.tar.gz",
            "patch_commands": [
                "sed -i 's|INETDefs.h|base/INETDefs.h|g' src/*/*.h",
                "sed -i 's|ChannelAccess.h|world/radio/ChannelAccess.h|g' src/*/*.h",
                "sed -i 's|InterfaceToken.h|networklayer/common/InterfaceToken.h|g' src/*/*.h src/*/*.h",
                "chmod +x simulations/run",
                "sed -i 's|-n .:../src|-n ..:../src:$\{INET_ROOT\}/src|g' simulations/run",
                "sed -i 's|opp_makemake -f --deep|opp_makemake -f --deep -I.     -I$(INET_ROOT)/src/.     -I$(INET_ROOT)/src/applications     -I$(INET_ROOT)/src/applications/common     -I$(INET_ROOT)/src/applications/dhcp     -I$(INET_ROOT)/src/applications/ethernet     -I$(INET_ROOT)/src/applications/generic     -I$(INET_ROOT)/src/applications/httptools     -I$(INET_ROOT)/src/applications/pingapp     -I$(INET_ROOT)/src/applications/rtpapp     -I$(INET_ROOT)/src/applications/sctpapp     -I$(INET_ROOT)/src/applications/tcpapp     -I$(INET_ROOT)/src/applications/traci     -I$(INET_ROOT)/src/applications/udpapp     -I$(INET_ROOT)/src/applications/voip     -I$(INET_ROOT)/src/base     -I$(INET_ROOT)/src/battery     -I$(INET_ROOT)/src/battery/models     -I$(INET_ROOT)/src/linklayer     -I$(INET_ROOT)/src/linklayer/common     -I$(INET_ROOT)/src/linklayer/configurator     -I$(INET_ROOT)/src/linklayer/contract     -I$(INET_ROOT)/src/linklayer/ethernet     -I$(INET_ROOT)/src/linklayer/ethernet/switch     -I$(INET_ROOT)/src/linklayer/ext     -I$(INET_ROOT)/src/linklayer/idealwireless     -I$(INET_ROOT)/src/linklayer/ieee80211     -I$(INET_ROOT)/src/linklayer/ieee80211/mac     -I$(INET_ROOT)/src/linklayer/ieee80211/mgmt     -I$(INET_ROOT)/src/linklayer/ieee80211/radio     -I$(INET_ROOT)/src/linklayer/ieee80211/radio/errormodel     -I$(INET_ROOT)/src/linklayer/ieee8021d     -I$(INET_ROOT)/src/linklayer/ieee8021d/common     -I$(INET_ROOT)/src/linklayer/ieee8021d/relay     -I$(INET_ROOT)/src/linklayer/ieee8021d/rstp     -I$(INET_ROOT)/src/linklayer/ieee8021d/stp     -I$(INET_ROOT)/src/linklayer/ieee8021d/tester     -I$(INET_ROOT)/src/linklayer/loopback     -I$(INET_ROOT)/src/linklayer/ppp     -I$(INET_ROOT)/src/linklayer/queue     -I$(INET_ROOT)/src/linklayer/radio     -I$(INET_ROOT)/src/linklayer/radio/propagation     -I$(INET_ROOT)/src/mobility     -I$(INET_ROOT)/src/mobility/common     -I$(INET_ROOT)/src/mobility/contract     -I$(INET_ROOT)/src/mobility/group     -I$(INET_ROOT)/src/mobility/single     -I$(INET_ROOT)/src/mobility/static     -I$(INET_ROOT)/src/networklayer     -I$(INET_ROOT)/src/networklayer/arp     -I$(INET_ROOT)/src/networklayer/autorouting     -I$(INET_ROOT)/src/networklayer/autorouting/ipv4     -I$(INET_ROOT)/src/networklayer/autorouting/ipv6     -I$(INET_ROOT)/src/networklayer/bgpv4     -I$(INET_ROOT)/src/networklayer/bgpv4/BGPMessage     -I$(INET_ROOT)/src/networklayer/common     -I$(INET_ROOT)/src/networklayer/contract     -I$(INET_ROOT)/src/networklayer/diffserv     -I$(INET_ROOT)/src/networklayer/icmpv6     -I$(INET_ROOT)/src/networklayer/internetcloud     -I$(INET_ROOT)/src/networklayer/ipv4     -I$(INET_ROOT)/src/networklayer/ipv6     -I$(INET_ROOT)/src/networklayer/ipv6tunneling     -I$(INET_ROOT)/src/networklayer/ldp     -I$(INET_ROOT)/src/networklayer/manetrouting     -I$(INET_ROOT)/src/networklayer/manetrouting/aodv-uu     -I$(INET_ROOT)/src/networklayer/manetrouting/aodv-uu/aodv-uu     -I$(INET_ROOT)/src/networklayer/manetrouting/base     -I$(INET_ROOT)/src/networklayer/manetrouting/batman     -I$(INET_ROOT)/src/networklayer/manetrouting/batman/batmand     -I$(INET_ROOT)/src/networklayer/manetrouting/batman/batmand/orig     -I$(INET_ROOT)/src/networklayer/manetrouting/dsdv     -I$(INET_ROOT)/src/networklayer/manetrouting/dsr     -I$(INET_ROOT)/src/networklayer/manetrouting/dsr/dsr-uu     -I$(INET_ROOT)/src/networklayer/manetrouting/dymo     -I$(INET_ROOT)/src/networklayer/manetrouting/dymo/dymoum     -I$(INET_ROOT)/src/networklayer/manetrouting/dymo_fau     -I$(INET_ROOT)/src/networklayer/manetrouting/olsr     -I$(INET_ROOT)/src/networklayer/mpls     -I$(INET_ROOT)/src/networklayer/ospfv2     -I$(INET_ROOT)/src/networklayer/ospfv2/interface     -I$(INET_ROOT)/src/networklayer/ospfv2/messagehandler     -I$(INET_ROOT)/src/networklayer/ospfv2/neighbor     -I$(INET_ROOT)/src/networklayer/ospfv2/router     -I$(INET_ROOT)/src/networklayer/routing     -I$(INET_ROOT)/src/networklayer/routing/aodv     -I$(INET_ROOT)/src/networklayer/routing/dymo     -I$(INET_ROOT)/src/networklayer/routing/gpsr     -I$(INET_ROOT)/src/networklayer/routing/rip     -I$(INET_ROOT)/src/networklayer/rsvp_te     -I$(INET_ROOT)/src/networklayer/ted     -I$(INET_ROOT)/src/networklayer/xmipv6     -I$(INET_ROOT)/src/nodes     -I$(INET_ROOT)/src/nodes/aodv     -I$(INET_ROOT)/src/nodes/bgp     -I$(INET_ROOT)/src/nodes/dymo     -I$(INET_ROOT)/src/nodes/ethernet     -I$(INET_ROOT)/src/nodes/gpsr     -I$(INET_ROOT)/src/nodes/httptools     -I$(INET_ROOT)/src/nodes/inet     -I$(INET_ROOT)/src/nodes/internetcloud     -I$(INET_ROOT)/src/nodes/ipv6     -I$(INET_ROOT)/src/nodes/mpls     -I$(INET_ROOT)/src/nodes/ospfv2     -I$(INET_ROOT)/src/nodes/rip     -I$(INET_ROOT)/src/nodes/rtp     -I$(INET_ROOT)/src/nodes/wireless     -I$(INET_ROOT)/src/nodes/xmipv6     -I$(INET_ROOT)/src/status     -I$(INET_ROOT)/src/transport     -I$(INET_ROOT)/src/transport/contract     -I$(INET_ROOT)/src/transport/rtp     -I$(INET_ROOT)/src/transport/rtp/profiles     -I$(INET_ROOT)/src/transport/rtp/profiles/avprofile     -I$(INET_ROOT)/src/transport/sctp     -I$(INET_ROOT)/src/transport/tcp     -I$(INET_ROOT)/src/transport/tcp/flavours     -I$(INET_ROOT)/src/transport/tcp/queues     -I$(INET_ROOT)/src/transport/tcp_common     -I$(INET_ROOT)/src/transport/udp     -I$(INET_ROOT)/src/util     -I$(INET_ROOT)/src/util/headerserializers     -I$(INET_ROOT)/src/util/headerserializers/headers     -I$(INET_ROOT)/src/util/headerserializers/ipv4     -I$(INET_ROOT)/src/util/headerserializers/ipv4/headers     -I$(INET_ROOT)/src/util/headerserializers/ipv6     -I$(INET_ROOT)/src/util/headerserializers/ipv6/headers     -I$(INET_ROOT)/src/util/headerserializers/sctp     -I$(INET_ROOT)/src/util/headerserializers/sctp/headers     -I$(INET_ROOT)/src/util/headerserializers/tcp     -I$(INET_ROOT)/src/util/headerserializers/tcp/headers     -I$(INET_ROOT)/src/util/headerserializers/udp     -I$(INET_ROOT)/src/util/headerserializers/udp/headers     -I$(INET_ROOT)/src/util/messageprinters     -I$(INET_ROOT)/src/world     -I$(INET_ROOT)/src/world/annotations     -I$(INET_ROOT)/src/world/httptools     -I$(INET_ROOT)/src/world/obstacles     -I$(INET_ROOT)/src/world/radio     -I$(INET_ROOT)/src/world/scenario     -I$(INET_ROOT)/src/world/traci -o ieee802154inet_standalone -L$(INET_ROOT)/src -linet|' Makefile",
            ],
            "setenv_commands": ["echo 'Hint: use the `./run` command in the simulations folder.'"],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },
        
        {
            # DONE - compiles and runs, but needs weather API access to test
            "name": "os3", "version": "1.0",
            "description": "Open Source Satellite Simulator",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/OS3.html",
            },
            "nix_packages": ["curl", "tcl"],
            "required_projects": {"omnetpp": ["4.2.*"], "inet": ["2.2.0"]},
            "download_url": "https://github.com/inet-framework/os3/archive/refs/tags/v1.0.tar.gz",
            "patch_commands": [
                "sed -i -E 's|-KINET_PROJ=[^ ]+|-KINET_PROJ=$(INET_ROOT)|' Makefile",
                "sed -i 's|$DIR/../../inet|$INET_ROOT|' src/run_cni-os3",
                "sed -i 's|static const double|constexpr static const double|' src/*/*.h",
                "sed -i 's|../src/cni_os3|../src/run_cni-os3|' simulations/run",
            ],
            "setenv_commands": ["export INET_PROJ=$INET_ROOT",
                                "export TCL_LIBRARY=$TCLLIBPATH",
                                "echo 'Hint: use the `./run` command in the simulations folder. For example: `./run Validation/omnetpp.ini`'"],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE - simulations start but segfault after some time
            "name": "oversim", "version": "20190424",       # last commit of master branch as of time of writing
            "description": "Overlay and Peer-to-Peer Network Simulation Framework",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/OverSim.html",
                "test_command": "cd oversim-20190424/simulations && ../src/OverSim omnetpp.ini -c Vast -u Cmdenv --sim-time-limit=10s"
            },
            "required_projects": {"inet": ["3.6.*"], "omnetpp": ["5.4.*"]},
            "download_url": "https://github.com/inet-framework/oversim/archive/refs/tags/v20190424.tar.gz",
            "patch_commands": ["sed -i -E 's|INETDIR = .*|INETDIR = $(INET_ROOT)|' Makefile",
                               "sed -i -E \"s|ned-path = .*|ned-path = $INET_ROOT/src;../src|\" simulations/default.ini",],
            "setenv_commands": ["echo 'Hint: use the `../src/OverSim omnetpp.ini` command in the simulations folder.'"],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "dctrafficgen", "version": "20181016",      # last commit of master branch as of time of writing
            "description": "Data Center Traffic Generator Library",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/DCTrafficGen.html",
                "test_command": "cd dctrafficgen-20181016/dctg_example/simulations && ../src/dctg_example -f omnetpp.ini -n ../../src:../src -u Cmdenv -c FrontEnd --sim-time-limit=10s",
            },
            "nix_packages": ["libxml2"],
            "required_projects": {"omnetpp": ["4.6.*"]},
            # "git_url": "https://github.com/Mellanox/DCTrafficGen.git",    # master branch
            "download_url": "https://github.com/Mellanox/DCTrafficGen/archive/dcfa2b9df46b1681634a340731d2242e97c10abd.tar.gz",
            "patch_commands": [
                "sed -i 's|/usr/include/libxml2/|${pkgs.libxml2.dev}/include/libxml2|g' Makefile dctg_example/Makefile",
            ],
            "setenv_commands": ["echo 'Hint: use the `../src/dctg_example -f omnetpp.ini -n ../../src:../src` command in the dctf_example/simulations folder.'"],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd dctg_example && make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "afdx", "version": "20220904",      # last commit of master branch as of time of writing
            "description": "Avionics Full-Duplex Switched Ethernet model for OMNeT++",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/Afdx.html",
                "test_command": "cd afdx-20220904/afdx/simulations && ./run AutoNetwork.ini -u Cmdenv --sim-time-limit=10s",
            },
            "required_projects": {"omnetpp": ["6.0.*"]},
            # "git_url": "https://github.com/badapplexx/AFDX.git",      # master branch
            "download_url": "https://github.com/badapplexx/AFDX/archive/f6ddd70438e1c9ee885a4adef8d2503a5108ade4.tar.gz",
            "patch_commands": [
                "sed -i 's|.:../src|.:../src:../../queueinglib|g' afdx/simulations/run",
                "sed -i 's|-lqueueinglib|-lqueueinglib$$\\\(D\\\)|g' afdx/Makefile",
            ],
            "build_commands": ["cd queueinglib && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd ../afdx && make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd simulations && chmod +x run && chmod +x run_ancat"],
            "setenv_commands": ["echo 'Hint: in the afdx/simulations folder, use the `./run AutoNetwork.ini` command to run the simulation'"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "quisp", "version": "20230807",     # last commit of master branch as of time of writing
            "description": "Quantum Internet Simulation Package",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/QuISP.html",
                "test_command": "cd quisp-20230807/quisp && ./quisp simulations/two_nodes.ini -c two_node_MIM -u Cmdenv --sim-time-limit=10s",
            },
            "required_projects": {"omnetpp": ["6.0.0"]},
            "git_url": "https://github.com/sfc-aqua/quisp.git",
            "patch_commands": [
                "git reset --hard eddfe7ee80535a624987941653c59da2ce138929",    # the releases need git, so we're using a commit of the master branch
            ],
            "setenv_commands": ["export OMNETPP_IMAGE_PATH=$QUISP_ROOT/quisp/images:$OMNETPP_IMAGE_PATH",
                                "echo 'Hint: in the quisp folder, use the `./quisp` command to run simulations. For example: `./quisp simulations/two_nodes.ini`'"],
            "build_commands": ["make IMAGE_PATH=quisp/images/ -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "cell", "version": "20140729",      # last commit of master branch as of time of writing
            "description": "Cell Communication Signaling Project (biological)",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/CellSignaling.html",
                "test_commands": "cd cell-20140729/src && ./cell -u Cmdenv -c demo-emission -n .. ../networks/demo.ini",
            },
            "required_projects": {"omnetpp": ["4.0.*"]},
            # "git_url": "https://github.com/dhuertas/cell-signaling.git",  # master branch
            # we're using a hash from master because there are no releases
            "download_url": "https://github.com/dhuertas/cell-signaling/archive/3434cc00f7ab7bfc33b4ff94e3a355df8e6947bb.tar.gz",
            "setenv_commands": ["echo 'Hint: in the src folder, use the `./cell` command to run simulations. For example: `./cell -n .. ../networks/demo.ini`'"],
            "build_commands": ["cd src && opp_makemake -f --deep -O out -o cell && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "inetmanet", "version": "4.0.0",
            "description": "Fork of INET 4.x, extending it with experimental features and protocols, mainly for mobile ad hoc networks, many of which are written by Alfonso Ariza",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/INETMANET-4.x.html",
                "test_command": "cd inetmanet-4.0.0/examples/aodv && inet -u Cmdenv -c Static --sim-time-limit=10s",
            },
            "nix_packages": ["python2"],
            "required_projects": {"omnetpp": ["5.4.*"]},
            "download_url": "https://github.com/aarizaq/inetmanet-4.x/archive/refs/tags/v4.0.0.tar.gz",
            "patch_commands": [
                "sed -i.bak 's| python$| python2|' bin/inet_featuretool",
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "setenv_commands": [
                ". setenv -f",
                "echo 'Hint: use the `inet` command in any example simulation folder.'"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "inetmanet", "version": "3.8.2",
            "description": "Fork of INET 3.x, containing additional adhoc routing protocols and other models written by the community",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/INETMANET-3.x.html",
                "test_command": "cd inetmanet-3.8.2/examples/aodv && ./run -u Cmdenv -c Static --sim-time-limit=10s",
            },
            "required_projects": {"omnetpp": ["5.7.*"]},
            "download_url": "https://github.com/aarizaq/inetmanet-3.x/archive/a206218213f96382217a8653ede21f15974c4e70.tar.gz",
            "patch_commands": ["find . -type f -name 'run' -exec chmod +x {} \;"],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "setenv_commands": ["echo 'Hint: use the `./run` command in any example simulation folder.'"],
            "clean_commands": ["make clean"],
        },
        
        {
            # DONE - only builds with just 'make'; TwoSubnets example works, but segfault when running some other simulations
            "name": "oppbsd", "version": "4.0",
            "description": "OppBSD integrates essential parts of the real FreeBSD networking stack into OMNeT++ as a simulation model",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/OppBSD-4.0.html",
                "test_command": "cd oppbsd-4.0/examples/TwoSubnets && ./out/gcc-debug/TwoSubnets -u Cmdenv -c ThreeHosts omnetpp.ini",
            },
            "required_projects": {"omnetpp": ["4.2.*"]},
            "download_url": "https://svn.tm.kit.edu/trac/OppBSD/downloads/2",
            "build_commands": ["make"],
            "setenv_commands": ["echo 'Hint: run example simulations from their folder. For example, in examples/TwoSubnets folder: `./out/gcc-debug/TwoSubnets omnetpp.ini`'"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "rease", "version": "20130819",     # last commit of master branch as of time of writing
            "description": "Realistic Simulation Environments for OMNeT++",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/ReaSE.html",
                "test_command": "cd rease-20130819/Topologies/topo_router && ../../ReaSE/src/rease -n .:../../ReaSE/src:$INET_ROOT/src -u Cmdenv --sim-time-limit=10s",
            },
            "nix_packages": ["libpcap"],
            "required_projects": {"omnetpp": ["4.1.0"], "inet": ["20100323"]},
            # "git_url": "https://github.com/ToGaKIT/ReaSE.git",    # master branch
            # we're using a hash from master because there are no releases
            "download_url": "https://github.com/ToGaKIT/ReaSE/archive/3f5cd1fd4373da44592a2a0ef160c22331f41967.tar.gz",
            "patch_commands": [
                "sed -i 's|INETDIR = ../../INET|INETDIR = $(INET_ROOT)|' ReaSE/Makefile",
                "sed -i 's|-u Cmdenv | |' ReaSE/Makefile",
                "sed -i 's|-L$(INETDIR)/out/gcc-debug/ -lINET|-L$(INETDIR)/src -linet|' ReaSE/Makefile",
            ],
            "setenv_commands": ["echo 'Hint: in the folder of an example simulation (located in Topologies folder), use the `../../ReaSE/src/rease -n .:../../ReaSE/src:$INET_ROOT/src` command to run the simulation'"],
            "build_commands": ["cd ReaSE && make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            # latest master hash; this version has examples, which the latest release version lacks
            "name": "inet_hnrl", "version": "20170217",
            "description": "Fork of INET developed for hybrid networking research, providing new models in both optical and wireless networking areas and their hybrid.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/INET-HNRL.html",
                "test_command": "cd inet_hnrl-20170217/examples/hybridpon/arptest && ./run -u Cmdenv",
            },
            "nix_packages": ["sqlite"],
            "required_projects": {"omnetpp": ["4.2.0"]},
            # "git_url": "https://github.com/kyeongsoo/inet-hnrl.git",
            "download_url": "https://github.com/kyeongsoo/inet-hnrl/archive/857ae37cd233914fd7271584afc4be10bcf75a61.tar.gz",
            "setenv_commands": ["export SQLITE_LIB=${pkgs.sqlite}/lib"],
            "patch_commands": [
                "sed -i 's|INETMANET_PROJ=/media/data/Linux/omnet/inetmanet-inetmanet-00f64c2|INETMANET_PROJ=$(INETMANET_ROOT)|g' Makefile",
                "sed -i 's|-L/usr/local/lib|-L$(SQLITE_LIB)|g' Makefile",
                "sed -i 's|-I/usr/local/include||g' Makefile",
                "sed -i 's|addr.sin_len|// addr.sin_len|' src/linklayer/ext/*.cc",  # ugly hack? this is needed on apple
                "sed -i 's|machine/endian|endian|' src/util/headerserializers/headers/defs.h",
                "sed -i 's|info\\[\\]|info[0]|' src/util/headerserializers/headers/sctp.h",
            ],
            "build_commands": ["make makefiles && make all -j$NIX_BUILD_CORES MODE=$BUILD_MODE CFLAGS='-std=c++14 -fpermissive -fPIC'"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "simcan", "version": "1.2",
            "description": "A simulation platform for modelling and simulating distributes architectures and applications.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/SIMCAN.html",
                "test_command": "cd simcan-1.2/simulations/cliServExample && ../../src/simcan -n ../../src:.:$INET_ROOT/src -u Cmdenv",
            },
            "required_projects": {"omnetpp": ["4.6.*"], "inet": ["2.6.0"]},
            "download_url": "https://github.com/omnetpp-models/archive/releases/download/archive/simcan.tar.gz",
            "setenv_commands": [
                "export INET_HOME=$INET_ROOT",
                "echo 'Hint: in the `simulations/cliServExample` folder, use the `../../src/simcan -n ../../src:.:$INET_ROOT/src` command to run the simulation'",
                ],
            "patch_commands": [     
                "sed -i 's|../../inet|$(INET_ROOT)|g' Makefile",
                "sed -i 's|/out/$$\(CONFIGNAME\)/src|/src|g' Makefile",
                "sed -i 's|-f --deep|-f --deep -o simcan|g' Makefile",
                "sed -i 's|ned-path = ../../../inet/src|#ned-path = ../../../inet/src|g' simulations/cliServExample/omnetpp.ini",
                "sed -i 's|package SIMCAN|// package SIMCAN|g' simulations/cliServExample/scenario.ned",
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "solarleach", "version": "1.01",
            "description": "A simulation of LEACH (Low-Energy Adaptive Clustering Hierarchy) cluster-based protocol for sensor networks with an extension to make it solar-aware.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/SolarLEACH.html",
                "test_command": "cd solarleach-1.01/leachDist && ./leachDist -u Cmdenv -L$OMNETPP_ROOT/src/cmdenv/libcmdenv -c Run1 -r 1 --sim-time-limit=10s",
            },
            "required_projects": {"omnetpp": ["3.3.*"]},
            "download_url": "https://github.com/omnetpp-models/archive/releases/download/archive/SolarLEACH-1.01.tgz",
            "setenv_commands": ["echo 'Hint: in the `leachDist` folder, use the `./runall.sh` command to run the simulations. In the `leachFarBS` folder, use the `./leachFarBS` command'",],
            "patch_commands": [
                "tr -d '\r' < leachDist/runall.sh > leachDist/runall_fixed.sh",
                "mv leachDist/runall_fixed.sh leachDist/runall.sh",
                "chmod +x leachDist/runall.sh",
                "sed -i 's|BS::||g' leachFarBS/bs.h",
            ],
            "build_commands": ["cd leachDist && opp_makemake -f -N && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd ../leachFarBS && opp_makemake -f -N && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "stochasticbattery", "version": "20170224",     # last commit of master branch as of time of writing
            "description": "An OMNeT++ simulation for stochastic battery behavior. It implements the Stochastic Battery Model by Chiasserini and Rao.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/StochasticBattery.html",
                "test_command": "cd stochasticbattery-20170224 && ./stochasticbattery -u Cmdenv",
            },
            "required_projects": {"omnetpp": ["5.0.*"]},    # TODO try *
            # "git_url": "https://github.com/brandte/stochastic_battery.git",
            "download_url": "https://github.com/brandte/stochastic_battery/archive/dd999402a0aa7c88a9f78a3ca23f193b8250a925.tar.gz",
            "patch_commands": [
                "rm -r out *.exe",
            ],
            "setenv_commands": ["echo 'Hint: use the `./stochasticbattery` command to run the simulation.'",],
            "build_commands": ["make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE - should this be a library?
            # TODO: how to test this?
            "name": "chaosmanager", "version": "20221210",      # last commit of master branch as of time of writing
            "description": "An automated hard faul injection tool inspired by Chaos Engineering principles for MANETs. This tool has been tested extensively on LEACH for OMNETPP.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/WSN-Chaos-Manager.html",
            },
            "required_projects": {"omnetpp": ["5.6.2"], "inet": ["4.2.5"]},
            # "git_url": "https://github.com/Agr-IoT/WSN-Chaos-Manager.git",
            "download_url": "https://github.com/Agr-IoT/WSN-Chaos-Manager/archive/07272355eb0e8d5fa6216b9dcfb07fcac0a5115b.tar.gz",
            "setenv_commands": [
                "echo 'Hint: use the `./chaosmanager` command to run simulations. Note that this project does not contain any example simulations.'",
                # ./chaosmanager $INET_ROOT/examples/aodv/omnetpp.ini -n $INET_ROOT/src:$INET_ROOT/examples -> for testing (or -h -> to load so)
            ],
            "patch_commands": [
                "sed -i 's|#include \"inet/common/chaos/ChaosEvent_m.h\"|#include \"ChaosEvent_m.h\"|g' ChaosManager.cc",
            ],
            "build_commands": ["opp_makemake -f --deep -o chaosmanager -O out -KINET_PROJ=$INET_ROOT -DINET_IMPORT -I. -I$INET_ROOT/src -L$INET_ROOT/src -lINET\$D && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "ops_allinone", "version": "20230331",      # last commit of master branch as of time of writing
            "description": "Opportunistic Protocol Simulator. This version downloads its own copy of INET, and does not use one installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/OPS.html",
                "test_command": "cd ops_allinone-20230331/simulations && ../ops-simu omnetpp-ops.ini -n ../src:.:../modules/inet/src -u Cmdenv -c Messenger-Epidemic-SWIM --sim-time-limit=10s",
            },
            "nix_packages": ["autoconf", "automake", "libtool"],
            "required_projects": {"omnetpp": ["5.4.*"]},
            # "git_url": "https://github.com/ComNets-Bremen/OPS.git",
            "download_url": "https://github.com/ComNets-Bremen/OPS/archive/57ecc379631eec4bb640b022391f2cf808ff09f4.tar.gz",
            "patch_commands": [
                "sed -i 's|-j 1|-j$NIX_BUILD_CORES|g' bootstrap.sh",
            ],
            "setenv_commands": ["echo 'Hint: in the `simulations` folder, use the `../ops-simu omnetpp-ops.ini -n ../src:.:../modules/inet/src` command to run the example simulation.'"], 
            "build_commands": ["./bootstrap.sh && ./ops-makefile-setup.sh && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE
            # TEST: ./opslite needs to be run from simulation folder
            "name": "opslite", "version": "20190624",       # last commit of master branch as of time of writing
            "description": "A Lightweight Opportunistic Networking Simulator in OMNeT++",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/OPSLite.html",
                "test_command": "cd opslite-20190624/simulations && ../src/opslite omnetpp.ini -n .:../src:$INET_ROOT/src -u Cmdenv --sim-time-limit=10s",
            },
            "required_projects": {"omnetpp": ["5.4.1"], "inet": ["4.0.0"]},
            # "git_url": "https://github.com/ComNets-Bremen/OPSLite.git",
            "download_url": "https://github.com/ComNets-Bremen/OPSLite/archive/df67c31eff6d20f91affd931638a058001d81e98.tar.gz",
            "setenv_commands": ["export INET_PROJ=$INET_ROOT",
                                "echo 'Hint: in the `simulations` folder, use the `../src/opslite omnetpp.ini -n .:../src:$INET_ROOT/src` command to run the example simulation.'"],
            "build_commands": ["cd src && opp_makemake -f --deep -o opslite -KINET_PROJ=$INET_PROJ -DINET_IMPORT -I$INET_PROJ/src -L$INET_PROJ/src -lINET\$D && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },
        
        {
            # DONE
            # this doesnt contain examples for swim
            "name": "swim_allinone", "version": "20180221",     # last commit of master branch as of time of writing
            "description": "Small Worlds in Motion (SWIM) mobility model. This version downloads its own copy of INET, and does not use ones installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/SWIMMobility.html",
                "test_command": "cd swim_allinone-20180221/examples/aodv && ./run -u Cmdenv --sim-time-limit=10s",
            },
            "required_projects": {"omnetpp": ["5.7.*"]},
            "download_commands": [
                "mkdir swim_allinone-20180221",
                "cd swim_allinone-20180221",
                "curl -L -o inet-3.8.3-src.tgz https://github.com/inet-framework/inet/releases/download/v3.8.3/inet-3.8.3-src.tgz --progress-bar",
                "tar -xzf inet-3.8.3-src.tgz --strip=1",
                "rm inet-3.8.3-src.tgz",
            ],
            "patch_commands": [
                "touch tutorials/package.ned",
                "sed -i.bak 's|info\\[\\]|info[0]|' src/inet/common/serializer/sctp/headers/sctphdr.h",
                "for f in $(grep -Rls 'defined(linux)'); do sed -i.bak 's|defined(linux)|defined(__linux__)|' $f; done",
                "for f in $(grep -Rl 'INT64_PRINTF_FORMAT'); do sed -i.bak 's|INT64_PRINTF_FORMAT|\"l\"|' $f; done",
                "echo 'Patching INET with SWIM....'",
                "mkdir swim-src",
                "cd swim-src",
                # "git clone https://github.com/ComNets-Bremen/SWIMMobility.git swim-src",      # master branch
                "curl -L -o master.tar.gz https://github.com/ComNets-Bremen/SWIMMobility/archive/refs/heads/master.tar.gz --progress-bar",
                "tar -xzf master.tar.gz --strip=1",
                "rm master.tar.gz",
                "cp SWIMMobility.* ../src/inet/mobility/single",
                "echo 'Patching done.'",
            ],
            "setenv_commands": [
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "tsch_allinone", "version": "6tisch_paper",
            "description": "6TiSCH-CLX ACM TOIT paper exact version. This version downloads its own copy of INET, and does not use ones installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/ComNetsHH-TSCH.html",
                "test_command": "cd tsch_allinone-6tisch_paper/src && ./tsch ../simulations/wireless/waic/omnetpp.ini -n .:../rpl/src:../rpl/inet/src:../simulations -c HPQ -r 0 -u Cmdenv --sim-time-limit=10s",
            },
            "nix_packages": ["rsync"],
            "required_projects": {"omnetpp": ["5.6.*"]},
            "download_commands": [
                "mkdir tsch_allinone-6tisch_paper",
                "cd tsch_allinone-6tisch_paper",
                "mkdir rpl && cd rpl",
                "curl -L -o rpl.tar.gz https://github.com/ComNetsHH/omnetpp-rpl/archive/792e6473145d482894f396fea146df9c27a0c758.tar.gz --progress-bar",
                "tar -xzf rpl.tar.gz --strip=1",
                "rm rpl.tar.gz",
                "mv inet inet_replacement_files",
                "curl -L -o inet-4.2.5-src.tgz https://github.com/inet-framework/inet/releases/download/v4.2.5/inet-4.2.5-src.tgz --progress-bar",
                "tar -xzf inet-4.2.5-src.tgz",
                "mv -f inet4 inet",
                "rm inet-4.2.5-src.tgz",
                "cd ..",
                "curl -L -o acm-toit-6tisch-clx.tar.gz https://github.com/ComNetsHH/omnetpp-tsch/archive/refs/tags/acm-toit-6tisch-clx.tar.gz --progress-bar",
                "tar -xzf acm-toit-6tisch-clx.tar.gz --strip=1",
                "rm acm-toit-6tisch-clx.tar.gz",
            ],
            "setenv_commands": [
                "echo 'Hint: use the `./tsch ../simulations/wireless/waic/omnetpp.ini -n .:../rpl/src:../rpl/inet/src:../simulations` command in the src folder to run the simulations. (note: in debug mode, use the `tsch_dbg` executable).'",
            ],
            "patch_commands": [
                """cd rpl && rsync -abuvP --include="*/" --include="*.cc" --include="*.h" --include="*.ned"  --exclude="*"  inet_replacement_files/  inet/src/inet/ \nfind inet/src/inet -name "*.*~" -delete""",
            ],
            "build_commands": [
                "cd rpl/inet", 
                "make makefiles",
                "make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
                "cd ../src",
                "opp_makemake -f --deep --make-so -o rpl -KINET_PROJ=../inet -I../inet/src -L../inet/src -lINET\$D", 
                "make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
                "cd ../../src",
                "opp_makemake -f --deep -o tsch -KINET_PROJ=../rpl/inet -I../rpl/inet/src -L../rpl/inet/src -lINET\$D -I../rpl/src -L../rpl/src -lrpl\$D -I. -Iapplications -IImobility -Icommon -Ilinklayer -Iradio",
                "make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
            ],
            "clean_commands": ["make clean && cd rpl/src && make clean && cd ../inet && make clean"],
        },

        {
            # DONE
            # TODO intended to be used as part of inet - this should be its own project
            "name": "can_allinone", "version": "0.1.0",
            "description": "Controller Area Network. This version downloads its own copy of INET, and does not use ones installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/CAN.html",
                "test_command": "cd can_allinone-0.1.0/examples/can/messagerouter1 && ./run -u Cmdenv -c CanMessageRouter --sim-time-limit=10s",
            },
            "required_projects": {"omnetpp": ["4.6.*"]},    # TODO: 4.6.0 to option --with-recommended-deps?
            "download_commands": [
                "mkdir can_allinone-0.1.0",
                "cd can_allinone-0.1.0",
                "curl -L -o inet-2.5.0-src.tgz https://github.com/inet-framework/inet/releases/download/v2.5.0/inet-2.5.0-src.tgz --progress-bar",
                "tar -xvzf inet-2.5.0-src.tgz --strip=1",
                "rm inet-2.5.0-src.tgz",
                "curl -L -o v0.1.0.tar.gz https://github.com/YutakaMatsubara/can-for-omnet/archive/refs/tags/v0.1.0.tar.gz --progress-bar",
                "tar -xzf v0.1.0.tar.gz",
                "mv can-for-omnet-0.1.0 can-src",
                "rm v0.1.0.tar.gz",
            ],
            "patch_commands": [
                "cp -r can-src/src/* src",
                "cp -r can-src/examples/* examples",
                "rm -r can-src",
                "sed -i.bak 's|info\\[\\]|info[0]|' src/util/headerserializers/sctp/headers/sctp.h",
                "for f in $(grep -Rls 'defined(linux)'); do sed -i.bak 's|defined(linux)|defined(__linux__)|' $f; done",
                "sed -i.bak 's/if (vector_cost<=0)/if (vector_cost == NULL)/' src/networklayer/manetrouting/dsr/dsr-uu/path-cache.cc",
                "find . -type f -name 'run' -exec chmod +x {} \;"
            ],
            "setenv_commands": ["echo 'Hint: use the `./run` command in any example simulation folder, located in `examples/can`.'"],
            "build_commands": ["make makefiles && make clean && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
            # TODO: this doesnt work
            # "options": {
            #     "with-recommended-deps": {
            #         "option_description": "Use recommended versions of dependent projects (omnetpp-4.6.0)",
            #         "option_category": "version",
            #         "option_is_default": False,
            #         "required_projects": {"omnetpp": ["4.6.0"]},
            #     },
            # }
        },

        	{
            # DONE
            # TODO no catalog entry yet
            "name": "lora_icn", "version": "paper",
            "nix_packages": ["docker"],
            "details": "This project contains code and documentation to reproduce experimental results of the paper 'Long-Range ICN for the IoT: Exploring a LoRa System Design' published in Proc. of the IFIP Networking Conference 2022.",
            # "metadata": {
            #     "catalog_url": "",
            # },
            "download_commands": [
                "git clone https://github.com/inetrg/IFIP-Networking-LoRa-ICN-2022.git lora_icn-paper",
                "cd lora_icn-paper",
                "git reset --hard c45a69b23f0fce467242b4c0b71b125bc450a0f0",
                "git submodule update --init --recursive",
            ],
            "setenv_commands": [
                """echo 'Hint: To generate all simulations, run the `docker run --rm -it -v "$(pwd)/data:/root/data" inetrg/ccnsim_dsme` command. \
                Note that this may take hours to execute all configurations. The collected data will be stored under data. Note that you need to use `sudo` to delete the `data` folder.\n \
                    Link to the paper: https://arxiv.org/pdf/2204.11040.pdf'""",
            ],
            "build_commands": [
                "docker build -t inetrg/ccnsim_dsme .",
            ],
            "clean_commands": ["make clean"],
        },
        
        {
            # DONE
            "name": "seapp", "version": "20191230",
            "description": "SEA++ - Simulating Security Attacks",
            "details": "SEA++ is an attack simulator which helps the user to quantitatively evaluate the impact of security attacks. SEA++ is compatible with both traditional and SDN architectures.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/SEA++.html",
            },
            "nix_packages": ["python2", "glibmm", "libxml2", "libsigcxx", "libxmlxx", "glib"],
            "required_projects": {"omnetpp": ["4.6.x", "4.6.1", "4.6.0"]},
            "download_url": "https://github.com/seapp/seapp_stable/archive/75bde5636917610b04e0dcaec21fbd3438063b79.tar.gz",    # latest master hash as of time of writing
            "setenv_commands": [
                                "export GLIBMM_ROOT=${pkgs.glibmm}",
                                "export GLIBMM_DEV_ROOT=${pkgs.glibmm.dev}",
                                "export LIBXMLXX_ROOT=${pkgs.libxmlxx}",
                                "export LIBSIGCXX_ROOT=${pkgs.libsigcxx}",
                                "export GLIB_ROOT=${pkgs.glib.out}",
                                "export GLIB_DEV_ROOT=${pkgs.glib.dev}",
                                "echo 'Hint: use the `./run` scripts in the example simulation folders, in examples/seapp.'"
            ],
            "patch_commands": [
                "sed -i 's|-I/usr/include/libxml2|-I${pkgs.libxml2.dev}/include/libxml2 |g' Makefile",
                "sed -i 's|-I/usr/include/libxml++-2.6|-I${pkgs.libxmlxx}/include/libxml++-2.6 -I${pkgs.libxmlxx}/lib/libxml++-2.6/include |g' Makefile",
                "sed -i 's|-I/usr/include/glibmm-2.4|-I${pkgs.glibmm.dev}/lib/glibmm-2.4/include -I${pkgs.glibmm.dev}/lib/glibmm-2.4 -I${pkgs.glibmm.dev}/include/glibmm-2.4 -I${pkgs.glibmm}/lib/glibmm-2.4/include -I${pkgs.glibmm}/lib/glibmm-2.4 -I${pkgs.glibmm}/include/glibmm-2.4 |g' Makefile",
                "sed -i 's|-I/usr/include/sigc++-2.0|-I${pkgs.libsigcxx}/include/sigc++-2.0 |g' Makefile",
                "sed -i 's|-I/usr/include/glib-2.0|-I${pkgs.glib.dev}/include/glib-2.0 -I${pkgs.glib.dev}/include/glib-2.0/include -I${pkgs.glib.out}/include/glib-2.0 -I${pkgs.glib.out}/lib/glib-2.0/include |g' Makefile",
                "sed -i 's|-I/usr/lib/x86_64-linux-gnu/libxml++-2.6/include|-L$(LIBXMLXX_ROOT)/lib |g' Makefile",
                "sed -i 's|-I/usr/lib/x86_64-linux-gnu/glibmm-2.4/include |-L$(GLIBMM_ROOT)/lib |g' Makefile",
                "sed -i 's|-I/usr/lib/x86_64-linux-gnu/sigc++-2.0/include |-L$(LIBSIGCXX_ROOT)/lib |g' Makefile",
                "sed -i 's|-I/usr/lib/x86_64-linux-gnu/glib-2.0/include|-L$(GLIB_ROOT)/lib |g' Makefile",
                "sed -i.bak 's/if (vector_cost<=0)/if (vector_cost == NULL)/' src/networklayer/manetrouting/dsr/dsr-uu/path-cache.cc",
            ],
            "build_commands": ["make makefiles && make CFLAGS+='-Wno-pointer-compare' CXXFLAGS+='-Wno-pointer-compare' -j$NIX_BUILD_CORES MODE=$BUILD_MODE CFLAGS='-fpermissive -fPIC'"],
            "clean_commands": ["make clean"],
        },
        
        {
            # DONE
            "name": "icancloud", "version": "1.0",
            "description": "Cloud Computing Systems",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/iCanCloud.html",
            },
            "required_projects": {"omnetpp": ["4.6.*"], "inet": ["2.5.0"]},
            "download_url": "http://sourceforge.net/projects/icancloudsim/files/iCanCloud_v1.0_20150216.tgz/download",
            "patch_commands": [
                "sed -i 's|unsigned int requestSize|int requestSize|g' src/Base/Messages/SMS/SMS_MainMemory.cc",
                "sed -i 's|ned-path|#net-path|g' simulations/*/omnetpp.ini",
                "sed -i 's|$DIR/../iCanCloud|$DIR/iCanCloud|g' src/run_iCanCloud",
                "sed -i 's|/simulations|/simulations:$INET_ROOT/src|g' src/run_iCanCloud",
            ],
            "setenv_commands": ["echo 'Hint: use the `./run` command in an example simulation folder.'"],
            "build_commands": ["cd src && opp_makemake -f --deep --make-so -O out -o iCanCloud -I$INET_ROOT/src/linklayer/ieee80211/radio -I$INET_ROOT/src/networklayer/routing/aodv -I$INET_ROOT/src/networklayer/common -I$INET_ROOT/src -I$INET_ROOT/src/networklayer/icmpv6 -I$INET_ROOT/src/world/obstacles -I$INET_ROOT/src/networklayer/xmipv6 -I$INET_ROOT/src/networklayer/contract -I$INET_ROOT/src/networklayer/autorouting/ipv4 -I$INET_ROOT/src/util -I$INET_ROOT/src/linklayer/common -I$INET_ROOT/src/transport/contract -I$INET_ROOT/src/status -I$INET_ROOT/src/linklayer/radio/propagation -I$INET_ROOT/src/linklayer/ieee80211/radio/errormodel -I$INET_ROOT/src/linklayer/radio -I$INET_ROOT/src/util/headerserializers/tcp -I$INET_ROOT/src/networklayer/ipv4 -I$INET_ROOT/src/mobility/contract -I$INET_ROOT/src/util/headerserializers/ipv4 -I$INET_ROOT/src/base -I$INET_ROOT/src/util/headerserializers -I$INET_ROOT/src/world/radio -I$INET_ROOT/src/linklayer/ieee80211/mac -I$INET_ROOT/src/networklayer/ipv6 -I$INET_ROOT/src/transport/sctp -I$INET_ROOT/src/util/headerserializers/udp -I$INET_ROOT/src/networklayer/ipv6tunneling -I$INET_ROOT/src/util/headerserializers/ipv6 -I$INET_ROOT/src/applications/pingapp -I$INET_ROOT/src/battery/models -I$INET_ROOT/src/linklayer/contract -I$INET_ROOT/src/util/headerserializers/sctp -I$INET_ROOT/src/transport/tcp_common -I$INET_ROOT/src/networklayer/arp -I$INET_ROOT/src/transport/udp -L$INET_ROOT/src -lz -linet -DINET_IMPORT -KINET_PROJ=$INET_ROOT && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },
        
        {
            # DONE
            # TODO: enable emulation by default in inet, and use nix inet version?
            "name": "sedencontroller_allinone", "version": "20230305",      # latest commit of master branch as of time of writing
            "description": "sEden Controller",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/SDNController.html",
            },
            "nix_packages": ["libmysqlconnectorcpp", "mysql", "libpcap", "wireshark-qt"],
            "required_projects": {"omnetpp": ["5.4.*"]},
            "download_commands": [
                "mkdir sedencontroller_allinone-20230305",
                "cd sedencontroller_allinone-20230305",
                "curl -L -o src.tar.gz --progress-bar https://github.com/swiru95/sEden_Controller/archive/50d4e9894de018b5c20579b99f423e88677c3c59.tar.gz",
                "tar -xzf src.tar.gz --strip=1",
                "rm src.tar.gz",
                "curl -L -o inet.src.tar.gz --progress-bar https://github.com/inet-framework/inet/releases/download/v4.0.0/inet-4.0.0-src.tgz",
                "tar -xzf inet.src.tar.gz",
                "mv inet4 inet",
                "rm inet.src.tar.gz",
            ],
            "patch_commands": [
                "cd inet",
                "touch tutorials/package.ned",
                "for f in $(grep -Rls 'defined(linux)'); do sed -i.bak 's|defined(linux)|defined(__linux__)|' $f; done",
            ],
            "setenv_commands": [
                "export MYSQL_ROOT=${pkgs.libmysqlconnectorcpp}/include/jdbc",
                "export MYSQL_LIB=${pkgs.libmysqlconnectorcpp}/lib",
                "export INET_ROOT=$SEDENCONTROLLER_ALLINONE_ROOT/inet",
                "echo '\nNOTE: After installing, use setcap to set the application permissions:'",
                "echo 'sudo setcap cap_net_raw,cap_net_admin=eip sdncontroller/src/sdncontroller'",
                "echo 'sudo setcap cap_net_raw,cap_net_admin=eip sdncontroller/src/sdncontroller_dbg\n'",
                "echo 'To enable Wireshark interface capture permissions, run the `sudo setcap cap_net_raw,cap_net_admin=ep $(which dumpcap)` command.'",
                "echo 'If Wireshark still complains about permissions, run the following command: `sudo chown root $(which dumpcap) && sudo chmod u+s $(which dumpcap)`.\n'",
                "echo 'Hint: In the `sdncontroller/simulations` folder, use the `../src/sdncontroller omnetpp.ini -n ../src:$INET_ROOT/src:.` command to run the example simulation.'",
            ],
            "build_commands": ["cd inet && opp_featuretool enable ExternalInterface && make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd ../sdncontroller/src && opp_makemake -f --deep -KINET_PROJ=$INET_ROOT -DINET_IMPORT -I$INET_ROOT/src -L$INET_ROOT/src -lINET\$D -I$MYSQL_ROOT -I$MYSQL_LIB -lmysqlcppconn -L$MYSQL_LIB && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean && cd inet && make clean"],
        },
        
        {
            # DONE
            "name": "gradys", "version": "0.5",
            "description": "A simulation framework developed for the GrADyS (Ground-and-Air Dynamic sensors networkS) project.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/SDNController.html",
            },
            "required_projects": {"omnetpp": ["5.6.*"], "inet": ["4.2.5"]},
            "patch_commands": [
                "sed -i 's|INET_PROJ=../inet|#INET_PROJ=../inet|g' Makefile",
            ],
            "download_url": "https://github.com/brunoolivieri/gradys-simulations/archive/refs/tags/v0.5.tar.gz",
            "setenv_commands": [
                "export INET_PROJ=$INET_ROOT",
                "echo 'Hint: To run the example simulation, use the `./gradys-simulations mobilityDrones-omnetpp.ini -n .:$INET_ROOT/src` command.'",
            ],
            "build_commands": [
                "make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
            ],
            "clean_commands": ["make clean"],
        },
        
        {
            # DONE
            "name": "omnet_tdma", "version": "1.0.2",
            "description": "An abstract TDMA MAC protocol for the INET Framework",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/ComNetsHH-TDMA.html",
            },
            "required_projects": {"omnetpp": ["5.6.*"], "inet": ["4.2.5"]},
            "download_url": "https://github.com/ComNetsHH/omnet-tdma/archive/refs/tags/v1.0.2.tar.gz",
            "setenv_commands": [
                "rm -r inet",
                "ln -s $INET_ROOT inet",
                "export INET_PROJ=$INET_ROOT",
                "echo 'Hint: To run the example simulation, use the `./tdma ../simulations/omnetpp.ini -n .:../simulations:$INET_ROOT/src` command in the tdma/src folder.'",
            ],
            "build_commands": [
                "cd tdma && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
            ],
            "clean_commands": ["make clean"],
        },

        {
            # DONE - some example simulations crash after some time though;
            "name": "opencv2x_veins", "version": "1.4.1",
            "description": "Open Cellular Vehicle To Everything (V2X) Mode 4",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/OpenCV2X.html",
            },
            "required_projects": {"omnetpp": ["5.5.1"], "inet": ["3.6.6"], "veins": ["5.2"]},
            "details": "An open source implementation of the 3GPP standard CV2X (Rel 14) Mode 4. It is based on an extended version of the SimuLTE OMNeT++ simulator which enables LTE network simulations.",
            "download_url": "https://github.com/brianmc95/simulte/archive/refs/tags/v1.4.1.tar.gz",
            "patch_commands": [
                "find . -type f -name 'run' -exec chmod +x {} \;",
                "sed -i 's|../../inet|$(INET_ROOT)|g' Makefile",
                "sed -i 's|-lINET|-lINET$$\\\(D\\\)|g' Makefile",
                "sed -i 's|\$DIR/../../inet|$INET_ROOT|g' src/run_lte",
                "sed -i 's|INET_DIR\"|INET_DIR:$VEINS_ROOT/src/veins:$VEINS_ROOT/subprojects/veins_inet3/src/veins_inet\"|g' src/run_lte",
                "sed -i 's|-l $INET_DIR/INET|-l $INET_DIR/INET -l $VEINS_ROOT/subprojects/veins_inet3/src/libveins_inet.so|g' src/run_lte",
                """find . -name '*.launchd.xml' -exec bash -c 'sed -i "s|UPDATE-WITH-YOUR-PATH|$(pwd)/{}|g" {}' \;""",
                "sed -i 's|/highway.launchd.xml||g' simulations/*/*/*/*.launchd.xml",
                "sed -i 's|/./|/|g' simulations/*/*/*/*.launchd.xml",
            ],
            "setenv_commands": [
                "export INET_PROJ=$INET_ROOT",
                'export OMNETPP_IMAGE_PATH="$OMNETPP_IMAGE_PATH:$VEINS_ROOT/images:$OPENCV2X_VEINS_ALLINONE_ROOT/images:$INET_ROOT/images:$VEINS_ROOT/subprojects/veins_inet3/images"',
                "export SUMO_ROOT=${pkgs.sumo}",
                "echo 'Hint: To run an example simulation, use the `$VEINS_ROOT/sumo-launchd.py &` to start the TraCI server, then in folder of the example simulation, use the `./run` command.'",
            ],
            "build_commands": [
                "opp_featuretool enable SimuLTE_Cars && make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"
            ],
            "clean_commands": ["make clean"],
        },
        
        {
            # DONE
            # TODO: LRE_Test.py doesnt work
            "name": "lre_omnet", "version": "1.0.1",
            "required_projects": {"omnetpp": ["5.4.*"], "inet": ["3.6.8"]},
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/LRE-OMNeT.html",
            },
            "nix_packages": ["python311", "python311Packages.boost.dev", "boost", "gcc"],
            "description": "Integration of the Limited Relative Error algorithm into OMNeT++",
            "details": "This project provides an integration of the Limited Relative Error (LRE) \
                algorithm into the OMNeT++ simulator. The LRE algorithm itself comes as a stand-alone implementation. \
                (The LRE algorithm is an alternative statistical method for data evaluation. \
                LRE continuously requests more samples until it deems the evaluation confident enough.) \
                This version of the network model contains the configuration that produces data as \
                contained in the paper for the OMNeT++ Summit 2018.",
            "git_url": "https://github.com/ComNetsHH/LRE-OMNeT.git",
            "setenv_commands": [
                "echo 'Hint: To run the example simulation, use the `opp_run -l lre_omnet -n .:$INET_ROOT/src` command.'",
            ],
            "build_commands": [
                "git reset --hard 683441ac7d72f7c9426120ac0f91bc0c575e4204",    # latest commit of master branch as of time of writing
                "git submodule init",
                "git submodule update",
                "sed -i 's|-I/usr/include/python3.6m|-I${pkgs.python311}/include/python3.11 -L${pkgs.python311}/lib -L${pkgs.python311Packages.boost.out}/lib|g' lre-src/Makefile",
                "sed -i 's|-lpython3.6m |-lpython3.11 |g' lre-src/Makefile",
                "sed -i 's|-lboost_python3 |-lboost_python311 |g' lre-src/Makefile",
                "cd lre-src",
                "make LRE3.6 -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
                "cd .. && opp_makemake --make-so -f --deep -O out -o lre_omnet -KINET_PROJ=$INET_ROOT -I. -I$INET_ROOT/src -L$INET_ROOT/src -lINET -Xlre-src/main",
                "make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"
            ],
            "clean_commands": ["make clean"],
        },

        {
            # DONE - no example simulation
            # TODO: metadata catalog url
            "name": "wifidirect_allinone", "version": "3.4",
            "required_projects": {"omnetpp": ["5.1.*"]},
            "download_url": "https://github.com/ashahin1/inet/archive/refs/tags/v3.4.0.tar.gz",
            "setenv_commands": [
            ],
            "patch_commands": [
                "sed -i.bak 's|cResultFilterDescriptor|cResultFilterType|' src/inet/common/figures/DelegateSignalConfigurator.cc"
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },
    ]
