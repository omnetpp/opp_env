# Support installing INET git (master) with OMNeT++ git omnetpp-6.x branch

## Goal

Make `opp_env` able to install the **INET git master** branch together with the
**OMNeT++ `omnetpp-6.x` git branch**, using the already-supported `@branch`
syntax:

```bash
opp_env install inet-git@master omnetpp-git@omnetpp-6.x
# equivalently, since inet-git already defaults to the master branch:
opp_env install inet-git omnetpp-git@omnetpp-6.x
```

This needs **one database change**: `inet-git` must declare the OMNeT++ `git`
version as a compatible dependency. No new `omnetpp-6.x` version entry is needed.

## Background / findings

### `@branch` syntax already exists

A project name may carry an `@<branch>` suffix that overrides which git branch is
checked out, on top of the project's normal git clone:

- `chop_branch_names()` (`opp_env.py` ~L1718) splits `name@branch` into the
  stripped project name plus a `{stripped_name: branch}` map, keyed by
  `get_full_name()` (e.g. `omnetpp-git`).
- `download_project()` (~L1267) does `git_branch = git_branch or
  project_description.git_branch`, then appends `git checkout <branch>` to the
  clone command.
- It is only valid for projects installed **from git** (~L1252 raises otherwise),
  which the `-git` versions are by default.
- It is documented in the CLI help (~L255, ~L403:
  `opp_env install inet-git@topic/mybranch`).

So `omnetpp-git@omnetpp-6.x` means: use the **`omnetpp-git`** project description
(master settings — modernized, newest nixos/toolchain, no base-release patching)
but `git checkout omnetpp-6.x` instead of `master`. The branch override changes
only the checkout; nix packages, patch/build commands, etc. come from the `git`
description, which is appropriate since both `master` and `omnetpp-6.x` are
modern branches.

### Why it doesn't work today: dependency compatibility

The `@` suffix changes only *which branch is checked out* — it does **not** affect
version-compatibility resolution, which runs purely on the version string. For
both projects that string is `"git"`.

`inet-git` currently declares compatibility only with released `6.4.*` versions
(`inet.py` ~L271):

```python
make_inet_project_description("git", ["6.4.*"]),
```

`_is_valid_combination()` rejects `(inet=git, omnetpp=git)` because `"git"` is not
in the expanded `["6.4.*"]`. So `opp_env install inet-git omnetpp-git@...` fails
to resolve before the branch override is ever applied.

### Resolution ordering keeps the branch combo opt-in

`get_project_version_names()` returns versions in **database declaration order**;
`expand_dependencies()` takes the first valid combination. OMNeT++'s `git`
(master) description is appended **last** (`omnetpp.py` ~L454), after all
releases, so it is the lowest-priority match. Adding `"git"` to INET git's
compatible list therefore does **not** change the default: bare
`opp_env install inet-git` still resolves to the highest-priority release
(`omnetpp-6.4.*`). The OMNeT++ git branch is selected only when the user names
`omnetpp-git` explicitly.

## Plan

### 1. INET database — declare omnetpp-git as a compatible dependency for INET git  ✅ DONE

File: `opp_env/database/inet.py`, `get_project_descriptions()` (~L271).

```python
        make_inet_project_description("git", ["6.4.*", "git"]),
```

`"6.4.*"` stays **first** so bare `inet-git` still defaults to a 6.4 release;
adding `"git"` makes `(inet-git, omnetpp-git)` a valid combination that the user
opts into by naming `omnetpp-git`. Combined with the `@omnetpp-6.x` branch
override, this installs INET master against the OMNeT++ `omnetpp-6.x` branch.

### 2. Drive-by: remove stray debug print  ✅ DONE

`opp_env.py` ~L1268 has a leftover `print(git_branch)` in `download_project()`.
Remove it.

### 3. Tests  ✅ DONE

- Added a resolution check to `tests/smoketest_list_and_info` (lightweight, no
  build): `list --matching inet-git omnetpp-git` lists the combination, and
  `list --expand inet-git` still defaults to `omnetpp-6.4.0` (not the git branch).
  This is the right place — there is no new listed version, and the existing
  `--print-commands`-style dry run does not exist as a flag; resolution is what
  the change affects. The heavy `@branch`-checkout/build path is covered by the
  full build in Verification step 3.

### 4. CHANGES.md  ✅ DONE

Added section `0.36.3.260622` with the inet-git/omnetpp-git entry and the
stray-print removal.

## Verification  ✅ DONE

Done in worktree `inet-git-omnetpp-6x` / scratch workspace
`opp_env-inet-git-6x-ws`:

1. ✅ Resolution: `list --matching inet-git omnetpp-git` lists `inet-git
   omnetpp-git` (empty on baseline `main`). (Note: there is no
   `--print-commands` flag; resolution is what the change affects.)
2. ✅ Opt-in preserved: `list --expand inet-git` → `inet-git omnetpp-6.4.0`.
3. ✅ **Full build succeeded** (`opp_env install inet-git
   omnetpp-git@omnetpp-6.x`, exit 0). Independently verified:
   - OMNeT++ on branch `omnetpp-6.x` (commit `820d04e7bb`), INET on `master`
     (commit `5db7070295`).
   - Built libs present: `omnetpp-git/bin/opp_run_release`,
     `inet-git/out/clang-release/src/libINET.so` (~124 MB).
   - **INET master compiled cleanly against the omnetpp-6.x branch — no
     source-level errors.** The compatibility risk below is resolved.
4. ✅ `tests/smoketest_list_and_info` passes against the worktree code.

## Open questions / risks

- ~~**Source compatibility:** INET master targets OMNeT++ master, not the 6.x
  maintenance branch.~~ **Resolved** — verified to build cleanly (step 3).
- This relies on the `omnetpp-6.x` branch existing on GitHub (confirmed via
  `git ls-remote https://github.com/omnetpp/omnetpp.git omnetpp-6.x`). The
  `@branch` mechanism requires the branch to exist at install time.
- **Pre-existing, out of scope:** there is no
  `opp_env/templates/workspace/26.05/flake.lock`, although `omnetpp.py` now uses
  `nixos_latest = "26.05"` (introduced earlier on `main`, not by this change). A
  fresh workspace that triggers 26.05 must bootstrap the lock via the GitHub API
  and can hit rate limits. Seeding a `26.05/flake.lock` template would fix this;
  track separately.
