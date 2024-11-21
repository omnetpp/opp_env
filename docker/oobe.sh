#!/bin/bash
# Out of Box Experience
# This script will run the first time the WSL container is run

echo "Welcome to the OMNeT++ WSL distribution (opp_env)."
echo
echo "1) Install the latest version of OMNeT++ (opp_env install omnetpp-latest)"
echo "2) Install the latest version of INET Framework and OMNeT++ (opp_env install inet-latest)"
echo "3) Do not install anything for now."
echo
read -p "Please choose an option (1-3): " choice

case $choice in
    1)
        sudo --user opp_env -- /bin/bash -c 'cd ; source .profile ; opp_env install omnetpp-latest' || exit 1
        ;;
    2)
        sudo --user opp_env -- /bin/bash -c 'cd ; source .profile ; opp_env install inet-latest' || exit 1
        ;;
    *)
        echo "Models can be installed later using the 'opp_env install model-version' command."
        ;;
esac
