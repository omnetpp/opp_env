# oppenv.omnetpp.org

The opp_env website and download statistics, served by one Cloudflare Worker
(`oppenv-website`) on the custom domain `oppenv.omnetpp.org`:

- `public/` is served as static assets: the site (`index.html`, `styles.css`,
  `script.js`, `images/`) and the privacy policy (`privacy.html`, served at
  `/privacy`).
- `src/` handles the requests that match no file: `POST /report` (download
  reports from opp_env); anything else gets a plain-text `404`.

This folder is not part of the opp_env Python package (see `MANIFEST.in`).

## Download reports

opp_env downloads archives directly from their original location; after a
project has been downloaded successfully, it posts a short report:

    POST https://oppenv.omnetpp.org/report
    Content-Type: application/json

    {"project": "inet", "version": "4.5.4", "dependency": false, "os": "linux",
     "arch": "x86_64", "ci": false, "opp_env_version": "0.36.3.261123"}

`project` and `version` are required, the rest is optional. `dependency` means
the project was downloaded as a dependency of the project the user asked for;
`ci` that opp_env ran in CI; `store_backed` that the project was installed as a
read-only Nix store package (`@`). opp_env releases without that feature do not
send it, so a missing or invalid `store_backed` is stored as 0 (a regular,
writable install). Strings must be short alphanumeric tokens, the flags JSON
booleans. A missing or invalid `project` or `version`, other
content types and bodies over 1 KiB are rejected (`400`/`415`/`413`); an
invalid optional field is stored as NULL, and unknown fields are ignored (so a
newer opp_env can add fields before the worker knows them). Accepted
reports get `204`, before the row is written (write errors only show up in the
worker's logs). More than 60 reports per minute from one IP address get `429`
(the `REPORT_LIMITER` rate-limiting binding in `wrangler.toml`; its counters
live in Cloudflare, not in D1).

Each report stores one row in the D1 table `downloads` (database
`oppenv-stats`): the reported fields, the date (UTC; not the time of day, which
would link the reports of one install), and the country (`request.cf.country`).
No IP addresses and no download URLs are stored. Users opt out by setting
`OPP_ENV_NO_TELEMETRY` or `DO_NOT_TRACK` to any non-empty value; see
`public/privacy.html`.

## Deploy

Deploys are manual, from this folder. The first time, create the D1 database
and its table:

    npx wrangler login
    npx wrangler d1 create oppenv-stats            # put the printed id into wrangler.toml
    npx wrangler d1 execute oppenv-stats --remote --file schema.sql

Then, and for every later change:

    npx wrangler deploy

`wrangler deploy` attaches the custom domain `oppenv.omnetpp.org` and creates
its DNS record; it fails while another DNS record for that name exists.

### Checking a deployment

    ./smoke.sh https://oppenv.omnetpp.org

Since `/report` answers `204` before writing, also check that a real report is
stored. Run opp_env itself, so bot protection sees the real client:

    mkdir /tmp/telemetry-check && cd /tmp/telemetry-check
    opp_env -l DEBUG install --init --no-build --no-deps veins-5.3.1   # look for "Reported download of veins-5.3.1"
    npx wrangler d1 execute oppenv-stats --remote --command "SELECT * FROM downloads ORDER BY id DESC LIMIT 5"

and delete the test rows again (`DELETE FROM downloads WHERE id IN (...)`; the
smoke rows: `DELETE FROM downloads WHERE opp_env_version = '0.0.0-smoke'`).

Do this from a machine outside your usual network (e.g. a cloud VM), because
bot protection (Bot Fight Mode or a WAF challenge rule) must not challenge
`POST /report`: opp_env cannot answer a challenge and only logs the failure at
debug level, so reports would silently go missing. If the row is missing and the
log shows `HTTP Error 403`, exempt `/report` from the challenge (Bot Fight Mode
itself cannot be skipped per path on the Free plan; it has to be turned off).

## Local testing

    npx wrangler d1 execute oppenv-stats --local --file schema.sql
    npx wrangler dev                               # site at http://localhost:8787/
    ./smoke.sh                                     # in another terminal

Against production, `./smoke.sh
https://oppenv.omnetpp.org` adds five rows (opp_env version `0.0.0-smoke`,
flagged as CI) to the statistics; delete them with
`DELETE FROM downloads WHERE opp_env_version = '0.0.0-smoke'`.

Point opp_env at it with `export OPP_ENV_TELEMETRY_URL=http://localhost:8787/report`.

## Querying

    npx wrangler d1 execute oppenv-stats --remote --command "
      SELECT project, version, count(*) AS n FROM downloads
      WHERE ci = 0 OR ci IS NULL
      GROUP BY project, version ORDER BY n DESC LIMIT 50"

    npx wrangler d1 execute oppenv-stats --remote --command "
      SELECT os, arch, country, count(*) AS n FROM downloads
      GROUP BY os, arch, country ORDER BY n DESC"

To start the statistics from scratch (e.g. to drop test reports):

    npx wrangler d1 execute oppenv-stats --remote --command "DELETE FROM downloads"
