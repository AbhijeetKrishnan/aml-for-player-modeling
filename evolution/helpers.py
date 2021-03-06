import os
import random
import tempfile
from deap import tools, algorithms
from library import *
from pddl_problem import PddlProblem

BLOCKS_X = 4
BLOCKS_Y = 4
BLOCK_WIDTH = 2
BLOCK_HEIGHT = 2
WIDTH = BLOCKS_X * BLOCK_WIDTH
HEIGHT = BLOCKS_Y * BLOCK_HEIGHT
NUM_STONES = 3

def choose(x, y, player, stones, goals):
    if y == 0:
        if x == 0:
            lib = lib_top_left
        elif x == BLOCKS_X - 1:
            lib = lib_top_right
        else:
            lib = lib_top
    elif y == BLOCKS_Y - 1:
        if x == 0:
            lib = lib_bottom_left
        elif x == BLOCKS_X - 1:
            lib = lib_bottom_right
        else:
            lib = lib_bottom
    else:
        if x == 0:
            lib = lib_left
        elif x == BLOCKS_X - 1:
            lib = lib_right
        else:
            lib = lib_center()

    choices = lib
    if player:
        choices = list(filter(lambda item: '@' not in item, choices))
    if stones >= NUM_STONES:
        choices = list(filter(lambda item: '$' not in item, choices))
    if goals >= NUM_STONES:
        choices = list(filter(lambda item: '.' not in item, choices))

    return random.choice(choices)


def init_level():
    # w = random.randint(3, 10)  # FIXME
    # h = random.randint(3, 10)

    grid = [['' for _ in range(BLOCKS_Y)] for _ in range(BLOCKS_X)]
    valid = False
    while not valid:
        player = False  # Has the player been placed yet?
        stones = 0
        goals = 0

        for y in range(BLOCKS_Y):
            for x in range(BLOCKS_X):
                block = choose(x, y, player, stones, goals)
                grid[x][y] = block
                for char in block:
                    if char == '@':
                        player = True
                    if char == '$':
                        stones += 1
                    if char == '.':
                        goals += 1

        # Sanity check: is there a player and are there an equal number of stones and goals?
        if player and stones == NUM_STONES and goals == NUM_STONES:
            valid = True
        else:  # Reset
            grid = [['' for _ in range(BLOCKS_Y)] for _ in range(BLOCKS_X)]

    level_str = ""
    for y in range(BLOCKS_Y):
        for sub_y in range(BLOCK_HEIGHT):
            for x in range(BLOCKS_X):
                block = grid[x][y]
                lines = block.split('\n')
                level_str += lines[sub_y]
            level_str += '\n'

    return level_str

def eval_level(level, eval, **kwargs):
    print(level)

    temp_prob = tempfile.mkstemp()[1]
    temp_soln = tempfile.mkstemp()[1]
    temp_traj = tempfile.mkstemp()[1]
    temp_model = tempfile.mkstemp()[1]

    pddl_problem = PddlProblem(level)

    # This outputs the PDDL problem to a temporary file
    esc_dollar = '\\$'  # This probably isn't necessary, but just to be safe
    echo_command = f'echo "{str(pddl_problem).replace("$", esc_dollar)}" > {temp_prob}'
    # print(echo_command)
    os.system(echo_command)

    # This runs FastDownward on the PDDL problem
    # The console output is dumped in /dev/null
    downward_command = f"~/downward/fast-downward.py --alias lama-first --plan-file {temp_soln} " \
                       f"../reference-sokoban.pddl {temp_prob} > /dev/null"
    print(downward_command)
    os.system(downward_command)
    if not os.path.isfile(temp_soln):  # If no solution, score is 0
        return 0,

    # This runs the trajectory generator on the PDDL problem and the solution
    traj_command = f"../trajectory/trajectory.py ../reference-sokoban.pddl {temp_prob} {temp_soln} > {temp_traj}"
    print(traj_command)
    os.system(traj_command)

    # This runs Blackout with the trajectory
    # The console output, including the time stuff, is dumped in /dev/null
    blackout_command = f"../blackout/blackout3.py {temp_traj} {temp_model} ../blackout/sokoban-sequential.pddl " \
                       f"> /dev/null 2> /dev/null"
    print(blackout_command)
    os.system(blackout_command)

    scores = eval(temp_model, **kwargs)

    # Clean up
    os.remove(temp_prob)
    os.remove(temp_soln)
    os.remove(temp_traj)
    os.remove(temp_model)

    return scores

# Crossover two levels on either the x or y axis
def crossover(level1, level2):
    # Column-major order so [x][y] coordinates will work
    grid1 = [[' ' for _ in range(HEIGHT)] for _ in range(WIDTH)]
    grid2 = [[' ' for _ in range(HEIGHT)] for _ in range(WIDTH)]

    lines = level1.split('\n')[:-1]  # The newline at the end creates an extra line
    for y in range(HEIGHT):
        line = lines[y]
        for x in range(WIDTH):
            char = line[x]
            grid1[x][y] = char

    lines = level2.split('\n')[:-1]  # The newline at the end creates an extra line
    for y in range(HEIGHT):
        line = lines[y]
        for x in range(WIDTH):
            char = line[x]
            grid2[x][y] = char

    grid1, grid2 = cx_two_point_2d(grid1, grid2)
    grid1 = check_crossover(grid1)
    grid2 = check_crossover(grid2)

    level1 = ""
    level2 = ""
    for y in range(HEIGHT):
        for x in range(WIDTH):
            level1 += grid1[x][y]
        level1 += '\n'

    for y in range(HEIGHT):
        for x in range(WIDTH):
            level2 += grid2[x][y]
        level2 += '\n'

    return level1, level2

def cx_two_point_2d(grid1, grid2):
    cx_on_x_axis = True if random.random() < 0.5 else False
    if cx_on_x_axis:
        grid1, grid2 = tools.cxTwoPoint(grid1, grid2)
    else:
        cx1 = random.randint(1, WIDTH)
        cx2 = random.randint(1, WIDTH - 1)
        if cx2 >= cx1:
            cx2 += 1
        else:
            cx1, cx2 = cx2, cx1

        for x in range(WIDTH):
            grid1[x][cx1:cx2], grid2[x][cx1:cx2] = grid2[x][cx1:cx2], grid1[x][cx1:cx2]

    return grid1, grid2

# Make sure an offspring level has exactly one player and as many stones as goals
def check_crossover(grid):
    # Count players, stones and goals
    # If there is more than one player, remove extra ones
    player = False
    stones = 0
    goals = 0
    for x in range(WIDTH):
        for y in range(HEIGHT):
            char = grid[x][y]
            if char == '@':
                if player:
                    grid[x][y] = ' '
                else:
                    player = True
            elif char == '%':
                if player:
                    grid[x][y] = '.'
                else:
                    player = True
                goals += 1
            elif char in '$*':
                stones += 1
            elif char in '.*':
                goals += 1

    # If there is no player, place one in the first empty space available
    # It is extremely unlikely that there will be no empty space, and such a level wouldn't be solvable anyway
    # If there are extra goals or stones, remove some until the number is equal
    if not player or stones != goals:
        for x in range(WIDTH):
            for y in range(HEIGHT):
                char = grid[x][y]
                if char == ' ':
                    if not player:
                        grid[x][y] = '@'
                        player = True
                    elif stones == 0:
                        grid[x][y] = '$'
                        stones += 1
                    elif goals == 0:
                        grid[x][y] = '.'
                        goals += 1
                elif char == '$' and stones > goals:
                    grid[x][y] = ' '
                    stones -= 1
                elif char == '.' and goals > stones:
                    grid[x][y] = ' '
                    goals -= 1
                elif char == '%' and goals > stones:
                    grid[x][y] = '@'
                    goals -= 1

    return grid

# Switch random walls and open spaces
def mutate(level, prob):
    for i in range(WIDTH, len(level) - (WIDTH + 1)):  # Skip the top and bottom
        if level[i-1] == '\n' or level[i+1] == '\n':  # Skip the left and right edges
            continue

        if random.random() < prob:
            if level[i] == ' ':
                level = level[:i] + '#' + level[i+1:]
            elif level[i] == '#':
                level = level[:i] + ' ' + level[i+1:]

    return level,

def ea_until_target(pop, toolbox, cxpb, mutpb, tar, hof):
    fitnesses = toolbox.map(toolbox.evaluate, pop)
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    for ind in pop:
        if ind.fitness.values[0] == 1:
            hof.insert(ind)
            return ind

    while True:
        pop = toolbox.select(pop, k=len(pop))
        pop = algorithms.varAnd(pop, toolbox, cxpb, mutpb)

        invalids = [ind for ind in pop if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalids)
        for ind, fit in zip(invalids, fitnesses):
            ind.fitness.values = fit

        for ind in pop:
            if ind.fitness.values == tar:
                hof.insert(ind)
                return ind
