def get_project_descriptions():
    return [
        {
            # DONE - ok
            "name": "fico4omnet", "version": "20210113",        # last commit of master branch as of time of writing
            "description": "Fieldbus Communication (CAN and FlexRay)",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/FiCo4OMNeT.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd examples/flexray/dynamic && run_fico4omnet$BUILD_MODE_SUFFIX -u Cmdenv --sim-time-limit=1s > /dev/null",
            ],
            "required_projects": {"omnetpp": ["5.5.*", "5.6.*", "5.7.*"]},
            "patch_commands": [
                "mkdir bin",
                "rm src/run_fico4omnet.cmd",
                "mv src/run_fico4omnet bin",
                "sed -i 's|DIR=`dirname $0`|DIR=`dirname \\$0`/../src|' bin/run_fico4omnet",
                "sed -i 's|MAKEMAKE_OPTIONS .* -I.|& -o FiCo4OMNeT|' Makefile",
                "cp bin/run_fico4omnet bin/run_fico4omnet_dbg",
                "sed -i 's|opp_run|opp_run_dbg|' bin/run_fico4omnet_dbg",
            ],
            "setenv_commands": [
                "export NEDPATH=$NEDPATH:.:$FICO4OMNET_ROOT/src:$FICO4OMNET_ROOT/examples:$FICO4OMNET_ROOT/examples_andl:$FICO4OMNET_ROOT/simulations",
                "export PATH=$PATH:$FICO4OMNET_ROOT/bin",
                "echo 'Hint: use the `run_fico4omnet` command to run the simulations in the examples folder.'"
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
            "options": {
                "from-release": {
                    "option_description": "Install from release tarball on GitHub",
                    "option_category": "download",
                    "option_is_default": True,
                    "download_url": "https://github.com/CoRE-RG/FiCo4OMNeT/archive/refs/tags/nightly/2021-01-13_00-00-25.tar.gz",       # there are no releases available, so we download the latest nightly
                },
                "from-git": {
                    "option_description": "Install from git repo on GitHub",
                    "option_category": "download",
                    "option_is_default": False,
                    "git_url": "https://github.com/CoRE-RG/FiCo4OMNeT.git",
                    "git_branch": "nightly/2021-01-13_00-00-25",
                },
            },
        },

        {
            # DONE - ok
            "name": "ansa", "version": "3.4.0",
            "description": "Automated Network Simulation and Analysis",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/ANSA.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then BUILD_MODE_SUFFIX="_release"; ANSA_LIB=$(echo $ANSA_ROOT/out/*-release/src/*INET*); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX=""; ANSA_LIB=$(echo $ANSA_ROOT/out/*-debug/src/*INET*); fi""",
                "cd examples/ansa/eigrp/basic",
                "opp_run$BUILD_MODE_SUFFIX -l $ANSA_LIB -n $ANSA_ROOT/tutorials:$ANSA_ROOT/examples:$ANSA_ROOT/src -c EIGRP_unequal_cost_lb -u Cmdenv > /dev/null",
            ],
            "required_projects": {"omnetpp": ["5.1.*"]},
            "patch_commands": [
                "chmod +x inet_featuretool",
                "chmod +x src/run_inet",
                "sed -i 's|getClassName() > 0)|getCount() > 0)|' src/ansa/routing/babel/BabelDef.cc",
                "sed -i 's|cResultFilterDescriptor|cResultFilterType|' src/inet/common/figures/DelegateSignalConfigurator.cc",
                "sed -i 's/if (vector_cost<=nullptr)/if (vector_cost == nullptr)/' src/inet/routing/extras/dsr/dsr-uu/path-cache.cc",
                "rm src/run_inet.cmd",
                "mkdir bin",
                "mv src/run_inet bin",
                "sed -i 's|DIR=`dirname $0`|DIR=`dirname \\$0`/../src|' bin/run_inet",
            ],
            "setenv_commands": [
                "echo 'Hint: use the `run_inet` command to run the simulations in the examples/ansa folder.'",
                "export PATH=$PATH:$ANSA_ROOT/bin"
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
            "options": {
                "from-release": {
                    "option_description": "Install from release tarball on GitHub",
                    "option_category": "download",
                    "option_is_default": True,
                    "download_url": "https://github.com/kvetak/ANSA/archive/58982068c3c1efc181631c4edf1e4be4c717a136.tar.gz",       # latest commit on ansainet-3.4.0 branch
                },
                "from-git": {
                    "option_description": "Install from git repo on GitHub",
                    "option_category": "download",
                    "option_is_default": False,
                    "git_url": "https://github.com/kvetak/ANSA.git",
                    "git_branch": "ansainet-3.4.0",
                },
            },
        },

        {
            # DONE - ok
            "name": "flora", "version": "1.1.0",
            "description": "Framework for LoRa",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/FLoRA.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd simulations && ../src/run_flora$BUILD_MODE_SUFFIX -u Cmdenv --sim-time-limit=10s > /dev/null",
            ],
            "required_projects": {"omnetpp": ["6.0.*"], "inet": ["4.4.0"]},
            "download_url": "https://github.com/florasim/flora/releases/download/v1.1.0/flora-1.1.0.tgz",
            "patch_commands": [
                "sed -i -E 's|INET_DIR = [^ ]+|INET_DIR = $(INET_ROOT)|' Makefile",
                "sed -i -E 's|-KINET_PROJ=[^ ]+|-KINET_PROJ=$(INET_DIR)|' Makefile",
                "cp src/run_flora src/run_flora_dbg",
                "sed -i 's|opp_run|opp_run_dbg|' src/run_flora_dbg",
            ],
            "setenv_commands": [
                "echo 'Hint: use the `./run` command to run the example in the simulations folder.'",
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE - ok
            "name": "core4inet", "version": "240124",
            "description": "Real-Time Ethernet protocols for INET",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/Core4INET.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd examples/IEEE8021Q/small_network && opp_run$BUILD_MODE_SUFFIX -l $CORE4INET_ROOT/src/CoRE4INET -l$INET_ROOT/src/INET -n $CORE4INET_ROOT/examples:$CORE4INET_ROOT/src:$INET_ROOT/src -u Cmdenv --sim-time-limit=1s > /dev/null",
            ],
            "required_projects": {"omnetpp": ["6.0.*"], "inet": ["3.8.3"]},
            "patch_commands": [
                "sed -i -E 's|INET_PROJ=[^ ]+|INET_PROJ=$(INET_ROOT)|' Makefile",
                "sed -i -E 's|-L.*/src|-L$$\\\\(INET_PROJ\\\\)/src|' Makefile",
                "sed -i -E 's|-O out |-O out -o CoRE4INET |' Makefile",
                "sed -i 's|-lINET$(DBG_SUFFIX)|-lINET$$\\\(D\\\)|' Makefile",
                "sed -i -E 's|INET_PROJ\); opp_featuretool|INET_PROJ\); ./inet_featuretool|' src/dependencies_makefrag",    # this is needed for the from-git option (but works with the from-release as well)
            ],
            "setenv_commands": [
                "echo 'Hint: use the `./rundemo` command in the examples folder or the `./run` command in any of the example subfolders.'",
                "export INETPATH=$INET_ROOT",
                "export INET_PROJ=$INET_ROOT",
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
            "options": {
                "from-release": {
                    "option_description": "Install from release tarball on GitHub",
                    "option_category": "download",
                    "option_is_default": True,
                    "download_url": "https://github.com/CoRE-RG/CoRE4INET/archive/refs/tags/nightly/2024-01-24_15-05-19.tar.gz"
                },
                "from-git": {
                    "option_description": "Install from git repo on GitHub",
                    "option_category": "download",
                    "option_is_default": False,
                    "git_url": "https://github.com/CoRE-RG/CoRE4INET.git",
                    "git_branch": "nightly/2024-01-24_15-05-19",
                },
            },
        },

        {
            # DONE - ok
            "name": "core4inet", "version": "221109",
            "description": "Real-Time Ethernet protocols for INET",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/Core4INET.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd examples/IEEE8021Q/small_network && opp_run$BUILD_MODE_SUFFIX -l $CORE4INET_ROOT/src/CoRE4INET -l$INET_ROOT/src/INET -n $CORE4INET_ROOT/examples:$CORE4INET_ROOT/src:$INET_ROOT/src -u Cmdenv --sim-time-limit=1s > /dev/null",
            ],
            "required_projects": {"omnetpp": ["5.5.*"], "inet": ["3.6.6"]},
            "patch_commands": [
                "sed -i -E 's|INET_PROJ=[^ ]+|INET_PROJ=$(INET_ROOT)|' Makefile",
                "sed -i -E 's|-L.*/src|-L$$\\\\(INET_PROJ\\\\)/src|' Makefile",
                "sed -i -E 's|-O out |-O out -o CoRE4INET |' Makefile",
                "sed -i 's|-lINET$(DBG_SUFFIX)|-lINET$$\\\(D\\\)|' Makefile",
                "sed -i -E 's|INET_PROJ\); opp_featuretool|INET_PROJ\); ./inet_featuretool|' src/dependencies_makefrag",    # this is needed for the from-git option (but works with the from-release as well)
            ],
            "setenv_commands": [
                "echo 'Hint: use the `./rundemo` command in the examples folder or the `./run` command in any of the example subfolders.'",
                "export INETPATH=$INET_ROOT",
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
            "options": {
                "from-release": {
                    "option_description": "Install from release tarball on GitHub",
                    "option_category": "download",
                    "option_is_default": True,
                    "download_url": "https://github.com/CoRE-RG/CoRE4INET/archive/refs/tags/nightly/2022-11-09_00-01-11.tar.gz"
                },
                "from-git": {
                    "option_description": "Install from git repo on GitHub",
                    "option_category": "download",
                    "option_is_default": False,
                    "git_url": "https://github.com/CoRE-RG/CoRE4INET.git",
                    "git_branch": "nightly/2022-11-09_00-01-11",
                },
            },
        },

        {
            # DONE - ok
            "name": "simproctc", "version": "2.0.2",
            "description": "Simulation Processing Tool-Chain",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/SimProcTC.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd example-simulation && ./example-simulation$BUILD_MODE_SUFFIX -u Cmdenv --sim-time-limit=10s > /dev/null",
            ],
            "required_projects": {"omnetpp": ["6.0.*"]},
            "setenv_commands": [
                "export OPPMAIN_LIB=$OMNETPP_ROOT/lib",
                "echo 'Hint: use the `./example_simulation` command in the example-simulation folder.'",
                ],
            "build_commands": ["cd example-simulation && opp_makemake -f && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
            "options": {
                "from-release": {
                    "option_description": "Install from release tarball on GitHub",
                    "option_category": "download",
                    "option_is_default": True,
                    "download_url": "https://github.com/dreibh/simproctc/archive/refs/tags/simproctc-2.0.2.tar.gz",
                },
                "from-git": {
                    "option_description": "Install from git repo on GitHub",
                    "option_category": "download",
                    "option_is_default": False,
                    "git_url": "https://github.com/dreibh/simproctc.git",
                    "git_branch": "simproctc-2.0.2",
                },
            },
        },

        {
            # DONE - ok
            "name": "hnocs", "version": "20221212",     # last commit of master branch as of time of writing
            "description": "Network on Chip Simulation Framework",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/HNOCS.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd examples/async/4x4 && ./run --$BUILD_MODE -u Cmdenv --sim-time-limit=0.01ms > /dev/null",
            ],
            "required_projects": {"omnetpp": ["5.5.*"]},
            "download_url": "https://github.com/yanivbi/HNOCS/archive/465754c28977a397e8ea4aef9296ca9987eb4f51.tar.gz",     # there are no releases, so we use a commit from the master branch
            "setenv_commands": [
                "echo 'Hint: use the `./run_nocs` command in the examples folder.'",
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
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd simulations/examples && MODE=$BUILD_MODE ../runsim 01_example_strict_priority.ini --sim-time-limit=0.1s > /dev/null",
            ],
            "required_projects": {"omnetpp": ["5.4.*"], "inet": ["4.1.0"]},
            "download_url": "https://gitlab.com/ipvs/nesting/-/archive/v0.9.1/nesting-v0.9.1.tar.gz",
            "patch_commands": [
                "sed -i -E 's|-KINET_PROJ=[^ ]+|-KINET_PROJ=$(INET_ROOT)|' Makefile",
                "sed -i 's|NESTING=.*|#NESTING=|' simulations/runsim simulations/runsim-qt",
                "sed -i -E 's|INET=.*|INET=$INET_ROOT|' simulations/runsim simulations/runsim-qt",
                "sed -i 's|./nesting$D|$NESTING/simulations/nesting$D|' simulations/runsim simulations/runsim-qt",
                "sed -i 's|-n .:|-n $NESTING/simulations:|' simulations/runsim simulations/runsim-qt",
                "sed -i 's|$1|$@|' simulations/runsim simulations/runsim-qt",
            ],
            "setenv_commands": ["export INET_PROJ=$INET_ROOT",
                                "export NESTING=$NESTING_ROOT",
                                "echo 'Hint: use the `../runsim-qt` command to run the examples in the simulations/examples folder.'"],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE
            # Castalia ported to omnetpp 5.4
            "name": "castalia", "version": "3.3pr16",
            "description": "Simulator for Wireless Sensor Networks (WSN), Body Area Networks (BAN) and generally networks of low-power embedded devices",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/Castalia.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then CASTALIA_BIN=$(echo $CASTALIA_ROOT/out/*-release/src/CastaliaBin); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then CASTALIA_BIN=$(echo $CASTALIA_ROOT/out/*-debug/src/CastaliaBin_dbg); fi""",
                "cd Simulations/BANtest && $CASTALIA_BIN -f omnetpp.ini -u Cmdenv -c TMAC > /dev/null",
            ],
            "nix_packages": ["python2"],
            "required_projects": {"omnetpp": ["5.3.*", "5.4.*", "5.6.*", "5.7.*"]},   # with omnetpp-6.0.*, 5.2.*: opp_msgtool: option is no longer supported: --msg4
            "download_url": "https://github.com/rhornig/Castalia/archive/refs/heads/topic/omnetpp54-compatibility.tar.gz",
            "setenv_commands": [
                "export PATH=$PATH:$CASTALIA_ROOT/Castalia/bin",
                "echo 'Hint: Use the `Castalia` command to run the examples in the Simulations folder.'"
            ],
            "build_commands": ["./makemake && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE - ok
            "name": "castalia", "version": "3.3",
            "description": "Simulator for Wireless Sensor Networks (WSN), Body Area Networks (BAN) and generally networks of low-power embedded devices",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/Castalia.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then CASTALIA_BIN=$(echo $CASTALIA_ROOT/Castalia/out/*-release/CastaliaBin); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then CASTALIA_BIN=$(echo $CASTALIA_ROOT/Castalia/out/*-debug/CastaliaBin); fi""",
                "cd Castalia/Simulations/BANtest && $CASTALIA_BIN -f omnetpp.ini -c TMAC > /dev/null",
            ],
            "nix_packages": ["python2"],
            "required_projects": {"omnetpp": ["4.1.*"]},
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
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then CASTALIA_BIN=$(echo $CASTALIA_ROOT/Castalia/out/*-release/CastaliaBin); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then CASTALIA_BIN=$(echo $CASTALIA_ROOT/Castalia/out/*-debug/CastaliaBin); fi""",
                "cd Castalia/Simulations/BANtest && $CASTALIA_BIN -f omnetpp.ini -c TMAC > /dev/null",
            ],
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
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then BUILD_MODE_SUFFIX='_release'; MIXIM_LIB=$(echo $MIXIM_ROOT/out/*-release/src/*mixim*); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then MIXIM_LIB=$(echo $MIXIM_ROOT/out/*-debug/src/*mixim*); fi""",
                "cd examples/bmac",
                "opp_run$BUILD_MODE_SUFFIX -l $MIXIM_LIB -n ..:../../src/base:../../src/modules:../../src/inet_stub > /dev/null",
            ],
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
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd examples/hls && inetgpl$BUILD_MODE_SUFFIX -c Experiment1 -u Cmdenv --sim-time-limit=1s > /dev/null",
            ],
            "required_projects": {"inet": ["4.5.*"], "omnetpp": ["6.0.*"]},
            "download_commands": ["git clone https://github.com/inet-framework/inet-gpl.git inetgpl-1.0"],
            "setenv_commands": ["source setenv",
                                "echo 'Hint: Use `inetgpl` command in any of the example simulation folders.'"],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"]
        },

        {
            # DONE
            "name": "rspsim", "version": "6.1.3",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/RSPSIM.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd model && ./model$BUILD_MODE_SUFFIX test1.ini -u Cmdenv > /dev/null",
            ],
            "required_projects": {"omnetpp": ["6.0.*"]}, # with omnetpp 5.7.*: error: no type named 'cValue' in namespace 'omnetpp'
            "patch_commands": [
                "sed -i -E 's|<ext_socket.h>|\"ext_socket.h\"|' model/poolelementnode-template.h",
                "sed -i -E 's|<ext_socket.h>|\"ext_socket.h\"|' model/transportaddressblock.c",
            ],
            "build_commands": ["cd model && opp_makemake -f && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd ../toolchain/tools && make"],
            "setenv_commands": ["echo 'Hint: Use `./model` command in the model folder. For example: ./model test1.ini'"],
            "clean_commands": ["make clean"],
            "options": {
                "from-release": {
                    "option_description": "Install from release tarball on GitHub",
                    "option_category": "download",
                    "option_is_default": True,
                    "download_url": "https://github.com/dreibh/rspsim/archive/refs/tags/rspsim-6.1.3.tar.gz",
                },
                "from-git": {
                    "option_description": "Install from git repo on GitHub",
                    "option_category": "download",
                    "option_is_default": False,
                    "git_url": "https://github.com/dreibh/rspsim.git",
                    "git_branch": "rspsim-6.1.3",
                },
            },
        },

        {
            # DONE - ok
            "name": "rspsim", "version": "6.1.2",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/RSPSIM.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd model && ./model$BUILD_MODE_SUFFIX test1.ini -u Cmdenv > /dev/null",
            ],
            "required_projects": {"omnetpp": ["6.0.*", "5.7.*"]},
            "patch_commands": [
                "sed -i -E 's|<ext_socket.h>|\"ext_socket.h\"|' model/poolelementnode-template.h",
                "sed -i -E 's|<ext_socket.h>|\"ext_socket.h\"|' model/transportaddressblock.c",
            ],
            "build_commands": ["cd model && opp_makemake -f && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd ../toolchain/tools && make"],
            "setenv_commands": ["echo 'Hint: Use `./model` command in the model folder. For example: ./model test1.ini'"],
            "clean_commands": ["make clean"],
            "options": {
                "from-release": {
                    "option_description": "Install from release tarball on GitHub",
                    "option_category": "download",
                    "option_is_default": True,
                    "download_url": "https://github.com/dreibh/rspsim/archive/refs/tags/rspsim-6.1.2.tar.gz",
                },
                "from-git": {
                    "option_description": "Install from git repo on GitHub",
                    "option_category": "download",
                    "option_is_default": False,
                    "git_url": "https://github.com/dreibh/rspsim.git",
                    "git_branch": "rspsim-6.1.2",
                },
            },
        },

        {
            # DONE - ok; when testing without '-u Cmdenv' -> segfault (but works in Cmdenv)
            "name": "rinasim", "version": "20200903",       # last commit of master branch as of time of writing
            "description": "Recursive InterNetwork Architecture Simulator",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/RINASim.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd examples/Demos/UseCase1 && opp_run$BUILD_MODE_SUFFIX omnetpp.ini -u Cmdenv -c Ping -n $RINASIM_ROOT -l $RINASIM_ROOT/policies/rinasim > /dev/null",
            ],
            "required_projects": {"omnetpp": ["5.2.*"]},
            "patch_commands": [
                "sed -i -E 's|-O out|-O out -I. -I../src|g' makemakefiles",
            ],
            "setenv_commands": [
                "echo 'Hint: use `./simulate.sh examples/Demos/UseCase1/ -G -c Ping`'",
            ],
            "build_commands": ["make -f makemakefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
            "options": {
                "from-release": {
                    "option_description": "Install from release tarball on GitHub",
                    "option_category": "download",
                    "option_is_default": True,
                    "download_url": "https://github.com/kvetak/RINA/archive/eb6baaf1034319245fa9e4b846a61094445c8d8a.tar.gz",
                },
                "from-git": {
                    "option_description": "Install from git repo on GitHub",
                    "option_category": "download",
                    "option_is_default": False,
                    "git_url": "https://github.com/kvetak/RINA.git",
                    "git_branch": "master",
                },
            },
        },

        {
            # DONE - builds and starts, simulations run, but segfault after some time (tested with inet 2.6, 2.4); only builds release (so only tested in release)
            "name": "ieee802154standalone", "version": "20180310",      # last commit of master branch as of time of writing
            "description": "IEEE 802.15.4-2006 simulation model for OMNeT++ / INET",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/IEEE802154INET-Standalone.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then cd simulations && ../src/ieee802154inet_standalone -n ..:../src:$INET_ROOT/src -c StartWPAN-1Node_Starting_WPAN -u Cmdenv > /dev/null; fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then echo 'Skipping test in debug, because currently the project only builds in release.'; fi""",
            ],
            "required_projects": {"omnetpp": ["4.6.*"], "inet": ["2.6.0"]},
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
            # DONE
            "name": "dctrafficgen", "version": "20181016",      # last commit of master branch as of time of writing
            "description": "Data Center Traffic Generator Library",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/DCTrafficGen.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then DCTRAFFICGEN_BIN=$(echo $DCTRAFFICGEN_ROOT/dctg_example/out/*-release/src/dctg_example); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then DCTRAFFICGEN_BIN=$(echo $DCTRAFFICGEN_ROOT/dctg_example/out/*-debug/src/dctg_example); fi""",
                "cd dctg_example/simulations",
                "$DCTRAFFICGEN_BIN -f omnetpp.ini -n ../../src:../src -u Cmdenv -c FrontEnd --sim-time-limit=10s > /dev/null",
            ],
            "nix_packages": ["libxml2"],
            "required_projects": {"omnetpp": ["4.6.*"]},
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
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd afdx/simulations && ../src/afdx$BUILD_MODE_SUFFIX -n .:../src:../../queueinglib AutoNetwork.ini -u Cmdenv --sim-time-limit=1s > /dev/null"
            ],
            "required_projects": {"omnetpp": ["6.0.*"]},
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
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd quisp && ./quisp$BUILD_MODE_SUFFIX simulations/two_nodes.ini -c two_node_MIM -u Cmdenv --sim-time-limit=10s > /dev/null"
            ],
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
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then BUILD_MODE_SUFFIX="_release"; CELL_BIN=$(echo $CELL_ROOT/src/out/*-release/cell); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX=""; CELL_BIN=$(echo $CELL_ROOT/src/out/*-debug/cell); fi""",
                "cd src",
                "$CELL_BIN -u Cmdenv -c demo-emission -n .. ../networks/demo.ini > /dev/null",
            ],
            "required_projects": {"omnetpp": ["4.0.*"]},
            # we're using a hash from master because there are no releases
            "download_url": "https://github.com/dhuertas/cell-signaling/archive/3434cc00f7ab7bfc33b4ff94e3a355df8e6947bb.tar.gz",
            "setenv_commands": ["echo 'Hint: in the src folder, use the `./cell` command to run simulations. For example: `./cell -n .. ../networks/demo.ini`'"],
            "build_commands": ["cd src && opp_makemake -f --deep -O out -o cell && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "inetmanet4", "version": "4.0.0",
            "description": "Fork of INET 4.x, extending it with experimental features and protocols, mainly for mobile ad hoc networks, many of which are written by Alfonso Ariza",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/INETMANET-4.x.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd examples/aodv && inet$BUILD_MODE_SUFFIX -u Cmdenv -c Static --sim-time-limit=10s > /dev/null",
            ],
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
            "name": "inetmanet3", "version": "3.8.2",
            "description": "Fork of INET 3.x, containing additional adhoc routing protocols and other models written by the community",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/INETMANET-3.x.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd examples/aodv && ../../src/run_inet$BUILD_MODE_SUFFIX -u Cmdenv -c Static --sim-time-limit=10s > /dev/null",
            ],
            "required_projects": {"omnetpp": ["5.7.*"]},
            "download_url": "https://github.com/aarizaq/inetmanet-3.x/archive/a206218213f96382217a8653ede21f15974c4e70.tar.gz",
            "patch_commands": [
                "find . -type f -name 'run' -exec chmod +x {} \;",
                "cp src/run_inet src/run_inet_dbg",
                "sed -i 's|opp_run|opp_run_dbg|' src/run_inet_dbg",
                ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "setenv_commands": ["echo 'Hint: use the `./run` command in any example simulation folder.'"],
            "clean_commands": ["make clean"],
        },
        
        {
            # DONE - TwoSubnets example works, but segfault when running some other simulations; only tested in debug
            # TODO this only builds debug (twice apparently)
            "name": "oppbsd", "version": "4.0",
            "description": "OppBSD integrates essential parts of the real FreeBSD networking stack into OMNeT++ as a simulation model",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/OppBSD-4.0.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then cd examples/TwoSubnets && ./out/gcc-release/TwoSubnets -u Cmdenv -c ThreeHosts omnetpp.ini > /dev/null; fi""",
                """if [ "$BUILD_MODE" = "release" ]; then echo 'Skipping test in release mode, because currently this project only builds in debug mode.'; fi""",
            ],
            "required_projects": {"omnetpp": ["4.2.0"]},
            "download_url": "https://github.com/omnetpp-models/archive/releases/download/archive/oppbsd-4.0.tar.gz",
            "build_commands": ["make MODE=$BUILD_MODE"],
            "setenv_commands": ["echo 'Hint: run example simulations from their folder. For example, in examples/TwoSubnets folder: `./out/gcc-debug/TwoSubnets omnetpp.ini`'"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE - release only
            "name": "rease", "version": "20130819",     # last commit of master branch as of time of writing
            "description": "Realistic Simulation Environments for OMNeT++",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/ReaSE.html",
            },
            "smoke_test_commands": [
                "cd Topologies/topo_router",
                """if [ "$BUILD_MODE" = "release" ]; then REASE_BIN=$(echo $REASE_ROOT/ReaSE/out/*-release/src/rease); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then echo 'Skipping test in debug mode, because the corresponding INET version is only built in release.'; fi""",
                "$REASE_BIN -n .:../../ReaSE/src:$INET_ROOT/src -u Cmdenv --sim-time-limit=10s &> /dev/null",
            ],
            "nix_packages": ["libpcap"],
            "required_projects": {"omnetpp": ["4.1.0"], "inet": ["20100323"]},
            # we're using a hash from master because there are no releases
            "download_url": "https://github.com/ToGaKIT/ReaSE/archive/3f5cd1fd4373da44592a2a0ef160c22331f41967.tar.gz",
            "patch_commands": [
                "sed -i 's|INETDIR = ../../INET|INETDIR = $(INET_ROOT)|' ReaSE/Makefile",
                "sed -i 's|-u Cmdenv | |' ReaSE/Makefile",
                "sed -i 's|-L$(INETDIR)/out/gcc-debug/ -lINET|-L$(INETDIR)/src -linet|' ReaSE/Makefile",
            ],
            "setenv_commands": ["echo 'Hint: in the folder of an example simulation (located in Topologies folder), use the `../../ReaSE/src/rease -n .:../../ReaSE/src:$INET_ROOT/src` command to run the simulation'"],
            "build_commands": ["cd ReaSE && make makefiles && make -j$NIX_BUILD_CORES MODE=release"],
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
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then BUILD_MODE_SUFFIX="_release"; INET_HNRL_LIB=$(echo $INET_HNRL_ROOT/out/*-release/src/*inet*); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX=""; INET_HNRL_LIB=$(echo $INET_HNRL_ROOT/out/*-debug/src/*inet*); fi""",
                "opp_run$BUILD_MODE_SUFFIX -l $INET_HNRL_LIB -n src:examples:examples/hybridpon/arptest -u Cmdenv -c ARPTest examples/hybridpon/arptest/omnetpp.ini > /dev/null"
            ],
            "nix_packages": ["sqlite"],
            "required_projects": {"omnetpp": ["4.2.0"]},
            "download_url": "https://github.com/kyeongsoo/inet-hnrl/archive/857ae37cd233914fd7271584afc4be10bcf75a61.tar.gz",
            "setenv_commands": ["export SQLITE_LIB=${pkgs.sqlite}/lib"],
            "patch_commands": [
                "sed -i 's|INETMANET_PROJ=/media/data/Linux/omnet/inetmanet-inetmanet-00f64c2|INETMANET_PROJ=$(INETMANET_ROOT)|g' Makefile",
                "sed -i 's|-L/usr/local/lib|-L$(SQLITE_LIB)|g' Makefile",
                "sed -i 's|-I/usr/local/include||g' Makefile",
                "sed -i 's|addr.sin_len|// addr.sin_len|' src/linklayer/ext/*.cc",  # ugly hack? this is needed on apple
                "sed -i 's|machine/endian|endian|' src/util/headerserializers/headers/defs.h",
                "sed -i 's|info\\[\\]|info[0]|' src/util/headerserializers/headers/sctp.h",
                "sed -i 's|$(OPP_LIBS)|-loppcommon$$\\\(D\\\)|' Makefile",
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
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then BUILD_MODE_SUFFIX="_release"; SIMCAN_BIN=$(echo $SIMCAN_ROOT/out/clang-release/src/simcan); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX=""; SIMCAN_BIN=$(echo $SIMCAN_ROOT/out/clang-debug/src/simcan); fi""",
                "cd simulations/cliServExample",
                "$SIMCAN_BIN -n ../../src:.:$INET_ROOT/src -u Cmdenv > /dev/null",
            ],
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
            # DONE -> only built and tested in release, because omnetpp 3.3 has no distinct debug/release
            "name": "solarleach", "version": "1.01",
            "description": "A simulation of LEACH (Low-Energy Adaptive Clustering Hierarchy) cluster-based protocol for sensor networks with an extension to make it solar-aware.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/SolarLEACH.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then cd leachDist && ./leachDist -u Cmdenv -L$OMNETPP_ROOT/src/cmdenv/libcmdenv -c Run1 -r 1 --sim-time-limit=10s > /dev/null; fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then echo 'Skipping test in debug mode, because this project is only built in release mode.'; fi""",
            ],
            "required_projects": {"omnetpp": ["3.3.*"]},
            "download_url": "https://github.com/omnetpp-models/archive/releases/download/archive/SolarLEACH-1.01.tgz",
            "setenv_commands": ["echo 'Hint: in the `leachDist` folder, use the `./runall.sh` command to run the simulations. In the `leachFarBS` folder, use the `./leachFarBS` command'",],
            "patch_commands": [
                "tr -d '\r' < leachDist/runall.sh > leachDist/runall_fixed.sh",
                "mv leachDist/runall_fixed.sh leachDist/runall.sh",
                "chmod +x leachDist/runall.sh",
                "sed -i 's|BS::||g' leachFarBS/bs.h",
            ],
            "build_commands": ["cd leachDist && opp_makemake -f -N && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd ../leachFarBS && opp_makemake -f -N && make -j$NIX_BUILD_CORES MODE=release"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "stochasticbattery", "version": "20170224",     # last commit of master branch as of time of writing
            "description": "An OMNeT++ simulation for stochastic battery behavior. It implements the Stochastic Battery Model by Chiasserini and Rao.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/StochasticBattery.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then BUILD_MODE_SUFFIX="_release"; STOCHASTICBATTERY_BIN=$(echo $STOCHASTICBATTERY_ROOT/out/*-release/stochastic_battery); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX=""; STOCHASTICBATTERY_BIN=$(echo $STOCHASTICBATTERY_ROOT/out/*-debug/stochastic_battery); fi""",
                "$STOCHASTICBATTERY_BIN -u Cmdenv --sim-time-limit=10s > /dev/null",
            ],
            "required_projects": {"omnetpp": ["5.0.*"]},
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
            "name": "chaosmanager", "version": "20221210",      # last commit of master branch as of time of writing
            "description": "An automated hard faul injection tool inspired by Chaos Engineering principles for MANETs. This tool has been tested extensively on LEACH for OMNETPP.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/WSN-Chaos-Manager.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "./chaosmanager$BUILD_MODE_SUFFIX $INET_ROOT/examples/aodv/omnetpp.ini -n $INET_ROOT/src:$INET_ROOT/examples -u Cmdenv --sim-time-limit=10s > /dev/null",
            ],
            "required_projects": {"omnetpp": ["5.6.2"], "inet": ["4.2.5"]},
            "download_url": "https://github.com/Agr-IoT/WSN-Chaos-Manager/archive/07272355eb0e8d5fa6216b9dcfb07fcac0a5115b.tar.gz",
            "setenv_commands": [
                "echo 'Hint: use the `./chaosmanager` command to run simulations. Note that this project does not contain any example simulations.'",
            ],
            "patch_commands": [
                "sed -i 's|#include \"inet/common/chaos/ChaosEvent_m.h\"|#include \"ChaosEvent_m.h\"|g' ChaosManager.cc",
            ],
            "build_commands": ["opp_makemake -f --deep -o chaosmanager -O out -KINET_PROJ=$INET_ROOT -DINET_IMPORT -I. -I$INET_ROOT/src -L$INET_ROOT/src -lINET\$D && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE - we only test release currently
            # UPDATE: this only builds inet release, and links the ops debug with that? should not be done with the bootstrap script but manually?
            "name": "ops_allinone", "version": "20230331",      # last commit of master branch as of time of writing
            "description": "Opportunistic Protocol Simulator. This version downloads its own copy of INET, and does not use one installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/OPS.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then cd simulations && ../ops-simu omnetpp-ops.ini -n ../src:.:../modules/inet/src -c Messenger-Epidemic-SWIM -u Cmdenv --sim-time-limit=10s > /dev/null; fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then echo 'Skipping test in debug mode, because currently the project only builds in release mode.'; fi"""
            ],
            "nix_packages": ["autoconf", "automake", "libtool"],
            "required_projects": {"omnetpp": ["5.4.*"]},
            "patch_commands": [
                "sed -i 's|-j 1|-j$NIX_BUILD_CORES|g' bootstrap.sh",
            ],
            "setenv_commands": ["echo 'Hint: in the `simulations` folder, use the `../ops-simu omnetpp-ops.ini -n ../src:.:../modules/inet/src` command to run the example simulation.'"],
            "build_commands": ["./bootstrap.sh && ./ops-makefile-setup.sh && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
            "options": {
                "from-release": {
                    "option_description": "Install from release tarball on GitHub",
                    "option_category": "download",
                    "option_is_default": True,
                    "download_url": "https://github.com/ComNets-Bremen/OPS/archive/57ecc379631eec4bb640b022391f2cf808ff09f4.tar.gz",
                },
                "from-git": {
                    "option_description": "Install from git repo on GitHub",
                    "option_category": "download",
                    "option_is_default": False,
                    "git_url": "https://github.com/ComNets-Bremen/OPS.git",
                    "git_branch": "master",
                },
            },
        },
        
        {
            # DONE
            # this does not contain examples for swim
            "name": "swim_allinone", "version": "20180221",     # last commit of master branch as of time of writing
            "description": "Small Worlds in Motion (SWIM) mobility model. This version downloads its own copy of INET, and does not use ones installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/SWIMMobility.html",
            },
            "smoke_test_commands": [
                # This projects doesn't contain any example simulations, so we test an INET example
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd examples/aodv && ../../src/run_inet$BUILD_MODE_SUFFIX -c Static -u Cmdenv --sim-time-limit=10s > /dev/null",
            ],
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
                "curl -L -o master.tar.gz https://github.com/ComNets-Bremen/SWIMMobility/archive/refs/heads/master.tar.gz --progress-bar",
                "tar -xzf master.tar.gz --strip=1",
                "rm master.tar.gz",
                "cp SWIMMobility.* ../src/inet/mobility/single",
                "echo 'Patching done.'",
                "cd ..",
                "cp src/run_inet src/run_inet_dbg",
                "sed -i 's|opp_run|opp_run_dbg|' src/run_inet_dbg",
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
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd src && ./tsch$BUILD_MODE_SUFFIX ../simulations/wireless/waic/omnetpp.ini -n .:../rpl/src:../rpl/inet/src:../simulations -c HPQ -r 0 -u Cmdenv --sim-time-limit=10s > /dev/null",
            ],
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
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then BUILD_MODE_SUFFIX="_release"; CAN_ALLINONE_LIB=$(echo $CAN_ALLINONE_ROOT/out/*-release/src/*inet*); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX=""; CAN_ALLINONE_LIB=$(echo $CAN_ALLINONE_ROOT/out/*-debug/src/*inet*); fi""",
                "cd examples/can/messagerouter1",
                "opp_run$BUILD_MODE_SUFFIX -l $CAN_ALLINONE_LIB omnetpp.ini -n ../..:../../../src -u Cmdenv -c CanMessageRouter > /dev/null",
            ],
            "required_projects": {"omnetpp": ["4.4.*", "4.6.*"]},    # TODO: 4.6.0 to option --with-recommended-deps?
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
            # DONE - release only
            # TODO no catalog entry yet
            "name": "lora_icn", "version": "paper",
            "nix_packages": ["docker"],
            "details": "This project contains code and documentation to reproduce experimental results of the paper 'Long-Range ICN for the IoT: Exploring a LoRa System Design' published in Proc. of the IFIP Networking Conference 2022.",
            # "metadata": {
            #     "catalog_url": "",
            # },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then docker run --rm -it -v "$(pwd)/data:/root/data" inetrg/ccnsim_dsme bash -c "cd ccnsim_dsme && cd simulations && ../src/ccnsim_dsme -m -n ../src:.:../../inet/src:../../inet/examples:../../inet/tutorials:../../inet/showcases:../../inet-dsme/src:../../inet-dsme/simulations:../../flora/src:../../ccnSim-0.4/:../../lora_omnetpp/src --image-path=../../inet/images -l ../../inet/src/INET -l ../../lora_omnetpp/src/lora_omnetpp  rfd_repos.ini -c INDICATION  --sim-time-limit=10s -r 0 > /dev/null"; fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then echo 'Skipping test in debug mode, because currently the project builds in release mode only.'; fi""",
            ],
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
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then BUILD_MODE_SUFFIX="_release"; SEAPP_LIB=$(echo $SEAPP_ROOT/src/out/*-release/*inet*); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX=""; SEAPP_LIB=$(echo $SEAPP_ROOT/src/out/*-debug/*inet*); fi""",
                "cd examples/seapp/simpleTopo",
                "opp_run$BUILD_MODE_SUFFIX -l $SEAPP_LIB omnetpp.ini -n ../..:../../../src -u Cmdenv -c Simple_attack > /dev/null",
            ],
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
            # DONE - simulations need pcap device for running, so we only test the executable with an inet example
            # TODO: enable emulation by default in inet, and use nix inet version?
            "name": "sedencontroller_allinone", "version": "20230305",      # latest commit of master branch as of time of writing
            "description": "sEden Controller",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/SDNController.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "sdncontroller/src/sdncontroller$BUILD_MODE_SUFFIX $INET_ROOT/examples/aodv/omnetpp.ini -n $INET_ROOT/src:$INET_ROOT/examples -c Static -u Cmdenv --sim-time-limit=10s > /dev/null",
            ],
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
                "catalog_url": "https://omnetpp.org/download-items/GrADyS.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd gradys-0.5",
                "./gradys-simulations$BUILD_MODE_SUFFIX mobilityDrones-omnetpp.ini -n .:$INET_ROOT/src -c Wifi -u Cmdenv --sim-time-limit=1s > /dev/null",
            ],
            "required_projects": {"omnetpp": ["5.7.*", "5.6.*"], "inet": ["4.2.5"]},
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
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd tdma/src",
                "./tdma$BUILD_MODE_SUFFIX ../simulations/omnetpp.ini -n .:../simulations:$INET_ROOT/src -r 0 -u Cmdenv > /dev/null",
            ],
            "required_projects": {"omnetpp": ["5.7.*", "5.6.*"], "inet": ["4.2.5"]},
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
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd simulations/x2",
                "../../src/run_lte$BUILD_MODE_SUFFIX -c X2-MeshTopology -r 0 -u Cmdenv --**.pdcpRrc.ipBased=false --sim-time-limit=10s > /dev/null",
            ],
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
                "cp src/run_lte src/run_lte_dbg",
                "sed -i 's|libveins_inet.so|veins_inet|' src/run_lte_dbg",
                "sed -i 's|opp_run|opp_run_dbg|' src/run_lte_dbg",
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
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "opp_run$BUILD_MODE_SUFFIX -l lre_omnet -n .:$INET_ROOT/src -u Cmdenv > /dev/null",
            ],
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
                "cd .. && opp_makemake --make-so -f --deep -O out -o lre_omnet -KINET_PROJ=$INET_ROOT -I. -I$INET_ROOT/src -L$INET_ROOT/src -lINET\$D -Xlre-src/main",
                "make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"
            ],
            "clean_commands": ["make clean"],
        },

        {
            # DONE - no example simulation
            "name": "wifidirect_allinone", "version": "3.4",
            "nix_packages": ["python2"],
            "required_projects": {"omnetpp": ["5.0.*"]},
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/Wifi-Direct.html",
            },
            "smoke_test_commands": [
                # This projects doesn't contain any example simulations, so we test the project lib with an INET example
                """if [ "$BUILD_MODE" = "release" ]; then BUILD_MODE_SUFFIX="_release"; WIFIDIRECT_ALLINONE_LIB=$(echo $WIFIDIRECT_ALLINONE_ROOT/out/*-release/src/*INET*); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX=""; WIFIDIRECT_ALLINONE_LIB=$(echo $WIFIDIRECT_ALLINONE_ROOT/out/*-debug/src/*INET*); fi""",
                "cd examples/aodv",
                "opp_run$BUILD_MODE_SUFFIX -l $WIFIDIRECT_ALLINONE_LIB -n ../../src:.. omnetpp.ini -c IPv4ModerateFastMobility -u Cmdenv --sim-time-limit=10s > /dev/null",
            ],
            "download_url": "https://github.com/ashahin1/inet/archive/refs/tags/v3.4.0.tar.gz",
            "setenv_commands": [
            ],
            "patch_commands": [
                "sed -i.bak 's| python$| python2|' inet_featuretool",
                "sed -i.bak 's|info\\[\\]|info[0]|' src/inet/common/serializer/sctp/headers/sctphdr.h",
                "for f in $(grep -Rls 'defined(linux)'); do sed -i.bak 's|defined(linux)|defined(__linux__)|' $f; done",
                "for f in $(grep -Rl 'INT64_PRINTF_FORMAT'); do sed -i.bak 's|INT64_PRINTF_FORMAT|\"l\"|' $f; done",
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },
        
        {
            # DONE - we only build (and test) this in release
            "name": "libara_allinone", "version": "20150402",       # last commit of master branch as of time of writing
            "description": "Routing algorithms based on the Ant Colony Optimization (ACO) metaheuristic. This version downloads its own copy of INETMANET, and does not use one installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/libARA.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then cd simulations/eara && ./run.sh EARA0ALT12 --test > /dev/null; fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then echo 'Skipping test in debug mode, because currently the project only builds in release mode.'; fi""",
            ],
            "required_projects": {"omnetpp": ["4.5.*"]},
            "download_commands": [
                "git clone https://github.com/des-testbed/libara.git libara_allinone-20150402",
                "cd libara_allinone-20150402",
                "git reset --hard 5b40a41839167c6709d86400d41be51f1ce51781",
                "sed -i 's|git:\/\/|https:\/\/|g' .gitmodules",
                "cd inetmanet",
                "git submodule init",
                "git submodule update",
            ],
            "patch_commands": [
                """sed -i 's|if \[ $2 == "--debug" \]; then|if [ $2 == "--test" ]; then $RELATIVE_PATH_TO_ROOT/omnetpp/ara-sim -u Cmdenv -c $experimentName -n "$nedPath" omnetpp.ini -r 0 --sim-time-limit=10s; fi\\nif [ $2 == "--debug" ]; then|' simulations/run.sh""",
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
                                "echo 'Hint: in an example simulation folder, use the `./run.sh` command to run the example simulation. Note: this project is only available in release mode.'"],
            "build_commands": [
                "make all -j$NIX_BUILD_CORES MODE=release"
            ],
            "clean_commands": ["cd inetmanet && make clean && cd .. && make clean"],
        },

        {
            # DONE
            "name": "opendsme_allinone", "version": "20201110",     # last commit of master branch as of time of writing
            "description": "IEEE 802.15.4 Deterministic and Synchronous Multi-channel Extension. This version downloads its own copy of INET, and does not use one installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/OpenDSME.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd inet-dsme/simulations && opp_run$BUILD_MODE_SUFFIX -r 0 --seed-set=0 --repeat=1 --cmdenv-express-mode=false --vector-recording=false -u Cmdenv -c DSME -n .:../src:../../inet/examples:../../inet/src:../../inet/tutorials:.:../src -l ../../inet/src/INET -l ../src/inet-dsme -l ../../inet/src/INET -l ../src/inet-dsme -l ../../inet/src/INET -l ../src/inet-dsme --debug-on-errors=false example.ini --sim-time-limit=10s > /dev/null",
            ],
            "required_projects": {"omnetpp": ["5.4.*"]},
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
            "build_commands": ["cd inet && make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd ../inet-dsme/src && opp_makemake -f --deep --make-so -I../../inet/src -I../../inet/src/inet/common -I.. -KINET_PROJ=../../inet && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            # core-rg version, compatible with core4inet as well
            # TODO does this need patched inet so allinone?
            "name": "openflow", "version": "20231017",      # last commit of master branch as of time of writing
            "description": "OpenFlow Extension for INET Framework",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/Openflow.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "cd scenarios/usa && opp_run$BUILD_MODE_SUFFIX -l $OPENFLOW_ROOT/src/openflow -n $INET_ROOT/src:$OPENFLOW_ROOT/scenarios:.:../../src Scenario_USA_ARP_Ping_Drop.ini -u Cmdenv -r 0 --sim-time-limit=1s > /dev/null",
            ],
            "required_projects": {"omnetpp": ["5.5.1"], "inet": ["3.6.6"]},
            # there are no releases, so we use a commit from the master branch
            "download_url": "https://github.com/CoRE-RG/OpenFlow/archive/72fc3c2bcfb720087225728e130c06fac1c7f0f2.tar.gz",
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
            # DONE
            "name": "ndnomnet", "version": "20200914",      # last commit of master branch as of time of writing
            "description": "Named Data Networking framework for OMNeT++",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/NDNOMNeT.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then BUILD_MODE_SUFFIX="_release"; NDNOMNET_LIB=$(echo $NDNOMNET_ROOT/inet/out/*-release/src/*INET*); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX=""; NDNOMNET_LIB=$(echo $NDNOMNET_ROOT/inet/out/*-debug/src/*INET*); fi""",
                "cd inet/examples/ndn",
                "opp_run$BUILD_MODE_SUFFIX -l$NDNOMNET_LIB omnetpp.ini -n ../../src:..:. -c NdnDemo -u Cmdenv > /dev/null"
            ],
            "nix_packages": ["python2"],
            "required_projects": {"omnetpp": ["5.1.*"]},
            # we're using a hash from master because there are no releases
            "download_url": "https://github.com/amar-ox/NDNOMNeT/archive/d98f80a8b837858e00224e7a37aba35947058002.tar.gz",
            "patch_commands": [
                "cd inet",
                "sed -i.bak 's| python$| python2|' inet_featuretool",
                "sed -i.bak 's|info\\[\\]|info[0]|' src/inet/common/serializer/sctp/headers/sctphdr.h",
                "for f in $(grep -Rls 'defined(linux)'); do sed -i.bak 's|defined(linux)|defined(__linux__)|' $f; done",
                "sed -i.bak 's|->spp_hbinterval > 0|->spp_hbinterval->getNum() > 0|' src/inet/applications/packetdrill/PacketDrillApp.cc",
                "sed -i.bak 's|->spp_pathmaxrxt > 0|->spp_pathmaxrxt->getNum() > 0|' src/inet/applications/packetdrill/PacketDrillApp.cc",
                "for f in $(grep -Rl 'INT64_PRINTF_FORMAT'); do sed -i.bak 's|INT64_PRINTF_FORMAT|\"l\"|' $f; done",
                "sed -i.bak 's|precompiled.h|precompiled_$(MODE).h|' src/makefrag",
                """echo '#include "precompiled.h"' > src/inet/common/precompiled_debug.h""",
                """echo '#include "precompiled.h"' > src/inet/common/precompiled_release.h""",
                 "cp src/run_inet src/run_inet_dbg",
                "sed -i 's|opp_run|opp_run_dbg|' src/run_inet_dbg",

            ],
            "build_commands": ["cd inet && make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "setenv_commands": ["echo 'Hint: use the `./run` command in any example simulation folder.'"],
            "clean_commands": ["cd inet && make clean"],
        },
        
        {
            # DONE
            "name": "inet_hnrl", "version": "20100723",     # This is the master_20100723 release
            "description": "Fork of INET developed for hybrid networking research, providing new models in both optical and wireless networking areas and their hybrid.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/INET-HNRL.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then BUILD_MODE_SUFFIX=""; INET_HNRL_LIB=$(echo $INET_HNRL_ROOT/out/*-release/src/*inet*); OPP_RUN_BIN=$(echo $OMNETPP_ROOT/out/*-release/src/envir/opp_run); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX=""; INET_HNRL_LIB=$(echo $INET_HNRL_ROOT/out/*-debug/src/*inet*); OPP_RUN_BIN=$(echo $OMNETPP_ROOT/out/*-debug/src/envir/opp_run); fi""",
                "$OPP_RUN_BIN -l $INET_HNRL_LIB -n src:examples  -c ARPTest -u Cmdenv examples/ethernet/arptest/omnetpp.ini > /dev/null"
            ],
            "nix_packages": ["sqlite"],
            "required_projects": {"omnetpp": ["4.1.0"]}, # with 4.1.1 and 4.1.x: error: non-constant-expression cannot be narrowed from type 'uint32_t' (aka 'unsigned int') to 'int' in initializer list [-Wc++11-narrowing]
            "download_url": "https://github.com/kyeongsoo/inet-hnrl/archive/refs/tags/master_20100723.tar.gz",
            "patch_commands": [
                "sed -i 's|info\\[\\]|info[0]|' src/util/headerserializers/headers/sctp.h",
                "sed -i 's|addr.sin_len|// addr.sin_len|' src/linklayer/ext/*.cc",  # ugly hack? this is needed on apple
                "sed -i 's|machine/endian|endian|' src/util/headerserializers/headers/defs.h",
                "chmod +x examples/rundemo",
            ],
            "setenv_commands": ["export SQLITE_LIB=${pkgs.sqlite}/lib"],
            "build_commands": ["make makefiles && make all -j$NIX_BUILD_CORES MODE=$BUILD_MODE CFLAGS='-std=c++14 -fpermissive -fPIC'"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "icancloud", "version": "1.0",
            "description": "Cloud Computing Systems",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/iCanCloud.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then BUILD_MODE_SUFFIX="_release"; ICANCLOUD_LIB=$(echo $ICANCLOUD_ROOT/out/clang-release/src/*iCanCloud*); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX=""; ICANCLOUD_LIB=$(echo $ICANCLOUD_ROOT/out/clang-debug/src/*iCanCloud*); fi""",
                "cd simulations/Cloud_A",
                "opp_run$BUILD_MODE_SUFFIX -l $ICANCLOUD_LIB -n../..:../../simulations:$INET_ROOT/src:../../src -u Cmdenv --sim-time-limit=10s > /dev/null",
            ],
            "required_projects": {"omnetpp": ["4.6.*"], "inet": ["2.5.0"]},
            "download_url": "http://sourceforge.net/projects/icancloudsim/files/iCanCloud_v1.0_20150216.tgz/download",
            "patch_commands": [
                "sed -i 's|unsigned int requestSize|int requestSize|g' src/Base/Messages/SMS/SMS_MainMemory.cc",
                "sed -i 's|ned-path|#net-path|g' simulations/*/omnetpp.ini",
                "sed -i 's|$DIR/../iCanCloud|$DIR/iCanCloud|g' src/run_iCanCloud",
                "sed -i 's|/simulations|/simulations:$INET_ROOT/src|g' src/run_iCanCloud",
            ],
            "setenv_commands": ["echo 'Hint: use the `./run` command in an example simulation folder.'"],
            "build_commands": ["cd src && opp_makemake -f --deep --make-so -O out -o iCanCloud -pINET -I$INET_ROOT/src/linklayer/ieee80211/radio -I$INET_ROOT/src/networklayer/routing/aodv -I$INET_ROOT/src/networklayer/common -I$INET_ROOT/src -I$INET_ROOT/src/networklayer/icmpv6 -I$INET_ROOT/src/world/obstacles -I$INET_ROOT/src/networklayer/xmipv6 -I$INET_ROOT/src/networklayer/contract -I$INET_ROOT/src/networklayer/autorouting/ipv4 -I$INET_ROOT/src/util -I$INET_ROOT/src/linklayer/common -I$INET_ROOT/src/transport/contract -I$INET_ROOT/src/status -I$INET_ROOT/src/linklayer/radio/propagation -I$INET_ROOT/src/linklayer/ieee80211/radio/errormodel -I$INET_ROOT/src/linklayer/radio -I$INET_ROOT/src/util/headerserializers/tcp -I$INET_ROOT/src/networklayer/ipv4 -I$INET_ROOT/src/mobility/contract -I$INET_ROOT/src/util/headerserializers/ipv4 -I$INET_ROOT/src/base -I$INET_ROOT/src/util/headerserializers -I$INET_ROOT/src/world/radio -I$INET_ROOT/src/linklayer/ieee80211/mac -I$INET_ROOT/src/networklayer/ipv6 -I$INET_ROOT/src/transport/sctp -I$INET_ROOT/src/util/headerserializers/udp -I$INET_ROOT/src/networklayer/ipv6tunneling -I$INET_ROOT/src/util/headerserializers/ipv6 -I$INET_ROOT/src/applications/pingapp -I$INET_ROOT/src/battery/models -I$INET_ROOT/src/linklayer/contract -I$INET_ROOT/src/util/headerserializers/sctp -I$INET_ROOT/src/transport/tcp_common -I$INET_ROOT/src/networklayer/arp -I$INET_ROOT/src/transport/udp -L$INET_ROOT/out/\$\(CONFIGNAME\)/src -lz -linet -DINET_IMPORT -KINET_PROJ=$INET_ROOT && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE - compiles and runs, but needs weather API access to test
            "name": "os3", "version": "1.0",
            "description": "Open Source Satellite Simulator",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/OS3.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then BUILD_MODE_SUFFIX="_release"; OS3_LIB=$(echo $OS3_ROOT/out/*-release/src/*cni-os3*); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX=""; OS3_LIB=$(echo $OS3_ROOT/out/*-debug/src/*cni-os3*); fi""",
                "opp_run$BUILD_MODE_SUFFIX -l $OS3_LIB -n simulations:src:$INET_ROOT/src:$INET_ROOT/examples $INET_ROOT/examples/ethernet/arptest/omnetpp.ini > /dev/null"
            ],
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
            # DONE - ok
            # UPDATE: error in example sim in dbg; only tested in release
            # TODO: what error?
            "name": "gptp", "version": "20200311",      # last commit of master branch as of time of writing
            "description": "IEEE 802.1AS gPTP for Clock Synchronization",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/gPTP.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then cd IEEE8021AS/simulations && ../src/IEEE8021AS -n $INET_ROOT/src:.:../src -c Network_daisy_chain -u Cmdenv --sim-time-limit=10s > /dev/null; fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then echo 'Skipping test in debug mode, because the example simulation doesn't work in debug due to an error.'; fi""",
            ],
            "required_projects": {"omnetpp": ["5.2.*"], "inet": ["3.6.3"]},
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
            # DONE
            "name": "streetlightsim", "version": "1.0",
            "description": "Research project for evaluating Autonomous and Adaptive Street Lighting Schemes based on Road User's presence detection over wireless sensor networks.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/StreetlightSim.html",
            },
            "required_projects": {"omnetpp": ["4.2.2"]},
            "nix_packages": ["sumo", "python2"],
            "download_url": "https://github.com/omnetpp-models/archive/releases/download/archive/streetlightsim.tar.gz",
            "smoke_test_commands": [
                "WSNROUTING_BIN=$(echo $STREETLIGHTSIM_ROOT/out/*-$BUILD_MODE/examples/WSNRouting/WSNRouting)",
                "cd examples/WSNRouting && $WSNROUTING_BIN -u Cmdenv -c flooding -r 0 > /dev/null",
            ],
            "build_commands": ["make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE - release only; this project links with the inet release libs
            "name": "quagga", "version": "20090803",
            "description": "Port of the Quagga routing daemon into the INET Framework",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/INET-Quagga.html",
            },
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then cd examples/simpleTest && ./run -c OSPF1 -u Cmdenv --sim-time-limit=10s > /dev/null; fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then echo 'Skipping test in debug mode, because currently this project is only built in release mode.'; fi""",
            ],
            "required_projects": {"omnetpp": ["4.1.*"], "inet": ["20100323"]},
            "download_url": "https://github.com/inet-framework/inet-quagga/archive/refs/tags/quagga-20090803.tar.gz",
            "patch_commands": [
                "sed -i 's|../../inet|$(INET_ROOT)|g' Makefile",
                "sed -i 's|-L$(INET_ROOT)/out/$$(CONFIGNAME)/src|-L$(INET_ROOT)/out/gcc-release/src|g' Makefile",
                "sed -i 's|libzebra.a|libzebra.a -o inet-quagga|g' Makefile",
                "sed -i 's|TCPOut|tcpOut|g' src/QuaggaRouter.ned",
                "sed -i 's|$DIR/../../inet|$INET_ROOT|g' src/run_inet-quagga",
                "sed -i 's|include ../../../../Makefile.inc|#include ../../../../Makefile.inc|g' src/quaggasrc/*/*/Makefile",
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=release && rm src/quagga-20090803"],     # rm is a kludge
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "tcp_fit_illinois", "version": "20150828",      # last commit of master branch as of time of writing
            "description": "TCP-Fit and TCP-Illinois models for OMNeT++ and INET",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/TCP-Fit-Illinois.html",
            },
            "smoke_test_commands": [
                # There is no example simulation in this project, so we copy a TCP example from inet and overwrite the TCP congestion control algorithm type
                "cp $INET_ROOT/examples/inet/tcpwindowscale/omnetpp.ini $INET_ROOT/examples/inet/tcpwindowscale/test.ini",
                """echo '**.tcpAlgorithmClass="TCPFit"' >> $INET_ROOT/examples/inet/tcpwindowscale/test.ini""",
                """if [ "$BUILD_MODE" = "debug" ]; then TCP_BIN=$(echo $TCP_FIT_ILLINOIS_ROOT/out/*-debug/tcp_fit_illinois); fi""",
                """if [ "$BUILD_MODE" = "release" ]; then TCP_BIN=$(echo $TCP_FIT_ILLINOIS_ROOT/out/*-release/tcp_fit_illinois); fi""",
                "$TCP_BIN $INET_ROOT/examples/inet/tcpwindowscale/test.ini -n $INET_ROOT/src:$INET_ROOT/examples -u Cmdenv -c WS_enabled --sim-time-limit=10s > /dev/null",
                "rm $INET_ROOT/examples/inet/tcpwindowscale/test.ini",
            ],
            "required_projects": {"omnetpp": ["4.6.*"], "inet": ["2.5.0"]},
            "setenv_commands": [
                "export INET_PROJ=$INET_ROOT",
            ],
            "download_url": "https://github.com/SpyrosMArtel/TCP-Fit-Illinois/archive/ba5e56f0bd13d6b40b40892ac61d82d4f9a7ac92.tar.gz",
            "build_commands": ["opp_makemake -f --deep -o tcp_fit_illinois -KINET_PROJ=$INET_PROJ -DINET_IMPORT -I. -I$INET_ROOT/src/applications -I$INET_ROOT/src/applications/common -I$INET_ROOT/src/applications/dhcp -I$INET_ROOT/src/applications/ethernet -I$INET_ROOT/src/applications/generic -I$INET_ROOT/src/applications/httptools -I$INET_ROOT/src/applications/netperfmeter -I$INET_ROOT/src/applications/pingapp -I$INET_ROOT/src/applications/rtpapp -I$INET_ROOT/src/applications/sctpapp -I$INET_ROOT/src/applications/tcpapp -I$INET_ROOT/src/applications/traci -I$INET_ROOT/src/applications/udpapp -I$INET_ROOT/src/applications/voip -I$INET_ROOT/src/base -I$INET_ROOT/src/battery -I$INET_ROOT/src/battery/models -I$INET_ROOT/src/linklayer -I$INET_ROOT/src/linklayer/common -I$INET_ROOT/src/linklayer/configurator -I$INET_ROOT/src/linklayer/contract -I$INET_ROOT/src/linklayer/ethernet -I$INET_ROOT/src/linklayer/ethernet/switch -I$INET_ROOT/src/linklayer/ext -I$INET_ROOT/src/linklayer/idealwireless -I$INET_ROOT/src/linklayer/ieee80211 -I$INET_ROOT/src/linklayer/ieee80211/mac -I$INET_ROOT/src/linklayer/ieee80211/mgmt -I$INET_ROOT/src/linklayer/ieee80211/radio -I$INET_ROOT/src/linklayer/ieee80211/radio/errormodel -I$INET_ROOT/src/linklayer/ieee8021d -I$INET_ROOT/src/linklayer/ieee8021d/common -I$INET_ROOT/src/linklayer/ieee8021d/relay -I$INET_ROOT/src/linklayer/ieee8021d/rstp -I$INET_ROOT/src/linklayer/ieee8021d/stp -I$INET_ROOT/src/linklayer/ieee8021d/tester -I$INET_ROOT/src/linklayer/loopback -I$INET_ROOT/src/linklayer/ppp -I$INET_ROOT/src/linklayer/queue -I$INET_ROOT/src/linklayer/radio -I$INET_ROOT/src/linklayer/radio/propagation -I$INET_ROOT/src/mobility -I$INET_ROOT/src/mobility/common -I$INET_ROOT/src/mobility/contract -I$INET_ROOT/src/mobility/group -I$INET_ROOT/src/mobility/single -I$INET_ROOT/src/mobility/static -I$INET_ROOT/src/networklayer -I$INET_ROOT/src/networklayer/arp -I$INET_ROOT/src/networklayer/autorouting -I$INET_ROOT/src/networklayer/autorouting/ipv4 -I$INET_ROOT/src/networklayer/autorouting/ipv6 -I$INET_ROOT/src/networklayer/bgpv4 -I$INET_ROOT/src/networklayer/bgpv4/BGPMessage -I$INET_ROOT/src/networklayer/common -I$INET_ROOT/src/networklayer/contract -I$INET_ROOT/src/networklayer/diffserv -I$INET_ROOT/src/networklayer/icmpv6 -I$INET_ROOT/src/networklayer/internetcloud -I$INET_ROOT/src/networklayer/ipv4 -I$INET_ROOT/src/networklayer/ipv6 -I$INET_ROOT/src/networklayer/ipv6tunneling -I$INET_ROOT/src/networklayer/ldp -I$INET_ROOT/src/networklayer/manetrouting -I$INET_ROOT/src/networklayer/manetrouting/aodv-uu -I$INET_ROOT/src/networklayer/manetrouting/aodv-uu/aodv-uu -I$INET_ROOT/src/networklayer/manetrouting/base -I$INET_ROOT/src/networklayer/manetrouting/batman -I$INET_ROOT/src/networklayer/manetrouting/batman/batmand -I$INET_ROOT/src/networklayer/manetrouting/batman/batmand/orig -I$INET_ROOT/src/networklayer/manetrouting/dsdv -I$INET_ROOT/src/networklayer/manetrouting/dsr -I$INET_ROOT/src/networklayer/manetrouting/dsr/dsr-uu -I$INET_ROOT/src/networklayer/manetrouting/dymo -I$INET_ROOT/src/networklayer/manetrouting/dymo/dymoum -I$INET_ROOT/src/networklayer/manetrouting/dymo_fau -I$INET_ROOT/src/networklayer/manetrouting/olsr -I$INET_ROOT/src/networklayer/mpls -I$INET_ROOT/src/networklayer/ospfv2 -I$INET_ROOT/src/networklayer/ospfv2/interface -I$INET_ROOT/src/networklayer/ospfv2/messagehandler -I$INET_ROOT/src/networklayer/ospfv2/neighbor -I$INET_ROOT/src/networklayer/ospfv2/router -I$INET_ROOT/src/networklayer/routing -I$INET_ROOT/src/networklayer/routing/aodv -I$INET_ROOT/src/networklayer/routing/dymo -I$INET_ROOT/src/networklayer/routing/gpsr -I$INET_ROOT/src/networklayer/routing/rip -I$INET_ROOT/src/networklayer/rsvp_te -I$INET_ROOT/src/networklayer/ted -I$INET_ROOT/src/networklayer/xmipv6 -I$INET_ROOT/src/nodes -I$INET_ROOT/src/nodes/aodv -I$INET_ROOT/src/nodes/bgp -I$INET_ROOT/src/nodes/dymo -I$INET_ROOT/src/nodes/ethernet -I$INET_ROOT/src/nodes/gpsr -I$INET_ROOT/src/nodes/httptools -I$INET_ROOT/src/nodes/inet -I$INET_ROOT/src/nodes/internetcloud -I$INET_ROOT/src/nodes/ipv6 -I$INET_ROOT/src/nodes/mpls -I$INET_ROOT/src/nodes/ospfv2 -I$INET_ROOT/src/nodes/rip -I$INET_ROOT/src/nodes/rtp -I$INET_ROOT/src/nodes/wireless -I$INET_ROOT/src/nodes/xmipv6 -I$INET_ROOT/src/status -I$INET_ROOT/src/transport -I$INET_ROOT/src/transport/contract -I$INET_ROOT/src/transport/rtp -I$INET_ROOT/src/transport/rtp/profiles -I$INET_ROOT/src/transport/rtp/profiles/avprofile -I$INET_ROOT/src/transport/sctp -I$INET_ROOT/src/transport/tcp -I$INET_ROOT/src/transport/tcp/flavours -I$INET_ROOT/src/transport/tcp/queues -I$INET_ROOT/src/transport/tcp_common -I$INET_ROOT/src/transport/udp -I$INET_ROOT/src/util -I$INET_ROOT/src/util/headerserializers -I$INET_ROOT/src/util/headerserializers/headers -I$INET_ROOT/src/util/headerserializers/ipv4 -I$INET_ROOT/src/util/headerserializers/ipv4/headers -I$INET_ROOT/src/util/headerserializers/ipv6 -I$INET_ROOT/src/util/headerserializers/ipv6/headers -I$INET_ROOT/src/util/headerserializers/sctp -I$INET_ROOT/src/util/headerserializers/sctp/headers -I$INET_ROOT/src/util/headerserializers/tcp -I$INET_ROOT/src/util/headerserializers/tcp/headers -I$INET_ROOT/src/util/headerserializers/udp -I$INET_ROOT/src/util/headerserializers/udp/headers -I$INET_ROOT/src/util/messageprinters -I$INET_ROOT/src/world -I$INET_ROOT/src/world/annotations -I$INET_ROOT/src/world/httptools -I$INET_ROOT/src/world/obstacles -I$INET_ROOT/src/world/radio -I$INET_ROOT/src/world/scenario -I$INET_ROOT/src/world/traci -L$(echo $INET_ROOT/out/*-$BUILD_MODE/src) -linet && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },
        
        {
            # DONE
            "name": "dns", "version": "20150911",     # last commit of master branch as of time of writing
            "description": "Provides models to simulate DNS and mDNS (multicast DNS) traffic within INET",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/INET-DNS.html",
            },
            "required_projects": {"omnetpp": ["4.6.*"], "inet": ["3.1.0"]},
            "download_url": "https://github.com/saenridanra/inet-dns-extension/archive/1fa452792f954297f2dc7ede3b699e73ca17c0c1.tar.gz",
            "smoke_test_commands": [
                "cd src/networks/stateless_network",
                """if [ "$BUILD_MODE" = "debug" ]; then DNS_BIN=$(echo $DNS_ROOT/out/*-debug/src/inet_dns*); fi""",
                """if [ "$BUILD_MODE" = "release" ]; then DNS_BIN=$(echo $DNS_ROOT/out/*-release/src/inet_dns*); fi""",
                "$DNS_BIN omnetpp.ini -n ../..:$INET_ROOT/src --sim-time-limit=10s -u Cmdenv > /dev/null",
            ],
            "patch_commands": [
                "sed -i 's|INETDefs.h|inet/common/INETDefs.h|g' src/*/*/*.h",
            ],
            "setenv_commands": ["echo 'Hint: Use the `../../inet_dns_extension omnetpp.ini -n ../..:$INET_ROOT/src` command in an example simulation folder to run the example simulation.'"],
            "build_commands": ["cd src && opp_makemake -f --deep -o inet_dns_extension -O out -L$(echo $INET_ROOT/out/*-$BUILD_MODE/src) -lINET -DINET_IMPORT -KINET_PROJ=$INET_ROOT -I$INET_ROOT/src/inet -I$INET_ROOT/src/inet/applications -I$INET_ROOT/src/inet/applications/base -I$INET_ROOT/src/inet/applications/contract -I$INET_ROOT/src/inet/applications/dhcp -I$INET_ROOT/src/inet/applications/ethernet -I$INET_ROOT/src/inet/applications/generic -I$INET_ROOT/src/inet/applications/httptools -I$INET_ROOT/src/inet/applications/httptools/browser -I$INET_ROOT/src/inet/applications/httptools/common -I$INET_ROOT/src/inet/applications/httptools/configurator -I$INET_ROOT/src/inet/applications/httptools/server -I$INET_ROOT/src/inet/applications/netperfmeter -I$INET_ROOT/src/inet/applications/packetdrill -I$INET_ROOT/src/inet/applications/pingapp -I$INET_ROOT/src/inet/applications/rtpapp -I$INET_ROOT/src/inet/applications/sctpapp -I$INET_ROOT/src/inet/applications/tcpapp -I$INET_ROOT/src/inet/applications/tunapp -I$INET_ROOT/src/inet/applications/udpapp -I$INET_ROOT/src/inet/applications/voip -I$INET_ROOT/src/inet/applications/voipstream -I$INET_ROOT/src/inet/common -I$INET_ROOT/src/inet/common/figures -I$INET_ROOT/src/inet/common/geometry -I$INET_ROOT/src/inet/common/geometry/base -I$INET_ROOT/src/inet/common/geometry/common -I$INET_ROOT/src/inet/common/geometry/container -I$INET_ROOT/src/inet/common/geometry/object -I$INET_ROOT/src/inet/common/geometry/shape -I$INET_ROOT/src/inet/common/geometry/shape/polyhedron -I$INET_ROOT/src/inet/common/lifecycle -I$INET_ROOT/src/inet/common/mapping -I$INET_ROOT/src/inet/common/misc -I$INET_ROOT/src/inet/common/packet -I$INET_ROOT/src/inet/common/queue -I$INET_ROOT/src/inet/common/scenario -I$INET_ROOT/src/inet/common/serializer -I$INET_ROOT/src/inet/common/serializer/headers -I$INET_ROOT/src/inet/common/serializer/headerserializers -I$INET_ROOT/src/inet/common/serializer/headerserializers/arp -I$INET_ROOT/src/inet/common/serializer/headerserializers/ethernet -I$INET_ROOT/src/inet/common/serializer/headerserializers/ieee80211 -I$INET_ROOT/src/inet/common/serializer/headerserializers/ieee80211/headers -I$INET_ROOT/src/inet/common/serializer/ipv4 -I$INET_ROOT/src/inet/common/serializer/ipv4/headers -I$INET_ROOT/src/inet/common/serializer/ipv6 -I$INET_ROOT/src/inet/common/serializer/ipv6/headers -I$INET_ROOT/src/inet/common/serializer/sctp -I$INET_ROOT/src/inet/common/serializer/sctp/headers -I$INET_ROOT/src/inet/common/serializer/tcp -I$INET_ROOT/src/inet/common/serializer/tcp/headers -I$INET_ROOT/src/inet/common/serializer/udp -I$INET_ROOT/src/inet/common/serializer/udp/headers -I$INET_ROOT/src/inet/environment -I$INET_ROOT/src/inet/environment/common -I$INET_ROOT/src/inet/environment/contract -I$INET_ROOT/src/inet/environment/objectcache -I$INET_ROOT/src/inet/linklayer -I$INET_ROOT/src/inet/linklayer/base -I$INET_ROOT/src/inet/linklayer/bmac -I$INET_ROOT/src/inet/linklayer/common -I$INET_ROOT/src/inet/linklayer/configurator -I$INET_ROOT/src/inet/linklayer/contract -I$INET_ROOT/src/inet/linklayer/csma -I$INET_ROOT/src/inet/linklayer/ethernet -I$INET_ROOT/src/inet/linklayer/ethernet/switch -I$INET_ROOT/src/inet/linklayer/ext -I$INET_ROOT/src/inet/linklayer/ideal -I$INET_ROOT/src/inet/linklayer/ieee80211 -I$INET_ROOT/src/inet/linklayer/ieee80211/mac -I$INET_ROOT/src/inet/linklayer/ieee80211/mgmt -I$INET_ROOT/src/inet/linklayer/ieee80211/newmac -I$INET_ROOT/src/inet/linklayer/ieee802154 -I$INET_ROOT/src/inet/linklayer/ieee8021d -I$INET_ROOT/src/inet/linklayer/ieee8021d/common -I$INET_ROOT/src/inet/linklayer/ieee8021d/relay -I$INET_ROOT/src/inet/linklayer/ieee8021d/rstp -I$INET_ROOT/src/inet/linklayer/ieee8021d/stp -I$INET_ROOT/src/inet/linklayer/ieee8021d/tester -I$INET_ROOT/src/inet/linklayer/lmac -I$INET_ROOT/src/inet/linklayer/loopback -I$INET_ROOT/src/inet/linklayer/ppp -I$INET_ROOT/src/inet/linklayer/tun -I$INET_ROOT/src/inet/mobility -I$INET_ROOT/src/inet/mobility/base -I$INET_ROOT/src/inet/mobility/contract -I$INET_ROOT/src/inet/mobility/group -I$INET_ROOT/src/inet/mobility/single -I$INET_ROOT/src/inet/mobility/static -I$INET_ROOT/src/inet/networklayer -I$INET_ROOT/src/inet/networklayer/arp -I$INET_ROOT/src/inet/networklayer/arp/generic -I$INET_ROOT/src/inet/networklayer/arp/ipv4 -I$INET_ROOT/src/inet/networklayer/base -I$INET_ROOT/src/inet/networklayer/common -I$INET_ROOT/src/inet/networklayer/configurator -I$INET_ROOT/src/inet/networklayer/configurator/base -I$INET_ROOT/src/inet/networklayer/configurator/contract -I$INET_ROOT/src/inet/networklayer/configurator/generic -I$INET_ROOT/src/inet/networklayer/configurator/ipv4 -I$INET_ROOT/src/inet/networklayer/configurator/ipv6 -I$INET_ROOT/src/inet/networklayer/contract -I$INET_ROOT/src/inet/networklayer/contract/generic -I$INET_ROOT/src/inet/networklayer/contract/ipv4 -I$INET_ROOT/src/inet/networklayer/contract/ipv6 -I$INET_ROOT/src/inet/networklayer/diffserv -I$INET_ROOT/src/inet/networklayer/flood -I$INET_ROOT/src/inet/networklayer/generic -I$INET_ROOT/src/inet/networklayer/icmpv6 -I$INET_ROOT/src/inet/networklayer/internetcloud -I$INET_ROOT/src/inet/networklayer/ipv4 -I$INET_ROOT/src/inet/networklayer/ipv6 -I$INET_ROOT/src/inet/networklayer/ipv6tunneling -I$INET_ROOT/src/inet/networklayer/ldp -I$INET_ROOT/src/inet/networklayer/mpls -I$INET_ROOT/src/inet/networklayer/multi -I$INET_ROOT/src/inet/networklayer/probabilistic -I$INET_ROOT/src/inet/networklayer/rsvp_te -I$INET_ROOT/src/inet/networklayer/ted -I$INET_ROOT/src/inet/networklayer/wiseroute -I$INET_ROOT/src/inet/networklayer/xmipv6 -I$INET_ROOT/src/inet/node -I$INET_ROOT/src/inet/node/aodv -I$INET_ROOT/src/inet/node/bgp -I$INET_ROOT/src/inet/node/dymo -I$INET_ROOT/src/inet/node/ethernet -I$INET_ROOT/src/inet/node/gpsr -I$INET_ROOT/src/inet/node/httptools -I$INET_ROOT/src/inet/node/inet -I$INET_ROOT/src/inet/node/internetcloud -I$INET_ROOT/src/inet/node/ipv6 -I$INET_ROOT/src/inet/node/mpls -I$INET_ROOT/src/inet/node/ospfv2 -I$INET_ROOT/src/inet/node/packetdrill -I$INET_ROOT/src/inet/node/rip -I$INET_ROOT/src/inet/node/rtp -I$INET_ROOT/src/inet/node/wireless -I$INET_ROOT/src/inet/node/xmipv6 -I$INET_ROOT/src/inet/physicallayer -I$INET_ROOT/src/inet/physicallayer/analogmodel -I$INET_ROOT/src/inet/physicallayer/analogmodel/bitlevel -I$INET_ROOT/src/inet/physicallayer/analogmodel/packetlevel -I$INET_ROOT/src/inet/physicallayer/antenna -I$INET_ROOT/src/inet/physicallayer/apskradio -I$INET_ROOT/src/inet/physicallayer/apskradio/bitlevel -I$INET_ROOT/src/inet/physicallayer/apskradio/bitlevel/errormodel -I$INET_ROOT/src/inet/physicallayer/apskradio/packetlevel -I$INET_ROOT/src/inet/physicallayer/apskradio/packetlevel/errormodel -I$INET_ROOT/src/inet/physicallayer/backgroundnoise -I$INET_ROOT/src/inet/physicallayer/base -I$INET_ROOT/src/inet/physicallayer/base/bitlevel -I$INET_ROOT/src/inet/physicallayer/base/packetlevel -I$INET_ROOT/src/inet/physicallayer/common -I$INET_ROOT/src/inet/physicallayer/common/bitlevel -I$INET_ROOT/src/inet/physicallayer/common/packetlevel -I$INET_ROOT/src/inet/physicallayer/communicationcache -I$INET_ROOT/src/inet/physicallayer/contract -I$INET_ROOT/src/inet/physicallayer/contract/bitlevel -I$INET_ROOT/src/inet/physicallayer/contract/packetlevel -I$INET_ROOT/src/inet/physicallayer/energyconsumer -I$INET_ROOT/src/inet/physicallayer/errormodel -I$INET_ROOT/src/inet/physicallayer/errormodel/bitlevel -I$INET_ROOT/src/inet/physicallayer/errormodel/packetlevel -I$INET_ROOT/src/inet/physicallayer/idealradio -I$INET_ROOT/src/inet/physicallayer/ieee80211 -I$INET_ROOT/src/inet/physicallayer/ieee80211/bitlevel -I$INET_ROOT/src/inet/physicallayer/ieee80211/bitlevel/errormodel -I$INET_ROOT/src/inet/physicallayer/ieee80211/mode -I$INET_ROOT/src/inet/physicallayer/ieee80211/packetlevel -I$INET_ROOT/src/inet/physicallayer/ieee80211/packetlevel/errormodel -I$INET_ROOT/src/inet/physicallayer/ieee802154 -I$INET_ROOT/src/inet/physicallayer/ieee802154/bitlevel -I$INET_ROOT/src/inet/physicallayer/ieee802154/packetlevel -I$INET_ROOT/src/inet/physicallayer/modulation -I$INET_ROOT/src/inet/physicallayer/neighborcache -I$INET_ROOT/src/inet/physicallayer/obstacleloss -I$INET_ROOT/src/inet/physicallayer/pathloss -I$INET_ROOT/src/inet/physicallayer/propagation -I$INET_ROOT/src/inet/power -I$INET_ROOT/src/inet/power/base -I$INET_ROOT/src/inet/power/consumer -I$INET_ROOT/src/inet/power/contract -I$INET_ROOT/src/inet/power/generator -I$INET_ROOT/src/inet/power/storage -I$INET_ROOT/src/inet/routing -I$INET_ROOT/src/inet/routing/aodv -I$INET_ROOT/src/inet/routing/bgpv4 -I$INET_ROOT/src/inet/routing/bgpv4/BGPMessage -I$INET_ROOT/src/inet/routing/contract -I$INET_ROOT/src/inet/routing/dymo -I$INET_ROOT/src/inet/routing/extras -I$INET_ROOT/src/inet/routing/extras/aodv-uu -I$INET_ROOT/src/inet/routing/extras/aodv-uu/aodv-uu -I$INET_ROOT/src/inet/routing/extras/base -I$INET_ROOT/src/inet/routing/extras/batman -I$INET_ROOT/src/inet/routing/extras/batman/batmand -I$INET_ROOT/src/inet/routing/extras/batman/batmand/orig -I$INET_ROOT/src/inet/routing/extras/dsdv -I$INET_ROOT/src/inet/routing/extras/dsr -I$INET_ROOT/src/inet/routing/extras/dsr/dsr-uu -I$INET_ROOT/src/inet/routing/extras/dymo -I$INET_ROOT/src/inet/routing/extras/dymo/dymoum -I$INET_ROOT/src/inet/routing/extras/dymo_fau -I$INET_ROOT/src/inet/routing/extras/olsr -I$INET_ROOT/src/inet/routing/gpsr -I$INET_ROOT/src/inet/routing/ospfv2 -I$INET_ROOT/src/inet/routing/ospfv2/interface -I$INET_ROOT/src/inet/routing/ospfv2/messagehandler -I$INET_ROOT/src/inet/routing/ospfv2/neighbor -I$INET_ROOT/src/inet/routing/ospfv2/router -I$INET_ROOT/src/inet/routing/pim -I$INET_ROOT/src/inet/routing/pim/modes -I$INET_ROOT/src/inet/routing/pim/tables -I$INET_ROOT/src/inet/routing/rip -I$INET_ROOT/src/inet/transportlayer -I$INET_ROOT/src/inet/transportlayer/base -I$INET_ROOT/src/inet/transportlayer/contract -I$INET_ROOT/src/inet/transportlayer/contract/sctp -I$INET_ROOT/src/inet/transportlayer/contract/tcp -I$INET_ROOT/src/inet/transportlayer/contract/udp -I$INET_ROOT/src/inet/transportlayer/rtp -I$INET_ROOT/src/inet/transportlayer/rtp/profiles -I$INET_ROOT/src/inet/transportlayer/rtp/profiles/avprofile -I$INET_ROOT/src/inet/transportlayer/sctp -I$INET_ROOT/src/inet/transportlayer/tcp -I$INET_ROOT/src/inet/transportlayer/tcp/flavours -I$INET_ROOT/src/inet/transportlayer/tcp/queues -I$INET_ROOT/src/inet/transportlayer/tcp_common -I$INET_ROOT/src/inet/transportlayer/tcp_lwip -I$INET_ROOT/src/inet/transportlayer/tcp_lwip/lwip -I$INET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/core -I$INET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/include -I$INET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/include/arch -I$INET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/include/ipv4 -I$INET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/include/ipv4/lwip -I$INET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/include/ipv6 -I$INET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/include/ipv6/lwip -I$INET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/include/lwip -I$INET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/include/netif -I$INET_ROOT/src/inet/transportlayer/tcp_lwip/queues -I$INET_ROOT/src/inet/transportlayer/tcp_nsc -I$INET_ROOT/src/inet/transportlayer/tcp_nsc/queues -I$INET_ROOT/src/inet/transportlayer/udp -Imessages -Inetworks -Icommon -Iapplications -Iutils -I$INET_ROOT/src && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE - only tested in debug (segfault in release); built in both
            "name": "obs", "version": "20130114",       # last commit of master branch as of time of writing
            "description": "Set of modules to simulate Optical Burst Switching networks in the OMNeT++ framework",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/OBS.html",
            },
            "required_projects": {"omnetpp": ["4.2.2", "4.2.1", "4.2.0"], "inet": ["2.2.0"]},
            "download_url": "https://github.com/mikelizal/OBSmodules/archive/704b685085a6cd8931521c0e052cd54c79327be7.tar.gz",
            "smoke_test_commands": [
                "cd Examples/BurstifierTest",
                """if [ "$BUILD_MODE" = "debug" ]; then OBS_BIN=$(echo $OBS_ROOT/out/*-debug/src/obs); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then $OBS_BIN -n ../..:$INET_ROOT/src -c config0 -u Cmdenv omnetpp.ini > /dev/null; fi""",
                """if [ "$BUILD_MODE" = "release" ]; then echo 'Skipping test in release mode due to segfault in debug mode.'; fi""",
            ],
            "build_commands": ["cd src && opp_makemake -f --deep -o obs -O out -KINET_PROJ=$INET_ROOT -DINET_IMPORT -L$(echo $INET_ROOT/out/*-$BUILD_MODE/src) -I. -I$INET_ROOT/src -I$INET_ROOT/src/applications -I$INET_ROOT/src/applications/dhcp -I$INET_ROOT/src/applications/ethernet -I$INET_ROOT/src/applications/generic -I$INET_ROOT/src/applications/httptools -I$INET_ROOT/src/applications/pingapp -I$INET_ROOT/src/applications/rtpapp -I$INET_ROOT/src/applications/sctpapp -I$INET_ROOT/src/applications/tcpapp -I$INET_ROOT/src/applications/traci -I$INET_ROOT/src/applications/udpapp -I$INET_ROOT/src/applications/voip -I$INET_ROOT/src/base -I$INET_ROOT/src/battery -I$INET_ROOT/src/battery/models -I$INET_ROOT/src/linklayer -I$INET_ROOT/src/linklayer/common -I$INET_ROOT/src/linklayer/contract -I$INET_ROOT/src/linklayer/ethernet -I$INET_ROOT/src/linklayer/ethernet/switch -I$INET_ROOT/src/linklayer/ext -I$INET_ROOT/src/linklayer/idealwireless -I$INET_ROOT/src/linklayer/ieee80211 -I$INET_ROOT/src/linklayer/ieee80211/mac -I$INET_ROOT/src/linklayer/ieee80211/mgmt -I$INET_ROOT/src/linklayer/ieee80211/radio -I$INET_ROOT/src/linklayer/ieee80211/radio/errormodel -I$INET_ROOT/src/linklayer/loopback -I$INET_ROOT/src/linklayer/ppp -I$INET_ROOT/src/linklayer/queue -I$INET_ROOT/src/linklayer/radio -I$INET_ROOT/src/linklayer/radio/propagation -I$INET_ROOT/src/mobility -I$INET_ROOT/src/mobility/models -I$INET_ROOT/src/networklayer -I$INET_ROOT/src/networklayer/arp -I$INET_ROOT/src/networklayer/autorouting -I$INET_ROOT/src/networklayer/autorouting/ipv4 -I$INET_ROOT/src/networklayer/autorouting/ipv6 -I$INET_ROOT/src/networklayer/bgpv4 -I$INET_ROOT/src/networklayer/bgpv4/BGPMessage -I$INET_ROOT/src/networklayer/common -I$INET_ROOT/src/networklayer/contract -I$INET_ROOT/src/networklayer/diffserv -I$INET_ROOT/src/networklayer/icmpv6 -I$INET_ROOT/src/networklayer/internetcloud -I$INET_ROOT/src/networklayer/ipv4 -I$INET_ROOT/src/networklayer/ipv6 -I$INET_ROOT/src/networklayer/ipv6tunneling -I$INET_ROOT/src/networklayer/ldp -I$INET_ROOT/src/networklayer/manetrouting -I$INET_ROOT/src/networklayer/manetrouting/aodv -I$INET_ROOT/src/networklayer/manetrouting/aodv/aodv-uu -I$INET_ROOT/src/networklayer/manetrouting/base -I$INET_ROOT/src/networklayer/manetrouting/batman -I$INET_ROOT/src/networklayer/manetrouting/batman/batmand -I$INET_ROOT/src/networklayer/manetrouting/batman/batmand/orig -I$INET_ROOT/src/networklayer/manetrouting/dsdv -I$INET_ROOT/src/networklayer/manetrouting/dsr -I$INET_ROOT/src/networklayer/manetrouting/dsr/dsr-uu -I$INET_ROOT/src/networklayer/manetrouting/dymo -I$INET_ROOT/src/networklayer/manetrouting/dymo/dymoum -I$INET_ROOT/src/networklayer/manetrouting/dymo_fau -I$INET_ROOT/src/networklayer/manetrouting/olsr -I$INET_ROOT/src/networklayer/mpls -I$INET_ROOT/src/networklayer/ospfv2 -I$INET_ROOT/src/networklayer/ospfv2/interface -I$INET_ROOT/src/networklayer/ospfv2/messagehandler -I$INET_ROOT/src/networklayer/ospfv2/neighbor -I$INET_ROOT/src/networklayer/ospfv2/router -I$INET_ROOT/src/networklayer/rsvp_te -I$INET_ROOT/src/networklayer/ted -I$INET_ROOT/src/networklayer/xmipv6 -I$INET_ROOT/src/nodes -I$INET_ROOT/src/nodes/bgp -I$INET_ROOT/src/nodes/ethernet -I$INET_ROOT/src/nodes/httptools -I$INET_ROOT/src/nodes/inet -I$INET_ROOT/src/nodes/internetcloud -I$INET_ROOT/src/nodes/ipv6 -I$INET_ROOT/src/nodes/mpls -I$INET_ROOT/src/nodes/ospfv2 -I$INET_ROOT/src/nodes/rtp -I$INET_ROOT/src/nodes/wireless -I$INET_ROOT/src/nodes/xmipv6 -I$INET_ROOT/src/status -I$INET_ROOT/src/transport -I$INET_ROOT/src/transport/contract -I$INET_ROOT/src/transport/rtp -I$INET_ROOT/src/transport/rtp/profiles -I$INET_ROOT/src/transport/rtp/profiles/avprofile -I$INET_ROOT/src/transport/sctp -I$INET_ROOT/src/transport/tcp -I$INET_ROOT/src/transport/tcp/flavours -I$INET_ROOT/src/transport/tcp/queues -I$INET_ROOT/src/transport/tcp_common -I$INET_ROOT/src/transport/udp -I$INET_ROOT/src/util -I$INET_ROOT/src/util/headerserializers -I$INET_ROOT/src/util/headerserializers/headers -I$INET_ROOT/src/util/headerserializers/ipv4 -I$INET_ROOT/src/util/headerserializers/ipv4/headers -I$INET_ROOT/src/util/headerserializers/sctp -I$INET_ROOT/src/util/headerserializers/sctp/headers -I$INET_ROOT/src/util/headerserializers/tcp -I$INET_ROOT/src/util/headerserializers/tcp/headers -I$INET_ROOT/src/util/headerserializers/udp -I$INET_ROOT/src/util/headerserializers/udp/headers -I$INET_ROOT/src/world -I$INET_ROOT/src/world/annotations -I$INET_ROOT/src/world/httptools -I$INET_ROOT/src/world/obstacles -I$INET_ROOT/src/world/radio -I$INET_ROOT/src/world/scenario -I$INET_ROOT/src/world/traci -linet && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "setenv_commands": ["export TCL_LIBRARY=${pkgs.tcl-8_6}/lib/tcl8.6 && echo 'Hint: in the folder of an example simulation, use the `../../src/obs -n ../..:$INET_ROOT/src omnetpp.ini` command to run the simulation.'"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "rpl_allinone", "version": "6tisch_paper",
            "description": "Routing Protocol for Low Power and Lossy Networks, 6TiSCH-CLX ACM TOIT paper exact version. This version downloads its own copy of INET, and does not use ones installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/ComNetsHH-RPL.html",
            },
            "smoke_test_commands": [
                "cd src",
                "opp_run -l rpl ../simulations/omnetpp.ini -n .:../inet/src:../simulations -c MP2P-Static -u Cmdenv --sim-time-limit=10s > /dev/null",
            ],
            "nix_packages": ["rsync"],
            "required_projects": {"omnetpp": ["5.6.*"]},
            "download_commands": [
                "mkdir rpl_allinone-6tisch_paper",
                "cd rpl_allinone-6tisch_paper",
                "curl -L -o rpl.tar.gz https://github.com/ComNetsHH/omnetpp-rpl/archive/792e6473145d482894f396fea146df9c27a0c758.tar.gz --progress-bar",
                "tar -xzf rpl.tar.gz --strip=1",
                "rm rpl.tar.gz",
                "mv -f inet inet_replacement_files",
                "curl -L -o inet-4.2.5-src.tgz https://github.com/inet-framework/inet/releases/download/v4.2.5/inet-4.2.5-src.tgz --progress-bar",
                "tar -xzf inet-4.2.5-src.tgz",
                "mv -f inet4 inet",
                "rm inet-4.2.5-src.tgz",
            ],
            "patch_commands": [
                """echo 'rsync -abuvP --include="*/" --include="*.cc" --include="*.h" --include="*.ned"  --exclude="*"  inet_replacement_files/  $1/src/inet/ \nfind $1/src/inet -name "*.*~" -delete' > replace_inet_files.sh""",
                "chmod +x replace_inet_files.sh",
                "./replace_inet_files.sh inet",
            ],
            "setenv_commands": [
                "export INET_ROOT=$RPL_ALLINONE_ROOT/inet",
                "echo 'Hint: in the `src` folder, use the `opp_run -l rpl ../simulations/omnetpp.ini -n .:../inet/src:../simulatio` command to run the example simulation.'"
            ],
            "build_commands": [
                "cd inet",
                "make makefiles",
                "make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
                "cd ../src",
                "opp_makemake --make-so -f --deep -o rpl -KINET4_PROJ=../inet -DINET_IMPORT -I$INET_ROOT/src -L$INET_ROOT/src -lINET$(D)", 
                "make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
            ],
            "clean_commands": ["make clean MODE=$BUILD_MODE && cd inet && make clean MODE=$BUILD_MODE"],
        },
        
        {
            # DONE - only tested in debug
            "name": "processbus_allinone", "version": "20180926",       # latest commit of master branch as of the time of writing
            "description": "IEC61850 process bus communication (GOOSE and SV) for INET. This version downloads its own copy of INET, and does not use one installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/ProcessBusIec61850.html",
            },
            "required_projects": {"omnetpp": ["4.6.*"]},
            "download_url": "https://github.com/hectordelahoz/ProcessBusIec61850/archive/c3f76083a52fc36ba086d949dcf1ff91acd788db.tar.gz",
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then cd iec61850InetV2.6/TestInet/simulations && ./run ../src/omnetpp.ini -c IecNetwork -r 0 -u Cmdenv --sim-time-limit=1s > /dev/null; fi""",
            ],
            "patch_commands": [
                "sed -i.bak 's/if (vector_cost<=0)/if (vector_cost == NULL)/' iec61850InetV2.6/inet/src/networklayer/manetrouting/dsr/dsr-uu/path-cache.cc",
                "sed -i 's|testinet|TestInet|' iec61850InetV2.6/TestInet/simulations/run",
                "chmod +x iec61850InetV2.6/TestInet/simulations/run",
                "sed -i 's|-n .:../src|-n .:../src:../../inet/src|' iec61850InetV2.6/TestInet/simulations/run",
                "chmod +x iec61850InetV2.6/inet/src/run_inet",
            ],
            "setenv_commands": ["echo 'Hint: in the `iec61850InetV2.6/TestInet/simulations` folder, use the `./run ../src/omnetpp.ini` command to run the example simulation.'"],
            "build_commands": ["cd iec61850InetV2.6/inet && make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd ../TestInet/src && opp_makemake -f --deep -I../../inet/src -L../../inet/src -linet && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": ["cd iec61850InetV2.6/inet && make clean && cd ../TestInet && make clean"],
        },
        
        {
            # DONE
            "name": "crsimulator", "version": "20140204",
            "description": "Model for Cognitive Radio Ad hoc Network Simulations in OMNeT++",
            "metadata": {
                "catalog_url": "",
            },
            "nix_packages": ["mysql", "sqlite", "libmysqlconnectorcpp"],
            "required_projects": {"omnetpp": ["4.6.*"]},
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "release" ]; then CRSIM_BIN=$(echo $CRSIMULATOR_ROOT/out/*-release/src/*crhandover*); fi""",
                """if [ "$BUILD_MODE" = "debug" ]; then CRSIM_BIN=$(echo $CRSIMULATOR_ROOT/out/*-debug/src/*crhandover*); fi""",
                "$CRSIM_BIN simulations/omnetpp.ini -n simulations:src -c Run0 -u Cmdenv > /dev/null",
            ],
            "download_url": "https://github.com/s2r2010/crSimulator/archive/ba0e65d6a293969400a214a0b434418e61f1581c.tar.gz",
            "patch_commands": ["chmod +x simulations/run"],
            "setenv_commands": [
                "export SQLITE_LIB=${pkgs.sqlite}/lib",
                "export MYSQL_LIB=${pkgs.libmysqlconnectorcpp}/lib",
                "echo 'Hint: use the `./run` command in the simulations folder to run the example simulation.'",
            ],
            "build_commands": ["cd src && opp_makemake -f --deep -o crhandover -I$SQLITE_LIB -lmysqlclient -lsqlite3 -lmysqlcppconn -L$MYSQL_LIB && make -j16 MODE=$BUILD_MODE"],
            "clean_commands": ["make clean"],
        },

        {
            # DONE
            "name": "veins_vlc", "version": "1.0",
            "description": "Veins VLC - Realistic Simulation of Vehicular Visible Light Communication",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/Veins-VLC.html",
            },
            "required_projects": {"omnetpp": ["5.5.*", "5.4.*", "5.3.*"], "inet": ["4.1.1", "4.1.0", "3.6.5"], "veins": ["5.0"]},
            "details": "Veins VLC extends Veins vehicular network simulation framework with channel models for Vehicular Visible Light Communication (V-VLC).",
            "smoke_test_commands": [
                """if [ "$BUILD_MODE" = "debug" ]; then DEBUG_MODE_OPTION="-d"; fi""",
                """if [ "$BUILD_MODE" = "release" ]; then DEBUG_MODE_OPTION=""; fi""",
                "$VEINS_ROOT/sumo-launchd.py &> /dev/null & bg_pid=$! &> /dev/null",
                "cd examples/veins-vlc && ./run $DEBUG_MODE_OPTION -c DriveVlc -u Cmdenv > /dev/null",
                "kill $bg_pid &> /dev/null",
            ],
            "download_url": "https://github.com/veins/veins_vlc/archive/refs/tags/veins-vlc-1.0.tar.gz",
            "build_commands": [
                "./configure --with-veins=$VEINS_ROOT && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"
            ],
            "clean_commands": ["make clean"],
        },
    ]
