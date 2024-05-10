import re
description = "INET Framework is an open-source OMNeT++ model suite for wired, wireless and mobile networks."

def dotx(version):
    # 4.2, 4.2.1, 4.2p1 -> 4.2.x
    return re.sub("(\\d\\.\\d)[\\.p]\\d", "\\1", version) + ".x"

def join_nonempty_items(sep, list):
    return sep.join([x for x in list if x])

def make_inet_project_description(inet_version, omnetpp_versions):
    is_git_branch = inet_version == "master" or inet_version.endswith(".x")
    is_modernized = inet_version == "master" or inet_version.endswith(".x") # TODO and the patch-release tags on .x branches

    git_branch_or_tag_name = f"v{inet_version}" if inet_version[0].isdigit() else inet_version

    # Some version tags have no entry on the Releases page
    missing_releases = [ "3.2.2", "3.1.0" ]

    return {
        "name": "inet", "version": inet_version, "description": description,
        "folder_name": "inet",
        "metadata": {
            "catalog_url": "https://omnetpp.org/download-items/INET.html",
        },
        "required_projects": {"omnetpp": omnetpp_versions}, # list(set([dotx(v) for v in omnetpp_versions]))},
        "nix_packages": [
            "z3" if inet_version >= "4.4" else None,  # ffmpeg needed for VoIPStream
            "ffmpeg-headless" if inet_version >= "4.5" else "ffmpeg_4-headless" if inet_version >= "4.0" else None,  # ffmpeg needed for VoIPStream
            "python3" if inet_version >= "3.6.7" or is_modernized else "python2" # up to inet-3.6.6, inet_featuretool uses python2 in original, and python3 in modernized versions
            ],
        "patch_commands": [
            "touch tutorials/package.ned" if inet_version <= "4.2.1" and inet_version >= "3.6.0" else "",

            # fix up shebang line in inet_featuretool (python -> python2)
            "sed -i.bak 's| python$| python2|' inet_featuretool" if inet_version >= "3.0" and inet_version < "3.6.7" and not is_modernized else "",

            # fix "error: flexible array member in union" in sctp.h, later renamed to sctphdr.h
            "sed -i.bak 's|info\\[\\]|info[0]|' src/inet/common/serializer/sctp/headers/sctphdr.h" if inet_version.startswith("3.") else "",
            "sed -i.bak 's|info\\[\\]|info[0]|' src/util/headerserializers/sctp/headers/sctp.h" if inet_version.startswith("2.") else "",

            # Linux appears to define "__linux__" nowadays, not "linux"; affected: serializer/headers/defs.h, ExtInterface.cc, RawSocket.cc, OsUdp.cc, Ext.cc, etc., and their renamed/moved versions
            # Note: grep -s suppresses error messages about broken media/ softlinks under showcases and tutorials in 4.x versions
            "for f in $(grep -Rls 'defined(linux)'); do sed -i.bak 's|defined(linux)|defined(__linux__)|' $f; done",

            # cResultFilterDescriptor was renamed in omnetpp-5.1
            "sed -i.bak 's|cResultFilterDescriptor|cResultFilterType|' src/inet/common/figures/DelegateSignalConfigurator.cc" if inet_version == "3.4.0" else "",

            # PacketDrillApp bug in early 3.x versions
            "sed -i.bak 's|->spp_hbinterval > 0|->spp_hbinterval->getNum() > 0|' src/inet/applications/packetdrill/PacketDrillApp.cc" if inet_version>="3.5.0" and inet_version<="3.6.1" else "",
            "sed -i.bak 's|->spp_pathmaxrxt > 0|->spp_pathmaxrxt->getNum() > 0|' src/inet/applications/packetdrill/PacketDrillApp.cc" if inet_version>="3.5.0" and inet_version<="3.6.1" else "",

            # INT64_PRINTF_FORMAT was removed in omnetpp-5.3 (?), replace with "l" for simplicity (suits all 64-bit platforms except Windows)
            "for f in $(grep -Rl 'INT64_PRINTF_FORMAT'); do sed -i.bak 's|INT64_PRINTF_FORMAT|\"l\"|' $f; done" if inet_version.startswith("3.") else "",

            # fix linklayer/radio/Radio.cc:1134:35: error: redefinition of 'it' with a different type in inet-2.0 thru 2.2
            "sed -i.bak 's/SensitivityList::iterator it = sensitivityList.find(0.0);/SensitivityList::iterator sit = sensitivityList.find(0.0);/' src/linklayer/radio/Radio.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "2.3" else None,
            "sed -i.bak 's/if (it == sensitivityList.end())/if (sit == sensitivityList.end())/' src/linklayer/radio/Radio.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "2.3" else None,

            # fix networklayer/ipv4/RoutingTableRecorder.cc:166:35: error: invalid suffix on literal in inet-2.3
            "sed -i.bak 's/\"LL\"/\" LL \"/' src/networklayer/ipv4/RoutingTableRecorder.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "2.5" else None,

            # fix src/networklayer/manetrouting/dsr/dsr-uu/path-cache.cc
            "sed -i.bak 's/if (vector_cost<=0)/if (vector_cost == NULL)/' src/networklayer/manetrouting/dsr/dsr-uu/path-cache.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "3.0" else None,
            "sed -i.bak 's/if (vector_cost<=nullptr)/if (vector_cost == nullptr)/' src/inet/routing/extras/dsr/dsr-uu/path-cache.cc" if not is_modernized and inet_version >= "3.0" and inet_version < "3.1" else None,

            # compile fix for omnetpp-4.3..4.6: getArraySize() was supposed to be renamed to getFieldArraySize() in omnetpp-4.3, but then the change was postponed to 5.0 as being a breaking change.
            "sed -i.bak 's/OMNETPP_VERSION < 0x0403/OMNETPP_VERSION < 0x0500/' src/networklayer/manetrouting/aodv/aodv_msg_struct_descriptor.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "2.1" else None,
            "sed -i.bak 's/OMNETPP_VERSION < 0x0403/OMNETPP_VERSION < 0x0500/' src/util/MessageChecker.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "2.1" else None,

            # fix no matching function for call to 'make_pair' in src/networklayer/manetrouting/base/ManetRoutingBase.cc (c++11 change in make_pair() signature)
            "sed -i.bak 's/std::make_pair<Uint128,ProtocolsRoutes>(getAddress(),vect)/std::make_pair((Uint128)getAddress(),vect)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "2.1" else None,
            "sed -i.bak 's/std::make_pair<Uint128,Uint128>(dst, gtwy)/std::make_pair((Uint128)dst, (Uint128)gtwy)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "2.1" else None,
            "sed -i.bak 's/std::make_pair<Uint128,Uint128>(destination, nextHop)/std::make_pair((Uint128)destination, (Uint128)nextHop)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc" if not is_modernized and inet_version >= "2.0" and inet_version < "2.1" else None,

            "sed -i.bak 's/std::make_pair<ManetAddress,ProtocolsRoutes>(getAddress(),vect)/std::make_pair((ManetAddress)getAddress(),vect)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc" if not is_modernized and inet_version == "2.1.0" else None,
            "sed -i.bak 's/std::make_pair<ManetAddress,ManetAddress>(dst, gtwy)/std::make_pair((ManetAddress)dst, (ManetAddress)gtwy)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc" if not is_modernized and inet_version == "2.1.0" else None,
            "sed -i.bak 's/std::make_pair<ManetAddress,ManetAddress>(destination, nextHop)/std::make_pair((ManetAddress)destination, (ManetAddress)nextHop)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc" if not is_modernized and inet_version == "2.1.0" else None,

            # fix no matching function for call to 'make_pair' in src/networklayer/manetrouting/base/ManetRoutingBase.cc (c++11 change in make_pair() signature)
            "sed -i.bak 's/std::make_pair<ManetAddress,ProtocolsRoutes>(getAddress(),vect)/std::make_pair((ManetAddress)getAddress(),vect)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc" if not is_modernized and inet_version >= "2.2" and inet_version < "2.4" else None,
            "sed -i.bak 's/std::make_pair<ManetAddress,ManetAddress>(dest, next)/std::make_pair((ManetAddress)dest, (ManetAddress)next)/' src/networklayer/manetrouting/base/ManetRoutingBase.cc" if not is_modernized and inet_version >= "2.2" and inet_version < "2.4" else None,

            # fix IPv6Address.cc:185: non-constant-expression cannot be narrowed from type 'unsigned int' to 'int' in initializer list in inet-2.1.0
            "sed -i.bak 's/  int groups\\[8\\] = /  unsigned int groups[8] = /' src/networklayer/contract/IPv6Address.cc" if not is_modernized and inet_version < "2.2" else None,
            "sed -i.bak 's/findGap(int \\*groups/findGap(unsigned int *groups/' src/networklayer/contract/IPv6Address.cc" if not is_modernized and inet_version < "2.2" else None,

            "sed -i.bak 's|precompiled.h|precompiled_$(MODE).h|' src/makefrag" if inet_version.startswith("3.5") else None,
            """echo '#include "precompiled.h"' > src/inet/common/precompiled_debug.h""" if inet_version.startswith("3.5") else None,
            """echo '#include "precompiled.h"' > src/inet/common/precompiled_release.h""" if inet_version.startswith("3.5") else None,
            ],
        "setenv_commands": [
            'export OMNETPP_IMAGE_PATH="$OMNETPP_IMAGE_PATH:$INET_ROOT/images"',
            "[ -f setenv ] && INET_ROOT= source setenv -f", # note: actually, setenv ought to contain adding INET to NEDPATH and OMNETPP_IMAGE_PATH
        ],
        "build_commands": [
            # we do have z3 and avcodec (in ffmpeg), so the first time we run, turn on the project features that use them
            # note: this should probably be in "patch_commands" instead, but opp_featuretool is not available there because omnetpp's setenv hasn't run and omnetpp hasn't been built yet
            # note: VoipStream could be turned on for earlier INET versions too, but it's not tested out / added yet
            "[ -f src/Makefile ] || opp_featuretool -v enable Z3GateSchedulingConfigurator" if inet_version >= "4.4" else "",
            "[ -f src/Makefile ] || opp_featuretool -v enable VoipStream VoipStreamExamples" if inet_version >= "4.3" else
            "[ -f src/Makefile ] || opp_featuretool -v enable VoIPStream VoIPStream_examples" if inet_version >= "4.0" else "",

            # build
            "make makefiles && make -j$NIX_BUILD_CORES MODE=$BUILD_MODE"
        ],
        "clean_commands": [ "[ ! -f src/Makefile ] || make clean" ],
        "smoke_test_commands": [
            "cd examples/ethernet/arptest",
            """if [ "$mode" = "debug" ]; then DBG_SUFFIX="_dbg"; INET_LIB=$(echo $INET_ROOT/out/*-debug/src/*INET*); fi""",
            """if [ "$mode" = "release" ]; then DBG_SUFFIX=""; INET_LIB=$(echo $INET_ROOT/out/*-release/src/*INET*); fi""",
            "opp_run$DBG_SUFFIX -l $INET_LIB -n $INET_ROOT/tutorials:$INET_ROOT/examples:.:$INET_ROOT/src -c ARPTest -u Cmdenv --sim-time-limit=10s > /dev/null" if inet_version < "4.0" else
            "inet$DBG_SUFFIX -c ARPTest -u Cmdenv --sim-time-limit=10s >/dev/null"
        ],
        "options": {
            "from-release": {
                "option_description": "Install from release tarball on GitHub",
                "option_category": "download",
                "option_is_default": inet_version not in missing_releases and not is_git_branch,
                "download_url": f"https://github.com/inet-framework/inet/releases/download/v{inet_version}/inet-{inet_version}-src.tgz" if inet_version not in missing_releases and not is_git_branch else None,
            },
            "from-source-archive": {
                "option_description": "Install from source archive on GitHub",
                "option_category": "download",
                "option_is_default": inet_version in missing_releases,
                "download_url": f"https://github.com/inet-framework/inet/archive/refs/{'heads' if is_git_branch else 'tags'}/{git_branch_or_tag_name}.tar.gz",
            },
            "from-git": {
                "option_description": "Install from git repo on GitHub",
                "option_category": "download",
                "option_is_default": is_git_branch,
                "git_url": "https://github.com/inet-framework/inet.git",
                "git_branch": git_branch_or_tag_name,
            },
        }
    }

def get_all_inet_released_versions():
    return [ make_inet_project_description(inet_version, omnetpp_versions) for inet_version, omnetpp_versions in [
        ["4.5.2", ["6.0.*"]],
        ["4.5.1", ["6.0.*"]],
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
        ["4.2.5", ["5.6.*", "5.7.*"]],
        ["4.2.4", ["5.4.2", "5.4.1", "5.4.x", "5.5.*", "5.6.*", "5.7.*"]],
        ["4.2.3", ["5.4.2", "5.4.1", "5.4.x", "5.5.*", "5.6.*", "5.7.*"]],
        ["4.2.2", ["5.4.2", "5.4.1", "5.4.x", "5.5.*", "5.6.*", "5.7.*"]],
        ["4.2.1", ["5.4.2", "5.4.1", "5.4.x", "5.5.*", "5.6.*", "5.7.*"]],
        ["4.2.0", ["5.4.2", "5.4.1", "5.4.x", "5.5.*", "5.6.*", "5.7.*"]],
        ["4.1.2", ["5.4.2", "5.4.1", "5.4.x", "5.5.*"]], # with omnetpp-5.6.*, omnetpp-5.7.*: error: Direct deletion of a module is illegal, use deleteModule() instead
        ["4.1.1", ["5.4.2", "5.4.1", "5.4.x", "5.5.*"]], # with omnetpp-5.6.*, omnetpp-5.7.*: error: Direct deletion of a module is illegal, use deleteModule() instead
        ["4.1.0", ["5.4.2", "5.4.1", "5.4.x"]], # with omnetpp-5.5.1: error: PacketQueue.cc:23: cPacketQueue constructor call is ambiguous
        ["4.0.0", ["5.4.2", "5.4.1", "5.4.x"]], # with omnetpp-5.5.1: error: PacketQueue.cc:23: cPacketQueue constructor call is ambiguous

        ["3.8.3", ["5.7.*", "6.0.*"]],
        ["3.8.2", ["5.7.*", "6.0.*"]],
        ["3.8.1", ["5.7.*"]],
        ["3.8.0", ["5.7.*"]],
        ["3.7.1", ["5.3.*", "5.4.*", "5.5.*", "5.6.*", "5.7.*"]],
        ["3.7.0", ["5.3.*", "5.4.*", "5.5.*", "5.6.*", "5.7.*"]],
        ["3.6.8", ["5.3.*", "5.4.*", "5.5.*", "5.6.*", "5.7.*"]],
        ["3.6.7", ["5.3.*", "5.4.*", "5.5.*"]], # with omnetpp-5.6.*, omnetpp-5.7.*: error: Direct deletion of a module is illegal, use deleteModule() instead
        ["3.6.6", ["5.3.*", "5.4.*", "5.5.*"]], # with omnetpp-5.6.*, omnetpp-5.7.*: error: Direct deletion of a module is illegal, use deleteModule() instead
        ["3.6.5", ["5.3.*", "5.4.*", "5.5.*"]], # with omnetpp-5.6.*, omnetpp-5.7.*: error: Direct deletion of a module is illegal, use deleteModule() instead
        ["3.6.4", ["5.1.*", "5.2.*", "5.3.*", "5.4.*"]], # note: this adds support for changed cMessagePrinter API in omnetpp-5.3; omnetpp-5.5 fails due to cPacketQueue constructor ambiguity
        ["3.6.3", ["5.1.*", "5.2.*"]], # with with omnetpp-5.3: error due to cMessagePrinter::printMessage() interface change
        ["3.6.2", ["5.1.*", "5.2.*"]], # with with omnetpp-5.3: error due to cMessagePrinter::printMessage() interface change
        ["3.6.1", ["5.1.*", "5.2.*"]], # with with omnetpp-5.3: error due to cMessagePrinter::printMessage() interface change
        ["3.6.0", ["5.1.*"]], # with omnetpp-5.2: Ieee80211ControlInfoDescr.h:16:6: error: Version mismatch! Probably this file was generated by an earlier version of nedtool
        ["3.5.x", ["5.1.*"]],
        ["3.5.0", ["5.1.*"]],
        ["3.4.0", ["5.1.*"]], # with omnetpp-5.0.*: cannot build. error: use of undeclared identifier 'cResultFilterType'; did you mean 'cResultFilter'?
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

        ["2.6.x", ["4.4.*", "4.5.*", "4.6.*"]],
        ["2.6.0", ["4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.5.x", ["4.4.*", "4.5.*", "4.6.*"]],
        ["2.5.0", ["4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.4.x", ["4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.4.0", ["4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.3.x", ["4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.3.0", ["4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.2.x", ["4.2.*", "4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.2.0", ["4.2.*", "4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.1.x", ["4.2.*", "4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.1.0", ["4.2.*", "4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.0.x", ["4.2.*", "4.3.*", "4.4.*", "4.5.*", "4.6.*"]],
        ["2.0.0", ["4.2.*"]], # 4.3+ versions don't work, due to getFieldArraySize issue

    ]]

def get_project_descriptions():
    return [
        *get_all_inet_released_versions(),
        inet_20100323, inet_20061020, # hand-picked time-stamped versions
        make_inet_project_description("master", ["6.0.*"]),
    ]

inet_20100323 = {
    # release only, because dependent projects (such as quagga) link with the release mode lib
    "name": "inet", "version": "20100323",
    "required_projects": {"omnetpp": ["4.1.0"]},        # TODO: try with 4.1.* -> build error
    "download_url": "https://github.com/inet-framework/inet/releases/download/master_20100323/inet-20100323-src.tgz",
    "patch_commands": [
        "sed -i 's|  int octals\\[8\\] = |  unsigned int octals[8] = |' src/networklayer/contract/IPv6Address.cc",
        "sed -i 's|findGap(int \\*octals|findGap(unsigned int *octals|' src/networklayer/contract/IPv6Address.cc",
        "sed -i 's|machine/endian|endian|' src/util/headerserializers/headers/defs.h",
        "sed -i 's|info\\[\\]|info[0]|' src/util/headerserializers/headers/sctp.h",
        "sed -i 's|addr.sin_len|// addr.sin_len|' src/linklayer/ext/*.cc",  # ugly hack? this is needed on apple
    ],
    "build_commands": ["make makefiles && make -j$NIX_BUILD_CORES MODE=release"],
    "clean_commands": ["make clean"],
}

inet_20061020 = {
    "name": "inet", "version": "20061020",
    "required_projects": {"omnetpp": ["3.3.1"]},        # TODO try with 3.3.* -> build error
    "download_url": "https://github.com/inet-framework/inet/releases/download/v1.x/INET-20061020-src.tgz",
    "patch_commands": [
        "sed -i 's|machine/endian|endian|' Util/HeaderSerializers/headers/defs.h",
        "sed -i 's|ROOT=$(HOME)/INET-svn|ROOT=$(INET_ROOT)|' inetconfig",
    ],
    "build_commands": ["./makemake && make"],
    "clean_commands": ["make clean"],
}