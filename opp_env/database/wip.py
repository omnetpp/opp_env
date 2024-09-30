def get_project_descriptions():
    return [
        {
            # NOT WORKING - simulations start but segfault after some time -> runtime error, can't test; update: other configs work
            # UPDATE: this needs parsim in omnetpp
            "name": "oversim", "version": "20190424",       # last commit of master branch as of time of writing
            "description": "Overlay and Peer-to-Peer Network Simulation Framework",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/OverSim.html",
            },
            "smoke_test_commands": [
                r"""cd simulations && ../src/OverSim omnetpp.ini -c Vast -u Cmdenv --sim-time-limit=10s""",
            ],
            "required_projects": {"inet": ["3.6.*"], "omnetpp": ["5.4.*"]},
            "download_url": "https://github.com/inet-framework/oversim/archive/refs/tags/v20190424.tar.gz",
            "patch_commands": [
                r"""sed -i -E 's|INETDIR = .*|INETDIR = $(INET_ROOT)|' Makefile""",
                """sed -i -E "s|ned-path = .*|ned-path = $INET_ROOT/src;../src|" simulations/default.ini""",    # TODO this should keep the rease line
            ],
            "setenv_commands": [
                r"""echo 'Hint: use the `../src/OverSim omnetpp.ini` command in the simulations folder.'"""
            ],
            "build_commands": [r"""make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"""],
            "clean_commands": [r"""make clean"""],
        },

        {
            # NOT WORKING - doesnt build
            "name": "paser_allinone", "version": "2.2",
            "description": "",
            "metadata": {
                "catalog_url": "",
            },
            "test_commands": [
                # "cd simulations/x2 && ../../src/run_lte$BUILD_MODE_SUFFIX -c X2-MeshTopology -r 0 -u Cmdenv --**.pdcpRrc.ipBased=false --sim-time-limit=10s",
            ],
            "required_projects": {"omnetpp": ["4.4.0"]},
            "details": "",
            "download_url": "https://github.com/aarizaq/inetmanet-3.x/archive/refs/heads/inetmanet-2.2.tar.gz",
            "patch_commands": [
                # "sed -i 's/\"LL\"/\" LL \"/' src/networklayer/ipv4/RoutingTableRecorder.cc",
                r"""sed -i 's|info\\[\\]|info[0]|' src/util/headerserializers/sctp/headers/sctp.h""",
                r"""for f in $(grep -Rls 'defined(linux)'); do sed -i 's|defined(linux)|defined(__linux__)|' $f; done""",
                r"""sed -i 's/\"LL\"/\" LL \"/' src/networklayer/ipv4/RoutingTableRecorder.cc""",
                r"""sed -i 's/if (vector_cost<=0)/if (vector_cost == NULL)/' src/networklayer/manetrouting/dsr/dsr-uu/path-cache.cc""",
                r"""sed -i 's/std::make_pair<ManetAddress,ProtocolsRoutes>(getAddress(),vect)/std::make_pair((ManetAddress)getAddress(),vect)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc""",
                r"""sed -i 's/std::make_pair<ManetAddress,ManetAddress>(dest, next)/std::make_pair((ManetAddress)dest, (ManetAddress)next)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc"""
                # "find . -type f -name 'run' -exec chmod +x {} \;",
                # "sed -i 's|../../inet|$(INET_ROOT)|g' Makefile",
                # "sed -i 's|-lINET|-lINET$$\\\(D\\\)|g' Makefile",
                # "sed -i 's|\$DIR/../../inet|$INET_ROOT|g' src/run_lte",
                # "sed -i 's|INET_DIR\"|INET_DIR:$VEINS_ROOT/src/veins:$VEINS_ROOT/subprojects/veins_inet3/src/veins_inet\"|g' src/run_lte",
                # "sed -i 's|-l $INET_DIR/INET|-l $INET_DIR/INET -l $VEINS_ROOT/subprojects/veins_inet3/src/libveins_inet.so|g' src/run_lte",
                # """find . -name '*.launchd.xml' -exec bash -c 'sed -i "s|UPDATE-WITH-YOUR-PATH|$(pwd)/{}|g" {}' \;""",
                # "sed -i 's|/highway.launchd.xml||g' simulations/*/*/*/*.launchd.xml",
                # "sed -i 's|/./|/|g' simulations/*/*/*/*.launchd.xml",
                # "cp src/run_lte src/run_lte_dbg",
                # r"""sed -i 's|libveins_inet.so|veins_inet|' src/run_lte_dbg""",
                # r"""sed -i 's|opp_run|opp_run_dbg|' src/run_lte_dbg""",
            ],
            "setenv_commands": [
                # r"""export INET_PROJ=$INET_ROOT""",
                # 'export OMNETPP_IMAGE_PATH="$OMNETPP_IMAGE_PATH:$VEINS_ROOT/images:$OPENCV2X_VEINS_ALLINONE_ROOT/images:$INET_ROOT/images:$VEINS_ROOT/subprojects/veins_inet3/images"',
                # r"""export SUMO_ROOT=${pkgs.sumo}""",
                # r"""echo 'Hint: To run an example simulation, use the `$VEINS_ROOT/sumo-launchd.py &` to start the TraCI server, then in folder of the example simulation, use the `./run` command.'""",
            ],
            "build_commands": [
                r"""make makefiles && make CFLAGS='-std=c++11'"""
                # r"""opp_featuretool enable SimuLTE_Cars && make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"""
            ],
            "clean_commands": [r"""make clean"""],
        },


                {
            # WIP - ok
            # when closing qtenv:
            # (omnetpp::cChannel)channel: Fatal: Direct deletion of a channel object is illegal, use cGate's disconnect() or reconnectWith() instead; ABORTING -- during network cleanup
            # needs another omnetpp version?
            # TODO: inet patch? omnetpp/inet version?
            "name": "openflow", "version": "20220615",      # last commit of master branch as of time of writing
            "description": "OpenFlow Extension for INET Framework",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/Openflow.html",
                "test_commands": "cd openflow-20220615/scenarios/usa && run_openflow Scenario_USA_ARP_Ping_Drop.ini -u Cmdenv --sim-time-limit=1s",
            },
            "required_projects": {"omnetpp": ["6.0.*"], "inet": ["4.4.*", "4.3.*"]},
            # git_url": "https://github.com/inet-framework/openflow.git",
            # there are no releases, so we use a commit from the master branch
            "download_url": "https://github.com/inet-framework/openflow/archive/9f8e9b88d8aa5d4310078f725227ccbd21f26e9c.tar.gz",
            "patch_commands": [
                r"""sed -i -E 's|-KINET_PROJ=[^ ]+|-KINET_PROJ=$(INET_ROOT) -o openflow|' Makefile""",
                r"""sed -i 's|$DIR/../../inet|$INET_ROOT|' src/run_openflow""",
                r"""sed -i 's|opp_run_dbg|opp_run|' src/run_openflow""",
                r"""sed -i 's|scenarios:$DIR|scenarios:$DIR -i $OPENFLOW_ROOT/images|' src/run_openflow""",
            ],
            "setenv_commands": [
                r"""export INET_PROJ=$INET_ROOT""",
                r"""export PATH=$PATH:$OPENFLOW_ROOT/src""",
                r"""echo 'Hint: use the `run_openflow` command to run the examples in the scenarios folder.'"""
            ],
            "build_commands": [r"""make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"""],
            "clean_commands": [r"""make clean"""]
        },

        {
            # WIP
            # this is the last version for omnetpp5
            "name": "openflow", "version": "20190516",      # last commit of master branch as of time of writing
            "description": "OpenFlow Extension for INET Framework",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/Openflow.html",
            },
            "test_commands": "cd openflow-20220615/scenarios/usa && run_openflow Scenario_USA_ARP_Ping_Drop.ini -u Cmdenv --sim-time-limit=1s",
            "required_projects": {"omnetpp": ["5.4.0"], "inet": ["3.6.*"]},
            # git_url": "https://github.com/inet-framework/openflow.git",
            # there are no releases, so we use a commit from the master branch
            "download_url": "https://github.com/inet-framework/openflow/archive/7d3e3a40a077a0880b1bfd1422a2dec927ca7d6a.tar.gz",
            "patch_commands": [
                r"""sed -i -E 's|-KINET_PROJ=[^ ]+|-KINET_PROJ=$(INET_ROOT) -o openflow|' Makefile""",
                r"""sed -i 's|$DIR/../../inet|$INET_ROOT|' src/run_openflow""",
                r"""sed -i 's|opp_run_dbg|opp_run|' src/run_openflow""",
                r"""sed -i 's|scenarios:$DIR|scenarios:$DIR -i $OPENFLOW_ROOT/images|' src/run_openflow""",
            ],
            "setenv_commands": [
                r"""export INET_PROJ=$INET_ROOT""",
                r"""export PATH=$PATH:$OPENFLOW_ROOT/src""",
                r"""echo 'Hint: use the `run_openflow` command to run the examples in the scenarios folder.'"""
            ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": [r"""make clean"""]
        },

        {
            # DONE BUT NOT NEEDED
            # core-rg version, compatible with core4inet as well; this is allinone version is currently not needed as the standalone one works if inet doesn't have to be patched
            # TODO inet patch? is that needed?
            "name": "openflow_allinone", "version": "20231017",      # last commit of master branch as of time of writing
            "description": "OpenFlow Extension for INET Framework",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/Openflow.html",
            },
            "test_commands": ["cd scenarios/usa && opp_run$BUILD_MODE_SUFFIX -l $OPENFLOW_ALLINONE_ROOT/src/openflow -n $INET_ROOT/src:$OPENFLOW_ALLINONE_ROOT/scenarios:.:../../src Scenario_USA_ARP_Ping_Drop.ini -u Cmdenv -r 0 --sim-time-limit=1s",],
            "required_projects": {"omnetpp": ["5.5.1"]},
            "download_commands": [
                r"""mkdir openflow_allinone-20231017""",
                r"""cd openflow_allinone-20231017""",
                r"""curl -L -o inet.src.tar.gz https://github.com/inet-framework/inet/releases/download/v3.6.6/inet-3.6.6-src.tgz --progress-bar""",
                r"""tar -xzf inet.src.tar.gz""",
                r"""rm inet.src.tar.gz""",
                r"""curl -L -o src.tar.gz https://github.com/CoRE-RG/OpenFlow/archive/72fc3c2bcfb720087225728e130c06fac1c7f0f2.tar.gz --progress-bar""",
                r"""tar -xzf src.tar.gz --strip=1""",
                r"""rm src.tar.gz""",
            ],
            "patch_commands": [
                "sed -i -E 's|-KINET_PROJ=[^ ]+|-KINET_PROJ=$(INET_ROOT) -o openflow|' Makefile",
                "sed -i 's|$DIR/../../inet|$INET_ROOT|' src/run_openflow",
                "sed -i 's|opp_run_dbg|opp_run|' src/run_openflow",
                "sed -i 's|scenarios:$DIR|scenarios:$DIR -i $OPENFLOW_ALLINONE_ROOT/images|' src/run_openflow",
            ],
            "setenv_commands": [
                r"""export INET_ROOT=$OPENFLOW_ALLINONE_ROOT/inet""",
                r"""export INET_PROJ=$INET_ROOT""",
                r"""export PATH=$PATH:$OPENFLOW_ALLINONE_ROOT/src""",
                r"""echo 'Hint: use the `run_openflow` command to run the examples in the scenarios folder.'"""
            ],
            "build_commands": ["cd inet && make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd .. && make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": [r"""make clean && cd inet && make clean"""]
        },

                {
            # NOT WORKING
            # TODO: debug mode
            # TODO: not git; also, this hash doesnt work -> the newest one neither, build error
            "name": "rpl_allinone", "version": "20231002",      # last commit of master branch as of time of writing
            "description": "Routing Protocol for Low Power and Lossy Networks. This version downloads its own copy of INET, and does not use ones installed by opp_env.",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/ComNetsHH-RPL.html",
            },
            "nix_packages": ["rsync"],
            "required_projects": {"omnetpp": ["5.7.*"]},
            "download_commands": [
                r"""git clone https://github.com/ComNetsHH/omnetpp-rpl.git rpl_allinone-20231002""",
                r"""cd rpl_allinone-20231002""",
                r"""git reset --hard f8914ce331092bcbce87b99acfe24c71dc334dde""",
                r"""mv -f inet inet_replacement_files""",
                r"""curl -L -o inet-4.2.10-src.tgz https://github.com/inet-framework/inet/releases/download/v4.2.10/inet-4.2.10-src.tgz --progress-bar""",
                r"""tar -xzf inet-4.2.10-src.tgz""",
                r"""mv -f inet4 inet""",
                r"""rm inet-4.2.10-src.tgz""",
                # r"""chmod +x replace_inet_files.sh""",
                # r"""./replace_inet_files.sh inet""",
            ],
            "patch_commands": [
                r"""chmod +x replace_inet_files.sh""",
                r"""sed -i 's|inet/  $1/src/inet/|inet_replacement_files/  $1/src/inet/|' replace_inet_files.sh""",
                r"""./replace_inet_files.sh inet""",
            ],
            "setenv_commands": [
                r"""echo 'Hint: in the `src` folder, use the `./rpl ../simulations/omnetpp.ini -n .:../inet/src:../simulations` command to run the example simulation.'"""
            ],
            "build_commands": [
                r"""cd inet""",
                r"""make makefiles""",
                r"""make -j$NIX_BUILD_CORES MODE=$BUILD_MODE""",
                r"""cd ../src""",
                r"""opp_makemake -f --deep -o rpl -KINET_PROJ=../inet -I../inet/src/inet -L../inet/src/inet -lINET\$D""",
                r"""make -j$NIX_BUILD_CORES MODE=$BUILD_MODE""",
            ],
            "clean_commands": [r"""make clean"""],
        },

        {
            # NOT WORKING - cant connect to TraCI server
            # TODO the launchd.xml files need to be fixed with <basedir path>; only allinone needed
            "name": "vanet_project_allinone", "version": "20200516",
            "description": "A Veins-based solutions for VANET communication with OMNeT++. This version downloads its own copy of INET, and does not use ones installed by opp_env.",
            "metadata": {
                "catalog_url": "",
            },
            "nix_packages": [
                "sumo",
                "python2",
            ],
            "required_projects": {"omnetpp": ["5.5.1"]},
            "download_commands": [
                r"""mkdir vanet_project_allinone-20200516 && cd vanet_project_allinone-20200516""",
                r"""mkdir inet && cd inet && curl -L -o src.tar.gz --progress-bar https://github.com/chaotictoejam/inet/archive/refs/tags/v4.2.0.tar.gz""",
                r"""tar -xzf src.tar.gz --strip=1""",
                r"""rm src.tar.gz""",
                r"""cd ..""",
                r"""mkdir veins && cd veins""",
                r"""curl -L -o src.tar.gz --progress-bar https://github.com/sommer/veins/archive/refs/tags/veins-5.0.tar.gz""",
                r"""tar -xzf src.tar.gz --strip=1""",
                r"""cd ..""",
                r"""curl -L -o src.tar.gz --progress-bar https://github.com/chaotictoejam/VANETProject/archive/3f56bed29f6c10d24e0794b9aba7efd87e21b83a.tar.gz""",   # latest commit of the master branch as of the time of writing
                r"""tar -xzf src.tar.gz --strip=1""",
                r"""rm src.tar.gz""",
            ],
            "patch_commands": [
                r"""cd inet""",
                r"""touch tutorials/package.ned""",
                r"""for f in $(grep -Rls 'defined(linux)'); do sed -i 's|defined(linux)|defined(__linux__)|' $f; done""",
                r"""cd ..""",
                r"""sed -i 's|F:\\\\Dev\\\\GitHub\\\\VANETProject|$VANET_PROJECT_ROOT|g' simulations/_maps/*/*.launchd.xml""",
                r"""sed -i 's|\\\\|/|g' simulations/_maps/*/*.launchd.xml""",
                r"""""sed -i "s|\$VANET_PROJECT_ROOT|$VANET_PROJECT_ROOT|g" simulations/_maps/*/*.launchd.xml""""",
                r"""chmod +x sumo-launchd.py""",
                r"""sed -i 's|opp_makemake -f --deep|opp_makemake --make-so -f --deep -O out -o vanet_project -KINET_PROJ=$$INET_ROOT -KVEINS_PROJ=$$VEINS_ROOT -DINET_IMPORT -DVEINS_IMPORT -I. -I$$INET_ROOT/src -I$$VEINS_ROOT/src -I$$VANET_PROJECT_ROOT/src/veins_inet -L$$INET_ROOT/src -L$$VEINS_ROOT/src -lINET$$\\\(D\\\) -lveins$$\\\(D\\\)|g' Makefile""",
            ],
            "setenv_commands": [
                r"""export OMNETPP_IMAGE_PATH=\"$OMNETPP_IMAGE_PATH:$INET_ROOT/images\"""",
                r"""export OMNETPP_IMAGE_PATH=\"$OMNETPP_IMAGE_PATH:$VEINS_ROOT/images\"""",
                r"""export SUMO_ROOT=${pkgs.sumo}""",
                r"""export VEINS_ROOT=$VANET_PROJECT_ALLINONE_ROOT/veins""",
                r"""export INET_ROOT=$VANET_PROJECT_ALLINONE_ROOT/inet""",
                r"""export SUMO_ROOT=${pkgs.sumo}""",
                r"""export SUMO_TOOLS=${pkgs.sumo}/share/sumo/tools""",
                r"""export PYTHONPATH=$SUMO_TOOLS:$PYTHONPATH""",
                r"""export INET_PROJ=$INET_ROOT""",
                r"""export VEINS_PROJ=$VEINS_ROOT""",
                r"""echo 'Hint: use the `opp_run -l ../../../src/libvanet_project.so -n ../../../src/vanetsim:../../../src/veins_inet:$INET_ROOT/src:$VEINS_ROOT/src/veins:../..` command in an example simulation folder.'""",
            ],
            "build_commands": [
                r"""cd inet && source setenv -f && make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd ..""",
                r"""cd veins && ./configure && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd ..""",
                r"""make makefiles && cd src && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE""",
                ],
            "clean_commands": [r"""make clean && cd veins && make clean && cd ../inet && make clean"""],
        },

        {
            # DONE - ok; needed by artery standalone versions
            "name": "vanetza", "version": "master",
            "description": "Open-source implementation of the ETSI C-ITS protocol suite",
            "nix_packages": ["cmake", "boost", "geographiclib", "cryptopp"],
            "git_url": "https://github.com/riebl/vanetza.git",
            "build_commands": ["mkdir -p build && cd build && cmake .. && make"],
            "clean_commands": [r"""make clean"""]
        },

        # {
        #     # DONE - ok; currently not used by anything, so it's not needed.
        #     "name": "keetchlib", "version": "master",
        #     "description": "A C++ implementation of the Organic Data Dissemination (ODD) model",
        #     "nix_packages": ["autoconf", "automake", "libtool"],
        #     "git_url": "https://github.com/ComNets-Bremen/KeetchiLib.git",
        #     "git_branch": "master",
        #     "build_commands": ["./bootstrap.sh && ./configure && make"],
        #     "clean_commands": [r"""make clean"""]
        # },

        # {
        #     # WIP - build errors
        #     "name": "libara_allinone", "version": "1.2",
        #     "description": "Routing algorithms based on the Ant Colony Optimization (ACO) metaheuristic. This version downloads its own copy of INETMANET, and does not use one installed by opp_env.",
        #     "metadata": {
        #         "catalog_url": "https://omnetpp.org/download-items/libARA.html",
        #     },
        #     "required_projects": {"omnetpp": ["4.5.x"]},
        #     "download_commands": [
        #         "git clone https://github.com/des-testbed/libara.git libara_allinone-1.2",
        #         "cd libara_allinone-1.2",
        #         "git reset --hard 1f57d746033fcc50d4c22385529bdd39867a29b6",
        #         "sed -i 's|git:\/\/|https:\/\/|g' .gitmodules",
        #         "pwd",
        #         "cd inetmanet",
        #         "git submodule init",
        #         "git submodule update",
        #     ],
        #     "patch_commands": [
        #         "cd inetmanet",
        #         "sed -i 's|info\\[\\]|info[0]|' src/util/headerserializers/sctp/headers/sctp.h",
        #         "for f in $(grep -Rls 'defined(linux)'); do sed -i 's|defined(linux)|defined(__linux__)|' $f; done",
        #         "sed -i 's/SensitivityList::iterator it = sensitivityList.find(0.0);/SensitivityList::iterator sit = sensitivityList.find(0.0);/' src/linklayer/radio/Radio.cc",
        #         "sed -i 's/if (it == sensitivityList.end())/if (sit == sensitivityList.end())/' src/linklayer/radio/Radio.cc",
        #         "sed -i 's/\"LL\"/\" LL \"/' src/networklayer/ipv4/RoutingTableRecorder.cc",
        #         "sed -i 's/if (vector_cost<=0)/if (vector_cost == NULL)/' src/networklayer/manetrouting/dsr/dsr-uu/path-cache.cc",
        #         "sed -i 's/std::make_pair<ManetAddress,ProtocolsRoutes>(getAddress(),vect)/std::make_pair((ManetAddress)getAddress(),vect)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc",
        #         "sed -i 's/std::make_pair<ManetAddress,ManetAddress>(dst, gtwy)/std::make_pair((ManetAddress)dst, (ManetAddress)gtwy)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc",
        #         "sed -i 's/std::make_pair<ManetAddress,ManetAddress>(destination, nextHop)/std::make_pair((ManetAddress)destination, (ManetAddress)nextHop)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc",
        #         "sed -i 's/  int groups\\[8\\] = /  unsigned int groups[8] = /' src/networklayer/contract/IPv6Address.cc",
        #         "sed -i 's/findGap(int \\*groups/findGap(unsigned int *groups/' src/networklayer/contract/IPv6Address.cc",
        #     ],
        #     "setenv_commands": ["export INETMANET_FOLDER=$LIBARA_ROOT/inetmanet",
        #                         "echo 'Hint: in an example simulation folder, use the `./run.sh` command to run the example simulation.'"],
        #     "build_commands": [
        #         "make all -j$NIX_BUILD_CORES MODE=$BUILD_MODE"
        #     ],
        #     "clean_commands": [r"""make clean"""],
        # },

        {
            # POSTPONED - this should be allinone -> need patched omnetpp
            # TODO: create own topology class, and dont patch omnetpp
            "name": "ccnsim", "version": "master",
            "description": " Simulation of Content Centric Networks (ICN/CCN)",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/ccnSim.html",
            },
            "nix_packages": ["boost"],
            "required_projects": {"omnetpp": ["ccnsim5"]},
            "git_url": "https://github.com/TeamRossi/ccnSim-0.4.git",
            "setenv_commands": [
                "echo 'Hint: use the `./run_ED_TTL_scenarios.sh` command to run the example simulation in Cmdenv. Note that this script creates ini files for simulation scenarios, which can be run in Tkenv with the `./ccnSim` command.'",
            ],
            "build_commands": ["./scripts/makemake.sh && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": [r"""make clean"""],
        },

        {
            # POSTPONED - doesn't build; postponed due to openGL
            "name": "artery", "version": "oppsummit2015",
            "required_projects": {"omnetpp": ["4.6.*"], "vanetza": ["master"], "veins": ["4.4"]},
            "nix_packages": ["cmake", "boost"],
            "download_url": "https://github.com/riebl/artery/archive/refs/tags/opp-summit2015.tar.gz",
            "setenv_commands": [
                "export ARTERY_PATH=$ARTERY_ROOT",
                "export Vanetza_DIR=$VANETZA_ROOT/build",
                "export Veins_DIR=$VEINS_ROOT",
                # "echo 'Hint: use the run_inet command to run the simulations in the examples folder.'",
            ],
            "build_commands": ["mkdir -p build && cd build && cmake .. && cmake --build ."],
            "clean_commands": [r"""make clean"""]
        },

        {
            # POSTPONED - a version of artery where external projects are provided by opp_env; postponed due to openGL
            "name": "artery", "version": "master_",
            "required_projects": {"omnetpp": ["5.5"], "vanetza": ["master"], "veins": ["5.2"], "inet": ["3.7.1"]},
            "nix_packages": ["cmake", "boost"],
            "git_url": "https://github.com/riebl/artery.git",
            "patch_commands": [
                "sed -i 's|check_git_submodule|#check_git_submodule|' CMakeLists.txt",
                "sed -i 's|add_subdirectory|#add_subdirectory|' CMakeLists.txt",
                "sed -i 's|add_opp_target|#add_opp_target|' CMakeLists.txt",
            ],
            "setenv_commands": [
                "export ARTERY_PATH=$ARTERY_ROOT",
                "export Vanetza_DIR=$VANETZA_ROOT/build",
                "export Veins_DIR=$VEINS_ROOT",
                # "export SimuLTE_DIR=$SIMULTE_ROOT"
                "export INET_DIR=$INET_ROOT",
                # "echo 'Hint: use the run_inet command to run the simulations in the examples folder.'",
                "cd extern && rm -r inet && ln -sf -T $INET_ROOT inet",
                "rm -r veins && ln -sf -T $VEINS_ROOT veins",
                "rm -r vanetza && ln -sf -T $VANETZA_ROOT vanetza",
                # "cd extern && rm -r inet && ln -sf -T $INET_ROOT inet",
                # "ln -sf $VANETZA_ROOT extern",
                # "ln -sf $VEINS_ROOT extern",
                # "ln -s $INET_ROOT" extern/inet"
                # "ln -s $INET_ROOT" extern/inet"
            ],
            "build_commands": ["mkdir -p build && cd build && cmake .. && make"],
            "clean_commands": [r"""make clean"""]
        },

        {
            # POSTPONED - openGL
            # TODO: add to catalog
            "name": "space_veins", "version": "master",
            "required_projects": {"omnetpp": ["5.6.2"], "veins": ["5.2"]},
            "nix_packages": ["proj", "python2"],
            "download_url": "https://github.com/veins/space_veins/archive/refs/tags/space_Veins-0.2.tar.gz",
            "patch_commands": [
                "mv src/makefrag src/makefrag.orig",
                "export PYTHON2_BIN=${pkgs.python2}/bin/python2",
                'sed -i "s|/usr/bin/env python2|$PYTHON2_BIN|" run',
                'sed -i "s|../veins/src/veins|$VEINS_ROOT/src/veins|" run',
                r"""sed -i 's|\\#\\*.satellite\[0\].satelliteMobility.satelliteName = ""|*.satellite[0].satelliteMobility.satelliteName = "ISS (ZARYA)"|' examples/space_veins/omnetpp.ini""",
                r"""sed -i 's|\\#\\*.satellite\[0\].satelliteMobility.tle_line_one = ""|*.satellite[0].satelliteMobility.tle_line_one = "1 25544U 98067A   24066.21503963  .00016480  00000+0  29947-3 0  9999"|' examples/space_veins/omnetpp.ini""",
                r"""sed -i 's|\\#\\*.satellite\[0\].satelliteMobility.tle_line_two = ""|*.satellite[0].satelliteMobility.tle_line_two = "2 25544  51.6406 105.7199 0005859 331.9893 139.5156 15.49668492442586"|' examples/space_veins/omnetpp.ini""",
            ],
            "setenv_commands": [
                "echo $PYTHON2_BIN",
                "export PROJ_ROOT=${pkgs.proj}",
                "export PROJ_DEV_ROOT=${pkgs.proj.dev}",
            ],
            "build_commands": [r"""cd src && opp_makemake -f --deep --no-deep-includes --make-so -I . -o space_veins -O ../out -I $VEINS_ROOT/src -L $VEINS_ROOT/src/ -lveins\$D -I$PROJ_DEV_ROOT/include -L$PROJ_ROOT/lib -lproj && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"""],
            "clean_commands": [r"""make clean"""]
        },

        {
            # NOT WORKING - build errors
            "name": "leach", "version": "master",
            "required_projects": {"omnetpp": ["5.6.2"], "inet": ["4.2.5"]},
            "git_url": "https://github.com/Agr-IoT/LEACH.git",
            "setenv_commands": ["export INET4_PROJ=$INET_ROOT"],
            "patch_commands": [
                "sed -i 's|inet.node.LEACHnode|leach.node.LEACHnode|' inet/*/*/*.ned",
                "sed -i 's|inet.routing.leach|leach.routing.leach|' inet/*/*/*.ned",
                "sed -i 's|inet/routing/leach|routing/leach|' inet/*/*/*.cc inet/*/*/*.h",
                "mv inet src",
            #     "sed -i -E 's|-n.*|-n $INET_ROOT/src:.:../src $*|' IEEE8021AS/simulations/run",
            #     "chmod +x IEEE8021AS/simulations/run",
            ],
            "build_commands": ["opp_makemake -f --deep -O out -KINET4_PROJ=$INET4_PROJ -DINET_IMPORT -I./src -I$INET4_PROJ/src -L$INET4_PROJ/src -lINET$D && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": [r"""make clean"""]
        },

        {
            # NOT WORKING this needs omnetpp 3.2
            "name": "fieldbus", "version": "20050901",
            "required_projects": {"omnetpp": ["3.3.1"]},
            "download_url": "https://sourceforge.net/projects/fieldbus.berlios/files/FIELDBUS.tar.gz/download",
            "patch_commands": [
                r"""sed -i 's|/usr/share/omnetpp-3.2pre4|\$(OMNETPP_ROOT)|g' fieldbusconfig""",
                "sed -i 's|-gstabs+3|-gstabs+|g' fieldbusconfig",
                "sed -i 's|TK_LIBS=-L/usr/lib|TK_LIB=-L$(TK_LIBS)|g' fieldbusconfig",
                # "chmod +x simulations/run",
                # "sed -i 's|-n .:../src|-n ..:../src:$\{INET_ROOT\}/src|g' simulations/run",
                # "sed -i 's|opp_makemake -f --deep|opp_makemake -f --deep -I.     -I$(INET_ROOT)/src/.     -I$(INET_ROOT)/src/applications     -I$(INET_ROOT)/src/applications/common     -I$(INET_ROOT)/src/applications/dhcp     -I$(INET_ROOT)/src/applications/ethernet     -I$(INET_ROOT)/src/applications/generic     -I$(INET_ROOT)/src/applications/httptools     -I$(INET_ROOT)/src/applications/pingapp     -I$(INET_ROOT)/src/applications/rtpapp     -I$(INET_ROOT)/src/applications/sctpapp     -I$(INET_ROOT)/src/applications/tcpapp     -I$(INET_ROOT)/src/applications/traci     -I$(INET_ROOT)/src/applications/udpapp     -I$(INET_ROOT)/src/applications/voip     -I$(INET_ROOT)/src/base     -I$(INET_ROOT)/src/battery     -I$(INET_ROOT)/src/battery/models     -I$(INET_ROOT)/src/linklayer     -I$(INET_ROOT)/src/linklayer/common     -I$(INET_ROOT)/src/linklayer/configurator     -I$(INET_ROOT)/src/linklayer/contract     -I$(INET_ROOT)/src/linklayer/ethernet     -I$(INET_ROOT)/src/linklayer/ethernet/switch     -I$(INET_ROOT)/src/linklayer/ext     -I$(INET_ROOT)/src/linklayer/idealwireless     -I$(INET_ROOT)/src/linklayer/ieee80211     -I$(INET_ROOT)/src/linklayer/ieee80211/mac     -I$(INET_ROOT)/src/linklayer/ieee80211/mgmt     -I$(INET_ROOT)/src/linklayer/ieee80211/radio     -I$(INET_ROOT)/src/linklayer/ieee80211/radio/errormodel     -I$(INET_ROOT)/src/linklayer/ieee8021d     -I$(INET_ROOT)/src/linklayer/ieee8021d/common     -I$(INET_ROOT)/src/linklayer/ieee8021d/relay     -I$(INET_ROOT)/src/linklayer/ieee8021d/rstp     -I$(INET_ROOT)/src/linklayer/ieee8021d/stp     -I$(INET_ROOT)/src/linklayer/ieee8021d/tester     -I$(INET_ROOT)/src/linklayer/loopback     -I$(INET_ROOT)/src/linklayer/ppp     -I$(INET_ROOT)/src/linklayer/queue     -I$(INET_ROOT)/src/linklayer/radio     -I$(INET_ROOT)/src/linklayer/radio/propagation     -I$(INET_ROOT)/src/mobility     -I$(INET_ROOT)/src/mobility/common     -I$(INET_ROOT)/src/mobility/contract     -I$(INET_ROOT)/src/mobility/group     -I$(INET_ROOT)/src/mobility/single     -I$(INET_ROOT)/src/mobility/static     -I$(INET_ROOT)/src/networklayer     -I$(INET_ROOT)/src/networklayer/arp     -I$(INET_ROOT)/src/networklayer/autorouting     -I$(INET_ROOT)/src/networklayer/autorouting/ipv4     -I$(INET_ROOT)/src/networklayer/autorouting/ipv6     -I$(INET_ROOT)/src/networklayer/bgpv4     -I$(INET_ROOT)/src/networklayer/bgpv4/BGPMessage     -I$(INET_ROOT)/src/networklayer/common     -I$(INET_ROOT)/src/networklayer/contract     -I$(INET_ROOT)/src/networklayer/diffserv     -I$(INET_ROOT)/src/networklayer/icmpv6     -I$(INET_ROOT)/src/networklayer/internetcloud     -I$(INET_ROOT)/src/networklayer/ipv4     -I$(INET_ROOT)/src/networklayer/ipv6     -I$(INET_ROOT)/src/networklayer/ipv6tunneling     -I$(INET_ROOT)/src/networklayer/ldp     -I$(INET_ROOT)/src/networklayer/manetrouting     -I$(INET_ROOT)/src/networklayer/manetrouting/aodv-uu     -I$(INET_ROOT)/src/networklayer/manetrouting/aodv-uu/aodv-uu     -I$(INET_ROOT)/src/networklayer/manetrouting/base     -I$(INET_ROOT)/src/networklayer/manetrouting/batman     -I$(INET_ROOT)/src/networklayer/manetrouting/batman/batmand     -I$(INET_ROOT)/src/networklayer/manetrouting/batman/batmand/orig     -I$(INET_ROOT)/src/networklayer/manetrouting/dsdv     -I$(INET_ROOT)/src/networklayer/manetrouting/dsr     -I$(INET_ROOT)/src/networklayer/manetrouting/dsr/dsr-uu     -I$(INET_ROOT)/src/networklayer/manetrouting/dymo     -I$(INET_ROOT)/src/networklayer/manetrouting/dymo/dymoum     -I$(INET_ROOT)/src/networklayer/manetrouting/dymo_fau     -I$(INET_ROOT)/src/networklayer/manetrouting/olsr     -I$(INET_ROOT)/src/networklayer/mpls     -I$(INET_ROOT)/src/networklayer/ospfv2     -I$(INET_ROOT)/src/networklayer/ospfv2/interface     -I$(INET_ROOT)/src/networklayer/ospfv2/messagehandler     -I$(INET_ROOT)/src/networklayer/ospfv2/neighbor     -I$(INET_ROOT)/src/networklayer/ospfv2/router     -I$(INET_ROOT)/src/networklayer/routing     -I$(INET_ROOT)/src/networklayer/routing/aodv     -I$(INET_ROOT)/src/networklayer/routing/dymo     -I$(INET_ROOT)/src/networklayer/routing/gpsr     -I$(INET_ROOT)/src/networklayer/routing/rip     -I$(INET_ROOT)/src/networklayer/rsvp_te     -I$(INET_ROOT)/src/networklayer/ted     -I$(INET_ROOT)/src/networklayer/xmipv6     -I$(INET_ROOT)/src/nodes     -I$(INET_ROOT)/src/nodes/aodv     -I$(INET_ROOT)/src/nodes/bgp     -I$(INET_ROOT)/src/nodes/dymo     -I$(INET_ROOT)/src/nodes/ethernet     -I$(INET_ROOT)/src/nodes/gpsr     -I$(INET_ROOT)/src/nodes/httptools     -I$(INET_ROOT)/src/nodes/inet     -I$(INET_ROOT)/src/nodes/internetcloud     -I$(INET_ROOT)/src/nodes/ipv6     -I$(INET_ROOT)/src/nodes/mpls     -I$(INET_ROOT)/src/nodes/ospfv2     -I$(INET_ROOT)/src/nodes/rip     -I$(INET_ROOT)/src/nodes/rtp     -I$(INET_ROOT)/src/nodes/wireless     -I$(INET_ROOT)/src/nodes/xmipv6     -I$(INET_ROOT)/src/status     -I$(INET_ROOT)/src/transport     -I$(INET_ROOT)/src/transport/contract     -I$(INET_ROOT)/src/transport/rtp     -I$(INET_ROOT)/src/transport/rtp/profiles     -I$(INET_ROOT)/src/transport/rtp/profiles/avprofile     -I$(INET_ROOT)/src/transport/sctp     -I$(INET_ROOT)/src/transport/tcp     -I$(INET_ROOT)/src/transport/tcp/flavours     -I$(INET_ROOT)/src/transport/tcp/queues     -I$(INET_ROOT)/src/transport/tcp_common     -I$(INET_ROOT)/src/transport/udp     -I$(INET_ROOT)/src/util     -I$(INET_ROOT)/src/util/headerserializers     -I$(INET_ROOT)/src/util/headerserializers/headers     -I$(INET_ROOT)/src/util/headerserializers/ipv4     -I$(INET_ROOT)/src/util/headerserializers/ipv4/headers     -I$(INET_ROOT)/src/util/headerserializers/ipv6     -I$(INET_ROOT)/src/util/headerserializers/ipv6/headers     -I$(INET_ROOT)/src/util/headerserializers/sctp     -I$(INET_ROOT)/src/util/headerserializers/sctp/headers     -I$(INET_ROOT)/src/util/headerserializers/tcp     -I$(INET_ROOT)/src/util/headerserializers/tcp/headers     -I$(INET_ROOT)/src/util/headerserializers/udp     -I$(INET_ROOT)/src/util/headerserializers/udp/headers     -I$(INET_ROOT)/src/util/messageprinters     -I$(INET_ROOT)/src/world     -I$(INET_ROOT)/src/world/annotations     -I$(INET_ROOT)/src/world/httptools     -I$(INET_ROOT)/src/world/obstacles     -I$(INET_ROOT)/src/world/radio     -I$(INET_ROOT)/src/world/scenario     -I$(INET_ROOT)/src/world/traci -o ieee802154inet_standalone -L$(INET_ROOT)/src -linet|' Makefile",
            ],
            "setenv_commands": [
                "export TK_LIB=${pkgs.tk-8_5}/lib && echo $TK_LIB",
            ],
            # "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": [r"""make clean"""]
        },

        {
            # POSTPONED - compiles; needs OSG; need ui with qt; need to try example simulation -> TODO can OSG be turned off? -> actually does it need osgearth as well? -> needs osgearth
            "name": "limosim", "version": "master",
            "nix_packages": ["qt5.qtbase", "qt5.qtsvg", "qt5.qtwayland", "openscenegraph"],
            # "required_projects": {"omnetpp": ["5.1.x"], "inet": ["3.3.0"]},
            "required_projects": {"omnetpp": ["5.4.x"], "inet": ["4.0.0"]},
            "git_url": "https://github.com/BenSliwa/LIMoSim.git",
            "setenv_commands": [
                "export PATH=$LIMOSIM_ROOT:$PATH",
            ],
            "patch_commands": [
                "echo 'package inet.LIMoSim.omnet;\n@namespace(inet);' > omnet/package.ned",
                # "sed -i 's|INETDefs.h|base/INETDefs.h|g' src/*/*.h",
                # "sed -i 's|ChannelAccess.h|world/radio/ChannelAccess.h|g' src/*/*.h",
                # "sed -i 's|InterfaceToken.h|networklayer/common/InterfaceToken.h|g' src/*/*.h src/*/*.h",
                # "chmod +x simulations/run",
                # "sed -i 's|-n .:../src|-n ..:../src:$\{INET_ROOT\}/src|g' simulations/run",
                # "sed -i 's|opp_makemake -f --deep|opp_makemake -f --deep -I.     -I$(INET_ROOT)/src/.     -I$(INET_ROOT)/src/applications     -I$(INET_ROOT)/src/applications/common     -I$(INET_ROOT)/src/applications/dhcp     -I$(INET_ROOT)/src/applications/ethernet     -I$(INET_ROOT)/src/applications/generic     -I$(INET_ROOT)/src/applications/httptools     -I$(INET_ROOT)/src/applications/pingapp     -I$(INET_ROOT)/src/applications/rtpapp     -I$(INET_ROOT)/src/applications/sctpapp     -I$(INET_ROOT)/src/applications/tcpapp     -I$(INET_ROOT)/src/applications/traci     -I$(INET_ROOT)/src/applications/udpapp     -I$(INET_ROOT)/src/applications/voip     -I$(INET_ROOT)/src/base     -I$(INET_ROOT)/src/battery     -I$(INET_ROOT)/src/battery/models     -I$(INET_ROOT)/src/linklayer     -I$(INET_ROOT)/src/linklayer/common     -I$(INET_ROOT)/src/linklayer/configurator     -I$(INET_ROOT)/src/linklayer/contract     -I$(INET_ROOT)/src/linklayer/ethernet     -I$(INET_ROOT)/src/linklayer/ethernet/switch     -I$(INET_ROOT)/src/linklayer/ext     -I$(INET_ROOT)/src/linklayer/idealwireless     -I$(INET_ROOT)/src/linklayer/ieee80211     -I$(INET_ROOT)/src/linklayer/ieee80211/mac     -I$(INET_ROOT)/src/linklayer/ieee80211/mgmt     -I$(INET_ROOT)/src/linklayer/ieee80211/radio     -I$(INET_ROOT)/src/linklayer/ieee80211/radio/errormodel     -I$(INET_ROOT)/src/linklayer/ieee8021d     -I$(INET_ROOT)/src/linklayer/ieee8021d/common     -I$(INET_ROOT)/src/linklayer/ieee8021d/relay     -I$(INET_ROOT)/src/linklayer/ieee8021d/rstp     -I$(INET_ROOT)/src/linklayer/ieee8021d/stp     -I$(INET_ROOT)/src/linklayer/ieee8021d/tester     -I$(INET_ROOT)/src/linklayer/loopback     -I$(INET_ROOT)/src/linklayer/ppp     -I$(INET_ROOT)/src/linklayer/queue     -I$(INET_ROOT)/src/linklayer/radio     -I$(INET_ROOT)/src/linklayer/radio/propagation     -I$(INET_ROOT)/src/mobility     -I$(INET_ROOT)/src/mobility/common     -I$(INET_ROOT)/src/mobility/contract     -I$(INET_ROOT)/src/mobility/group     -I$(INET_ROOT)/src/mobility/single     -I$(INET_ROOT)/src/mobility/static     -I$(INET_ROOT)/src/networklayer     -I$(INET_ROOT)/src/networklayer/arp     -I$(INET_ROOT)/src/networklayer/autorouting     -I$(INET_ROOT)/src/networklayer/autorouting/ipv4     -I$(INET_ROOT)/src/networklayer/autorouting/ipv6     -I$(INET_ROOT)/src/networklayer/bgpv4     -I$(INET_ROOT)/src/networklayer/bgpv4/BGPMessage     -I$(INET_ROOT)/src/networklayer/common     -I$(INET_ROOT)/src/networklayer/contract     -I$(INET_ROOT)/src/networklayer/diffserv     -I$(INET_ROOT)/src/networklayer/icmpv6     -I$(INET_ROOT)/src/networklayer/internetcloud     -I$(INET_ROOT)/src/networklayer/ipv4     -I$(INET_ROOT)/src/networklayer/ipv6     -I$(INET_ROOT)/src/networklayer/ipv6tunneling     -I$(INET_ROOT)/src/networklayer/ldp     -I$(INET_ROOT)/src/networklayer/manetrouting     -I$(INET_ROOT)/src/networklayer/manetrouting/aodv-uu     -I$(INET_ROOT)/src/networklayer/manetrouting/aodv-uu/aodv-uu     -I$(INET_ROOT)/src/networklayer/manetrouting/base     -I$(INET_ROOT)/src/networklayer/manetrouting/batman     -I$(INET_ROOT)/src/networklayer/manetrouting/batman/batmand     -I$(INET_ROOT)/src/networklayer/manetrouting/batman/batmand/orig     -I$(INET_ROOT)/src/networklayer/manetrouting/dsdv     -I$(INET_ROOT)/src/networklayer/manetrouting/dsr     -I$(INET_ROOT)/src/networklayer/manetrouting/dsr/dsr-uu     -I$(INET_ROOT)/src/networklayer/manetrouting/dymo     -I$(INET_ROOT)/src/networklayer/manetrouting/dymo/dymoum     -I$(INET_ROOT)/src/networklayer/manetrouting/dymo_fau     -I$(INET_ROOT)/src/networklayer/manetrouting/olsr     -I$(INET_ROOT)/src/networklayer/mpls     -I$(INET_ROOT)/src/networklayer/ospfv2     -I$(INET_ROOT)/src/networklayer/ospfv2/interface     -I$(INET_ROOT)/src/networklayer/ospfv2/messagehandler     -I$(INET_ROOT)/src/networklayer/ospfv2/neighbor     -I$(INET_ROOT)/src/networklayer/ospfv2/router     -I$(INET_ROOT)/src/networklayer/routing     -I$(INET_ROOT)/src/networklayer/routing/aodv     -I$(INET_ROOT)/src/networklayer/routing/dymo     -I$(INET_ROOT)/src/networklayer/routing/gpsr     -I$(INET_ROOT)/src/networklayer/routing/rip     -I$(INET_ROOT)/src/networklayer/rsvp_te     -I$(INET_ROOT)/src/networklayer/ted     -I$(INET_ROOT)/src/networklayer/xmipv6     -I$(INET_ROOT)/src/nodes     -I$(INET_ROOT)/src/nodes/aodv     -I$(INET_ROOT)/src/nodes/bgp     -I$(INET_ROOT)/src/nodes/dymo     -I$(INET_ROOT)/src/nodes/ethernet     -I$(INET_ROOT)/src/nodes/gpsr     -I$(INET_ROOT)/src/nodes/httptools     -I$(INET_ROOT)/src/nodes/inet     -I$(INET_ROOT)/src/nodes/internetcloud     -I$(INET_ROOT)/src/nodes/ipv6     -I$(INET_ROOT)/src/nodes/mpls     -I$(INET_ROOT)/src/nodes/ospfv2     -I$(INET_ROOT)/src/nodes/rip     -I$(INET_ROOT)/src/nodes/rtp     -I$(INET_ROOT)/src/nodes/wireless     -I$(INET_ROOT)/src/nodes/xmipv6     -I$(INET_ROOT)/src/status     -I$(INET_ROOT)/src/transport     -I$(INET_ROOT)/src/transport/contract     -I$(INET_ROOT)/src/transport/rtp     -I$(INET_ROOT)/src/transport/rtp/profiles     -I$(INET_ROOT)/src/transport/rtp/profiles/avprofile     -I$(INET_ROOT)/src/transport/sctp     -I$(INET_ROOT)/src/transport/tcp     -I$(INET_ROOT)/src/transport/tcp/flavours     -I$(INET_ROOT)/src/transport/tcp/queues     -I$(INET_ROOT)/src/transport/tcp_common     -I$(INET_ROOT)/src/transport/udp     -I$(INET_ROOT)/src/util     -I$(INET_ROOT)/src/util/headerserializers     -I$(INET_ROOT)/src/util/headerserializers/headers     -I$(INET_ROOT)/src/util/headerserializers/ipv4     -I$(INET_ROOT)/src/util/headerserializers/ipv4/headers     -I$(INET_ROOT)/src/util/headerserializers/ipv6     -I$(INET_ROOT)/src/util/headerserializers/ipv6/headers     -I$(INET_ROOT)/src/util/headerserializers/sctp     -I$(INET_ROOT)/src/util/headerserializers/sctp/headers     -I$(INET_ROOT)/src/util/headerserializers/tcp     -I$(INET_ROOT)/src/util/headerserializers/tcp/headers     -I$(INET_ROOT)/src/util/headerserializers/udp     -I$(INET_ROOT)/src/util/headerserializers/udp/headers     -I$(INET_ROOT)/src/util/messageprinters     -I$(INET_ROOT)/src/world     -I$(INET_ROOT)/src/world/annotations     -I$(INET_ROOT)/src/world/httptools     -I$(INET_ROOT)/src/world/obstacles     -I$(INET_ROOT)/src/world/radio     -I$(INET_ROOT)/src/world/scenario     -I$(INET_ROOT)/src/world/traci -o ieee802154inet_standalone -L$(INET_ROOT)/src -linet|' Makefile",
            ],
            "build_commands": ["opp_makemake -f --deep -o limosim -O out -KINET_PROJ=$INET_ROOT -DINET_IMPORT -X./ui -I. -I$INET_ROOT/src -L$INET_ROOT/src -lINET && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": [r"""make clean"""]
            # limosim -n $LIMOSIM_ROOT/omnet:$INET_ROOT/src
        },

        {
            # NOT WORKING - model error
            "name": "ble_allinone", "version": "master",
            "required_projects": {"omnetpp": ["4.4.1"], "inet": ["2.1.0"]},
            "download_commands": [
                "mkdir ble_allinone-master",
                "cd ble_allinone-master",
                "curl -L -o BLEsim.tgz https://github.com/omnetpp-models/archive/releases/download/archive/BLEsim.tgz --progress-bar",
                "tar -xvzf BLEsim.tgz",
                "rm BLEsim.tgz",
                "mv MiXiM ble-src",
                "curl -L -o 2.3.tar.gz https://github.com/omnetpp-models/mixim/archive/refs/tags/2.3.tar.gz --progress-bar",
                "tar -xvzf 2.3.tar.gz --strip=1",
                "rm 2.3.tar.gz",
                "cp -r ble-src/* .",
            ],
            # "download_url": "https://github.com/omnetpp-models/mixim/archive/refs/tags/2.3.tar.gz",
            "patch_commands": ["sed -i -E 's|INET_PROJECT_DIR=.*|INET_PROJECT_DIR=$(INET_ROOT)|' Makefile",
                               "sed -i -E 's|lINETPath=.*|lINETPath=\"$INET_ROOT\"|' src/run_mixim",
                               "sed -i 's|package inet|package inet_stub|' src/inet_stub/*.ned",
                               "sed -i 's|package inet.|package inet_stub.|' src/inet_stub/*/*.ned",
                               "sed -i 's|package inet.|package inet_stub.|' src/inet_stub/*/*/*.ned",
                               "sed -i 's|ChannelTbl({1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1})|ChannelTbl{1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1}|' src/modules/utility/ConstsBLE.h",
                               r"""find . -type f -name 'run' -exec chmod +x {} \;""",
            ],
            "setenv_commands": [
                "export INET_PROJ=$INET_ROOT",
                "export MIXIM_ROOT=$BLE_ALLINONE_ROOT",
                "export PATH=$MIXIM_ROOT/src:$PATH",
            ],
            # "download_url": "https://github.com/omnetpp-models/archive/releases/download/archive/BLEsim.tgz",
            # "patch_commands": [
                # "sed -i 's|||g' ",
                # "sed -i 's|MiXiMDefs.h|base/utils/MiXiMDefs.h|g' src/*/*/*.h",
            # ],
            "build_commands": ["make makefiles-using-inet && CXXFLAGS='-Wno-gnu-array-member-paren-init' make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            # "build_commands": ["cd src && opp_makemake -f --deep -o ble -O out -KINET_PROJ=$MIXIM_ROOT -DINET_IMPORT -L$MIXIM_ROOT/src -I. -I$MIXIM_ROOT/src -I$MIXIM_ROOT/base  -I$MIXIM_ROOT/base/connectionManager  -I$MIXIM_ROOT/base/messages  -I$MIXIM_ROOT/base/modules  -I$MIXIM_ROOT/base/phyLayer  -I$MIXIM_ROOT/base/utils  -I$MIXIM_ROOT/inet_stub  -I$MIXIM_ROOT/inet_stub/base  -I$MIXIM_ROOT/inet_stub/linklayer  -I$MIXIM_ROOT/inet_stub/linklayer/contract  -I$MIXIM_ROOT/inet_stub/mobility  -I$MIXIM_ROOT/inet_stub/mobility/models  -I$MIXIM_ROOT/inet_stub/networklayer  -I$MIXIM_ROOT/inet_stub/networklayer/common  -I$MIXIM_ROOT/inet_stub/util  -I$MIXIM_ROOT/modules  -I$MIXIM_ROOT/modules/analogueModel  -I$MIXIM_ROOT/modules/application  -I$MIXIM_ROOT/modules/connectionManager  -I$MIXIM_ROOT/modules/mac  -I$MIXIM_ROOT/modules/messages  -I$MIXIM_ROOT/modules/netw  -I$MIXIM_ROOT/modules/nic  -I$MIXIM_ROOT/modules/node  -I$MIXIM_ROOT/modules/phy  -I$MIXIM_ROOT/modules/power  -I$MIXIM_ROOT/modules/power/battery  -I$MIXIM_ROOT/modules/transport  -I$MIXIM_ROOT/modules/utility && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": [r"""make clean"""],
        },

        {
            # NOT WORKING - build error
            "name": "ble_allinone", "version": "withoutinet",
            "required_projects": {"omnetpp": ["4.4.1"]},
            "download_commands": [
                "mkdir ble_allinone-withoutinet",
                "cd ble_allinone-withoutinet",
                "curl -L -o BLEsim.tgz https://github.com/omnetpp-models/archive/releases/download/archive/BLEsim.tgz --progress-bar",
                "tar -xvzf BLEsim.tgz",
                "rm BLEsim.tgz",
                "mv MiXiM ble-src",
                "curl -L -o 2.3.tar.gz https://github.com/omnetpp-models/mixim/archive/refs/tags/2.3.tar.gz --progress-bar",
                "tar -xvzf 2.3.tar.gz --strip=1",
                "rm 2.3.tar.gz",
                "cp -r ble-src/* .",
            ],
            # "download_url": "https://github.com/omnetpp-models/mixim/archive/refs/tags/2.3.tar.gz",
            "patch_commands": [
                "sed -i -E 's|INET_PROJECT_DIR=.*|INET_PROJECT_DIR=$(INET_ROOT)|' Makefile",
                "echo 'WTF'",
                "pwd",
                "sed -i -E 's|lINETPath=.*|lINETPath=$(INET_ROOT)|' src/run_mixim",
                "sed -i 's|ChannelTbl({1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1})|ChannelTbl{1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1}|' src/modules/utility/ConstsBLE.h"
                ],
            "setenv_commands": [
                # "export INET_PROJ=$INET_ROOT",
                "export MIXIM_ROOT=$BLE_ALLINONE_ROOT",
                "export PATH=$MIXIM_ROOT/src:$PATH",
            ],
            # "download_url": "https://github.com/omnetpp-models/archive/releases/download/archive/BLEsim.tgz",
            # "patch_commands": [
                # "sed -i 's|||g' ",
                # "sed -i 's|MiXiMDefs.h|base/utils/MiXiMDefs.h|g' src/*/*/*.h",
            # ],
            "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            # "build_commands": ["cd src && opp_makemake -f --deep -o ble -O out -KINET_PROJ=$MIXIM_ROOT -DINET_IMPORT -L$MIXIM_ROOT/src -I. -I$MIXIM_ROOT/src -I$MIXIM_ROOT/base  -I$MIXIM_ROOT/base/connectionManager  -I$MIXIM_ROOT/base/messages  -I$MIXIM_ROOT/base/modules  -I$MIXIM_ROOT/base/phyLayer  -I$MIXIM_ROOT/base/utils  -I$MIXIM_ROOT/inet_stub  -I$MIXIM_ROOT/inet_stub/base  -I$MIXIM_ROOT/inet_stub/linklayer  -I$MIXIM_ROOT/inet_stub/linklayer/contract  -I$MIXIM_ROOT/inet_stub/mobility  -I$MIXIM_ROOT/inet_stub/mobility/models  -I$MIXIM_ROOT/inet_stub/networklayer  -I$MIXIM_ROOT/inet_stub/networklayer/common  -I$MIXIM_ROOT/inet_stub/util  -I$MIXIM_ROOT/modules  -I$MIXIM_ROOT/modules/analogueModel  -I$MIXIM_ROOT/modules/application  -I$MIXIM_ROOT/modules/connectionManager  -I$MIXIM_ROOT/modules/mac  -I$MIXIM_ROOT/modules/messages  -I$MIXIM_ROOT/modules/netw  -I$MIXIM_ROOT/modules/nic  -I$MIXIM_ROOT/modules/node  -I$MIXIM_ROOT/modules/phy  -I$MIXIM_ROOT/modules/power  -I$MIXIM_ROOT/modules/power/battery  -I$MIXIM_ROOT/modules/transport  -I$MIXIM_ROOT/modules/utility && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": [r"""make clean"""],
        },

        {
            # NOT WORKING
            # cant find includes
            # opp_makemake -f --deep -o epon -O out -L$INETMANET_ROOT/src -lINET -KINETMANET_PROJ=$INETMANET_ROOT -I$INETMANET_ROOT/src -I.
            # TODO: use download commands
            "name": "epon", "version": "0.8b",
            # "nix_packages": ["glibc"],
            "required_projects": {"omnetpp": ["5.7.0"], "inetmanet3": ["3.8.2"]},
            "download_url": "https://github.com/omnetpp-models/archive/releases/download/archive/epon-0.8b__.tar.gz",
            # "setenv_commands": ["export INETMANET_PROJ=$INETMANET_ROOT"],
            "patch_commands": [
                "sed -i 's|INETMANET_PROJ=/media/data/Linux/omnet/inetmanet-inetmanet-00f64c2|INETMANET_PROJ=$(INETMANET_ROOT)|g' */Makefile",
                # "sed -i 's|EtherEncap.h|inet/linklayer/ethernet/EtherEncap.h|g' */*/*.cc */*/*/*.h",
            ],
            # "build_commands": ["opp_makemake -f --deep --nolink -O out -d src -X. -I$INETMANET_ROOT/src/inet -L$INETMANET_ROOT/out/$CONFIGNAME/src -L./out/$CONFIGNAME/src -linet -KINETMANET_PROJ=$INETMANET_ROOT && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            # "build_commands": ["cd Vlans/src && opp_makemake -f --deep --make-so -o epon -O out -I. -I/common -I/linklayer -I/networklayer -I/networklayer/autoconfig -I/OLT -I/ONU -I$INETMANET_ROOT/src/inet/util/headerserializers/headers -I$INETMANET_ROOT/src/inet/networklayer/arp -I$INETMANET_ROOT/src/inet/transport/sctp -I$INETMANET_ROOT/src/inet/world -I$INETMANET_ROOT/src/inet/transport/contract -I$INETMANET_ROOT/src/inet/linklayer/mfcore -I$INETMANET_ROOT/src/inet/linklayer/ethernet -I$INETMANET_ROOT/src/inet/util -I$INETMANET_ROOT/src/inet/networklayer/ted -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac -I$INETMANET_ROOT/src/inet/networklayer/common -I$INETMANET_ROOT/src/inet/networklayer/ipv6 -I$INETMANET_ROOT/src/inet/applications/pingapp -I$INETMANET_ROOT/src/inet/networklayer/ldp -I$INETMANET_ROOT/src/inet/transport/tcp -I$INETMANET_ROOT/src/inet/util/headerserializers -I$INETMANET_ROOT/src/inet/networklayer/rsvp_te -I$INETMANET_ROOT/src/inet/transport/udp -I$INETMANET_ROOT/src/inet/networklayer/ipv4 -I$INETMANET_ROOT/src/inet/networklayer/icmpv6 -I$INETMANET_ROOT/src/inet/base -I$INETMANET_ROOT/src/inet/networklayer/contract -I$INETMANET_ROOT/src/inet/networklayer/manetrouting/base -I$INETMANET_ROOT/src/inet/networklayer/mpls -I$INETMANET_ROOT/src/inet/linklayer/contract -I$INETMANET_ROOT/src/inet/networklayer/autorouting -L$INETMANET_ROOT/src -lINET -I$OMNETPP_ROOT/src -KINETMANET_PROJ=$INETMANET_ROOT"],
            "build_commands": ["cd Vlans/src && opp_makemake -f --deep --make-so -o epon -O out -I. -I/common -I/linklayer -I/networklayer -I/networklayer/autoconfig -I/OLT -I/ONU -I$INETMANET_ROOT/src -I$INETMANET_ROOT/src/inet -I$INETMANET_ROOT/src/inet/visualizer -I$INETMANET_ROOT/src/inet/visualizer/scene -I$INETMANET_ROOT/src/inet/visualizer/transportlayer -I$INETMANET_ROOT/src/inet/visualizer/contract -I$INETMANET_ROOT/src/inet/visualizer/util -I$INETMANET_ROOT/src/inet/visualizer/power -I$INETMANET_ROOT/src/inet/visualizer/networklayer -I$INETMANET_ROOT/src/inet/visualizer/integrated -I$INETMANET_ROOT/src/inet/visualizer/mobility -I$INETMANET_ROOT/src/inet/visualizer/common -I$INETMANET_ROOT/src/inet/visualizer/linklayer -I$INETMANET_ROOT/src/inet/visualizer/physicallayer -I$INETMANET_ROOT/src/inet/visualizer/environment -I$INETMANET_ROOT/src/inet/visualizer/base -I$INETMANET_ROOT/src/inet/routing -I$INETMANET_ROOT/src/inet/routing/gpsr -I$INETMANET_ROOT/src/inet/routing/aodv -I$INETMANET_ROOT/src/inet/routing/pim -I$INETMANET_ROOT/src/inet/routing/pim/tables -I$INETMANET_ROOT/src/inet/routing/pim/modes -I$INETMANET_ROOT/src/inet/routing/extras -I$INETMANET_ROOT/src/inet/routing/extras/dsr -I$INETMANET_ROOT/src/inet/routing/extras/dsr/dsr-uu -I$INETMANET_ROOT/src/inet/routing/extras/saors -I$INETMANET_ROOT/src/inet/routing/extras/saors/SimBetTS -I$INETMANET_ROOT/src/inet/routing/extras/saors/SaorsManager -I$INETMANET_ROOT/src/inet/routing/extras/saors/r_dymo -I$INETMANET_ROOT/src/inet/routing/extras/saors/dtrouting -I$INETMANET_ROOT/src/inet/routing/extras/saors/ep_dymo -I$INETMANET_ROOT/src/inet/routing/extras/saors/dt_dymo -I$INETMANET_ROOT/src/inet/routing/extras/saors/base -I$INETMANET_ROOT/src/inet/routing/extras/saors/sampho -I$INETMANET_ROOT/src/inet/routing/extras/PASER -I$INETMANET_ROOT/src/inet/routing/extras/PASER/IPv4_ADAPTED -I$INETMANET_ROOT/src/inet/routing/extras/PASER/paser_socket -I$INETMANET_ROOT/src/inet/routing/extras/PASER/paser_configuration -I$INETMANET_ROOT/src/inet/routing/extras/PASER/paser_buffer -I$INETMANET_ROOT/src/inet/routing/extras/PASER/paser_timer_management -I$INETMANET_ROOT/src/inet/routing/extras/PASER/simple_kdc -I$INETMANET_ROOT/src/inet/routing/extras/PASER/simple_kdc/kdc_message -I$INETMANET_ROOT/src/inet/routing/extras/PASER/paser_tables -I$INETMANET_ROOT/src/inet/routing/extras/PASER/paser_logic -I$INETMANET_ROOT/src/inet/routing/extras/PASER/paser_logic/message_processing -I$INETMANET_ROOT/src/inet/routing/extras/PASER/paser_logic/route_discovery -I$INETMANET_ROOT/src/inet/routing/extras/PASER/paser_logic/route_maintenance -I$INETMANET_ROOT/src/inet/routing/extras/PASER/paser_logic/cryptography -I$INETMANET_ROOT/src/inet/routing/extras/PASER/paser_message_structure -I$INETMANET_ROOT/src/inet/routing/extras/PASER/generic -I$INETMANET_ROOT/src/inet/routing/extras/aodv-uu -I$INETMANET_ROOT/src/inet/routing/extras/aodv-uu/aodv-uu -I$INETMANET_ROOT/src/inet/routing/extras/dymo -I$INETMANET_ROOT/src/inet/routing/extras/dymo/dymoum -I$INETMANET_ROOT/src/inet/routing/extras/olsr -I$INETMANET_ROOT/src/inet/routing/extras/dsdv -I$INETMANET_ROOT/src/inet/routing/extras/dymo_fau -I$INETMANET_ROOT/src/inet/routing/extras/batman -I$INETMANET_ROOT/src/inet/routing/extras/batman/batmand -I$INETMANET_ROOT/src/inet/routing/extras/batman/batmand/orig -I$INETMANET_ROOT/src/inet/routing/extras/base -I$INETMANET_ROOT/src/inet/routing/rip -I$INETMANET_ROOT/src/inet/routing/contract -I$INETMANET_ROOT/src/inet/routing/ospfv2 -I$INETMANET_ROOT/src/inet/routing/ospfv2/interface -I$INETMANET_ROOT/src/inet/routing/ospfv2/router -I$INETMANET_ROOT/src/inet/routing/ospfv2/neighbor -I$INETMANET_ROOT/src/inet/routing/ospfv2/messagehandler -I$INETMANET_ROOT/src/inet/routing/dymo -I$INETMANET_ROOT/src/inet/routing/bgpv4 -I$INETMANET_ROOT/src/inet/routing/bgpv4/BGPMessage -I$INETMANET_ROOT/src/inet/transportlayer -I$INETMANET_ROOT/src/inet/transportlayer/tcp_nsc -I$INETMANET_ROOT/src/inet/transportlayer/tcp_nsc/queues -I$INETMANET_ROOT/src/inet/transportlayer/tcp -I$INETMANET_ROOT/src/inet/transportlayer/tcp/flavours -I$INETMANET_ROOT/src/inet/transportlayer/tcp/queues -I$INETMANET_ROOT/src/inet/transportlayer/tcp_lwip -I$INETMANET_ROOT/src/inet/transportlayer/tcp_lwip/lwip -I$INETMANET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/core -I$INETMANET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/include -I$INETMANET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/include/ipv6 -I$INETMANET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/include/ipv6/lwip -I$INETMANET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/include/lwip -I$INETMANET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/include/netif -I$INETMANET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/include/arch -I$INETMANET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/include/ipv4 -I$INETMANET_ROOT/src/inet/transportlayer/tcp_lwip/lwip/include/ipv4/lwip -I$INETMANET_ROOT/src/inet/transportlayer/tcp_lwip/queues -I$INETMANET_ROOT/src/inet/transportlayer/contract -I$INETMANET_ROOT/src/inet/transportlayer/contract/tcp -I$INETMANET_ROOT/src/inet/transportlayer/contract/sctp -I$INETMANET_ROOT/src/inet/transportlayer/contract/udp -I$INETMANET_ROOT/src/inet/transportlayer/rtp -I$INETMANET_ROOT/src/inet/transportlayer/rtp/profiles -I$INETMANET_ROOT/src/inet/transportlayer/rtp/profiles/avprofile -I$INETMANET_ROOT/src/inet/transportlayer/sctp -I$INETMANET_ROOT/src/inet/transportlayer/udp -I$INETMANET_ROOT/src/inet/transportlayer/tcp_common -I$INETMANET_ROOT/src/inet/transportlayer/base -I$INETMANET_ROOT/src/inet/node -I$INETMANET_ROOT/src/inet/node/internetcloud -I$INETMANET_ROOT/src/inet/node/gpsr -I$INETMANET_ROOT/src/inet/node/mpls -I$INETMANET_ROOT/src/inet/node/aodv -I$INETMANET_ROOT/src/inet/node/wireless -I$INETMANET_ROOT/src/inet/node/ipv6 -I$INETMANET_ROOT/src/inet/node/rip -I$INETMANET_ROOT/src/inet/node/ospfv2 -I$INETMANET_ROOT/src/inet/node/rtp -I$INETMANET_ROOT/src/inet/node/xmipv6 -I$INETMANET_ROOT/src/inet/node/dymo -I$INETMANET_ROOT/src/inet/node/inet -I$INETMANET_ROOT/src/inet/node/httptools -I$INETMANET_ROOT/src/inet/node/ethernet -I$INETMANET_ROOT/src/inet/node/bgp -I$INETMANET_ROOT/src/inet/node/packetdrill -I$INETMANET_ROOT/src/inet/neta -I$INETMANET_ROOT/src/inet/neta/attacks -I$INETMANET_ROOT/src/inet/neta/attacks/controlmessages -I$INETMANET_ROOT/src/inet/neta/attacks/controlmessages/droppingAttack -I$INETMANET_ROOT/src/inet/neta/attacks/controlmessages/delayAttack -I$INETMANET_ROOT/src/inet/neta/attacks/controlmessages/sinkholeAttack -I$INETMANET_ROOT/src/inet/neta/attacks/controllers -I$INETMANET_ROOT/src/inet/neta/attacks/controllers/droppingAttack -I$INETMANET_ROOT/src/inet/neta/attacks/controllers/delayAttack -I$INETMANET_ROOT/src/inet/neta/attacks/controllers/sinkholeAttack -I$INETMANET_ROOT/src/inet/neta/nodes -I$INETMANET_ROOT/src/inet/neta/common -I$INETMANET_ROOT/src/inet/neta/common/log -I$INETMANET_ROOT/src/inet/neta/common/utils -I$INETMANET_ROOT/src/inet/neta/hackedmodules -I$INETMANET_ROOT/src/inet/neta/hackedmodules/networklayer -I$INETMANET_ROOT/src/inet/neta/hackedmodules/networklayer/manetrouting -I$INETMANET_ROOT/src/inet/neta/hackedmodules/networklayer/manetrouting/aodv -I$INETMANET_ROOT/src/inet/neta/hackedmodules/networklayer/manetrouting/aodv/NA_aodv-uu -I$INETMANET_ROOT/src/inet/neta/hackedmodules/networklayer/ipv4 -I$INETMANET_ROOT/src/inet/neta/hackedmodules/applications -I$INETMANET_ROOT/src/inet/neta/hackedmodules/applications/udpapp -I$INETMANET_ROOT/src/inet/power -I$INETMANET_ROOT/src/inet/power/contract -I$INETMANET_ROOT/src/inet/power/management -I$INETMANET_ROOT/src/inet/power/generator -I$INETMANET_ROOT/src/inet/power/consumer -I$INETMANET_ROOT/src/inet/power/base -I$INETMANET_ROOT/src/inet/power/storage -I$INETMANET_ROOT/src/inet/networklayer -I$INETMANET_ROOT/src/inet/networklayer/internetcloud -I$INETMANET_ROOT/src/inet/networklayer/mpls -I$INETMANET_ROOT/src/inet/networklayer/ldp -I$INETMANET_ROOT/src/inet/networklayer/wiseroute -I$INETMANET_ROOT/src/inet/networklayer/ted -I$INETMANET_ROOT/src/inet/networklayer/ipv6 -I$INETMANET_ROOT/src/inet/networklayer/contract -I$INETMANET_ROOT/src/inet/networklayer/contract/ipv6 -I$INETMANET_ROOT/src/inet/networklayer/contract/generic -I$INETMANET_ROOT/src/inet/networklayer/contract/ipv4 -I$INETMANET_ROOT/src/inet/networklayer/flood -I$INETMANET_ROOT/src/inet/networklayer/multi -I$INETMANET_ROOT/src/inet/networklayer/ipv6tunneling -I$INETMANET_ROOT/src/inet/networklayer/icmpv6 -I$INETMANET_ROOT/src/inet/networklayer/xmipv6 -I$INETMANET_ROOT/src/inet/networklayer/diffserv -I$INETMANET_ROOT/src/inet/networklayer/common -I$INETMANET_ROOT/src/inet/networklayer/configurator -I$INETMANET_ROOT/src/inet/networklayer/configurator/ipv6 -I$INETMANET_ROOT/src/inet/networklayer/configurator/contract -I$INETMANET_ROOT/src/inet/networklayer/configurator/generic -I$INETMANET_ROOT/src/inet/networklayer/configurator/base -I$INETMANET_ROOT/src/inet/networklayer/configurator/ipv4 -I$INETMANET_ROOT/src/inet/networklayer/probabilistic -I$INETMANET_ROOT/src/inet/networklayer/generic -I$INETMANET_ROOT/src/inet/networklayer/arp -I$INETMANET_ROOT/src/inet/networklayer/arp/generic -I$INETMANET_ROOT/src/inet/networklayer/arp/ipv4 -I$INETMANET_ROOT/src/inet/networklayer/base -I$INETMANET_ROOT/src/inet/networklayer/rsvp_te -I$INETMANET_ROOT/src/inet/networklayer/ipv4 -I$INETMANET_ROOT/src/inet/networklayer/ipv4/ipsec -I$INETMANET_ROOT/src/inet/applications -I$INETMANET_ROOT/src/inet/applications/voipstream -I$INETMANET_ROOT/src/inet/applications/netperfmeter -I$INETMANET_ROOT/src/inet/applications/voip -I$INETMANET_ROOT/src/inet/applications/sctpapp -I$INETMANET_ROOT/src/inet/applications/udpapp -I$INETMANET_ROOT/src/inet/applications/rtpapp -I$INETMANET_ROOT/src/inet/applications/pingapp -I$INETMANET_ROOT/src/inet/applications/contract -I$INETMANET_ROOT/src/inet/applications/tunapp -I$INETMANET_ROOT/src/inet/applications/tcpapp -I$INETMANET_ROOT/src/inet/applications/httptools -I$INETMANET_ROOT/src/inet/applications/httptools/browser -I$INETMANET_ROOT/src/inet/applications/httptools/common -I$INETMANET_ROOT/src/inet/applications/httptools/configurator -I$INETMANET_ROOT/src/inet/applications/httptools/server -I$INETMANET_ROOT/src/inet/applications/dhcp -I$INETMANET_ROOT/src/inet/applications/ethernet -I$INETMANET_ROOT/src/inet/applications/generic -I$INETMANET_ROOT/src/inet/applications/base -I$INETMANET_ROOT/src/inet/applications/trafgen -I$INETMANET_ROOT/src/inet/applications/packetdrill -I$INETMANET_ROOT/src/inet/mobility -I$INETMANET_ROOT/src/inet/mobility/traci -I$INETMANET_ROOT/src/inet/mobility/contract -I$INETMANET_ROOT/src/inet/mobility/group -I$INETMANET_ROOT/src/inet/mobility/static -I$INETMANET_ROOT/src/inet/mobility/single -I$INETMANET_ROOT/src/inet/mobility/base -I$INETMANET_ROOT/src/inet/common -I$INETMANET_ROOT/src/inet/common/misc -I$INETMANET_ROOT/src/inet/common/lifecycle -I$INETMANET_ROOT/src/inet/common/queue -I$INETMANET_ROOT/src/inet/common/scenario -I$INETMANET_ROOT/src/inet/common/geometry -I$INETMANET_ROOT/src/inet/common/geometry/object -I$INETMANET_ROOT/src/inet/common/geometry/shape -I$INETMANET_ROOT/src/inet/common/geometry/shape/polyhedron -I$INETMANET_ROOT/src/inet/common/geometry/common -I$INETMANET_ROOT/src/inet/common/geometry/base -I$INETMANET_ROOT/src/inet/common/geometry/container -I$INETMANET_ROOT/src/inet/common/mapping -I$INETMANET_ROOT/src/inet/common/packet -I$INETMANET_ROOT/src/inet/common/serializer -I$INETMANET_ROOT/src/inet/common/serializer/tcp -I$INETMANET_ROOT/src/inet/common/serializer/tcp/headers -I$INETMANET_ROOT/src/inet/common/serializer/ipv6 -I$INETMANET_ROOT/src/inet/common/serializer/ipv6/headers -I$INETMANET_ROOT/src/inet/common/serializer/headers -I$INETMANET_ROOT/src/inet/common/serializer/sctp -I$INETMANET_ROOT/src/inet/common/serializer/sctp/headers -I$INETMANET_ROOT/src/inet/common/serializer/udp -I$INETMANET_ROOT/src/inet/common/serializer/udp/headers -I$INETMANET_ROOT/src/inet/common/serializer/headerserializers -I$INETMANET_ROOT/src/inet/common/serializer/headerserializers/ieee80211 -I$INETMANET_ROOT/src/inet/common/serializer/headerserializers/ieee80211/headers -I$INETMANET_ROOT/src/inet/common/serializer/headerserializers/ethernet -I$INETMANET_ROOT/src/inet/common/serializer/headerserializers/arp -I$INETMANET_ROOT/src/inet/common/serializer/ipv4 -I$INETMANET_ROOT/src/inet/common/serializer/ipv4/headers -I$INETMANET_ROOT/src/inet/common/figures -I$INETMANET_ROOT/src/inet/underTest -I$INETMANET_ROOT/src/inet/underTest/hip -I$INETMANET_ROOT/src/inet/underTest/hip/nodes -I$INETMANET_ROOT/src/inet/underTest/hip/application -I$INETMANET_ROOT/src/inet/underTest/hip/base -I$INETMANET_ROOT/src/inet/linklayer -I$INETMANET_ROOT/src/inet/linklayer/bmac -I$INETMANET_ROOT/src/inet/linklayer/ppp -I$INETMANET_ROOT/src/inet/linklayer/tun -I$INETMANET_ROOT/src/inet/linklayer/ieee80211mesh -I$INETMANET_ROOT/src/inet/linklayer/ieee80211mesh/nodes -I$INETMANET_ROOT/src/inet/linklayer/ieee80211mesh/hwmp -I$INETMANET_ROOT/src/inet/linklayer/ieee80211mesh/mgmt -I$INETMANET_ROOT/src/inet/linklayer/ieee80211mesh/locator -I$INETMANET_ROOT/src/inet/linklayer/ieee80211mesh/ethernet -I$INETMANET_ROOT/src/inet/linklayer/lmac -I$INETMANET_ROOT/src/inet/linklayer/channels -I$INETMANET_ROOT/src/inet/linklayer/ieee802154 -I$INETMANET_ROOT/src/inet/linklayer/xmac -I$INETMANET_ROOT/src/inet/linklayer/ieee8021d -I$INETMANET_ROOT/src/inet/linklayer/ieee8021d/stp -I$INETMANET_ROOT/src/inet/linklayer/ieee8021d/rstp -I$INETMANET_ROOT/src/inet/linklayer/ieee8021d/tester -I$INETMANET_ROOT/src/inet/linklayer/ieee8021d/common -I$INETMANET_ROOT/src/inet/linklayer/ieee8021d/relay -I$INETMANET_ROOT/src/inet/linklayer/loopback -I$INETMANET_ROOT/src/inet/linklayer/contract -I$INETMANET_ROOT/src/inet/linklayer/ideal -I$INETMANET_ROOT/src/inet/linklayer/csma -I$INETMANET_ROOT/src/inet/linklayer/ext -I$INETMANET_ROOT/src/inet/linklayer/ieee80211 -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/queue -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/sequencenumberassignment -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/blockackreordering -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/lifetime -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/framesequence -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/contract -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/recipient -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/contention -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/channelaccess -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/blockack -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/rateselection -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/common -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/aggregation -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/ratecontrol -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/coordinationfunction -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/statistics -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/protectionmechanism -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/originator -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/fragmentation -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mac/duplicateremoval -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mgmt -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/mgmt/wpa2 -I$INETMANET_ROOT/src/inet/linklayer/ieee80211/oldmac -I$INETMANET_ROOT/src/inet/linklayer/common -I$INETMANET_ROOT/src/inet/linklayer/configurator -I$INETMANET_ROOT/src/inet/linklayer/csmaca -I$INETMANET_ROOT/src/inet/linklayer/ethernet -I$INETMANET_ROOT/src/inet/linklayer/ethernet/switch -I$INETMANET_ROOT/src/inet/linklayer/base -I$INETMANET_ROOT/src/inet/securityModule -I$INETMANET_ROOT/src/inet/securityModule/message -I$INETMANET_ROOT/src/inet/physicallayer -I$INETMANET_ROOT/src/inet/physicallayer/analogmodel -I$INETMANET_ROOT/src/inet/physicallayer/analogmodel/bitlevel -I$INETMANET_ROOT/src/inet/physicallayer/analogmodel/packetlevel -I$INETMANET_ROOT/src/inet/physicallayer/apskradio -I$INETMANET_ROOT/src/inet/physicallayer/apskradio/bitlevel -I$INETMANET_ROOT/src/inet/physicallayer/apskradio/bitlevel/errormodel -I$INETMANET_ROOT/src/inet/physicallayer/apskradio/packetlevel -I$INETMANET_ROOT/src/inet/physicallayer/apskradio/packetlevel/errormodel -I$INETMANET_ROOT/src/inet/physicallayer/idealradio -I$INETMANET_ROOT/src/inet/physicallayer/ieee802154 -I$INETMANET_ROOT/src/inet/physicallayer/ieee802154/bitlevel -I$INETMANET_ROOT/src/inet/physicallayer/ieee802154/packetlevel -I$INETMANET_ROOT/src/inet/physicallayer/antenna -I$INETMANET_ROOT/src/inet/physicallayer/pathloss -I$INETMANET_ROOT/src/inet/physicallayer/backgroundnoise -I$INETMANET_ROOT/src/inet/physicallayer/contract -I$INETMANET_ROOT/src/inet/physicallayer/contract/bitlevel -I$INETMANET_ROOT/src/inet/physicallayer/contract/packetlevel -I$INETMANET_ROOT/src/inet/physicallayer/errormodel -I$INETMANET_ROOT/src/inet/physicallayer/errormodel/bitlevel -I$INETMANET_ROOT/src/inet/physicallayer/errormodel/packetlevel -I$INETMANET_ROOT/src/inet/physicallayer/ieee80211 -I$INETMANET_ROOT/src/inet/physicallayer/ieee80211/mode -I$INETMANET_ROOT/src/inet/physicallayer/ieee80211/bitlevel -I$INETMANET_ROOT/src/inet/physicallayer/ieee80211/bitlevel/errormodel -I$INETMANET_ROOT/src/inet/physicallayer/ieee80211/packetlevel -I$INETMANET_ROOT/src/inet/physicallayer/ieee80211/packetlevel/errormodel -I$INETMANET_ROOT/src/inet/physicallayer/obstacleloss -I$INETMANET_ROOT/src/inet/physicallayer/common -I$INETMANET_ROOT/src/inet/physicallayer/common/bitlevel -I$INETMANET_ROOT/src/inet/physicallayer/common/packetlevel -I$INETMANET_ROOT/src/inet/physicallayer/energyconsumer -I$INETMANET_ROOT/src/inet/physicallayer/propagation -I$INETMANET_ROOT/src/inet/physicallayer/communicationcache -I$INETMANET_ROOT/src/inet/physicallayer/modulation -I$INETMANET_ROOT/src/inet/physicallayer/neighborcache -I$INETMANET_ROOT/src/inet/physicallayer/base -I$INETMANET_ROOT/src/inet/physicallayer/base/bitlevel -I$INETMANET_ROOT/src/inet/physicallayer/base/packetlevel -I$INETMANET_ROOT/src/inet/environment -I$INETMANET_ROOT/src/inet/environment/contract -I$INETMANET_ROOT/src/inet/environment/common -I$INETMANET_ROOT/src/inet/environment/ground -I$INETMANET_ROOT/src/inet/environment/objectcache -L-I$INETMANET_ROOT/src -lINET -I$OMNETPP_ROOT/src -KINETMANET_PROJ=-I$INETMANET_ROOT"],
            "clean_commands": [r"""make clean"""],
        },

        {   # NOT WORKING - builds; model error Error in module (IBGenerator) FABRIC.H_1.gen: has no parameter called `GenModel'
            "name": "infiniband", "version": "1.0",
            "nix_packages": ["xml2"],
            "required_projects": {"omnetpp": ["3.3.1"]},
            "download_url": "https://github.com/omnetpp-models/archive/releases/download/archive/ib_macro_model.tgz",
            # "setenv_commands": ["export INETMANET_PROJ=$INETMANET_ROOT"],
            "patch_commands": [
                # """sed -i 's|<omnetpp.h>|"omnetpp.h"|g' src/*.h""",
                "sed -i 's|#include <stdio.h>|#include <stdio.h>\\n#include <cstring>|g' utils/vec_file.cpp",
                "sed -i 's|tclsh8.4|tclsh|g' utils/genIni",
            ],
            "build_commands": ["cd utils && make && cd ../src && make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": [r"""make clean"""],
        },

        {
            # NOT WORKING - builds; model error Error in module (IBGenerator) FABRIC.H_1.gen: has no parameter called `GenModel'
            "name": "infiniband_flit", "version": "1.0",
            "required_projects": {"omnetpp": ["3.3.1"]},
            "download_url": "https://github.com/omnetpp-models/archive/releases/download/archive/ib_macro_model.tgz",
            # "setenv_commands": ["export INETMANET_PROJ=$INETMANET_ROOT"],
            "patch_commands": [
                "sed -i 's|#include <stdio.h>|#include <stdio.h>\\n#include <cstring>|g' utils/vec_file.cpp",
                "sed -i 's|tclsh8.4|tclsh|g' utils/genIni",
            #     "sed -i 's|INETMANET_PROJ=/media/data/Linux/omnet/inetmanet-inetmanet-00f64c2|INETMANET_PROJ=$(INETMANET_ROOT)|g' Makefile src/Makefile",
            ],
            # "build_commands": ["make makefiles && make all -j$NIX_BUILD_CORES MODE=$BUILD_MODE CFLAGS='-std=c++11 -Wall -Wextra'"],
            "build_commands": ["cd utils && make && cd ../src && make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": [r"""make clean"""],
            # opp_makemake -N -u Cmdenv -f -I../utils -i '$OMNETPP_ROOT/include/omnetpp.h' -w -o ib_macro_model
        },

        {
            # WIP - compile error
            # make[5]: *** No rule to make target '../../.lib/libmodlib.la', needed by 'allsimple'.  Stop.
            "name": "pawis", "version": "2.0",
            "nix_packages": ["lua51Packages.lua", "automake", "perl", "libtool", "autoconf", "gcc48", "tk-8_5", "tcl-8_5",],
            "required_projects": {"omnetpp": ["3.3.1"]},
            "download_url": "https://sourceforge.net/projects/pawis/files/latest/download",
            "setenv_commands": ["export LUA_LIBS=${pkgs.lua51Packages.lua}/lib && echo $LUA_LIBS",
                                "export LUA_CFLAGS=${pkgs.lua51Packages.lua}/include && echo $LUA_CFLAGS",
                                "export PKG_CONFIG_PATH=${pkgs.lua51Packages.lua}/lib/pkgconfig",
                                "export OMNET_BASE=$OMNETPP_ROOT",
                                "export PAWIS_BASE=$PAWIS_ROOT/sim-framework",
                                "export LIBTOOL_ROOT=${pkgs.libtool}",
                                # 'export NIX_CFLAGS_COMPILE="-isystem ${pkgs.lua51Packages.lua}/include $NIX_CFLAGS_COMPILE"',
                                ],
            "patch_commands": [
                "sed -i 's|-llua5.1|-llua|g' sim-framework/configure modlib/configure",
                "sed -i 's|lua5.1|lua|g' sim-framework/configure.ac modlib/configure.in",
                "sed -i 's|#include <list>|#include <list>\\n#include <memory>|g' sim-framework/inc/base/*.h",
                "sed -i 's|../../../lib/libmodlib.la|../../../.lib/libmodlib.la|g' modlib/src/test/*/Makefile*",
                # ../../../lib/libmodlib.la
            ],
            # "build_commands": ['cd sim-framework && ./configure --prefix $PAWIS_ROOT/sim-framework OMNET_BASE=$OMNETPP_ROOT'],
            "build_commands": [
                # 'cd sim-framework && ./configure --prefix $PAWIS_ROOT/sim-framework OMNET_BASE=$OMNETPP_ROOT CXXFLAGS="-ggdb -O0 -Wall" LDFLAGS="-L$LUA_LIBS" LIBS="-llua"',
                # 'cd sim-framework && ./configure --includedir=$PAWIS_ROOT/sim-framework/inc --libdir=$PAWIS_ROOT/sim-framework/lib OMNET_BASE=$OMNETPP_ROOT CXXFLAGS="-ggdb -O0 -Wall"'
                'cd sim-framework && libtoolize --automake --copy && aclocal && autoheader && automake --add-missing --copy && autoconf && autoupdate',
                # './configure --includedir=$PAWIS_ROOT/sim-framework/inc --libdir=$PAWIS_ROOT/sim-framework/lib OMNET_BASE=$OMNETPP_ROOT CXXFLAGS="-ggdb -O0 -Wall"',
                './configure --prefix $PAWIS_ROOT/sim-framework OMNET_BASE=$OMNETPP_ROOT CXXFLAGS="-ggdb -O0 -Wall" LDFLAGS="-L$LUA_LIBS" LIBS="-llua" && make -j16 && make install',
                'cd ../modlib',
                'rm libtool && ln -v -s $LIBTOOL_ROOT/bin/libtool libtool',
                # './autogen.sh',
                'rm config.sub && ln -v -s $LIBTOOL_ROOT/share/libtool/build-aux/config.sub config.sub',
                'rm config.guess && ln -v -s $LIBTOOL_ROOT/share/libtool/build-aux/config.guess config.guess',
                'pwd && aclocal && autoheader && automake --add-missing --copy && autoconf && autoupdate',
                "./configure --prefix $PAWIS_ROOT/modlib PAWIS_BASE=$PAWIS_ROOT/sim-framework OMNET_BASE=$OMNETPP_ROOT CXXFLAGS='-ggdb -O0 -Wall' LDFLAGS='-L$LUA_LIBS' LIBS='-llua' --with-tkenv",
            ],
            # "setenv_commands": ["echo 'Hint: run exa - cant find NED includesmple simulations from their folder. For example, in examples/TwoSubnets folder: ./out/gcc-debug/TwoSubnets omnetpp.ini"]
            "clean_commands": [r"""make clean"""],
            # ./configure --prefix $PAWIS_ROOT/sim-framework OMNET_BASE=$OMNETPP_ROOT CXXFLAGS="-ggdb -O0 -Wall" LDFLAGS="-L$LUA_LIBS" LIBS="-llua"
        },

        {
            # NOT WORKING - needs matlab-link to build
            "name": "phoenixsim", "version": "master",
            # "nix_packages": ["lua"],
            "required_projects": {"omnetpp": ["4.5.x"]},
            "git_url": "https://github.com/lebiednik/PhoenixSim.git",
            # "setenv_commands": ["export LUA_LIBS=${pkgs.lua51Packages.lua}/lib && echo $LUA_LIBS",
            #                     "export LUA_CFLAGS=${pkgs.lua51Packages.lua}/include",
            #                     # "export PKG_CONFIG_PATH=${pkgs.lua51Packages.lua}/lib/pkgconfig",
            #                     # "export NIX_CFLAGS_COMPILE=${pkgs.lua51Packages.lua}/include"
            #                     ],
            "patch_commands": [
                """sed -i 's|include "MAC_token.h"|include "MAC_TOKEN.h"|g' */*/*.cc"""
            ],
            "build_commands": ["opp_makemake -f --deep -o PhoenixSim -O out -L$OMNETPP_ROOT/lib -loppsim && make -j16"],
            # "setenv_commands": ["echo 'Hint: run example simulations from their folder. For example, in examples/TwoSubnets folder: ./out/gcc-debug/TwoSubnets omnetpp.ini"]
            "clean_commands": [r"""make clean"""],
            # ./configure --prefix $PAWIS_ROOT/sim-framework OMNET_BASE=$OMNETPP_ROOT CXXFLAGS="-ggdb -O0 -Wall" LDFLAGS="-L$LUA_LIBS" LIBS="-llua"
        },

        {
            # WIP - model error; this should be its own project; should this be linked to inet?
            "name": "rimfading", "version": "20171123",    # latest master as of time of writing
            "nix_packages": ["python2"],
            "required_projects": {"omnetpp": ["5.4.x"], "inet": ["4.0.0"]},
            "smoke_test_commands": [
                "cp $INET_ROOT/showcases/wireless/pathloss/omnetpp.ini $INET_ROOT/showcases/wireless/pathloss/test.ini",
                """echo "\n[Config Test]\n*.radioMedium.pathLoss.typename = "RIMFading" " >> $INET_ROOT/showcases/wireless/pathloss/test.ini """,
                """if [ "$BUILD_MODE" = "debug" ]; then BUILD_MODE_SUFFIX="_dbg"; fi""",
                "inet$BUILD_MODE_SUFFIX $INET_ROOT/showcases/wireless/pathloss/test.ini",
                "rm $INET_ROOT/showcases/wireless/pathloss/test.ini",
            ],
            "download_url": "https://github.com/ComNets-Bremen/RIMFading/archive/609c3cb5121f50a8481754042ad4122d320008be.tar.gz",
            "patch_commands": [
                "sed -i 's|inet/physicallayer/pathloss/RIMFading.h|RIMFading.h|' RIMFading.cc",
            ],
            "build_commands": [r"""opp_makemake -f --deep -o rimfading -I $INET_ROOT/src -L $INET_ROOT/src -lINET\$D && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"""],
            "clean_commands": [r"""make clean"""],
        },

        {
            # POSTPONED - doesnt build; install script is outdated, should do the same in opp_env?
            # UPDATE: no shark in nix
            # "name": "ventos", "version": "1.01",
            "name": "ventos", "version": "master",
            # https://github.com/ManiAm/VENTOS_Public.git
            "nix_packages": ["sumo", "webkitgtk", "boost168", "curl", "gtk3", "eigen", "rapidxml", "glibmm", "glib", "gtkmm3", "libsigcxx", "pangomm_2_48", "pango", "harfbuzz", "cairomm", "cairo", "atkmm", "gdk-pixbuf", "atk", "llvmPackages.openmp"],
            "required_projects": {"omnetpp": ["5.4.1"], "exprtk": ["master"], "shark": ["4.0.1"]},
            # "download_url": "https://github.com/ManiAm/VENTOS_Public/archive/refs/tags/v1.0.1.tar.gz",
            "git_url": "https://github.com/ManiAm/VENTOS_Public.git",
            "setenv_commands": [
                "export BOOST_DEV_ROOT=${pkgs.boost.dev}",
                "export BOOST_ROOT=${pkgs.boost}",
                "export RAPIDXML_ROOT=${pkgs.rapidxml}",
                "export GLIBMM_DEV_ROOT=${pkgs.glibmm.dev}",
                "export GLIBMM_ROOT=${pkgs.glibmm}",
                "export GLIB_ROOT=${pkgs.glib.out}",
                "export GLIB_DEV_ROOT=${pkgs.glib.dev}",
                "export GTKMM_DEV_ROOT=${pkgs.gtkmm3.dev}",
                "export GTKMM_ROOT=${pkgs.gtkmm3}",
                "export SIGCXX_ROOT=${pkgs.libsigcxx}",
                "export PANGOMM_ROOT=${pkgs.pangomm_2_48}",
                "export PANGOMM_DEV_ROOT=${pkgs.pangomm_2_48.dev}",
                "export PANGO_ROOT=${pkgs.pango.dev}",
                "export HB_ROOT=${pkgs.harfbuzz.dev}",
                "export CAIROMM_ROOT=${pkgs.cairomm}",
                "export CAIROMM_DEV_ROOT=${pkgs.cairomm.dev}",
                "export CAIRO_DEV_ROOT=${pkgs.cairo.dev}",
                "export ATKMM_DEV_ROOT=${pkgs.atkmm.dev}",
                "export ATKMM_ROOT=${pkgs.atkmm}",
                "export GTK3_ROOT=${pkgs.gtk3}",
                "export GTK3_DEV_ROOT=${pkgs.gtk3.dev}",
                "export GDK_PIXBUF_ROOT=${pkgs.gdk-pixbuf}",
                "export GDK_PIXBUF_DEV_ROOT=${pkgs.gdk-pixbuf.dev}",
                "export ATK_ROOT=${pkgs.atk}",
                "export ATK_DEV_ROOT=${pkgs.atk.dev}",
                "export OPENMP_ROOT=${pkgs.llvmPackages.openmp}",
                # "export OPENMP_DEV_ROOT=${pkgs.llvmPackages.openmp.dev}",
                # "export EXPRTK_ROOT=${pkgs.exprtk}",
                # "export INET_PROJ=$INET_ROOT",
                # "export VEINS_PROJ=$VEINS_ROOT",
            ],
            "patch_commands": [
                # "tr -d '\r' < leachDist/runall.sh > leachDist/runall_fixed.sh",
                # "mv leachDist/runall_fixed.sh leachDist/runall.sh",
                # "chmod +x leachDist/runall.sh",
                """sed -i 's|ver=$(sumo 2.*?|#ver=$(sumo 2\\nver="X"|g' runme""",
                "sed -i 's|, SUMOID|, SUMOID.c_str()|g' src/*/AddNode.cc",
                """sed -i 's|#include "global/MiXiMDefs.h"|#include "global/MiXiMDefs.h"\\n#include <deque>|g' src/*/*/*/MappingUtils.h src/*/*/*/*/BaseDecider.h""",
                "sed -i 's|#include <ratio>|#include <ratio>\\n#include <deque>|g' src/*/*.h",
                "sed -i 's|if(tag.isItalic)|/* if(tag.isItalic)|g' src/loggingWindow/debugStream.h",    # very ugly hack
                "sed -i 's|STYLE_OBLIQUE|STYLE_OBLIQUE */|g' src/loggingWindow/debugStream.h",          # very ugly hack
            ],
            "build_commands": ["cd src && opp_makemake -f --deep -I . -I $BOOST_DEV_ROOT/include/boost -I $RAPIDXML_ROOT/include/rapidxml -I $EXPRTK_ROOT -I $GLIBMM_DEV_ROOT/include/glibmm-2.4 -I$GLIBMM_DEV_ROOT/include/giomm-2.4 -I$GLIBMM_ROOT/lib/glibmm-2.4/include -I$GLIBMM_ROOT/lib/giomm-2.4/include -I$GLIBMM_DEV_ROOT/lib/glibmm-2.4/include -I$GLIBMM_DEV_ROOT/lib/glibmm-2.4 -I$GLIBMM_DEV_ROOT/include/glibmm-2.4 -I$GLIBMM_ROOT/lib/glibmm-2.4/include -I$GLIBMM_ROOT/lib/glibmm-2.4 -I$GLIBMM_ROOT/include/glibmm-2.4 -I$GLIB_DEV_ROOT/include/glib-2.0 -I$GLIB_DEV_ROOT/include/glib-2.0/include -I${pkgs.glib.out}/include/glib-2.0 -I${pkgs.glib.out}/lib/glib-2.0/include -I$GTKMM_DEV_ROOT/include/gtkmm-3.0 -I$GTKMM_DEV_ROOT/include/gtkmm-3.0/gtkmm -I$GTKMM_DEV_ROOT/lib/gtkmm-3.0/include -I$GTKMM_DEV_ROOT/include/gdkmm-3.0 -I$GTKMM_DEV_ROOT/include/gdkmm-3.0/gtkmm -I$GTKMM_DEV_ROOT/lib/gdkmm-3.0/include -I$SIGCXX_ROOT/include/sigc++-2.0 -I$SIGCXX_ROOT/include/sigc++-2.0/gtkmm -I$SIGCXX_ROOT/lib/sigc++-2.0/include -I$GTKMM_ROOT/include/gtkmm-3.0 -I$GTKMM_ROOT/include/gtkmm-3.0/gtkmm -I$GTKMM_ROOT/lib/gtkmm-3.0/include -I$GTKMM_ROOT/lib/gdkmm-3.0/include -I$PANGOMM_ROOT/include/pangomm-2.48 -I$PANGOMM_ROOT/include/pangomm-2.48/pangomm -I$PANGOMM_ROOT/lib/pangomm-2.48/include -I$PANGOMM_DEV_ROOT/include/pangomm-2.48 -I$PANGOMM_DEV_ROOT/include/pangomm-2.48/pangomm -I$PANGOMM_DEV_ROOT/lib/pangomm-2.48/include -I$PANGO_ROOT/include/pango-1.0 -I$PANGO_ROOT/include/pango-1.0/pango -I$PANGO_ROOT/lib/pango-1.0/include -I$HB_ROOT/include/harfbuzz -I$CAIROMM_DEV_ROOT/include/cairomm-1.0 -I$CAIROMM_ROOT/lib/cairomm-1.0/include -I$CAIRO_DEV_ROOT/include/cairo -I$ATKMM_DEV_ROOT/include/atkmm-1.6 -I$ATKMM_ROOT/lib/atkmm-1.6/include -I$GTK3_DEV_ROOT/include/gtk-3.0 -I$GDK_PIXBUF_DEV_ROOT/include/gdk-pixbuf-2.0 -I$ATK_DEV_ROOT/include/atk-1.0 -L$(GTK3_ROOT)/lib -L$(GTK3_DEV_ROOT)/lib -L$(LIBXMLXX_ROOT)/lib -L$(GLIBMM_ROOT)/lib -L$(LIBSIGCXX_ROOT)/lib -L$(GLIB_ROOT)/lib -L$(PANGO_ROOT)/lib -L$(BOOST_ROOT)/lib -I$SHARK_ROOT/include -lxml2 -lglibmm-2.4 -lgobject-2.0 -lsigc-2.0 -lglib-2.0 -lboost_atomic -lboost_chrono -lboost_container -lboost_context -lboost_contract -lboost_coroutine -lboost_date_time -lboost_fiber -lboost_filesystem -lboost_graph -lboost_iostreams -lboost_json -lboost_locale -lboost_log_setup -lboost_log -lboost_math_c99f -lboost_math_c99l -lboost_math_c99 -lboost_math_tr1f -lboost_math_tr1l -lboost_math_tr1 -lboost_nowide -lboost_prg_exec_monitor -lboost_program_options -lboost_random -lboost_regex -lboost_serialization -lboost_stacktrace_addr2line -lboost_stacktrace_basic -lboost_stacktrace_noop -lboost_system -lboost_thread -lboost_timer -lboost_type_erasure -lboost_unit_test_framework -lboost_wave -lboost_wserialization -lgtk-3 -lgdk-3 && make -j16"],
            # "build_commands": ["cd src && opp_makemake -f --deep -o vanet -O out -KINET_PROJ=$INET_ROOT -KVEINS_PROJ=$VEINS_ROOT -DINET_IMPORT -DVEINS_IMPORT -I. -I$INET_ROOT/src -I$VEINS_ROOT/src -I. -L$INET_PROJ/src -L$VEINS_ROOT/src -lINET -lveins && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd veins_inet && opp_makemake --nolink -f --deep -o veins_inet -O out -KINET_PROJ=$INET_ROOT -KVEINS_PROJ=$VEINS_ROOT -DINET_IMPORT -DVEINS_IMPORT -I. -I$$\(INET_PROJ\)/src -I$$\(VEINS_PROJ\)/src -I.. -L$$\(INET_PROJ\)/src -L$$\(VEINS_PROJ\)/src -L$VEINS_ROOT/src -lINET$$\(D\) -lveins$$\(D\)"],
            "clean_commands": [r"""make clean"""],
            # run example simulation from src folder with:
            # ./cell -n .. ../networks/demo.ini
        },

        {
            "name": "exprtk", "version": "master",
            "nix_packages": ["sumo", "webkitgtk", "boost168", "curl", "gtk3", "eigen", "rapidxml"],
            "download_url": "https://github.com/ArashPartow/exprtk/archive/refs/heads/master.tar.gz",
            "setenv_commands": [
                # "export BOOST_ROOT=${pkgs.boost180.dev}",
                # "export RAPIDXML_ROOT=${pkgs.rapidxml}",
                # "export EXPRTK_ROOT=${pkgs.exprtk}",
                # "export INET_PROJ=$INET_ROOT",
                # "export VEINS_PROJ=$VEINS_ROOT",
            ],
            "patch_commands": [
                # "tr -d '\r' < leachDist/runall.sh > leachDist/runall_fixed.sh",
                # "mv leachDist/runall_fixed.sh leachDist/runall.sh",
                # "chmod +x leachDist/runall.sh",
                # """sed -i 's|ver=$(sumo 2.*?|#ver=$(sumo 2\\nver="X"|g' runme""",
                # "sed -i 's|, SUMOID|, SUMOID.c_str()|g' src/*/AddNode.cc",
            ],
            # "build_commands": ["cd src && opp_makemake -f --deep -I . -I $BOOST_ROOT/include/boost -I $RAPIDXML_ROOT/include/rapidxml -I $EXPRTK_ROOT/include/exprtk && make"],
            # "build_commands": ["cd src && opp_makemake -f --deep -o vanet -O out -KINET_PROJ=$INET_ROOT -KVEINS_PROJ=$VEINS_ROOT -DINET_IMPORT -DVEINS_IMPORT -I. -I$INET_ROOT/src -I$VEINS_ROOT/src -I. -L$INET_PROJ/src -L$VEINS_ROOT/src -lINET -lveins && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd veins_inet && opp_makemake --nolink -f --deep -o veins_inet -O out -KINET_PROJ=$INET_ROOT -KVEINS_PROJ=$VEINS_ROOT -DINET_IMPORT -DVEINS_IMPORT -I. -I$$\(INET_PROJ\)/src -I$$\(VEINS_PROJ\)/src -I.. -L$$\(INET_PROJ\)/src -L$$\(VEINS_PROJ\)/src -L$VEINS_ROOT/src -lINET$$\(D\) -lveins$$\(D\)"],
            "clean_commands": [r"""make clean"""],
            # run example simulation from src folder with:
            # ./cell -n .. ../networks/demo.ini
        },

        {
            # DONE - needed by ventos
            "name": "shark", "version": "4.0.1",
            "nix_packages": ["boost168", "cmake"],
            "download_url": "https://github.com/Shark-ML/Shark/archive/refs/tags/v4.0.1.tar.gz",
            "build_commands": ["$CMAKE_ROOT/bin/cmake CMakeLists.txt -DCMAKE_BUILD_TYPE=$BUILD_MODE^ && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"],
            "clean_commands": [r"""make clean"""],
        },

        {
            # NOT WORKING - doesn't build; noone tried this code?
            "name": "vns", "version": "master",
            # qt6.qtbase
            # libsForQt5.qt5.qtbase
            # qt6.qt5compat
            "nix_packages": ["SDL", "openscenegraph", "libsForQt5.qt5.qtbase", "llvmPackages.openmp"],
            "required_projects": {},
            # "nix_packages": ["SDL"],
            "git_url": "https://github.com/enriquefynn/libvns.git",
            "setenv_commands": [
                # "export QTBASE_ROOT=$INET_ROOT",
                # "export VEINS_PROJ=$VEINS_ROOT",

            ],
            "patch_commands": [
                # "tr -d '\r' < leachDist/runall.sh > leachDist/runall_fixed.sh",
                # "mv leachDist/runall_fixed.sh leachDist/runall.sh",
                # "chmod +x leachDist/runall.sh",
                # "sed -i 's|QMAKE_CXXFLAGS += -fopenmp|QMAKE_CXXFLAGS += -fopenmp -std=c++11 -fpermissive -Wextra -Wno-pointer-compare|g' libvns.pro",
            ],
            "build_commands": ["qmake && make -j16 CFLAGS+='-Wno-pointer-compare -fopenmp -std=c++11 -fPIC -fpermissive -Wextra' CXXFLAGS+='-Wno-pointer-compare -fopenmp -std=c++11 -fPIC -fpermissive -Wextra'"],
            "clean_commands": [r"""make clean"""],
            # run example simulation from src folder with:
            # ./cell -n .. ../networks/demo.ini
        },

        {
            # NOT WORKING - doesn't build; noone tried this code?
            "name": "vns_allinone", "version": "master",
            # qt6.qtbase
            # libsForQt5.qt5.qtbase
            # qt6.qt5compat
            "nix_packages": ["openscenegraph", "libsForQt5.qt5.qtbase", "llvmPackages.openmp"],
            "required_projects": {},
            "git_url": "https://github.com/enriquefynn/libvns.git",
            "setenv_commands": [
                # "export QTBASE_ROOT=$INET_ROOT",
                # "export VEINS_PROJ=$VEINS_ROOT",
            ],
            "patch_commands": [
                # "tr -d '\r' < leachDist/runall.sh > leachDist/runall_fixed.sh",
                # "mv leachDist/runall_fixed.sh leachDist/runall.sh",
                # "chmod +x leachDist/runall.sh",
                "sed -i 's|QMAKE_CXXFLAGS += -fopenmp|QMAKE_CXXFLAGS += -fopenmp -std=c++11 -fPIC -fpermissive -Wextra|g' libvns.pro",
            ],
            "build_commands": ["qmake && make -j16"],
            "clean_commands": [r"""make clean"""],
            # run example simulation from src folder with:
            # ./cell -n .. ../networks/demo.ini
        },

        {
            # NOT WORKING
            "name": "vns_omnetpp", "version": "master",
            # qt6.qtbase
            # libsForQt5.qt5.qtbase
            # qt6.qt5compat
            # "nix_packages": ["openscenegraph", "libsForQt5.qt5.qtbase", "llvmPackages_9.openmp"],
            # "required_projects": {},
            "download_url": "https://github.com/omnetpp-models/archive/releases/download/archive/libvns_omnetpp.tar.gz",
            "setenv_commands": [
                # "export QTBASE_ROOT=$INET_ROOT",
                # "export VEINS_PROJ=$VEINS_ROOT",
            ],
            "patch_commands": [
                # "tr -d '\r' < leachDist/runall.sh > leachDist/runall_fixed.sh",
                # "mv leachDist/runall_fixed.sh leachDist/runall.sh",
                # "chmod +x leachDist/runall.sh",
                # "sed -i 's|QMAKE_CXXFLAGS += -fopenmp|QMAKE_CXXFLAGS += -fopenmp -std=c++11 -fpermissive|g' libvns.pro",
            ],
            # "build_commands": ["qmake && make -j16"],
            "clean_commands": [r"""make clean"""],
            # run example simulation from src folder with:
            # ./cell -n .. ../networks/demo.ini
        },

        {
            # POSTPONED - osg
            "name": "otwlan", "version": "1.0", # this needs inet20061020
            # qt6.qtbase
            # libsForQt5.qt5.qtbase
            # qt6.qt5compat
            # "nix_packages": ["openscenegraph", "libsForQt5.qt5.qtbase", "llvmPackages_9.openmp"],
            "required_projects": {"omnetpp": ["3.3.1"], "inet": ["20061020"]},
            "download_url": "https://sourceforge.net/projects/otwlan/files/version%201.0/files/otwlanV1.tar.gz/download",
            "setenv_commands": [
                # "export QTBASE_ROOT=$INET_ROOT",
                # "export VEINS_PROJ=$VEINS_ROOT",
                'export NIX_CFLAGS_COMPILE="-isystem ${pkgs.qt4}/include/QtCore -isystem ${pkgs.qt4}/include/QtGui $NIX_CFLAGS_COMPILE"'
            ],
            "patch_commands": [
                # "tr -d '\r' < leachDist/runall.sh > leachDist/runall_fixed.sh",
                # "mv leachDist/runall_fixed.sh leachDist/runall.sh",
                # "chmod +x leachDist/runall.sh",
                # "sed -i 's|abs|std::abs|g' src/*/*/*/*.cc",
            ],
            # "build_commands": ["opp_makemake -f --deep --make-so -O out -I$INET_ROOT/src/linklayer/ieee80211/radio -I$INET_ROOT/src/networklayer/routing/aodv -I$INET_ROOT/src/networklayer/common -I$INET_ROOT/src -I$INET_ROOT/src/networklayer/icmpv6 -I$INET_ROOT/src/world/obstacles -I$INET_ROOT/src/networklayer/xmipv6 -I$INET_ROOT/src/networklayer/contract -I$INET_ROOT/src/networklayer/autorouting/ipv4 -I$INET_ROOT/src/util -I$INET_ROOT/src/linklayer/common -I$INET_ROOT/src/transport/contract -I$INET_ROOT/src/status -I$INET_ROOT/src/linklayer/radio/propagation -I$INET_ROOT/src/linklayer/ieee80211/radio/errormodel -I$INET_ROOT/src/linklayer/radio -I$INET_ROOT/src/util/headerserializers/tcp -I$INET_ROOT/src/networklayer/ipv4 -I$INET_ROOT/src/mobility/contract -I$INET_ROOT/src/util/headerserializers/ipv4 -I$INET_ROOT/src/base -I$INET_ROOT/src/util/headerserializers -I$INET_ROOT/src/world/radio -I$INET_ROOT/src/linklayer/ieee80211/mac -I$INET_ROOT/src/networklayer/ipv6 -I$INET_ROOT/src/transport/sctp -I$INET_ROOT/src/util/headerserializers/udp -I$INET_ROOT/src/networklayer/ipv6tunneling -I$INET_ROOT/src/util/headerserializers/ipv6 -I$INET_ROOT/src/applications/pingapp -I$INET_ROOT/src/battery/models -I$INET_ROOT/src/linklayer/contract -I$INET_ROOT/src/util/headerserializers/sctp -I$INET_ROOT/src/transport/tcp_common -I$INET_ROOT/src/networklayer/arp -I$INET_ROOT/src/transport/udp -L$INET_ROOT/out/$$\(CONFIGNAME\)/src -lz -linet -DINET_IMPORT -KINET_PROJ=../inet"],
            "clean_commands": [r"""make clean"""],
            # run example simulation from src folder with:
            # ./cell -n .. ../networks/demo.ini
        },

        {
            # POSTPONED - osg; this needs qt4 but omnetpp 5.x uses qt5
            "name": "otwlan", "version": "2.0",
            # qt6.qtbase
            # libsForQt5.qt5.qtbase
            # qt6.qt5compat
            # "nix_packages": ["openscenegraph", "libsForQt5.qt5.qtbase", "llvmPackages_9.openmp"],
            # "nix_packages": ["qt5.qtbase.dev"],
            "nix_packages": ["qt4"],
            "required_projects": {"omnetpp": ["4.6"], "inetmanet4": ["4.0.0"]},
            "download_url": "https://sourceforge.net/projects/otwlan/files/version%202.0/files/otwlanV2_beta1.tar.gz/download",
            "setenv_commands": [
                # "export $QT_PLUGIN_PATH"
                "export QTBASE_ROOT=${pkgs.qt4}",
                # "export VEINS_PROJ=$VEINS_ROOT",
                "export INET_DIR=$INETMANET_ROOT",
                "export OMNET_DIR=$OMNETPP_ROOT",
                'export NIX_CFLAGS_COMPILE="-isystem ${pkgs.qt4}/include/QtCore -isystem ${pkgs.qt4}/include/QtGui $NIX_CFLAGS_COMPILE"'
            ],
            "patch_commands": [
                # "tr -d '\r' < leachDist/runall.sh > leachDist/runall_fixed.sh",
                # "mv leachDist/runall_fixed.sh leachDist/runall.sh",
                # "chmod +x leachDist/runall.sh",
                "sed -i 's|/home/tore/software/inetmanet_inetmanet_v4/INET/src/base|$(INETMANET_ROOT)/src/inet|g' oprobe/oprobe.pro src/src.pro inet/inet.pro otwlan.pro",
                "sed -i 's|/home/tore/software/inetmanet_inetmanet_v4/INET/src|$(INETMANET_ROOT)/src/inet|g' oprobe/oprobe.pro src/src.pro inet/inet.pro otwlan.pro",
                "sed -i 's|/home/tore/software/omnetpp-4.0|$(OMNETPP_ROOT)|g' oprobe/oprobe.pro src/src.pro inet/inet.pro otwlan.pro",
            ],
            "build_commands": [r"""opp_makemake -f --deep --make-so -O out -I$QTBASE_ROOT/include -I$INET_ROOT/src/linklayer/ieee80211/radio -I$INET_ROOT/src/networklayer/routing/aodv -I$INET_ROOT/src/networklayer/common -I$INET_ROOT/src -I$INET_ROOT/src/networklayer/icmpv6 -I$INET_ROOT/src/world/obstacles -I$INET_ROOT/src/networklayer/xmipv6 -I$INET_ROOT/src/networklayer/contract -I$INET_ROOT/src/networklayer/autorouting/ipv4 -I$INET_ROOT/src/util -I$INET_ROOT/src/linklayer/common -I$INET_ROOT/src/transport/contract -I$INET_ROOT/src/status -I$INET_ROOT/src/linklayer/radio/propagation -I$INET_ROOT/src/linklayer/ieee80211/radio/errormodel -I$INET_ROOT/src/linklayer/radio -I$INET_ROOT/src/util/headerserializers/tcp -I$INET_ROOT/src/networklayer/ipv4 -I$INET_ROOT/src/mobility/contract -I$INET_ROOT/src/util/headerserializers/ipv4 -I$INET_ROOT/src/base -I$INET_ROOT/src/util/headerserializers -I$INET_ROOT/src/world/radio -I$INET_ROOT/src/linklayer/ieee80211/mac -I$INET_ROOT/src/networklayer/ipv6 -I$INET_ROOT/src/transport/sctp -I$INET_ROOT/src/util/headerserializers/udp -I$INET_ROOT/src/networklayer/ipv6tunneling -I$INET_ROOT/src/util/headerserializers/ipv6 -I$INET_ROOT/src/applications/pingapp -I$INET_ROOT/src/battery/models -I$INET_ROOT/src/linklayer/contract -I$INET_ROOT/src/util/headerserializers/sctp -I$INET_ROOT/src/transport/tcp_common -I$INET_ROOT/src/networklayer/arp -I$INET_ROOT/src/transport/udp -L$INET_ROOT/out/$$\(CONFIGNAME\)/src -lz -linet -DINET_IMPORT -KINET_PROJ=../inet"""],
            "clean_commands": [r"""make clean"""],
            # run example simulation from src folder with:
            # ./cell -n .. ../networks/demo.ini
        },

        {
            # NOT WORKING - build error so far
            "name": "mimicnet", "version": "master",
            "nix_packages": [
                "webkitgtk",
                "bison",
                "flex",
                "perl",
                "qt5.qtbase",
                "qt5.qtsvg",
                "qt5.qtwayland",
                "zlib",
                "glib",
                "temurin-jre-bin-8",
                "tk-8_6",
                "tcl-8_6",
                "libxml2",
                "doxygen",
                "graphviz",
                "openmpi",
                "python3",
                "python310Packages.torch",
                "python310Packages.pybind11",
                "glog"
            ],
            "required_projects": {"omnetpp": ["4.5.0"], "inet": ["2.4.0"]},
            "git_url": "https://github.com/eniac/MimicNet.git",
            "setenv_commands": [
                # "cd third_party/parallel-inet-omnet",
                # "pwd",
                # ". setenv",
                "export INET_ROOT=$MIMICNET_ROOT/third_party/parallel-inet && echo $INET_ROOT",
                # "export MYSQL_ROOT=${pkgs.libmysqlconnectorcpp}/include/jdbc",
                # "export MYSQL_LIB=${pkgs.libmysqlconnectorcpp}/lib",
                # "export VEINS_PROJ=$VEINS_ROOT",
            ],
            "patch_commands": [
                "rm -rf third_party/parallel-inet-omnet third_party/parallel-inet",
                "cd third_party",
                "ln -v -s $OMNETPP_ROOT parallel-inet-omnet",
                "ln -v -s $INET_ROOT parallel-inet",
                "sed -i 's|INET_HOME|INET_ROOT|g' ../simulate/src/makemake.sh ../simulate/homatransport/makemake.sh",
                # "mv omnetpp-4.5.0 parallel-inet-omnet",
                # "sed -i 's|../../inet|../inet|g' simulations/singlerun.sh simulations/runall.sh simulations/evaluation.sh",
                # "sed -i 's|make-so|make-so -o inet-dsme|g' build.sh",
                # "tr -d '\r' < leachDist/runall.sh > leachDist/runall_fixed.sh",
                # "mv leachDist/runall_fixed.sh leachDist/runall.sh",
                # "chmod +x leachDist/runall.sh",
                # "sed -i 's|abs|std::abs|g' src/*/*/*/*.cc",
            ],
            "build_commands": [
                "./run_1_compile.sh CPU",
                # "cd third_party/parallel-inet-omnet && . setenv && ./configure",
            ],
            # "build_commands": ["cd sdncontroller/src && opp_makemake -f --deep -KINET_PROJ=$INET_ROOT -DINET_IMPORT -I$INET_ROOT/src -L$INET_ROOT/src -lINET -I$MYSQL_ROOT -I$MYSQL_LIB -lmysqlcppconn -L$MYSQL_LIB && make -j16"],
            "clean_commands": [r"""make clean"""],
            # run example simulation from simulations folder with:
            # ../src/sdncontroller omnetpp.ini -n ../src:$INET_ROOT/src:.
        },

        # {
        #     # DONE - needed by mimicnet
        #     "name": "anaconda", "version": "5.3.1",
        #     "download_commands": [
        #         "mkdir anaconda-5.3.1",
        #         "cd anaconda-5.3.1",
        #         "curl -L -o install.sh --progress-bar https://repo.anaconda.com/archive/Anaconda3-5.3.1-Linux-x86_64.sh",
        #     ],
        #     "patch_commands": ["chmod +x install.sh"],
        #     "build_commands": ["./install.sh -b -p $ANACONDA_ROOT/src"],
        #     "clean_commands": [r"""make clean"""],
        # },

        {
            # POSTPONED - cant find sumo docker image; need to use latest;
            # needs osgearth -> postponed -> TODO check if OSG can be turned off -> apparently not
            "name": "crownet", "version": "master",
            "nix_packages": ["docker", "python3", "python311Packages.setuptools", "boost174", "cryptopp", "cmake", "geographiclib", "git-lfs", "sumo"],
            "required_projects": {"omnetpp": ["6.0.0"]},
            # "download_url": "https://github.com/roVer-HM/crownet/archive/refs/tags/ieee_mass23.tar.gz",
            "download_commands": [
                # "mkdir crownet-master",
                # "cd crownet-master",
                "git clone --recurse-submodules https://github.com/roVer-HM/crownet.git crownet-master",
            ],
            "setenv_commands": [
                # "export MYSQL_ROOT=${pkgs.libmysqlconnectorcpp}/include/jdbc",
                # "export MYSQL_LIB=${pkgs.libmysqlconnectorcpp}/lib",
                # "export VEINS_PROJ=$VEINS_ROOT",
                "export BOOST_ROOT=${pkgs.boost174.dev}"
            ],
            "patch_commands": [
                # "sed -i 's|../../inet|../inet|g' simulations/singlerun.sh simulations/runall.sh simulations/evaluation.sh",
                # "sed -i 's|make-so|make-so -o inet-dsme|g' build.sh",
                # "tr -d '\r' < leachDist/runall.sh > leachDist/runall_fixed.sh",
                # "mv leachDist/runall_fixed.sh leachDist/runall.sh",
                # "chmod +x leachDist/runall.sh",
                "sed -i 's|tests/validation||g' inet4/.nedfolders",
                "sed -i 's|tests/networks||g' inet4/.nedfolders",
                "sed -i 's|python3.8|python3|g' Makefile",
                "sed -i 's|enable VisualizationOsg|disable VisualizationOsg|g' Makefile",       # temp
                # enable VisualizationOsg
            ],
            "build_commands": [
                # "source setup",
                # "./scripts/get_images",
                # "cd inet4 && . setenv && opp_featuretool disable VisualizationOsg"      # crownet needs OSG so need to actually enable it in omnetpp
                "make makefiles && make MODE=release"
            ],
            # "build_commands": ["cd sdncontroller/src && opp_makemake -f --deep -KINET_PROJ=$INET_ROOT -DINET_IMPORT -I$INET_ROOT/src -L$INET_ROOT/src -lINET -I$MYSQL_ROOT -I$MYSQL_LIB -lmysqlcppconn -L$MYSQL_LIB && make -j16"],
            "clean_commands": [r"""make clean"""],
            # run example simulation from simulations folder with:
            # ../src/sdncontroller omnetpp.ini -n ../src:$INET_ROOT/src:.
        },

        {
            # NOT RELEVANT
            "name": "veins_gym", "version": "pip",
            # "nix_packages": ["docker"],
            # "description": "This project contains code and documentation to reproduce experimental results of the paper 'Long-Range ICN for the IoT: Exploring a LoRa System Design' published in Proc. of the IFIP Networking Conference 2022.",
            # "download_commands": [
                # "git clone https://github.com/inetrg/IFIP-Networking-LoRa-ICN-2022.git lora_icn-paper",
                # "cd lora_icn-paper",
                # "git reset --hard c45a69b23f0fce467242b4c0b71b125bc450a0f0",
                # "git submodule update --init --recursive",
            # ],
            "download_url": "https://github.com/tkn-tub/veins-gym/archive/refs/tags/veins_gym-0.3.3.tar.gz",
            "setenv_commands": [
                # """echo 'Hint: To generate all simulations, run the `docker run --rm -it -v "$(pwd)/data:/root/data" inetrg/ccnsim_dsme` command. \
                # Note that this may take hours to execute all configurations. The collected data will be stored under data/.'""",
            ],
            "build_commands": [
                # "docker build -t inetrg/ccnsim_dsme .",
            ],
            "clean_commands": [r"""make clean"""],
        },

        {
            # POSTPONED - build error
            "name": "wvsn", "version": "v4",
            "required_projects": {"omnetpp": ["4.1.0"], "castalia": ["3.2"]},
            # "description": "This project contains code and documentation to reproduce experimental results of the paper 'Long-Range ICN for the IoT: Exploring a LoRa System Design' published in Proc. of the IFIP Networking Conference 2022.",
            # "download_commands": [
                # "git clone https://github.com/inetrg/IFIP-Networking-LoRa-ICN-2022.git lora_icn-paper",
                # "cd lora_icn-paper",
                # "git reset --hard c45a69b23f0fce467242b4c0b71b125bc450a0f0",
                # "git submodule update --init --recursive",
            # ],
            # "download_url": "https://cpham.perso.univ-pau.fr/WSN-MODEL/distrib/wvsnmodel-v4.tgz",
            "download_commands": [
                "mkdir wvsn-v4",
                "cd wvsn-v4",
                "curl -L -o wvsnmodel-v4.tgz https://cpham.perso.univ-pau.fr/WSN-MODEL/distrib/wvsnmodel-v4.tgz --progress-bar",
                "curl -L -o install.bash https://cpham.perso.univ-pau.fr/WSN-MODEL/distrib/install.bash --progress-bar",
                "chmod +x install.bash",
                # opp_makemake -f --deep -I$OMNETPP_ROOT/include -e cc -I$CASTALIA_ROOT/Castalia/src  -I$CASTALIA_ROOT/Castalia/src  -I$CASTALIA_ROOT/Castalia/src/helpStructures  -I$CASTALIA_ROOT/Castalia/src/node  -I$CASTALIA_ROOT/Castalia/src/node/application  -I$CASTALIA_ROOT/Castalia/src/node/application/bridgeTest  -I$CASTALIA_ROOT/Castalia/src/node/application/connectivityMap  -I$CASTALIA_ROOT/Castalia/src/node/application/simpleAggregation  -I$CASTALIA_ROOT/Castalia/src/node/application/throughputTest  -I$CASTALIA_ROOT/Castalia/src/node/application/valuePropagation  -I$CASTALIA_ROOT/Castalia/src/node/application/valueReporting  -I$CASTALIA_ROOT/Castalia/src/node/communication  -I$CASTALIA_ROOT/Castalia/src/node/communication/mac  -I$CASTALIA_ROOT/Castalia/src/node/communication/mac/baselineBanMac  -I$CASTALIA_ROOT/Castalia/src/node/communication/mac/bypassMac  -I$CASTALIA_ROOT/Castalia/src/node/communication/mac/mac802154  -I$CASTALIA_ROOT/Castalia/src/node/communication/mac/tMac  -I$CASTALIA_ROOT/Castalia/src/node/communication/mac/tunableMac  -I$CASTALIA_ROOT/Castalia/src/node/communication/radio  -I$CASTALIA_ROOT/Castalia/src/node/communication/routing  -I$CASTALIA_ROOT/Castalia/src/node/communication/routing/bypassRouting  -I$CASTALIA_ROOT/Castalia/src/node/communication/routing/multipathRingsRouting  -I$CASTALIA_ROOT/Castalia/src/node/mobilityManager  -I$CASTALIA_ROOT/Castalia/src/node/mobilityManager/lineMobilityManager  -I$CASTALIA_ROOT/Castalia/src/node/mobilityManager/noMobilityManager  -I$CASTALIA_ROOT/Castalia/src/node/resourceManager  -I$CASTALIA_ROOT/Castalia/src/node/sensorManager  -I$CASTALIA_ROOT/Castalia/src/physicalProcess  -I$CASTALIA_ROOT/Castalia/src/physicalProcess/carsPhysicalProcess  -I$CASTALIA_ROOT/Castalia/src/physicalProcess/customizablePhysicalProcess  -I$CASTALIA_ROOT/Castalia/src/wirelessChannel
            ],
            "setenv_commands": [
                # """echo 'Hint: To generate all simulations, run the `docker run --rm -it -v "$(pwd)/data:/root/data" inetrg/ccnsim_dsme` command. \
                # Note that this may take hours to execute all configurations. The collected data will be stored under data/.'""",
            ],
            "build_commands": [
                # "docker build -t inetrg/ccnsim_dsme .",
            ],
            "clean_commands": [r"""make clean"""],
        },

                {
            # POSTPONED - build error
            "name": "wvsn_allinone", "version": "v4",
            "nix_packages": ["SDL"],
            "required_projects": {"omnetpp": ["4.1.0"]},
            # "description": "This project contains code and documentation to reproduce experimental results of the paper 'Long-Range ICN for the IoT: Exploring a LoRa System Design' published in Proc. of the IFIP Networking Conference 2022.",
            # "download_commands": [
                # "git clone https://github.com/inetrg/IFIP-Networking-LoRa-ICN-2022.git lora_icn-paper",
                # "cd lora_icn-paper",
                # "git reset --hard c45a69b23f0fce467242b4c0b71b125bc450a0f0",
                # "git submodule update --init --recursive",
            # ],
            # "download_url": "https://cpham.perso.univ-pau.fr/WSN-MODEL/distrib/wvsnmodel-v4.tgz",
            "download_commands": [
                "mkdir wvsn_allinone-v4",
                "cd wvsn_allinone-v4",
                "curl -L -o wvsnmodel-v4.tgz https://cpham.perso.univ-pau.fr/WSN-MODEL/distrib/wvsnmodel-v4.tgz --progress-bar",
                "curl -L -o install.bash https://cpham.perso.univ-pau.fr/WSN-MODEL/distrib/install.bash --progress-bar",
                "chmod +x install.bash",
                "tar -xzf wvsnmodel-v4.tgz --strip=1",
                "curl -L -o src.tar.gz https://github.com/boulis/Castalia/archive/refs/tags/3.2.tar.gz",
                "tar -xzf src.tar.gz --strip=1",
                # opp_makemake -f --deep -I$OMNETPP_ROOT/include -e cc -I$CASTALIA_ROOT/Castalia/src  -I$CASTALIA_ROOT/Castalia/src  -I$CASTALIA_ROOT/Castalia/src/helpStructures  -I$CASTALIA_ROOT/Castalia/src/node  -I$CASTALIA_ROOT/Castalia/src/node/application  -I$CASTALIA_ROOT/Castalia/src/node/application/bridgeTest  -I$CASTALIA_ROOT/Castalia/src/node/application/connectivityMap  -I$CASTALIA_ROOT/Castalia/src/node/application/simpleAggregation  -I$CASTALIA_ROOT/Castalia/src/node/application/throughputTest  -I$CASTALIA_ROOT/Castalia/src/node/application/valuePropagation  -I$CASTALIA_ROOT/Castalia/src/node/application/valueReporting  -I$CASTALIA_ROOT/Castalia/src/node/communication  -I$CASTALIA_ROOT/Castalia/src/node/communication/mac  -I$CASTALIA_ROOT/Castalia/src/node/communication/mac/baselineBanMac  -I$CASTALIA_ROOT/Castalia/src/node/communication/mac/bypassMac  -I$CASTALIA_ROOT/Castalia/src/node/communication/mac/mac802154  -I$CASTALIA_ROOT/Castalia/src/node/communication/mac/tMac  -I$CASTALIA_ROOT/Castalia/src/node/communication/mac/tunableMac  -I$CASTALIA_ROOT/Castalia/src/node/communication/radio  -I$CASTALIA_ROOT/Castalia/src/node/communication/routing  -I$CASTALIA_ROOT/Castalia/src/node/communication/routing/bypassRouting  -I$CASTALIA_ROOT/Castalia/src/node/communication/routing/multipathRingsRouting  -I$CASTALIA_ROOT/Castalia/src/node/mobilityManager  -I$CASTALIA_ROOT/Castalia/src/node/mobilityManager/lineMobilityManager  -I$CASTALIA_ROOT/Castalia/src/node/mobilityManager/noMobilityManager  -I$CASTALIA_ROOT/Castalia/src/node/resourceManager  -I$CASTALIA_ROOT/Castalia/src/node/sensorManager  -I$CASTALIA_ROOT/Castalia/src/physicalProcess  -I$CASTALIA_ROOT/Castalia/src/physicalProcess/carsPhysicalProcess  -I$CASTALIA_ROOT/Castalia/src/physicalProcess/customizablePhysicalProcess  -I$CASTALIA_ROOT/Castalia/src/wirelessChannel
            ],
            "patch_commands": [
                "sed -i 's|bin/python|bin/env python2|' Castalia/bin/Castalia",
                "sed -i 's|bin/python|bin/env python2|' Castalia/bin/CastaliaResults",
                "sed -i 's|bin/python|bin/env python2|' Castalia/bin/extractOmnetppINI",
                "sed -i 's|vidmodel/wvsn-model-omnetpp-v4/||' Castalia-files/src-videoSensorNode/createLinks",
                'sed -i "s|~/vidmodel/wvsn-model-omnetpp-v4|$(eval echo $WVSN_ALLINONE_ROOT)|g" Castalia-files/input/makefrag',
                # "cp -v Castalia-files/input/SensorNetwork.ned.custom Castalia/src/SensorNetwork.ned",
                # "cp -rv Castalia-files/src-videoSensorNode Castalia/src/node/application/videoSensorNode",
                # "mv Castalia/src/node/application/videoSensorNode/VideoSensorNode.ned.custom Castalia/src/node/application/videoSensorNode/VideoSensorNode.ned",
                # "cp -rv Castalia-files/Simulations-videoSensor Castalia/Simulations/videoSensor",
                # "Castalia/src/node/application/videoSensorNode/createLinks $WVSN_ALLINONE_ROOT",
                # "cd Castalia-files && cp -rv src-videoSensorNode $CASTALIA_ROOT/src/node/application/videoSensorNode && cd $CASTALIA_ROOT/src/node/application/videoSensorNode && mv VideoSensorNode.ned.custom VideoSensorNode.ned && cd $CASTALIA_ROOT && cp -rv Simulations-videoSensor CASTALIA_ROOT/Simulations/videoSensor && cd CASTALIA_ROOT/src/node/application/videoSensorNode && ./createLinks ~/my_test/video/wvsn-model-omnetpp-v4",
                # "cd Castalia-files && cp -rv src-videoSensorNode ../Castalia/src/node/application/videoSensorNode && cd $CASTALIA_ROOT/src/node/application/videoSensorNode && mv VideoSensorNode.ned.custom VideoSensorNode.ned && cd $CASTALIA_ROOT && cd .. && cd Castalia-files && cp -rv Simulations-videoSensor $CASTALIA_ROOT/Simulations/videoSensor && cd $CASTALIA_ROOT/src/node/application/videoSensorNode",
                # "./createLinks $WVSN_ALLINONE_ROOT",
            ],
            "setenv_commands": [
                "export CASTALIA_ROOT=$WVSN_ALLINONE_ROOT/Castalia",
                "export PATH=$PATH:$CASTALIA_ROOT/Castalia/bin",
                # "echo 'Hint: Use the `Castalia` command to run the examples in the Simulations folder.'"
            ],
            "build_commands": [
                                               "cp -v Castalia-files/input/SensorNetwork.ned.custom Castalia/src/SensorNetwork.ned",
                "cp -rv Castalia-files/src-videoSensorNode Castalia/src/node/application/videoSensorNode",
                "mv Castalia/src/node/application/videoSensorNode/VideoSensorNode.ned.custom Castalia/src/node/application/videoSensorNode/VideoSensorNode.ned",
                "cp -rv Castalia-files/Simulations-videoSensor Castalia/Simulations/videoSensor",
                "pwd",
                "cd Castalia/src/node/application/videoSensorNode && ./createLinks $WVSN_ALLINONE_ROOT && cd $WVSN_ALLINONE_ROOT",
                "cp -v Castalia-files/input/makefrag Castalia",
                "cd Castalia && ./makemake && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE && cd ..",
],
            "clean_commands": [r"""make clean"""],
        },

        # {
        #     # WIP - opencv2x_veins standalone version; some example simulations crash after some time though; needs veins_inet3 veins subproject and SimuLTE_Cars opp feature
        #     "name": "opencv2x_veins", "version": "1.4.1",
        #     "nix_packages": ["sumo"],
        #     "required_projects": {"omnetpp": ["5.5.1"], "veins": ["5.0"], "inet": ["3.6.6"]},
        #     "description": "An abstract TDMA MAC protocol for the INET Framework",
        #     "download_commands": [
        #         "git clone https://github.com/brianmc95/simulte.git opencv2x_veins-1.4.1",
        #         "cd opencv2x_veins-1.4.1",
        #         "git reset --hard 4b5d33d28aa1ec3ca108b5ba3a3be1b38e10cf5e",    # v1.4.1
        #     ],
        #     "patch_commands": [
        #         "find . -type f -name 'run' -exec chmod +x {} \;",
        #         "sed -i 's|../../inet|$(INET_ROOT)|g' Makefile",
        #         "sed -i 's|\$DIR/../../inet|$INET_ROOT|g' src/run_lte",
        #         "sed -i 's|INET_DIR\"|INET_DIR:$VEINS_ROOT/src/veins:$VEINS_ROOT/subprojects/veins_inet3/src/veins_inet\"|g' src/run_lte",
        #         "sed -i 's|-l $INET_DIR/INET|-l $INET_DIR/INET -l $VEINS_ROOT/subprojects/veins_inet3/src/libveins_inet.so|g' src/run_lte",
        #     ],
        #     "setenv_commands": [
        #         "export INET_PROJ=$INET_ROOT",
        #     ],
        #     "build_commands": [
        #         "make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
        #     ],
        #     "clean_commands": [r"""make clean"""],
        # },

        {
            # WIP - doesnt build
            "name": "libptp", "version": "master",
            "nix_packages": ["boost", "fftw"],
            "required_projects": {"omnetpp": ["4.6.*"], "inet": ["2.6.0"], "omnet_utils": ["1.0"], "libpln": ["1.0"]},
            "description": "An abstract TDMA MAC protocol for the INET Framework",
            "download_url": "https://github.com/ptp-sim/libPTP/archive/7e98b4338bc92016f9cf7468185cf1303f6e43c0.tar.gz",
            "setenv_commands": [
                # "rm -r inet",
                # "ln -s $INET_ROOT inet",
                # "export INET_PROJ=$INET_ROOT",
                # "echo 'Hint: To run the example simulation, use the `./tdma ../simulations/omnetpp.ini -n .:../simulations:$INET_ROOT/src` command in the tdma/src folder.'",
                "export BOOST_INCLUDE=${pkgs.boost.dev}/include",
                "export FFTW_INCLUDE=${pkgs.fftw.dev}/include",
                "export FFTW_LIB=${pkgs.fftw.dev}"
            ],
            "build_commands": [
                "cd src && opp_makemake -f --deep -I$INET_ROOT/src -I$OMNET_UTILS_ROOT/src -I$OMNET_UTILS_ROOT/src/Callable -I$OMNET_UTILS_ROOT/src/Channels -I$OMNET_UTILS_ROOT/src/Channels/VolatileDelayChannel -I$OMNET_UTILS_ROOT/src/DynamicSignals -I$OMNET_UTILS_ROOT/src/InitBase -I$OMNET_UTILS_ROOT/src/ParameterParser -KINET_PROJ=$INET_ROOT -DINET_IMPORT -I$INET_ROOT/src/ -I$INET_ROOT/src/applications -I$INET_ROOT/src/applications/common -I$INET_ROOT/src/applications/dhcp -I$INET_ROOT/src/applications/ethernet -I$INET_ROOT/src/applications/generic -I$INET_ROOT/src/applications/httptools -I$INET_ROOT/src/applications/netperfmeter -I$INET_ROOT/src/applications/pingapp -I$INET_ROOT/src/applications/rtpapp -I$INET_ROOT/src/applications/sctpapp -I$INET_ROOT/src/applications/tcpapp -I$INET_ROOT/src/applications/traci -I$INET_ROOT/src/applications/udpapp -I$INET_ROOT/src/applications/voip -I$INET_ROOT/src/base -I$INET_ROOT/src/battery -I$INET_ROOT/src/battery/models -I$INET_ROOT/src/linklayer -I$INET_ROOT/src/linklayer/common -I$INET_ROOT/src/linklayer/configurator -I$INET_ROOT/src/linklayer/contract -I$INET_ROOT/src/linklayer/ethernet -I$INET_ROOT/src/linklayer/ethernet/switch -I$INET_ROOT/src/linklayer/ext -I$INET_ROOT/src/linklayer/idealwireless -I$INET_ROOT/src/linklayer/ieee80211 -I$INET_ROOT/src/linklayer/ieee80211/mac -I$INET_ROOT/src/linklayer/ieee80211/mgmt -I$INET_ROOT/src/linklayer/ieee80211/radio -I$INET_ROOT/src/linklayer/ieee80211/radio/errormodel -I$INET_ROOT/src/linklayer/ieee8021d -I$INET_ROOT/src/linklayer/ieee8021d/common -I$INET_ROOT/src/linklayer/ieee8021d/relay -I$INET_ROOT/src/linklayer/ieee8021d/rstp -I$INET_ROOT/src/linklayer/ieee8021d/stp -I$INET_ROOT/src/linklayer/ieee8021d/tester -I$INET_ROOT/src/linklayer/loopback -I$INET_ROOT/src/linklayer/ppp -I$INET_ROOT/src/linklayer/queue -I$INET_ROOT/src/linklayer/radio -I$INET_ROOT/src/linklayer/radio/propagation -I$INET_ROOT/src/mobility -I$INET_ROOT/src/mobility/common -I$INET_ROOT/src/mobility/contract -I$INET_ROOT/src/mobility/group -I$INET_ROOT/src/mobility/single -I$INET_ROOT/src/mobility/static -I$INET_ROOT/src/networklayer -I$INET_ROOT/src/networklayer/arp -I$INET_ROOT/src/networklayer/autorouting -I$INET_ROOT/src/networklayer/autorouting/ipv4 -I$INET_ROOT/src/networklayer/autorouting/ipv6 -I$INET_ROOT/src/networklayer/bgpv4 -I$INET_ROOT/src/networklayer/bgpv4/BGPMessage -I$INET_ROOT/src/networklayer/common -I$INET_ROOT/src/networklayer/contract -I$INET_ROOT/src/networklayer/diffserv -I$INET_ROOT/src/networklayer/icmpv6 -I$INET_ROOT/src/networklayer/internetcloud -I$INET_ROOT/src/networklayer/ipv4 -I$INET_ROOT/src/networklayer/ipv6 -I$INET_ROOT/src/networklayer/ipv6tunneling -I$INET_ROOT/src/networklayer/ldp -I$INET_ROOT/src/networklayer/manetrouting -I$INET_ROOT/src/networklayer/manetrouting/aodv-uu -I$INET_ROOT/src/networklayer/manetrouting/aodv-uu/aodv-uu -I$INET_ROOT/src/networklayer/manetrouting/base -I$INET_ROOT/src/networklayer/manetrouting/batman -I$INET_ROOT/src/networklayer/manetrouting/batman/batmand -I$INET_ROOT/src/networklayer/manetrouting/batman/batmand/orig -I$INET_ROOT/src/networklayer/manetrouting/dsdv -I$INET_ROOT/src/networklayer/manetrouting/dsr -I$INET_ROOT/src/networklayer/manetrouting/dsr/dsr-uu -I$INET_ROOT/src/networklayer/manetrouting/dymo -I$INET_ROOT/src/networklayer/manetrouting/dymo/dymoum -I$INET_ROOT/src/networklayer/manetrouting/dymo_fau -I$INET_ROOT/src/networklayer/manetrouting/olsr -I$INET_ROOT/src/networklayer/mpls -I$INET_ROOT/src/networklayer/ospfv2 -I$INET_ROOT/src/networklayer/ospfv2/interface -I$INET_ROOT/src/networklayer/ospfv2/messagehandler -I$INET_ROOT/src/networklayer/ospfv2/neighbor -I$INET_ROOT/src/networklayer/ospfv2/router -I$INET_ROOT/src/networklayer/routing -I$INET_ROOT/src/networklayer/routing/aodv -I$INET_ROOT/src/networklayer/routing/dymo -I$INET_ROOT/src/networklayer/routing/gpsr -I$INET_ROOT/src/networklayer/routing/rip -I$INET_ROOT/src/networklayer/rsvp_te -I$INET_ROOT/src/networklayer/ted -I$INET_ROOT/src/networklayer/xmipv6 -I$INET_ROOT/src/nodes -I$INET_ROOT/src/nodes/aodv -I$INET_ROOT/src/nodes/bgp -I$INET_ROOT/src/nodes/dymo -I$INET_ROOT/src/nodes/ethernet -I$INET_ROOT/src/nodes/gpsr -I$INET_ROOT/src/nodes/httptools -I$INET_ROOT/src/nodes/inet -I$INET_ROOT/src/nodes/internetcloud -I$INET_ROOT/src/nodes/ipv6 -I$INET_ROOT/src/nodes/mpls -I$INET_ROOT/src/nodes/ospfv2 -I$INET_ROOT/src/nodes/rip -I$INET_ROOT/src/nodes/rtp -I$INET_ROOT/src/nodes/wireless -I$INET_ROOT/src/nodes/xmipv6 -I$INET_ROOT/src/status -I$INET_ROOT/src/transport -I$INET_ROOT/src/transport/contract -I$INET_ROOT/src/transport/rtp -I$INET_ROOT/src/transport/rtp/profiles -I$INET_ROOT/src/transport/rtp/profiles/avprofile -I$INET_ROOT/src/transport/sctp -I$INET_ROOT/src/transport/tcp -I$INET_ROOT/src/transport/tcp/flavours -I$INET_ROOT/src/transport/tcp/queues -I$INET_ROOT/src/transport/tcp_common -I$INET_ROOT/src/transport/udp -I$INET_ROOT/src/util -I$INET_ROOT/src/util/headerserializers -I$INET_ROOT/src/util/headerserializers/headers -I$INET_ROOT/src/util/headerserializers/ipv4 -I$INET_ROOT/src/util/headerserializers/ipv4/headers -I$INET_ROOT/src/util/headerserializers/ipv6 -I$INET_ROOT/src/util/headerserializers/ipv6/headers -I$INET_ROOT/src/util/headerserializers/sctp -I$INET_ROOT/src/util/headerserializers/sctp/headers -I$INET_ROOT/src/util/headerserializers/tcp -I$INET_ROOT/src/util/headerserializers/tcp/headers -I$INET_ROOT/src/util/headerserializers/udp -I$INET_ROOT/src/util/headerserializers/udp/headers -I$INET_ROOT/src/util/messageprinters -I$INET_ROOT/src/world -I$INET_ROOT/src/world/annotations -I$INET_ROOT/src/world/httptools -I$INET_ROOT/src/world/obstacles -I$INET_ROOT/src/world/radio -I$INET_ROOT/src/world/scenario -I$INET_ROOT/src/world/traci -I${pkgs.boost.dev}/include -I$LIBPLN_ROOT/src -I$LIBPLN_ROOT -I${pkgs.fftw.dev}/include -LI${pkgs.fftw.dev} -L$LIBPLN_ROOT/lib/static && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
            ],
            "clean_commands": [r"""make clean"""],
        },

        {
            # DONE - needed by libptp
            "name": "omnet_utils", "version": "1.0",
            "nix_packages": ["boost"],
            "required_projects": {"omnetpp": ["4.6.0"]},
            "description": "Provides useful utilities to be used with the OMNeT++",
            "download_url": "https://github.com/ptp-sim/OMNeT_Utils/archive/refs/tags/v1.0.tar.gz",
            "setenv_commands": [
            ],
            "build_commands": [
                "cd src && opp_makemake -f --deep && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
            ],
            "clean_commands": [r"""make clean"""],
        },

        {
            # DONE - needed by libptp
            "name": "libpln", "version": "1.0",
            "nix_packages": ["boost", "cmake", "gcc", "fftw"],
            "description": "A Library for Efficient Powerlaw Noise Generation",
            "download_url": "https://github.com/ptp-sim/libPLN/archive/refs/tags/v1.0.tar.gz",
            "build_commands": [
                "cmake CMakeLists.txt && make all install SimpleDemo TestBench PLN_Generator -j$NIX_BUILD_CORES MODE=$BUILD_MODE",
            ],
            "clean_commands": [r"""make clean"""],
        },

        {
            # POSTPONED - this needs patched omnetpp -> does that patch do something that is already done in omnetpp?
            "name": "steamsim", "version": "master",
            "description": "Steam-sim",
            "metadata": {
                "catalog_url": "https://omnetpp.org/download-items/SteamSim.html",
            },
            "required_projects": {"omnetpp": ["4.1.0"]},
            "details": "An open source implementation of the 3GPP standard CV2X (Rel 14) Mode 4. It is based on an extended version of the SimuLTE OMNeT++ simulator which enables LTE network simulations.",
            "download_url": "https://github.com/brianmc95/simulte/archive/refs/tags/v1.4.1.tar.gz",
            "patch_commands": [
                r"""find . -type f -name 'run' -exec chmod +x {} \;""",
                "sed -i 's|../../inet|$(INET_ROOT)|g' Makefile",
                r"""sed -i 's|-lINET|-lINET$$\\\(D\\\)|g' Makefile""",
                r"""sed -i 's|\$DIR/../../inet|$INET_ROOT|g' src/run_lte""",
                "sed -i 's|INET_DIR\"|INET_DIR:$VEINS_ROOT/src/veins:$VEINS_ROOT/subprojects/veins_inet3/src/veins_inet\"|g' src/run_lte",
                "sed -i 's|-l $INET_DIR/INET|-l $INET_DIR/INET -l $VEINS_ROOT/subprojects/veins_inet3/src/libveins_inet.so|g' src/run_lte",
                r"""find . -name '*.launchd.xml' -exec bash -c 'sed -i "s|UPDATE-WITH-YOUR-PATH|$(pwd)/{}|g" {}' \;""",
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
            "clean_commands": [r"""make clean"""],
        },
    ]