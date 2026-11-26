#!/usr/bin/env bash
# Usage: ./smoke.sh [base-url]   (default: http://localhost:8787, i.e. `wrangler dev`)
# Note: against production this adds five rows (opp_env version 0.0.0-smoke, CI) to the statistics.
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

if [[ "$failures" -gt 0 ]]; then
    echo "$failures check(s) failed"
    exit 1
fi
echo "all checks passed"
