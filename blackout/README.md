
# To reproduce our results, run these commands in your preferred UNIX terminal:

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


