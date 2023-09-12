def get_project_descriptions():
    return [
        {
            # DONE - ok
            "name": "fico4omnet", "version": "20210113",        # last commit of master branch as of time of writing
            "description": "Fieldbus Communication (CAN and FlexRay)",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/FiCo4OMNeT.html",
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
            },
            "required_projects": {"omnetpp": ["5.1"]},
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
            },
            "required_projects": {"omnetpp": ["6.0"], "inet": ["4.4.0"]},
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
            },
            "required_projects": {"omnetpp": ["5.5"], "inet": ["3.6.6"]},
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
            },
            "required_projects": {"omnetpp": ["6.0"]},
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
            },
            "required_projects": {"omnetpp": ["5.5"]},
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
            },
            "required_projects": {"omnetpp": ["5.2"], "inet": ["3.6.3"]},
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
            "build_commands": ["cd IEEE8021AS/src && opp_makemake -f --deep -KINET_PROJ=$INET_PROJ -DINET_IMPORT -I$INET_PROJ/src -L$INET_PROJ/src -lINET && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE - ok
            # when closing qtenv:
            # (omnetpp::cChannel)channel: Fatal: Direct deletion of a channel object is illegal, use cGate's disconnect() or reconnectWith() instead; ABORTING -- during network cleanup
            # needs another omnetpp version?
            "name": "openflow", "version": "20220615",      # last commit of master branch as of time of writing
            "description": "OpenFlow Extension for INET Framework",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/Openflow.html",
            },
            "required_projects": {"omnetpp": ["6.0"], "inet": ["4.4.0"]},
            # git_url": "https://github.com/inet-framework/openflow.git",
            # there are no releases, so we use a commit from the master branch
            "download_url": "https://github.com/inet-framework/openflow/archive/9f8e9b88d8aa5d4310078f725227ccbd21f26e9c.tar.gz",
            "patch_commands": [
                "sed -i -E 's|-KINET_PROJ=[^ ]+|-KINET_PROJ=$(INET_ROOT) -o openflow|' Makefile",
                "sed -i 's|$DIR/../../inet|$INET_ROOT|' src/run_openflow",
                "sed -i 's|opp_run_dbg|opp_run|' src/run_openflow",
                "sed -i 's|scenarios:$DIR|scenarios:$DIR -i $OPENFLOW_ROOT/images|' src/run_openflow",
            ],
            "setenv_commands": [
                "export INET_PROJ=$INET_ROOT",
                "export PATH=$PATH:$OPENFLOW_ROOT/src",
                "echo 'Hint: use the `run_openflow` command to run the examples in the scenarios folder.'"
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE - ok
            "name": "nesting", "version": "0.9.1",
            "description": "Network Simulator for Time-Sensitive Networking (TSN)",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/NeSTiNg.html",
            },
            "required_projects": {"omnetpp": ["5.4.1"], "inet": ["4.1.0"]},
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
            },
            "nix_packages": ["python2"],
            "required_projects": {"omnetpp": ["4.1"]},
            # "git_url": "https://github.com/boulis/Castalia.git",  # for master branch version
            # "required_projects": {"omnetpp": ["4.4"]},
            "download_url": "https://github.com/boulis/Castalia/archive/refs/tags/3.3.tar.gz",
            "patch_commands": [
                "sed -i 's|bin/python|bin/env python2|' Castalia/bin/Castalia",
                "sed -i 's|bin/python|bin/env python2|' Castalia/bin/CastaliaResults",
                "sed -i 's|bin/python|bin/env python2|' Castalia/bin/extractOmnetppINI",
                """sed -i 's|traceFile.open(par("traceFile"));|traceFile.open((const char *)par("traceFile"));|' Castalia/src/wirelessChannel/traceChannel/TraceChannel.cc""",
                # "sed -i 's|bin/python|bin/env python2|' Castalia/bin/CastaliaPlot",   # for master branch version
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
            "description": "MiXiM is a simulation framework to support modeling and simulation of wireless and mobile networks. NOTE: This is a deprecated model kept only for archival purposes. All functionality of this model is available in the INET Framework.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/MiXiM.html",
            },
            "required_projects": {"omnetpp": ["4.6", "4.5", "4.4", "4.3", "4.2"], "inet": ["2.1.0"]},
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
            # <!> Error: Cannot load library '/home/user/opp_env_workspace/inet-4.4.1/bin/../src/../src//libINET.so': 
            # /nix/store/4nlgxhb09sdr51nc9hdm8az5b08vzkgx-glibc-2.35-163/lib/libc.so.6: version `GLIBC_2.36' not found 
            # (required by /home/user/opp_env_workspace/inet-4.4.1/bin/../src/../src//libINET.so)
            "name": "inetgpl", "version": "1.0",
            "description": "GPL licensed models for INET",
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
            },
            "required_projects": {"omnetpp": ["6.0", "5.7"]},
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
            },
            "required_projects": {"omnetpp": ["5.2"]},
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
            },
            "required_projects": {"omnetpp": ["4.6.x"], "inet": ["2.6.0"]},
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
            "required_projects": {"omnetpp": ["4.2"], "inet": ["2.2.0"]},
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
            },
            "nix_packages": ["libxml2"],
            "required_projects": {"omnetpp": ["4.6.x"]},
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
            },
            "required_projects": {"omnetpp": ["6.0.0"]},
            # "git_url": "https://github.com/badapplexx/AFDX.git",      # master branch
            "download_url": "https://github.com/badapplexx/AFDX/archive/f6ddd70438e1c9ee885a4adef8d2503a5108ade4.tar.gz",
            "patch_commands": [
                "sed -i 's|.:../src|.:../src:../../queueinglib|g' afdx/simulations/run",
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
            },
            "required_projects": {"omnetpp": ["4.0.x"]},
            # "git_url": "https://github.com/dhuertas/cell-signaling.git",  # master branch
            # we're using a hash from master because there are no releases
            "download_url": "https://github.com/dhuertas/cell-signaling/archive/3434cc00f7ab7bfc33b4ff94e3a355df8e6947bb.tar.gz",
            "setenv_commands": ["echo 'Hint: in the src folder, use the `./cell` command to run simulations. For example: `./cell -n .. ../networks/demo.ini`'"],
            "build_commands": ["cd src && opp_makemake -f --deep -O out -o cell && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "inetmanet", "version": "3.8.2",
            "description": "Fork of INET 3.x, containing additional adhoc routing protocols and other models written by the community",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/INETMANET-3.x.html",
            },
            "required_projects": {"omnetpp": ["5.7.x"]},
            "download_url": "https://github.com/aarizaq/inetmanet-3.x/archive/a206218213f96382217a8653ede21f15974c4e70.tar.gz",
            "patch_commands": ["find . -type f -name 'run' -exec chmod +x {} \;"],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "setenv_commands": ["echo 'Hint: use the `./run` command in any example simulation folder.'"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "inetmanet", "version": "4.0.0",
            "description": "Fork of INET 4.x, extending it with experimental features and protocols, mainly for mobile ad hoc networks, many of which are written by Alfonso Ariza",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/INETMANET-4.x.html",
            },
            "required_projects": {"omnetpp": ["5.4.x"]},
            "download_url": "https://github.com/aarizaq/inetmanet-4.x/archive/refs/tags/v4.0.0.tar.gz",
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "setenv_commands": [
                ". setenv -f",
                "echo 'Hint: use the `inet` command in any example simulation folder.'"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "ndnomnet", "version": "20200914",      # last commit of master branch as of time of writing
            "description": "Named Data Networking framework for OMNeT++",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/NDNOMNeT.html",
            },
            "required_projects": {"omnetpp": ["5.1.x"]},
            # "git_url": "https://github.com/amar-ox/NDNOMNeT.git",
            # we're using a hash from master because there are no releases
            "download_url": "https://github.com/amar-ox/NDNOMNeT/archive/d98f80a8b837858e00224e7a37aba35947058002.tar.gz",
            "patch_commands": [
                "sed -i.bak 's|->spp_hbinterval > 0|->spp_hbinterval->getNum() > 0|' inet/src/inet/applications/packetdrill/PacketDrillApp.cc",
                "sed -i.bak 's|->spp_pathmaxrxt > 0|->spp_pathmaxrxt->getNum() > 0|' inet/src/inet/applications/packetdrill/PacketDrillApp.cc",
            ],
            "build_commands": ["cd inet && make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "setenv_commands": ["echo 'Hint: use the `./run` command in any example simulation folder.'"],
            "clean_commands": ["make clean"],
        },
        
        {
            # DONE - only builds with just 'make'; TwoSubnets example works, but segfault when running some other simulations
            "name": "oppbsd", "version": "4.0",
            "description": "OppBSD integrates essential parts of the real FreeBSD networking stack into OMNeT++ as a simulation model",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/OppBSD-4.0.html",
            },
            "required_projects": {"omnetpp": ["4.2.0"]},
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
            },
            "nix_packages": ["sqlite"],
            "required_projects": {"omnetpp": ["4.2.0"]},
            # "git_url": "https://github.com/kyeongsoo/inet-hnrl.git",
            "download_url": "https://github.com/kyeongsoo/inet-hnrl/archive/857ae37cd233914fd7271584afc4be10bcf75a61.zip",
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
            # This is the master_20100723 release
            "name": "inet_hnrl", "version": "20100723",
            "description": "Fork of INET developed for hybrid networking research, providing new models in both optical and wireless networking areas and their hybrid.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/INET-HNRL.html",
            },
            "nix_packages": ["sqlite"],
            "required_projects": {"omnetpp": ["4.1.0"]},
            "download_url": "https://github.com/kyeongsoo/inet-hnrl/archive/refs/tags/master_20100723.tar.gz",
            "patch_commands": [
                "sed -i 's|INETMANET_PROJ=/media/data/Linux/omnet/inetmanet-inetmanet-00f64c2|INETMANET_PROJ=$(INETMANET_ROOT)|g' Makefile",
                "sed -i 's|-L/usr/local/lib|-L$(SQLITE_LIB)|g' Makefile",
                "sed -i 's|-I/usr/local/include||g' Makefile",
                "sed -i 's|addr.sin_len|// addr.sin_len|' src/linklayer/ext/*.cc",  # ugly hack? this is needed on apple
                "sed -i 's|machine/endian|endian|' src/util/headerserializers/headers/defs.h",
                "sed -i 's|info\\[\\]|info[0]|' src/util/headerserializers/headers/sctp.h",
                "chmod +x examples/rundemo",
            ],
            "setenv_commands": ["export SQLITE_LIB=${pkgs.sqlite}/lib"],
            "build_commands": ["make makefiles && make all -j$NIX_BUILD_CORES MODE=$BUILD_MODE CFLAGS='-std=c++14 -fpermissive -fPIC'"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "simcan", "version": "1.2",
            "description": "A simulation platform for modelling and simulating distributes architectures and applications.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/SIMCAN.html",
            },
            "required_projects": {"omnetpp": ["4.6.x"], "inet": ["2.6.0"]},
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
            },
            "required_projects": {"omnetpp": ["3.3.x"]},
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
            },
            "required_projects": {"omnetpp": ["5.0.x"]},
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
            # DONE - should this be a library? any hint?
            "name": "tcp_fit_illinois", "version": "20150828",      # last commit of master branch as of time of writing
            "description": "TCP-Fit and TCP-Illinois models for OMNeT++ and INET",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/TCP-Fit-Illinois.html",
            },
            "required_projects": {"omnetpp": ["4.6.0"], "inet": ["2.5.0"]},
            # "git_url": "https://github.com/SpyrosMArtel/TCP-Fit-Illinois.git",
            "download_url": "https://github.com/SpyrosMArtel/TCP-Fit-Illinois/archive/ba5e56f0bd13d6b40b40892ac61d82d4f9a7ac92.tar.gz",
            "build_commands": ["opp_makemake -f --deep -o tcp_fit_illinois -KINET_PROJ=$INET_PROJ -DINET_IMPORT -I. -I$INET_ROOT/src/applications -I$INET_ROOT/src/applications/common -I$INET_ROOT/src/applications/dhcp -I$INET_ROOT/src/applications/ethernet -I$INET_ROOT/src/applications/generic -I$INET_ROOT/src/applications/httptools -I$INET_ROOT/src/applications/netperfmeter -I$INET_ROOT/src/applications/pingapp -I$INET_ROOT/src/applications/rtpapp -I$INET_ROOT/src/applications/sctpapp -I$INET_ROOT/src/applications/tcpapp -I$INET_ROOT/src/applications/traci -I$INET_ROOT/src/applications/udpapp -I$INET_ROOT/src/applications/voip -I$INET_ROOT/src/base -I$INET_ROOT/src/battery -I$INET_ROOT/src/battery/models -I$INET_ROOT/src/linklayer -I$INET_ROOT/src/linklayer/common -I$INET_ROOT/src/linklayer/configurator -I$INET_ROOT/src/linklayer/contract -I$INET_ROOT/src/linklayer/ethernet -I$INET_ROOT/src/linklayer/ethernet/switch -I$INET_ROOT/src/linklayer/ext -I$INET_ROOT/src/linklayer/idealwireless -I$INET_ROOT/src/linklayer/ieee80211 -I$INET_ROOT/src/linklayer/ieee80211/mac -I$INET_ROOT/src/linklayer/ieee80211/mgmt -I$INET_ROOT/src/linklayer/ieee80211/radio -I$INET_ROOT/src/linklayer/ieee80211/radio/errormodel -I$INET_ROOT/src/linklayer/ieee8021d -I$INET_ROOT/src/linklayer/ieee8021d/common -I$INET_ROOT/src/linklayer/ieee8021d/relay -I$INET_ROOT/src/linklayer/ieee8021d/rstp -I$INET_ROOT/src/linklayer/ieee8021d/stp -I$INET_ROOT/src/linklayer/ieee8021d/tester -I$INET_ROOT/src/linklayer/loopback -I$INET_ROOT/src/linklayer/ppp -I$INET_ROOT/src/linklayer/queue -I$INET_ROOT/src/linklayer/radio -I$INET_ROOT/src/linklayer/radio/propagation -I$INET_ROOT/src/mobility -I$INET_ROOT/src/mobility/common -I$INET_ROOT/src/mobility/contract -I$INET_ROOT/src/mobility/group -I$INET_ROOT/src/mobility/single -I$INET_ROOT/src/mobility/static -I$INET_ROOT/src/networklayer -I$INET_ROOT/src/networklayer/arp -I$INET_ROOT/src/networklayer/autorouting -I$INET_ROOT/src/networklayer/autorouting/ipv4 -I$INET_ROOT/src/networklayer/autorouting/ipv6 -I$INET_ROOT/src/networklayer/bgpv4 -I$INET_ROOT/src/networklayer/bgpv4/BGPMessage -I$INET_ROOT/src/networklayer/common -I$INET_ROOT/src/networklayer/contract -I$INET_ROOT/src/networklayer/diffserv -I$INET_ROOT/src/networklayer/icmpv6 -I$INET_ROOT/src/networklayer/internetcloud -I$INET_ROOT/src/networklayer/ipv4 -I$INET_ROOT/src/networklayer/ipv6 -I$INET_ROOT/src/networklayer/ipv6tunneling -I$INET_ROOT/src/networklayer/ldp -I$INET_ROOT/src/networklayer/manetrouting -I$INET_ROOT/src/networklayer/manetrouting/aodv-uu -I$INET_ROOT/src/networklayer/manetrouting/aodv-uu/aodv-uu -I$INET_ROOT/src/networklayer/manetrouting/base -I$INET_ROOT/src/networklayer/manetrouting/batman -I$INET_ROOT/src/networklayer/manetrouting/batman/batmand -I$INET_ROOT/src/networklayer/manetrouting/batman/batmand/orig -I$INET_ROOT/src/networklayer/manetrouting/dsdv -I$INET_ROOT/src/networklayer/manetrouting/dsr -I$INET_ROOT/src/networklayer/manetrouting/dsr/dsr-uu -I$INET_ROOT/src/networklayer/manetrouting/dymo -I$INET_ROOT/src/networklayer/manetrouting/dymo/dymoum -I$INET_ROOT/src/networklayer/manetrouting/dymo_fau -I$INET_ROOT/src/networklayer/manetrouting/olsr -I$INET_ROOT/src/networklayer/mpls -I$INET_ROOT/src/networklayer/ospfv2 -I$INET_ROOT/src/networklayer/ospfv2/interface -I$INET_ROOT/src/networklayer/ospfv2/messagehandler -I$INET_ROOT/src/networklayer/ospfv2/neighbor -I$INET_ROOT/src/networklayer/ospfv2/router -I$INET_ROOT/src/networklayer/routing -I$INET_ROOT/src/networklayer/routing/aodv -I$INET_ROOT/src/networklayer/routing/dymo -I$INET_ROOT/src/networklayer/routing/gpsr -I$INET_ROOT/src/networklayer/routing/rip -I$INET_ROOT/src/networklayer/rsvp_te -I$INET_ROOT/src/networklayer/ted -I$INET_ROOT/src/networklayer/xmipv6 -I$INET_ROOT/src/nodes -I$INET_ROOT/src/nodes/aodv -I$INET_ROOT/src/nodes/bgp -I$INET_ROOT/src/nodes/dymo -I$INET_ROOT/src/nodes/ethernet -I$INET_ROOT/src/nodes/gpsr -I$INET_ROOT/src/nodes/httptools -I$INET_ROOT/src/nodes/inet -I$INET_ROOT/src/nodes/internetcloud -I$INET_ROOT/src/nodes/ipv6 -I$INET_ROOT/src/nodes/mpls -I$INET_ROOT/src/nodes/ospfv2 -I$INET_ROOT/src/nodes/rip -I$INET_ROOT/src/nodes/rtp -I$INET_ROOT/src/nodes/wireless -I$INET_ROOT/src/nodes/xmipv6 -I$INET_ROOT/src/status -I$INET_ROOT/src/transport -I$INET_ROOT/src/transport/contract -I$INET_ROOT/src/transport/rtp -I$INET_ROOT/src/transport/rtp/profiles -I$INET_ROOT/src/transport/rtp/profiles/avprofile -I$INET_ROOT/src/transport/sctp -I$INET_ROOT/src/transport/tcp -I$INET_ROOT/src/transport/tcp/flavours -I$INET_ROOT/src/transport/tcp/queues -I$INET_ROOT/src/transport/tcp_common -I$INET_ROOT/src/transport/udp -I$INET_ROOT/src/util -I$INET_ROOT/src/util/headerserializers -I$INET_ROOT/src/util/headerserializers/headers -I$INET_ROOT/src/util/headerserializers/ipv4 -I$INET_ROOT/src/util/headerserializers/ipv4/headers -I$INET_ROOT/src/util/headerserializers/ipv6 -I$INET_ROOT/src/util/headerserializers/ipv6/headers -I$INET_ROOT/src/util/headerserializers/sctp -I$INET_ROOT/src/util/headerserializers/sctp/headers -I$INET_ROOT/src/util/headerserializers/tcp -I$INET_ROOT/src/util/headerserializers/tcp/headers -I$INET_ROOT/src/util/headerserializers/udp -I$INET_ROOT/src/util/headerserializers/udp/headers -I$INET_ROOT/src/util/messageprinters -I$INET_ROOT/src/world -I$INET_ROOT/src/world/annotations -I$INET_ROOT/src/world/httptools -I$INET_ROOT/src/world/obstacles -I$INET_ROOT/src/world/radio -I$INET_ROOT/src/world/scenario -I$INET_ROOT/src/world/traci -L$INET_ROOT/src -linet && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE - should this be a library?
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
                # ./chaosmanager $INET_ROOT/examples/aodv/omnetpp.ini -n $INET_ROOT/src:$INET_ROOT/examples
            ],
            "patch_commands": [
                "sed -i 's|#include \"inet/common/chaos/ChaosEvent_m.h\"|#include \"ChaosEvent_m.h\"|g' ChaosManager.cc",
            ],
            "build_commands": ["opp_makemake -f --deep -o chaosmanager -O out -KINET_PROJ=$INET_ROOT -DINET_IMPORT -I. -I$INET_ROOT/src -L$INET_ROOT/src -lINET && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE - needs omnetpp debug
            # when running with sumo gui:
            # FXGLVisual::create: requested OpenGL visual unavailable.
            "name": "artery_allinone", "version": "20230820",       # last commit of master branch as of time of writing
            "description": "V2X simulation framework for ETSI ITS-G5. This version downloads its own copy of Veins, INET, SimuLTE, and Vanetza, and does not use ones installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/Artery.html",
            },
            "required_projects": {"omnetpp": ["5.6"]},
            "nix_packages": ["cmake", "boost", "cryptopp", "geographiclib", "sumo", "git-lfs" ],
            # we use a hash from master because the opp-summit release needs git to build
            "download_commands": [
                "mkdir artery_allinone-20230820",
                "git clone https://github.com/riebl/artery.git artery_allinone-20230820",
                "cd artery_allinone-20230820",
                "git reset --hard ad201f699fb7b22319497b31fe0ea437bb2ef2e3",
                "git submodule update --init --recursive",
            ],
            "patch_commands": [
            ],
            "setenv_commands": [
                "export ARTERY_PATH=$ARTERY_ROOT",
                "echo 'Hint: use the `cmake --build build --target run_example` command to run the example simulation.'"
            ],
            "build_commands": ["mkdir -p build && cd build && cmake .. && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE
            "name": "ops_allinone", "version": "20230331",      # last commit of master branch as of time of writing
            "description": "Opportunistic Protocol Simulator. This version downloads its own copy of INET, and does not use one installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/OPS.html",
            },
            "nix_packages": ["autoconf", "automake", "libtool"],
            "required_projects": {"omnetpp": ["5.4.x"]},
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
            "name": "opslite", "version": "20190624",       # last commit of master branch as of time of writing
            "description": "A Lightweight Opportunistic Networking Simulator in OMNeT++",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/OPSLite.html",
            },
            "required_projects": {"omnetpp": ["5.4.1"], "inet": ["4.0.0"]},
            # "git_url": "https://github.com/ComNets-Bremen/OPSLite.git",
            "download_url": "https://github.com/ComNets-Bremen/OPSLite/archive/df67c31eff6d20f91affd931638a058001d81e98.tar.gz",
            "setenv_commands": ["export INET_PROJ=$INET_ROOT",
                                "echo 'Hint: in the `simulations` folder, use the `../src/opslite omnetpp.ini -n .:../src:$INET_ROOT/src` command to run the example simulation.'"],
            "build_commands": ["cd src && opp_makemake -f --deep -o opslite -KINET_PROJ=$INET_PROJ -DINET_IMPORT -I$INET_PROJ/src -L$INET_PROJ/src -lINET && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE
            "name": "libara_allinone", "version": "20150402",       # last commit of master branch as of time of writing
            "description": "Routing algorithms based on the Ant Colony Optimization (ACO) metaheuristic. This version downloads its own copy of INETMANET, and does not use one installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/libARA.html",
            },
            "required_projects": {"omnetpp": ["4.5.x"]},
            "download_commands": [
                "git clone https://github.com/des-testbed/libara.git libara_allinone-20150402",
                "cd libara_allinone-20150402",
                "git reset --hard 5b40a41839167c6709d86400d41be51f1ce51781",
                "sed -i 's|git:\/\/|https:\/\/|g' .gitmodules",
                "pwd",
                "cd inetmanet",
                "git submodule init",
                "git submodule update",
            ],
            "patch_commands": [
                "cd inetmanet",
                "sed -i.bak 's|info\\[\\]|info[0]|' src/util/headerserializers/sctp/headers/sctp.h",
                "for f in $(grep -Rls 'defined(linux)'); do sed -i.bak 's|defined(linux)|defined(__linux__)|' $f; done",
                "sed -i.bak 's/SensitivityList::iterator it = sensitivityList.find(0.0);/SensitivityList::iterator sit = sensitivityList.find(0.0);/' src/linklayer/radio/Radio.cc",
                "sed -i.bak 's/if (it == sensitivityList.end())/if (sit == sensitivityList.end())/' src/linklayer/radio/Radio.cc",
                "sed -i.bak 's/\"LL\"/\" LL \"/' src/networklayer/ipv4/RoutingTableRecorder.cc",
                "sed -i.bak 's/if (vector_cost<=0)/if (vector_cost == NULL)/' src/networklayer/manetrouting/dsr/dsr-uu/path-cache.cc",
                "sed -i.bak 's/std::make_pair<ManetAddress,ProtocolsRoutes>(getAddress(),vect)/std::make_pair((ManetAddress)getAddress(),vect)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc",
                "sed -i.bak 's/std::make_pair<ManetAddress,ManetAddress>(dst, gtwy)/std::make_pair((ManetAddress)dst, (ManetAddress)gtwy)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc",
                "sed -i.bak 's/std::make_pair<ManetAddress,ManetAddress>(destination, nextHop)/std::make_pair((ManetAddress)destination, (ManetAddress)nextHop)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc",
                "sed -i.bak 's/  int groups\\[8\\] = /  unsigned int groups[8] = /' src/networklayer/contract/IPv6Address.cc",
                "sed -i.bak 's/findGap(int \\*groups/findGap(unsigned int *groups/' src/networklayer/contract/IPv6Address.cc",
            ],
            "setenv_commands": ["export INETMANET_FOLDER=$LIBARA_ROOT/inetmanet",
                                "echo 'Hint: in an example simulation folder, use the `./run.sh` command to run the example simulation.'"],
            "build_commands": [
                "make all -j$NIX_BUILD_CORES MODE=$BUILD_MODE"
            ],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "opendsme_allinone", "version": "20201110",     # last commit of master branch as of time of writing
            "description": "IEEE 802.15.4 Deterministic and Synchronous Multi-channel Extension. This version downloads its own copy of INET, and does not use one installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/OpenDSME.html",
            },
            "required_projects": {"omnetpp": ["5.4.x"]},
            "download_commands": [
                "mkdir opendsme_allinone-20201110",
                "cd opendsme_allinone-20201110",
                "git clone https://github.com/openDSME/inet.git --single-branch",
                "cd inet",
                "git reset --hard 550e4e4592481f005cd135f038d458cf17d857b3",
                "git submodule update --init",
                "cd ..",
                "git clone https://github.com/openDSME/inet-dsme.git --single-branch",
                "cd inet-dsme",
                "git reset --hard eb8e76ca6f88f0b8a75db00e5b6c4cdebb1c6bc9",
                "git submodule update --init",                
            ],
            "setenv_commands": [
                "echo 'Hint: in the `inet-dsme/simulations` folder, use the `./singlerun.sh` command to run the example simulation.'"
            ],
            "build_commands": ["cd inet && make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd ../inet-dsme && ./build.sh ../inet"],
            "clean_commands": ["make clean"],
        },
        
        {
            # DONE
            "name": "rpl_allinone", "version": "20221102",      # last commit of master branch as of time of writing
            "description": "Routing Protocol for Low Power and Lossy Networks. This version downloads its own copy of INET, and does not use ones installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/ComNetsHH-RPL.html",
            },
            "nix_packages": ["wget", "rsync"],
            "required_projects": {"omnetpp": ["5.6.x"]},
            "download_commands": [
                "git clone https://github.com/ComNetsHH/omnetpp-rpl.git rpl_allinone-20221102",
                "cd rpl_allinone-20221102",
                "git reset --hard ae9f4e69306a6dfc0aeac8d19423a7ccb52f2a50",
                "wget https://github.com/inet-framework/inet/releases/download/v4.2.5/inet-4.2.5-src.tgz",
                "tar -xzvf inet-4.2.5-src.tgz",
                "mv -f inet4 inet",
                "rm inet-4.2.5-src.tgz",
                "chmod +x replace_inet_files.sh",
                "./replace_inet_files.sh inet",
            ],
            "setenv_commands": [
                "echo 'Hint: in the `src` folder, use the `./rpl ../simulations/omnetpp.ini -n .:../inet/src:../simulations` command to run the example simulation.'"
            ],
            "build_commands": [
                "cd inet",
                "make makefiles",
                "make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
                "cd ../src",
                "opp_makemake -f --deep -o rpl -KINET_PROJ=../inet -I../inet/src -L../inet/src -lINET", 
                "make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
            ],
            "clean_commands": ["make clean"],
        },
        
        {
            # DONE
            "name": "swim_allinone", "version": "20180221",     # last commit of master branch as of time of writing
            "description": "Small Worlds in Motion (SWIM) mobility model. This version downloads its own copy of INET, and does not use ones installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/SWIMMobility.html",
            },
            "nix_packages": ["wget"],
            "required_projects": {"omnetpp": ["5.7.x"]},
            "download_commands": [
                "mkdir swim_allinone-20180221",
                "cd swim_allinone-20180221",
                "wget https://github.com/inet-framework/inet/releases/download/v3.8.3/inet-3.8.3-src.tgz",
                "tar -xzvf inet-3.8.3-src.tgz --strip=1",
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
                "wget https://github.com/ComNets-Bremen/SWIMMobility/archive/refs/heads/master.tar.gz",
                "tar -xzvf master.tar.gz --strip=1",
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
            "name": "tsch_allinone", "version": "6tisch_20221102",      # last commit of 6tisch branch as of time of writing
            "description": "6tisch branch, 11 nov 2022",
            "nix_packages": ["wget", "rsync"],
            "required_projects": {"omnetpp": ["5.6.x"]},
            "download_commands": [
                "mkdir tsch_allinone-6tisch_20221102",
                "cd tsch_allinone-6tisch_20221102",
                "git clone https://github.com/ComNetsHH/omnetpp-rpl.git rpl",
                "cd rpl",
                "git reset --hard ae9f4e69306a6dfc0aeac8d19423a7ccb52f2a50",
                "wget https://github.com/inet-framework/inet/releases/download/v4.2.5/inet-4.2.5-src.tgz",
                "tar -xzvf inet-4.2.5-src.tgz",
                "mv -f inet4 inet",
                "rm inet-4.2.5-src.tgz",
                "cd ..",
                "wget https://github.com/ComNetsHH/omnetpp-tsch/archive/29a08b2a402da0506da8385abd824736f1181671.tar.gz",
                "tar -xzvf 29a08b2a402da0506da8385abd824736f1181671.tar.gz --strip=1",
            ],
            "setenv_commands": [
                "echo 'Hint: use the `./tsch ../simulations/wireless/waic/omnetpp.ini -n .:../rpl/src:../rpl/inet/src:../simulations` command in the src folder to run the simulations.'",
            ],
            "patch_commands": [
                "cd rpl",
                "chmod +x replace_inet_files.sh",
                "./replace_inet_files.sh inet",
                "cd ..",
                "sed -i 's|../inet/  $1/src/inet/|../inet/  $1/src/inet/|g' tools/replace_inet_files.sh",
                "cd tools",
                "chmod +x replace_inet_files.sh",
                "./replace_inet_files.sh ../rpl/inet",
                # this still doesnt work
                r"sed -i 's|\:$.*?/omnetpp-5\.6\.2-new/samples/omnetpp-rpl/src|../../rpl/src|g' hpq_sim/hpq_run.sh",
                r"sed -i 's|\:$.*?/omnetpp-5\.6\.2-new/samples/inet4/src|../../rpl/inet/src|g' hpq_sim/hpq_run.sh",
            ],
            "build_commands": [
                "cd rpl/inet", 
                "make makefiles",
                "make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
                "cd ../src",
                "opp_makemake -f --deep --make-so -o rpl -KINET_PROJ=../inet -I../inet/src -L../inet/src -lINET", 
                "make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
                "cd ../../src",
                "opp_makemake -f --deep -o tsch -KINET_PROJ=../rpl/inet -I../rpl/inet/src -L../rpl/inet/src -lINET -I../rpl/src -L../rpl/src -lrpl -I. -Iapplications -IImobility -Icommon -Ilinklayer -Iradio",
                "make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
            ],
            "clean_commands": ["make clean && cd rpl/src && make clean && cd ../inet && make clean"],
        },

        {
            # DONE
            "name": "tsch_allinone", "version": "6tisch_paper",
            "description": "6TiSCH-CLX ACM TOIT paper exact version",
            "nix_packages": ["wget", "rsync"],
            "required_projects": {"omnetpp": ["5.6.x"]},
            "download_commands": [
                "mkdir tsch_allinone-6tisch_paper",
                "cd tsch_allinone-6tisch_paper",
                "git clone https://github.com/ComNetsHH/omnetpp-rpl.git rpl",
                "cd rpl",
                "ls",
                "git reset --hard 792e6473145d482894f396fea146df9c27a0c758",
                "mv inet inet_replacement_files",
                "wget https://github.com/inet-framework/inet/releases/download/v4.2.5/inet-4.2.5-src.tgz",
                "tar -xzvf inet-4.2.5-src.tgz",
                "mv -f inet4 inet",
                "rm inet-4.2.5-src.tgz",
                "cd ..",
                "wget https://github.com/ComNetsHH/omnetpp-tsch/archive/refs/tags/acm-toit-6tisch-clx.tar.gz",
                "tar -xzvf acm-toit-6tisch-clx.tar.gz --strip=1",
                "rm acm-toit-6tisch-clx.tar.gz",
            ],
            "setenv_commands": [
                "echo 'Hint: use the `./tsch ../simulations/wireless/waic/omnetpp.ini -n .:../rpl/src:../rpl/inet/src:../simulations` command in the src folder to run the simulations.'",
            ],
            "patch_commands": [
                "cd rpl",
                """echo 'rsync -abuvP --include="*/" --include="*.cc" --include="*.h" --include="*.ned"  --exclude="*"  inet_replacement_files/  $1/src/inet/ \nfind $1/src/inet -name "*.*~" -delete' > replace_inet_files.sh""",
                "chmod +x replace_inet_files.sh",
                "./replace_inet_files.sh inet",
            ],
            "build_commands": [
                "cd rpl/inet", 
                "make makefiles",
                "make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
                "cd ../src",
                "opp_makemake -f --deep --make-so -o rpl -KINET_PROJ=../inet -I../inet/src -L../inet/src -lINET", 
                "make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
                "cd ../../src",
                "opp_makemake -f --deep -o tsch -KINET_PROJ=../rpl/inet -I../rpl/inet/src -L../rpl/inet/src -lINET -I../rpl/src -L../rpl/src -lrpl -I. -Iapplications -IImobility -Icommon -Ilinklayer -Iradio",
                "make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
            ],
            "clean_commands": ["make clean && cd rpl/src && make clean && cd ../inet && make clean"],
        },

        {
            # DONE
            # intended to be used as part of inet - this should be its own project
            "name": "can_allinone", "version": "0.1.0",
            "description": "Controller Area Network. This version downloads its own copy of INET, and does not use ones installed by opp_env.",
            "nix_packages": ["wget"],
            "required_projects": {"omnetpp": ["4.6.0"]},
            "download_commands": [
                "mkdir can_allinone-0.1.0",
                "cd can_allinone-0.1.0",
                "wget https://github.com/inet-framework/inet/releases/download/v2.5.0/inet-2.5.0-src.tgz",
                "tar -xvzf inet-2.5.0-src.tgz --strip=1",
                "rm inet-2.5.0-src.tgz",
                "wget https://github.com/YutakaMatsubara/can-for-omnet/archive/refs/tags/v0.1.0.tar.gz",
                "tar -xzvf v0.1.0.tar.gz",
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
            "clean_commands": ["make clean"]
        },
    ]