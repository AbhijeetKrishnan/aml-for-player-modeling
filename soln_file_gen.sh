#!/bin/bash

# Script to call FastDownward to generate a solution for all instances in a given folder

# Usage: ./soln_file_gen.sh [DOMAIN] [INSTANCES_FOLDER] [SOLUTIONS_FOLDER]
# e.g. ./soln_file_gen.sh domain-sokoban.pddl instances solutions

FAST_DOWNWARD=~/downward/fast-downward.py
FAST_DOWNWARD_ARGS="--alias lama-first" # uses lama-2011 alias to return the first solution found

DOMAIN=$1
INSTANCES=$2/*
SOLUTIONS=$3

inst_regex="instance-([0-9]+)\.pddl$"

for instance in $INSTANCES
do
    if [[ $instance =~ $inst_regex ]]
    then
        id_inst=${BASH_REMATCH[1]}
        solution="${SOLUTIONS}/solution-${id_inst}.soln"
        echo "$FAST_DOWNWARD" "$FAST_DOWNWARD_ARGS" "--plan-file" "$solution" "$DOMAIN" "$instance"
        $FAST_DOWNWARD $FAST_DOWNWARD_ARGS --plan-file $solution $DOMAIN $instance
    fi
done