# Towards Action Model Learning for Player Moeling
Code repository for Toward Action Model Learning for Player Modeling by Abhijeet Krishnan, Aaron Williams and Dr. Chris Martens

# Feasibility Evaluation
In this, we show that AML is a feasible approach to player modeling by successfully learning a player model using AML

## Install FAMA
1. Clone their [repo](https://github.com/daineto/meta-planning)
2. Follow the installation instructions in their README

## Sokoban PDDL Domain
- Taken from the Potassco pddl-instances [repo](https://github.com/potassco/pddl-instances)
- File located [here](https://github.com/potassco/pddl-instances/blob/master/ipc-2011/domains/sokoban-sequential-satisficing/domain.pddl)
- All code related to action costs have been removed from the domain and instances
- The empty domain has been created from the original by removing the preconditions and effects for every action

## PUCRS PDDL Parser code
- Taken from their [repo](https://github.com/pucrs-automated-planning/pddl-parser)
- Uses the `PDDL.py` and `action.py` files

## Instructions for reproducing results
1. Install FAMA locally
2. Obtain the Potassco Sokoban PDDL domain
3. Convert the custom levels into PDDL instances using `./instances_gen levels instances`
4. Run FastDownward to generate the solution files for each instance using `./soln_file_gen.sh reference-sokoban.pddl instances solutions`
5. Generate trajectories for each solution using `./traj_file_gen.sh reference-sokoban.pddl instances solutions logs`
6. Run FAMA to obtain an action model for each trajectory using `./run_fama.py empty-sokoban.pddl logs models`

# Usefulness Evaluation
In this, we show that AML is a useful approach to player modeling by quantifying player skill using a learned player model

## Instructions for reproducing results
1. Learn a player model following the steps in the feasibility evaluation
2 . Run evaluation for each action model using `./trajectory/evaluation.py reference-sokoban.pddl [PATH/TO/MODEL]`

# Domain-agnosticity Evaluation
In this, we show that AML is a domain-agnostic approach to player modeling by successfully learning player models in two different domains

## Instructions for reproducing results
1. Repeat step 6 in the feasibility evaluation but replace `*-sokoban.pddl` with `*-hanoi.pddl` and `*-npuzzle.pddl` in two separate runs
2. Use the first two trajectories (`trajectory-00` and `trajectory-01`) in the [FAMA evaluation dataset](https://github.com/daineto/meta-planning/tree/master/src/meta_planning/dataset) corresponding to these two domains as test trajectories

# Comparing Blackout and FAMA for Player Modeling
In this, we compare Blackout, our novel algorithm for AML, with FAMA, a SOTA algorithm for AML, for their suitability to player modeling

## Learned Model Evaluation
1. Locate the instances L1, L2 and L3 under `blackout/trajectory` as `small-*.pddl`, `medium-*.pddl` and `large-*.pddl` respectively (the verbose variants contained failed actions which only Blackout can use)
2. Learn 3 models using FAMA following the steps in the feasibility evaluation
3. Learn 3 models using Blackout following the steps below for each of L1, L2 and L3 -
    1. Run Blackout stage 1 using `python blackout1.py trajectory/[size]-verbose.log model/[size]-blackout-1.pddl sokoban-sequential`
    2. Run Blackout stage 2 using `python blackout2.py trajectory/[size]-verbose.log model/[size]-blackout-2.pddl sokoban-sequential`
    3. Run Blackout stage 3 using `python blackout3.py trajectory/[size]-verbose.log model/[size]-blackout-3.pddl sokoban-sequential`
4. Run the evaluation script to obtain precision and recall values for each learned model using `python evaluation.py reference-sokoban.pddl path/to/model`

## Performance Evaluation
The evaluation procedure is described in sufficient detail in the paper for reproducibility