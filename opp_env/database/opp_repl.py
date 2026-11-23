def make_opp_repl_project_description(version):
    is_git = version == "git"

    return {
        "name": "opp_repl", "version": version,
        "description": "OMNeT++ Python REPL for running and testing simulations",
        "details": "An interactive Python REPL for OMNeT++: run simulations, compare results, optimize parameters, and run a wide range of regression tests "
                   "(smoke, fingerprint, statistical, speed, chart, sanitizer, etc.). Provides an MCP server for AI assistants. "
                   "All features are accessible from both the interactive REPL and command-line tools (opp_repl, opp_run_*_tests, etc.).",
        "metadata": {
            "catalog_url": "https://github.com/omnetpp/opp_repl",
        },
        # opp_repl itself is pure Python; it is used together with an OMNeT++ installation, and the nixos version comes from omnetpp.
        # Compatibility (tested on the fifo sample with omnetpp-6.0.3, 6.1.0, 6.2.0, 6.5.0):
        # - omnetpp-6.0: statistical and chart tests fail: the scave library of 6.0 drops run attributes with an empty
        #   value, e.g. measurement="" (KeyError "['measurement'] not in index"; chart legends fall back to the
        #   timestamped runID, so every chart test fails). Also, sanitizer builds fail with the old AddressSanitizer of 6.0's toolchain.
        # - omnetpp-6.1: OK for 0.5, except coverage/profile tests (MODE=coverage/profile only exist from omnetpp-6.2)
        #   and speed tests (they need the -S option of omnetpp-6.2 and INET>=4.6 for --measure-cpu-usage).
        # - opp_repl-git requires omnetpp-6.2: since opp_repl commit f2fd1de (after 0.5), the smoke, sanitizer and
        #   fingerprint tests pass --record-scalar-results=false and --record-vector-results=false (added in omnetpp-6.2.0);
        #   with omnetpp-6.0/6.1 these tests fail with "Unknown command-line configuration option --record-scalar-results".
        "required_projects": {"omnetpp": ["6.5.*", "6.4.*", "6.3.*", "6.2.*"] if is_git else ["6.5.*", "6.4.*", "6.3.*", "6.2.*", "6.1.*"]},
        "nix_packages": [
            "python3",  # opp_repl requires Python >= 3.10 (nixos-23.05, used for omnetpp-6.0, has 3.10)
            # mandatory dependencies
            "python3Packages.ipython",
            "python3Packages.pandas",
            # optional dependencies (extras in pyproject.toml), all available in every nixos version used by omnetpp-6.x
            "python3Packages.httpx",
            "python3Packages.dask",
            "python3Packages.distributed",
            "python3Packages.matplotlib",
            "python3Packages.numpy",
            "python3Packages.scipy",
            "python3Packages.requests",
            "python3Packages.py4j",
            "python3Packages.pyqt6",
            # the MCP server needs "mcp", which is only available from nixos-25.05 (omnetpp-6.2) on;
            # with older omnetpp versions, opp_repl works without the MCP server
            "(python3Packages.mcp or null)",
            # opp_sandbox runs commands under bubblewrap, which is Linux-only
            "(if stdenv.isLinux then bubblewrap else null)",
        ],
        **({"git_url": "https://github.com/omnetpp/opp_repl.git", "git_branch": "main"} if is_git else
           {"download_url": f"https://github.com/omnetpp/opp_repl/archive/refs/tags/{version}.tar.gz"}),
        "build_commands": [
            # opp_repl's setenv activates .venv if it exists. With Nix, the .venv only holds the packages
            # that Nix does not provide (optimparallel, a pure-Python package which only needs scipy and numpy);
            # the rest come from nix_packages. Note: these are not patch_commands, because the .venv files would
            # then be added to the checksum list used to detect modifications.
            # Without Nix (nixless workspace), the .venv holds opp_repl and all its dependencies installed via pip.
            r"""if [ -n "$NIX_BINTOOLS" ]; then [ -d .venv ] || python3 -m venv .venv; fi""",
            r"""if [ -n "$NIX_BINTOOLS" ]; then .venv/bin/python3 -m pip install --disable-pip-version-check -q --no-deps optimparallel; fi""",
            r"""if [ -z "$NIX_BINTOOLS" ]; then [ -d .venv ] || python3 -m venv .venv --upgrade-deps; fi""",
            # the version of opp_repl comes from git tags (setuptools_scm), which are missing from a release tarball
            (r"""if [ -z "$NIX_BINTOOLS" ]; then .venv/bin/python3 -m pip install --disable-pip-version-check -q -e .; fi""" if is_git else
             f"""if [ -z "$NIX_BINTOOLS" ]; then SETUPTOOLS_SCM_PRETEND_VERSION={version} .venv/bin/python3 -m pip install --disable-pip-version-check -q -e .; fi"""),
            (r"""if [ -z "$NIX_BINTOOLS" ]; then .venv/bin/python3 -m pip install --disable-pip-version-check -q -e '.[all]' || echo 'WARNING: Some optional dependencies of opp_repl could not be installed'; fi""" if is_git else
             f"""if [ -z "$NIX_BINTOOLS" ]; then SETUPTOOLS_SCM_PRETEND_VERSION={version} .venv/bin/python3 -m pip install --disable-pip-version-check -q -e '.[all]' || echo 'WARNING: Some optional dependencies of opp_repl could not be installed'; fi"""),
        ],
        "setenv_commands": [
            # adds bin/ to PATH and the project root to PYTHONPATH, and activates .venv
            r"""source setenv""",
            r"""echo 'Hint: Use the `opp_repl` command to start the REPL. For example: `opp_repl --load @opp` loads the OMNeT++ samples, `opp_repl --load @inet` loads INET.'""",
        ],
        "smoke_test_commands": [
            # every command-line tool must be able to start (i.e. all its imports must succeed).
            # opp_repl_self_test is skipped: it ignores --help, and its tests pip-install opp_repl into fresh venvs
            r"""for f in bin/*; do [ "$f" = bin/opp_repl_self_test ] && continue; echo "Checking $f"; $f --help > /dev/null || exit 1; done""",
        ],
    }

def get_project_descriptions():
    return [make_opp_repl_project_description(version) for version in ["0.5", "git"]]
