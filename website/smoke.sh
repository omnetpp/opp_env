#!/usr/bin/env bash
# Usage: ./smoke.sh [base-url]   (default: http://localhost:8787, i.e. `wrangler dev`)
# Note: against production this adds five rows (opp_env version 0.0.0-smoke, CI) to the statistics, and the
# /stats/ checks fail there unless the request carries a Cloudflare Access session.
set -uo pipefail

BASE="${1:-http://localhost:8787}"
REPORT='{"project":"inet","version":"4.5.4","dependency":false,"os":"linux","arch":"x86_64","ci":true,"opp_env_version":"0.0.0-smoke"}'
failures=0

result() {
    local desc="$1" got="$2" want="$3"
    if [[ "$got" != "$want" ]]; then
        echo "FAIL: $desc: got '$got', want '$want'"
        failures=$((failures + 1))
    else
        echo "ok:   $desc"
    fi
}

check() {
    local desc="$1" path="$2" want_code="$3" want_location="${4:-}"
    local out code location
    out=$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' "$BASE$path")
    code="${out%% *}"
    location="${out#* }"
    if [[ -n "$want_location" ]]; then
        result "$desc" "$code $location" "$want_code $want_location"
    else
        result "$desc" "$code" "$want_code"
    fi
}

report() {
    local desc="$1" body="$2" want_code="$3" content_type="${4:-application/json}"
    result "$desc" "$(curl -s -o /dev/null -w '%{http_code}' -X POST -H "content-type: $content_type" --data-binary "$body" "$BASE/report")" "$want_code"
}

report "report is accepted" "$REPORT" 204
report "minimal report is accepted" '{"project":"omnetpp","version":"6.2.0","ci":true,"opp_env_version":"0.0.0-smoke"}' 204
report "report needs JSON content type" "$REPORT" 415 text/plain
report "report must be JSON" 'project=inet' 400
report "report must be an object" '["inet"]' 400
report "unknown field is ignored" '{"project":"inet","version":"4.5.4","ci":true,"opp_env_version":"0.0.0-smoke","url":"https://x"}' 204
report "project is required" '{"version":"4.5.4"}' 400
report "bad project name" '{"project":"<b>inet</b>","version":"4.5.4"}' 400
report "bad version is rejected" '{"project":"inet","version":"4.5 4"}' 400
report "invalid optional values are dropped" '{"project":"inet","version":"4.5.4","ci":true,"opp_env_version":"0.0.0-smoke","os":"Windows NT","store_backed":"yes"}' 204
report "inherited name as field is ignored" '{"project":"inet","version":"4.5.4","ci":true,"opp_env_version":"0.0.0-smoke","constructor":"x"}' 204
report "oversized report" "{\"project\":\"inet\",\"version\":\"4.5.4\",\"os\":\"$(printf 'a%.0s' {1..2000})\"}" 413
chunked=$(printf 'a%.0s' {1..2000} | curl -s -o /dev/null -w '%{http_code}' -X POST -H "content-type: application/json" \
    -H "transfer-encoding: chunked" --data-binary @- "$BASE/report")
result "oversized chunked report" "$chunked" 413
check "report rejects GET" "/report" 405

# Last of the /report checks: afterwards this IP may not report for up to a minute. These requests are
# rejected for their content type, so they add no rows.
limited=""
for i in {1..70}; do
    code=$(curl -s -o /dev/null -w '%{http_code}' -X POST -H "content-type: text/plain" --data-binary x "$BASE/report")
    if [[ "$code" == 429 ]]; then limited=yes; break; fi
done
result "reports are rate limited" "${limited:-no}" yes

check "home page is served" "/" 200
check "stylesheet is served" "/styles.css" 200
check "logo is served" "/images/opp_env_logo.svg" 200
check "privacy policy is served" "/privacy" 200
check "unknown path is 404" "/nothing" 404
check "unknown stats path is 404" "/stats/nothing" 404
check "stats page is served" "/stats/" 200
check "stats without slash redirects" "/stats" 307 "$BASE/stats/"
check "chart library is served" "/stats/chart.umd.min.js" 200
check "csv export is served" "/stats/csv" 200
check "api: valid query" "/stats/api?group=project&from=2026-01-01&ci=0" 200
check "api: two groups" "/stats/api?group=week&group2=os&dependency=1" 200
check "api: group is required" "/stats/api?project=inet" 400
check "api: unknown dimension" "/stats/api?group=ip" 400
check "api: url is not a dimension" "/stats/api?group=url" 400
check "api: unknown parameter" "/stats/api?group=project&sql=1" 400
check "api: bad date" "/stats/api?group=project&from=yesterday" 400
check "api: bad flag value" "/stats/api?group=project&ci=yes" 400
check "api: same group twice" "/stats/api?group=os&group2=os" 400
check "api: inherited name as group" "/stats/api?group=constructor" 400
check "api: inherited name as filter" "/stats/api?group=project&toString=x" 400

body=$(curl -s "$BASE/stats/api?group=os")
if [[ "$body" == '{"rows":['* ]]; then echo "ok:   api returns rows"; else echo "FAIL: api body: $body"; failures=$((failures + 1)); fi

# The smoke reports include one without "dependency" (NULL) and some with false (0).
dups=$(curl -s "$BASE/stats/api?group=dependency" | grep -o '"dependency":[^,}]*' | sort | uniq -d)
result "api: NULL and 0 form one group" "$dups" ""

result "csv header" "$(curl -s "$BASE/stats/csv" | head -1 | tr -d '\r')" "date,project,version,dependency,country,os,arch,opp_env_version,ci,store_backed"

cc=$(curl -s -o /dev/null -D - "$BASE/stats/api?group=os" | tr -d '\r' | grep -i '^cache-control:')
if [[ "$cc" == *private* ]]; then echo "ok:   api responses are private"; else echo "FAIL: api cache-control: $cc"; failures=$((failures + 1)); fi

if [[ "$failures" -gt 0 ]]; then
    echo "$failures check(s) failed"
    exit 1
fi
echo "all checks passed"
