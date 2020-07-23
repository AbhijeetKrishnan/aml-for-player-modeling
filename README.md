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

## Performance Evaluation

The evaluation procedure is described in sufficient detail in the paper for reproducibility

cd blackout
 # Remove the :action-failed lines and whatnot from the trajectory files, so FAMA can use them
cd trajectory
python strip-verbose.py small-verbose.log small-brief.log
python strip-verbose.py medium-verbose.log medium-brief.log
python strip-verbose.py large-verbose.log large-brief.log
cd ..
 # Run blackout
python blackout1.py trajectory/small-verbose.log model/small-blackout-1.pddl sokoban-sequential
python blackout2.py trajectory/small-verbose.log model/small-blackout-2.pddl sokoban-sequential
python blackout3.py trajectory/small-verbose.log model/small-blackout-3.pddl sokoban-sequential
python blackout1.py trajectory/medium-verbose.log model/medium-blackout-1.pddl sokoban-sequential
python blackout2.py trajectory/medium-verbose.log model/medium-blackout-2.pddl sokoban-sequential
python blackout3.py trajectory/medium-verbose.log model/medium-blackout-3.pddl sokoban-sequential
python blackout1.py trajectory/large-verbose.log model/large-blackout-1.pddl sokoban-sequential
python blackout2.py trajectory/large-verbose.log model/large-blackout-2.pddl sokoban-sequential
python blackout3.py trajectory/large-verbose.log model/large-blackout-3.pddl sokoban-sequential
 # Run FAMA
 ##TODO insert commands to run FAMA on trajectory/small-brief.log and trajectory/medium-brief.log
 ## and put the results in model/small-FAMA.pddl and model/medium-FAMA.pddl
 ## here
 # Run evaluation script
cd ../trajectory
python evaluation.py ../blackout/sokoban-sequential.pddl ../blackout/model/small-blackout-1.pddl
python evaluation.py ../blackout/sokoban-sequential.pddl ../blackout/model/small-blackout-2.pddl
python evaluation.py ../blackout/sokoban-sequential.pddl ../blackout/model/small-blackout-3.pddl
python evaluation.py ../blackout/sokoban-sequential.pddl ../blackout/model/small-FAMA.pddl
python evaluation.py ../blackout/sokoban-sequential.pddl ../blackout/model/medium-blackout-1.pddl
python evaluation.py ../blackout/sokoban-sequential.pddl ../blackout/model/medium-blackout-2.pddl
python evaluation.py ../blackout/sokoban-sequential.pddl ../blackout/model/medium-blackout-3.pddl
python evaluation.py ../blackout/sokoban-sequential.pddl ../blackout/model/medium-FAMA.pddl
python evaluation.py ../blackout/sokoban-sequential.pddl ../blackout/model/large-blackout-1.pddl
python evaluation.py ../blackout/sokoban-sequential.pddl ../blackout/model/large-blackout-2.pddl
python evaluation.py ../blackout/sokoban-sequential.pddl ../blackout/model/large-blackout-3.pddl

