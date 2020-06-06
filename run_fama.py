#!/usr/bin/env python

# Usage: ./run_fama.py [EMPTY_DOMAIN] [LOGS_FOLDER] [MODELS_FOLDER]
# e.g. ./run_fama.py empty-sokoban.pddl logs models

import sys, os

from meta_planning.parsers import parse_trajectory, parse_model
from meta_planning import LearningTask
from meta_planning.evaluation import SynEvaluator

model = sys.argv[1]
log = sys.argv[2]
# models_folder = sys.argv[3]

# Define the initial model
M = parse_model(model)

# Define the set of trajectories, observations
#for log in os.listdir(logs_folder):
#    print('Generating trajectory for', log)
#    id = log.split('.')[0].split('-')[1]

T = [parse_trajectory(log, M)]

O = [t.observe(1, action_observability=1) for t in T]

# Create learning task
lt = LearningTask(M, O)

solution = lt.learn()
id = 1
try:
    print(solution.learned_model)
    #with open(os.path.join(models_folder, f'model-{id}.pddl'), 'w') as model:
    #    model.write(str(solution.learned_model))
except AttributeError:
    print('No solution found')