#!/bin/bash

# Script to generate valid PDDL problem files from level descriptions fitting the IPC 2011 Sokoban domain

# Usage: ./instance_gen.sh [LEVELS_FOLDER] [INSTANCES_FOLDER]
# e.g. ./instance_gen.sh levels instances

CONVERTER=./trajectory/converter.py

LEVELS=$1/*
INSTANCES=$2

level_regex="level-([0-9]+)\.lvl$"

for level in $LEVELS
do
    if [[ $level =~ $level_regex ]]
    then
        id_lvl=${BASH_REMATCH[1]}
        instance="${INSTANCES}/instance-${id_lvl}.pddl"
        echo "Converting ${level} to ${instance}"
        $CONVERTER $level > $instance
    fi
done