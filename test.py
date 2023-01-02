#!/usr/bin/env bash

rm -rf test-workspace
mkdir test-workspace
cd test-workspace
opp_env list
opp_env shell omnetpp-6.0
