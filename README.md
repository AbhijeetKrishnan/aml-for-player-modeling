# Expertise Estimation
Code repository for Expertise Estimation paper

## Install FAMA
1. Clone their [repo](https://github.com/daineto/meta-planning)
2. Follow the installation instructions in their README

## Sokoban PDDL Domin
- Taken from the Potassco pddl-instances [repo](https://github.com/potassco/pddl-instances)
- File located [here](https://github.com/potassco/pddl-instances/blob/master/ipc-2011/domains/sokoban-sequential-satisficing/domain.pddl)
- All code related to action costs have been removed from the domain and instances
- The empty domain has been created from the original by removing the preconditions and effects for every action

## PUCRS PDDL Parser code
- Taken from their [repo](https://github.com/pucrs-automated-planning/pddl-parser)
- Uses the `PDDL.py` and `action.py` files

# Instructions for reproducing results
1. Install FAMA locally
2. Obtain the Potassco Sokoban PDDL domain
3. Convert the custom levels into PDDL instances using `./instances_gen levels instances`
4. Run FastDownward to generate the solution files for each instance using `./soln_file_gen.sh reference-sokoban.pddl instances solutions`
5. Generate trajectories for each solution using `./traj_file_gen.sh reference-sokoban.pddl instances solutions logs`
6. Run FAMA to obtain an action model for each trajectory using `./run_fama.py empty-sokoban.pddl logs models`
7. Run evaluation for each action model using `./trajectory/evaluation.py reference-sokoban.pddl [PATH/TO/MODEL]`