#!/bin/bash

# Script to generate trajectory files from the solution files automatically by calling the parser engine

# Usage: ./traj_file_gen.sh [DOMAIN_FILE] [INSTANCES_FOLDER] [SOLUTIONS_FOLDER] [LOGS_FOLDER]
# e.g. ./traj_file_gen.sh reference-sokoban.pddl instances solutions logs

ENGINE=./trajectory/trajectory.py
DOMAIN=$1
INSTANCES=$2/*.pddl
SOLUTIONS=$3/*
LOGS=$4

inst_regex="instance-([0-9]+)\.pddl$"
soln_regex="solution-([0-9]+)\.soln$"

for instance in $INSTANCES
do
    if [[ $instance =~ $inst_regex ]]
    then
        id_inst=${BASH_REMATCH[1]}
        for solution in $SOLUTIONS
        do
            if [[ $solution =~ $soln_regex ]]
            then
                id_soln=${BASH_REMATCH[1]}
                if [ "$id_inst" == "$id_soln" ]
                then
                    echo $instance $solution
                    log="${LOGS}/log-$id_soln.log"
                    echo python "$ENGINE" "$DOMAIN" "$instance" "$solution" "$log"
                    python "$ENGINE" "$DOMAIN" "$instance" "$solution" > "$log"
                fi
            fi
        done
    fi
done