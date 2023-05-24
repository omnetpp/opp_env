import re
description = "INET Framework is an open-source OMNeT++ model suite for wired, wireless and mobile networks."

def dotx(version):
    # 4.2, 4.2.1, 4.2p1 -> 4.2.x
    return re.sub("(\\d\\.\\d)[\\.p]\\d", "\\1", version) + ".x"

def join_nonempty_items(sep, list):
    return sep.join([x for x in list if x])

def make_inet_project_description(inet_version, omnetpp_versions):
    # It is possible to install from locally downloaded tarballs and repo, using the  "local" or "local-git" options.
    # This is used mainly for testing. The following are the locations of the local files.
    downloads_dir = "~/projects/opp_env_downloads"
    local_inet_git_repo = "~/projects/inet"

    is_git_branch = inet_version == "master" or inet_version.endswith(".x")
    is_modernized = inet_version == "master" or inet_version.endswith(".x") # TODO and the patch-release tags on .x branches

    # Some version tags have no entry on the Releases page
    missing_releases = [ "3.2.2", "3.1.0" ]

    return {
        "name": "inet", "version": inet_version, "description": description,
        "folder_name": "inet",
        "required_projects": {"omnetpp": omnetpp_versions}, # list(set([dotx(v) for v in omnetpp_versions]))},
        "external_nix_packages":
            ["z3"] if inet_version >= "4.4" else
            [] if inet_version >= "4.0" else # inet-4.x uses omnetpp-6.x, so python3 doesn't need to be spelled out
            ["python3"] if inet_version >= "3.6.7" or is_modernized else
            ["python2"], # up to inet-3.6.6, inet_featuretool uses python2 in original, and python3 in modernized versions
        "download_url":
            f"https://github.com/inet-framework/inet/archive/refs/tags/v{inet_version}.tar.gz" if inet_version in missing_releases else
            f"https://github.com/inet-framework/inet/releases/download/v{inet_version}/inet-{inet_version}-src.tgz" if not is_git_branch else
            f"https://github.com/inet-framework/inet/archive/refs/heads/v{inet_version}.tar.gz",
        "setenv_commands": [
            'export NEDPATH="$NEDPATH:$INET_ROOT/src:$INET_ROOT/examples:$INET_ROOT/showcases:$INET_ROOT/tutorials"',
            'export OMNETPP_IMAGE_PATH="$OMNETPP_IMAGE_PATH:$INET_ROOT/images"',
            "source setenv -f" if inet_version.startswith("4.") else "", # note: actually, setenv ought to contain adding INET to NEDPATH and OMNETPP_IMAGE_PATH
        ],
        "patch_commands": [
            "touch tutorials/package.ned" if inet_version <= "4.2.1" and inet_version >= "3.6.0" else "",

            # wipe out the "-n" (NED path) options from run scripts, as we prefer using the NEDPATH environment variable
            #TODO this might be unnecessary
            "sed -i -E 's|-n [^ ]+||' src/run_inet" if inet_version < "4.0" else "",
            "sed -i -E 's|-n [^ ]+||' bin/inet" if inet_version >= "4.0" else "",

            # also wipe out the explicit "--image-path=" option, as we use OMNETPP_IMAGE_PATH instead
            #TODO this might be unnecessary
            "sed -i -E 's|--image-path=[^ ]+||' src/run_inet" if inet_version < "4.0" else "",

            # fix up shebang line in inet_featuretool (python -> python2)
            "sed -i 's| python$| python2|' inet_featuretool" if inet_version >= "3.0" and inet_version < "3.6.7" else "",

            # fix "error: flexible array member in union" in sctp.h, later renamed to sctphdr.h
            "sed -i 's|info\\[\\]|info[0]|' src/inet/common/serializer/sctp/headers/sctphdr.h" if inet_version.startswith("3.") else "",
            "sed -i 's|info\\[\\]|info[0]|' src/util/headerserializers/sctp/headers/sctp.h" if inet_version.startswith("2.") else "",

            # Linux appears to define "__linux__" nowadays, not "linux"; affected: serializer/headers/defs.h, ExtInterface.cc, RawSocket.cc, OsUdp.cc, Ext.cc, etc., and their renamed/moved versions
            "for f in $(grep -Rl 'defined(linux)'); do sed -i 's|defined(linux)|defined(__linux__)|' $f; done",

            # cResultFilterDescriptor was renamed in omnetpp-5.1
            "sed -i 's|cResultFilterDescriptor|cResultFilterType|' src/inet/common/figures/DelegateSignalConfigurator.cc" if inet_version == "3.4.0" else "",

            # PacketDrillApp bug in early 3.x versions
            "sed -i 's|->spp_hbinterval > 0|->spp_hbinterval->getNum() > 0|' src/inet/applications/packetdrill/PacketDrillApp.cc" if inet_version>="3.5.0" and inet_version<="3.6.1" else "",
            "sed -i 's|->spp_pathmaxrxt > 0|->spp_pathmaxrxt->getNum() > 0|' src/inet/applications/packetdrill/PacketDrillApp.cc" if inet_version>="3.5.0" and inet_version<="3.6.1" else "",

            # INT64_PRINTF_FORMAT was removed in omnetpp-5.3 (?), replace with "l" for simplicity (suits all 64-bit platforms except Windows)
            "for f in $(grep -Rl 'INT64_PRINTF_FORMAT'); do sed -i 's|INT64_PRINTF_FORMAT|\"l\"|' $f; done" if inet_version.startswith("3.") else "",

            # fix linklayer/radio/Radio.cc:1134:35: error: redefinition of 'it' with a different type in inet-2.0 thru 2.2
            "sed -i 's/SensitivityList::iterator it = sensitivityList.find(0.0);/SensitivityList::iterator sit = sensitivityList.find(0.0);/' src/linklayer/radio/Radio.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "2.3" else None,
            "sed -i 's/if (it == sensitivityList.end())/if (sit == sensitivityList.end())/' src/linklayer/radio/Radio.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "2.3" else None,

            # fix networklayer/ipv4/RoutingTableRecorder.cc:166:35: error: invalid suffix on literal in inet-2.3
            "sed -i 's/\"LL\"/\" LL \"/' src/networklayer/ipv4/RoutingTableRecorder.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "2.5" else None,

            # fix src/networklayer/manetrouting/dsr/dsr-uu/path-cache.cc
            "sed -i 's/if (vector_cost<=0)/if (vector_cost == NULL)/' src/networklayer/manetrouting/dsr/dsr-uu/path-cache.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "3.0" else None,
            "sed -i 's/if (vector_cost<=nullptr)/if (vector_cost == nullptr)/' src/inet/routing/extras/dsr/dsr-uu/path-cache.cc" if not is_modernized and inet_version >= "3.0" and inet_version < "3.1" else None,

            # compile fix for omnetpp-4.3..4.6: getArraySize() was supposed to be renamed to getFieldArraySize() in omnetpp-4.3, but then the change was postponed to 5.0 as being a breaking change.
            "sed -i 's/OMNETPP_VERSION < 0x0403/OMNETPP_VERSION < 0x0500/' src/networklayer/manetrouting/aodv/aodv_msg_struct_descriptor.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "2.1" else None,
            "sed -i 's/OMNETPP_VERSION < 0x0403/OMNETPP_VERSION < 0x0500/' src/util/MessageChecker.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "2.1" else None,

            # fix no matching function for call to 'make_pair' in src/networklayer/manetrouting/base/ManetRoutingBase.cc (c++11 change in make_pair() signature)
            "sed -i 's/std::make_pair<Uint128,ProtocolsRoutes>(getAddress(),vect)/std::make_pair((Uint128)getAddress(),vect)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "2.1" else None,
            "sed -i 's/std::make_pair<Uint128,Uint128>(dst, gtwy)/std::make_pair((Uint128)dst, (Uint128)gtwy)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "2.1" else None,
            "sed -i 's/std::make_pair<Uint128,Uint128>(destination, nextHop)/std::make_pair((Uint128)destination, (Uint128)nextHop)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "2.1" else None,

            "sed -i 's/std::make_pair<ManetAddress,ProtocolsRoutes>(getAddress(),vect)/std::make_pair((ManetAddress)getAddress(),vect)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc" if not is_modernized and inet_version == "2.1.0" else None,
            "sed -i 's/std::make_pair<ManetAddress,ManetAddress>(dst, gtwy)/std::make_pair((ManetAddress)dst, (ManetAddress)gtwy)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc" if not is_modernized and inet_version == "2.1.0" else None,
            "sed -i 's/std::make_pair<ManetAddress,ManetAddress>(destination, nextHop)/std::make_pair((ManetAddress)destination, (ManetAddress)nextHop)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc" if not is_modernized and inet_version == "2.1.0" else None,

            # fix no matching function for call to 'make_pair' in src/networklayer/manetrouting/base/ManetRoutingBase.cc (c++11 change in make_pair() signature)
            "sed -i 's/std::make_pair<ManetAddress,ProtocolsRoutes>(getAddress(),vect)/std::make_pair((ManetAddress)getAddress(),vect)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc" if not is_modernized and inet_version >= "2.2" and inet_version < "2.4" else None,
            "sed -i 's/std::make_pair<ManetAddress,ManetAddress>(dest, next)/std::make_pair((ManetAddress)dest, (ManetAddress)next)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc" if not is_modernized and inet_version >= "2.2" and inet_version < "2.4" else None,

            # fix IPv6Address.cc:185: non-constant-expression cannot be narrowed from type 'unsigned int' to 'int' in initializer list in inet-2.1.0
            "sed -i 's/  int groups\\[8\\] = /  unsigned int groups[8] = /' src/networklayer/contract/IPv6Address.cc" if not is_modernized and inet_version < "2.2" else None,
            "sed -i 's/findGap(int \\*groups/findGap(unsigned int *groups/' src/networklayer/contract/IPv6Address.cc" if not is_modernized and inet_version < "2.2" else None,
        ],
        "build_commands": [ "make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE" ],
        "clean_commands": [ "[ ! -f src/Makefile ] || make clean" ],
        "options": {
            "git": {
                "option_description": "Install from git repo on github",
                "category": "download",
                "git_url": "git@github.com:inet-framework/inet.git",
                "git_branch": f"v{inet_version}",
                "download_url": "",
            },
            "local": {
                "option_description": "Install from tarballs on local disk",
                "category": "download",
                "download_commands": f"mkdir inet-{inet_version} && cd inet-{inet_version} && tar --strip-components=1 -xzf {downloads_dir}/inet-{inet_version}.tar.gz",
                "download_url": "",
            },
            "local-git": {
                "option_description": "Install from git repo on local disk",
                "category": "download",
                "download_commands": f"git clone -l {local_inet_git_repo} inet-{inet_version} --branch v{inet_version}",
                "download_url": "",
            }
        }
    }

def get_all_inet_released_versions():
    return [ make_inet_project_description(inet_version, omnetpp_versions) for inet_version, omnetpp_versions in [
        ["4.5.0", ["6.0.*"]],
        ["4.4.1", ["6.0.*"]],
        ["4.4.0", ["6.0.*"]],
        ["4.3.9", ["6.0.*"]],
        ["4.3.8", ["6.0.*"]],
        ["4.3.7", ["6.0.*"]],
        # ["4.3.6", ["6.0.*"]],  Note: these versions only worked with preview versions of OMNeT++ 6.0, which are no longer available
        # ["4.3.5", ["6.0.*"]],
        # ["4.3.4", ["6.0.*"]],
        # ["4.3.3", ["6.0.*"]],
        # ["4.3.2", ["6.0.*"]],
        # ["4.3.1", ["6.0.*"]],
        # ["4.3.0", ["6.0.*"]],
        ["4.2.10",["5.7.*", "6.0.*"]],
        ["4.2.9", ["5.7.*", "6.0.*"]],
        ["4.2.8", ["5.7.*"]],
        ["4.2.7", ["5.7.*"]],
        ["4.2.6", ["5.7.*"]],
        ["4.2.5", ["5.6.2", "5.6.x", "5.7.*"]],
        ["4.2.4", ["5.4.1", "5.4.x", "5.5.*", "5.6.*", "5.7.*"]],
        ["4.2.3", ["5.4.1", "5.4.x", "5.5.*", "5.6.*", "5.7.*"]],
        ["4.2.2", ["5.4.1", "5.4.x", "5.5.*", "5.6.*", "5.7.*"]],
        ["4.2.1", ["5.4.1", "5.4.x", "5.5.*", "5.6.*", "5.7.*"]],
        ["4.2.0", ["5.4.1", "5.4.x", "5.5.*", "5.6.*", "5.7.*"]],
        ["4.1.2", ["5.4.1", "5.4.x", "5.5.*", "5.6.*", "5.7.*"]],
        ["4.1.1", ["5.4.1", "5.4.x", "5.5.*", "5.6.*", "5.7.*"]],
        ["4.1.0", ["5.4.1", "5.4.x"]], # with omnetpp-5.5.1: error: PacketQueue.cc:23: cPacketQueue constructor call is ambiguous
        ["4.0.0", ["5.4.1", "5.4.x"]], # with omnetpp-5.5.1: error: PacketQueue.cc:23: cPacketQueue constructor call is ambiguous

        ["3.8.3", ["5.7.*", "6.0.*"]],
        ["3.8.2", ["5.7.*", "6.0.*"]],
        ["3.8.1", ["5.7.*"]],
        ["3.8.0", ["5.7.*"]],
        ["3.7.1", ["5.3.*", "5.4.*", "5.5.*", "5.6.*", "5.7.*"]],
        ["3.7.0", ["5.3.*", "5.4.*", "5.5.*", "5.6.*", "5.7.*"]],
        ["3.6.8", ["5.3.*", "5.4.*", "5.5.*", "5.6.*", "5.7.*"]],
        ["3.6.7", ["5.3.*", "5.4.*", "5.5.*", "5.6.*", "5.7.*"]],
        ["3.6.6", ["5.3.*", "5.4.*", "5.5.*", "5.6.*", "5.7.*"]],
        ["3.6.5", ["5.3.*", "5.4.*", "5.5.*", "5.6.*", "5.7.*"]],
        ["3.6.4", ["5.1.*", "5.2.*", "5.3.*", "5.4.*"]], # note: this adds support for changed cMessagePrinter API in omnetpp-5.3; omnetpp-5.5 fails due to cPacketQueue constructor ambiguity
        ["3.6.3", ["5.1.*", "5.2.*"]], # with with omnetpp-5.3: error due to cMessagePrinter::printMessage() interface change
        ["3.6.2", ["5.1.*", "5.2.*"]], # with with omnetpp-5.3: error due to cMessagePrinter::printMessage() interface change
        ["3.6.1", ["5.1.*", "5.2.*"]], # with with omnetpp-5.3: error due to cMessagePrinter::printMessage() interface change
        ["3.6.0", ["5.1.*"]], # with omnetpp-5.2: Ieee80211ControlInfoDescr.h:16:6: error: Version mismatch! Probably this file was generated by an earlier version of nedtool
        ["3.5.x", ["5.1.*"]],
        ["3.5.0", ["5.1.*"]],
        ["3.4.0", ["5.1.*"]],
        ["3.3.0", ["4.6.*", "5.0.*", "5.1.*"]], # with omnetpp-5.2.1: RoutingTableRecorder.cc:296:37: error: expected ')' (due to missing INT64_PRINTF_FORMAT symbol?)
        ["3.2.4", ["4.6.*", "5.0.*", "5.1.*"]], # # with omnetpp-5.2.1: RoutingTableRecorder.cc:296:37: error: expected ')' (due to missing INT64_PRINTF_FORMAT symbol?)
        ["3.2.3", ["4.6.*"]], # with omnetpp-5.0: Ieee80211OldMac.cc:38:21: error: no member named 'Ieee80211OldMac' in namespace 'inet'; MAYBE Register_Enum issue?
        ["3.2.2", ["4.6.*"]], # with omnetpp-5.0: Ieee80211OldMac.cc:38:21: error: no member named 'Ieee80211OldMac' in namespace 'inet'; MAYBE Register_Enum issue?
        ["3.2.1", ["4.6.*"]], # with omnetpp-5.0: HeatMapFigure.cc:27:5: error: use of undeclared identifier 'fill' (fixed in inet-3.2.2)
        ["3.2.0", ["4.6.*"]], # with omnetpp-5.0: HeatMapFigure.cc:27:5: error: use of undeclared identifier 'fill' (fixed in inet-3.2.2)
        ["3.1.x", ["4.6.*"]],
        ["3.1.1", ["4.6.*"]],
        ["3.1.0", ["4.6.*"]],
        ["3.0.x", ["4.6.*"]],
        ["3.0.0", ["4.6.*"]],

        ["2.6.0", ["4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.5.0", ["4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.4.0", ["4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.3.0", ["4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.2.0", ["4.2.*", "4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.1.0", ["4.2.*", "4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.0.0", ["4.2.*"]], # 4.3+ versions don't work, due to getFieldArraySize issue

        ["2.6.x", ["4.4.*", "4.5.*", "4.6.*"]],
        ["2.5.x", ["4.4.*", "4.5.*", "4.6.*"]],
        ["2.4.x", ["4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.3.x", ["4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.2.x", ["4.2.*", "4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.1.x", ["4.2.*", "4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.0.x", ["4.2.*", "4.3.*", "4.4.*", "4.5.*", "4.6.*"]]
    ]]

def get_project_descriptions():
    return [
        {
            "name": "inet", "version": "git", "description": description,
            "folder_name": "inet",
            "required_projects": {"omnetpp": ["master"]},
            "external_nix_packages": ["python3", "z3"],
            "git_url": "git@github.com:inet-framework/inet.git",
            "setenv_commands": [ "source setenv" ],
            "build_commands": [ "make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE" ],
            "clean_commands": "[ ! -f src/Makefile ] || make clean"
        },
        *get_all_inet_released_versions()
    ]
