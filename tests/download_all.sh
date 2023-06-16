# extract non-empty download URLs from all project descriptions, and download the files (add the -P 4 option to xargs to use 4 threads)
opp_env info --raw | jq '.[].download_url | select(. != null and . != "")' | sort | xargs -n 1 curl -LO

