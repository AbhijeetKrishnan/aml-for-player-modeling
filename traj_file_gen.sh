#!/bin/bash

# Script to generate trajectory files from the solution files automatically by calling the parser engine

ENGINE=./trajectory/trajectory.py
DOMAIN=./domain.pddl
INSTANCES=./instances/*.pddl
SOLUTIONS=./solutions/*
LOGS=./logs

inst_regex="instance-([0-9]+)\.pddl$"
soln_regex="solution-([0-9]+)$"

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
                    log="${LOGS}/log-$id_soln"
                    echo python "$ENGINE" "$DOMAIN" "$instance" "$solution" "$log"
                    python "$ENGINE" "$DOMAIN" "$instance" "$solution" "$log"
                fi
            fi
        done
    fi
done