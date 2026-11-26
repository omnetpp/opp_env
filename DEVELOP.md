# Contributing to opp_env

If you want to contribute to the development of `opp_env` or need to modify the
source code for any reason, you can install the package in editable mode by
cloning the git repo, changing to its root directory and using
the following command:

    pip install --editable .

This will install the Python module and the `opp_env` command, but with the
added ability to make local modifications that will take effect immediately.

In case of other errors, try upgrading pip to the latest version first by
running `python3 -m pip install --upgrade pip`.

## Download Statistics

After `download_project` succeeds (tarball, git clone, or `download_commands`;
but not with `--local`), opp_env posts a JSON report to `TELEMETRY_URL`
(`$OPP_ENV_TELEMETRY_URL`, by default `https://oppenv.omnetpp.org/report`,
served by the worker in `website/`) for the download statistics described in
the README. The request is sent from a daemon thread with a 3 s timeout, so it
does not delay the install. At exit, opp_env waits at most 1 s in total for
reports still in flight (e.g. after `install --no-build`), then drops them.
Errors are only logged at debug level.

Before the first download that will be reported starts (not with the report
itself, which would come after the download, lost in its output), opp_env logs
a one-time notice (INFO level) and creates
`$XDG_CONFIG_HOME/omnetpp/opp_env-telemetry-notice-shown` (default `~/.config`;
the `omnetpp` directory is meant to be shared by all OMNeT++ tools), so the
notice does not appear again. If that file cannot be created (e.g. a read-only
home directory), the notice is shown once per run instead. Delete the file to
see the notice again.

The worker only accepts project names of lowercase letters, digits and `_`, and
versions of letters, digits and `._+-` (at most 40 characters each); reports
for other names are rejected and therefore not counted.

To test against another instance, set `OPP_ENV_TELEMETRY_URL`, e.g. to
`http://localhost:8787/report` for `wrangler dev`. Setting `OPP_ENV_NO_TELEMETRY`
or `DO_NOT_TRACK` to any non-empty value (even `0`) disables the reports. The test scripts (`tests/testlib.inc` and
`tests/project_tester`) set it, so test runs, including all CI workflows that
use them, are not counted.

Unit tests for this can be run with:

    python3 tests/test_telemetry.py

## Website

The `website/` folder holds https://oppenv.omnetpp.org: the site itself, the
privacy policy, the download statistics dashboard, and the Cloudflare Worker
that serves all of it and receives the download reports. See
`website/README.md` for local testing and deployment. It is not part of the
Python package.

## Building the Python Package

To build the Python package, you first need to install the `build` package by
running the following command:

    pip install --upgrade build

Once you have `build` installed, you can build the package by running:

    python3 -m build

If you have any issues or questions, feel free to open an issue on the GitHub
repository. We are always happy to help!

