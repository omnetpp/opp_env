# Publishing opp_env Nix store packages to a binary cache

Projects installed with the `@` version suffix (e.g. `opp_env install omnetpp-latest@`)
are built as pure, sandboxed Nix derivations. This makes their build results
distributable through a Nix binary cache: consumers download the prebuilt package
instead of compiling it, and `opp_env install omnetpp-latest@` (or a plain
`nix build` of an exported flake) completes in the time of a download.

## Exporting the flake

```
opp_env export-flake omnetpp-6.4.0 -o ./flakes
```

writes one flake directory per project (use `--bundle` for a single self-contained
flake). Each directory contains a `push-to-cachix.sh` helper and a README.

## Pushing to cachix

1. Create a cache at https://app.cachix.org and get an auth token.
2. `cachix authtoken <token>`
3. In the exported flake directory:

   ```
   ./push-to-cachix.sh <cache-name>
   ```

   This builds the package and pushes its full runtime closure to the cache.

## Consuming

On the consumer machine (any Linux with Nix):

```
cachix use <cache-name>
```

after which `nix build` of the exported flake, or an `opp_env install ...@` that
resolves to the same derivation, substitutes the prebuilt package from the cache.

Notes:

- Binary caches are per-system: an `x86_64-linux` closure only serves `x86_64-linux`
  consumers.
- The derivation (and hence the cache hit) is identified by all of its inputs:
  project version, selected options (e.g. `no-ide`), build modes, the pinned nixpkgs
  release, and the source archive hash. The same request on any machine yields the
  same store path.
- The `no-ide` option (`--options omnetpp:no-ide`) reduces the closure size
  substantially (no Eclipse IDE, webkitgtk, etc.) and is recommended for caches
  that only serve command-line/CI use.
- The `out/` build output tree is pruned from the package, which cuts the size of
  INET by about 75% and of OMNeT++ by about 40%. The finished libraries and
  executables are unaffected: the makefiles place them in `lib/`, `bin/` and `src/`.

## Verifying a package before publishing

Every store package build runs basic checks automatically (path validity,
`nix store verify`, a scan for `/home/` path leaks); problems are reported as
warnings. For a stricter bit-reproducibility check, rebuild and compare:

```
nix build --rebuild 'path:<flake-dir>#<attr>'
```

(Note: OMNeT++ builds embed timestamps, so bit-identical rebuilds are not
guaranteed; treat differences as informational.)
