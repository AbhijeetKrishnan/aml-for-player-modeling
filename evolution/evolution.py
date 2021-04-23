import os
import numpy
import helpers
import evaluation
import multiprocessing
from deap import base, creator, tools, algorithms
from evaluation import Mode

creator.create('F1Max', base.Fitness, weights=(1.0,))  # level evaluated by average F1 score
creator.create('Level', str, fitness=creator.F1Max)  # individual represented by level grid

def init_level():
    return creator.Level(helpers.init_level())

toolbox = base.Toolbox()
toolbox.register('level', lambda: creator.Level(helpers.init_level()))  # Lambda to turn str into Level object
toolbox.register('population', tools.initRepeat, list, toolbox.level)

# toolbox.register('evaluate', helpers.eval_level, eval=evaluation.eval_target,
#                  targets=[('push-to-nongoal', Mode.NEG_EFF, 'at-goal ?1stone'),
#                           ('move', Mode.POS_EFF, 'at ?0player ?2location'),
#                           ])
toolbox.register('evaluate', helpers.eval_level, eval=evaluation.eval_f1)
toolbox.register('select', tools.selTournament, tournsize=3)  # TODO selection method?

# helpers.crossover returns regular strs, so we need this
def mate(level1, level2):
    level1, level2 = helpers.crossover(level1, level2)
    return creator.Level(level1), creator.Level(level2)

toolbox.register('mate', mate)
toolbox.register('mutate', lambda a, prob: (creator.Level(helpers.mutate(a, prob)[0]),), prob=0.1)

# pool = multiprocessing.Pool()
# toolbox.register('map', pool.map)

pop = toolbox.population(n=10)
hof = tools.HallOfFame(1)
cxpb, mutpb = 0.5, 0.2

pop, log = algorithms.eaSimple(pop, toolbox, cxpb, mutpb, ngen=10, halloffame=hof, verbose=True)
# best = helpers.ea_until_target(pop, toolbox, cxpb, mutpb, tar=(1,), hof=hof)

print(f"Best level is:\n{hof[0]} ...with fitness {hof[0].fitness}")
# print(f"Best level is:\n{best} ...with fitness {best.fitness}")
