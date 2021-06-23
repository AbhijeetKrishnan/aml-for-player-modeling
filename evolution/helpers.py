import os
import random
import signal
import subprocess
import tempfile
from deap import tools, algorithms
from library import *
from pddl_problem import PddlProblem

BLOCK_WIDTH = 2
BLOCK_HEIGHT = 2
NUM_STONES = 3

def choose(x, y, player, width, height, stones, goals):
    if y == 0:
        if x == 0:
            lib = lib_top_left
        elif x == width - 1:
            lib = lib_top_right
        else:
            lib = lib_top
    elif y == height - 1:
        if x == 0:
            lib = lib_bottom_left
        elif x == width - 1:
            lib = lib_bottom_right
        else:
            lib = lib_bottom
    else:
        if x == 0:
            lib = lib_left
        elif x == width - 1:
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
    blocks_x = random.randint(3, 5)
    blocks_y = 3  # Has to be fixed for crossover to work

    grid = [['' for _ in range(blocks_y)] for _ in range(blocks_x)]
    valid = False
    while not valid:
        player = False  # Has the player been placed yet?
        stones = 0
        goals = 0

        for y in range(blocks_y):
            for x in range(blocks_x):
                block = choose(x, y, player, blocks_x, blocks_y, stones, goals)
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
            grid = [['' for _ in range(blocks_y)] for _ in range(blocks_x)]

    level_str = ""
    for y in range(blocks_y):
        for sub_y in range(BLOCK_HEIGHT):
            for x in range(blocks_x):
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
    # Note that we're using subprocess.run here, so the command is a list
    downward_args = ['../downward/fast-downward.py', '--alias', 'lama-first', '--plan-file', temp_soln,
                     '../reference-sokoban.pddl', temp_prob]
    print(downward_args)

    with open('/dev/null', 'w') as null:
        try:
            subprocess.run(downward_args, stdout=null, timeout=5)
        except subprocess.TimeoutExpired:
            return 0,  # Fitness is 0 if solver times out
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
    lines1 = level1.split('\n')[:-1]  # The newline at the end creates an extra line
    lines2 = level2.split('\n')[:-1]

    height1 = len(lines1)
    width1 = len(lines1[0])
    height2 = len(lines2)
    width2 = len(lines2[0])

    # Column-major order so [x][y] coordinates will work
    grid1 = [[' ' for _ in range(height1)] for _ in range(width1)]
    grid2 = [[' ' for _ in range(height2)] for _ in range(width2)]

    for y in range(height1):
        line = lines1[y]
        for x in range(width1):
            char = line[x]
            grid1[x][y] = char
    for y in range(height2):
        line = lines2[y]
        for x in range(width2):
            char = line[x]
            grid2[x][y] = char

    grid1, grid2 = cx_two_point_2d(grid1, grid2)
    grid1 = check_crossover(grid1)
    grid2 = check_crossover(grid2)

    width1 = len(grid1)  # Dimensions might have changed
    height1 = len(grid1[0])
    width2 = len(grid2)
    height2 = len(grid2[0])

    level1 = ""
    level2 = ""
    for y in range(height1):
        for x in range(width1):
            level1 += grid1[x][y]
        level1 += '\n'
    for y in range(height2):
        for x in range(width2):
            level2 += grid2[x][y]
        level2 += '\n'

    return level1, level2

# Can't make crossover with variable lengths work, so just crossing over columns for now
def cx_two_point_2d(grid1, grid2):
    max_idx = len(grid1) - 1
    cx11 = random.randint(1, max_idx)
    cx12 = random.randint(1, max_idx - 1)
    if cx12 >= cx11:
        cx12 += 1
    else:
        cx11, cx12 = cx12, cx11

    max_idx = len(grid2) - 1
    cx21 = random.randint(1, max_idx)
    cx22 = random.randint(1, max_idx - 1)
    if cx22 >= cx21:
        cx22 += 1
    else:
        cx21, cx22 = cx22, cx21

    grid1[cx11:cx12], grid2[cx21:cx22] = grid2[cx21:cx22], grid1[cx11:cx12]

    return grid1, grid2

# Make sure an offspring level has exactly one player and as many stones as goals
def check_crossover(grid):
    width = len(grid)
    height = len(grid[0])

    # Count players, stones and goals
    # If there is more than one player, remove extra ones
    player = False
    stones = 0
    goals = 0
    for x in range(width):
        for y in range(height):
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
        for x in range(width):
            for y in range(height):
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
    width = level.index('\n')
    for i in range(width, len(level) - (width + 1)):  # Skip the top and bottom
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
