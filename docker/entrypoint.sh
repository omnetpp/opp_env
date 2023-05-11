#!/bin/bash
set -e

# Source .profile so all commands have a proper environment
# (by default docker does not source the initialization files on shells)
if [ -e $HOME/.profile ]; then
 source $HOME/.profile;
fi

# Execute the command passed to the container
exec "$@"
