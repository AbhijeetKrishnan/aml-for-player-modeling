#!/usr/bin/env python

from PDDL import PDDL_Parser
from planner import Planner
from action import Action

import datetime
# from pynput import keyboard

# def on_press(key):
#     try:
#         print('alphanumeric key {0} pressed'.format(
#             key.char))
#     except AttributeError:
#         print('special key {0} pressed'.format(
#             key))

# def on_release(key):
#     print('{0} released'.format(
#         key))
#     if key == keyboard.Key.esc:
#         # Stop listener
#         return False

# # Collect events until released
# # with keyboard.Listener(
# #         on_press=on_press,
# #         on_release=on_release) as listener:
# #     listener.join()

# # ...or, in a non-blocking fashion:
# listener = keyboard.Listener(
#     on_press=on_press,
#     on_release=on_release)
# listener.start()
# listener.join

class Engine:

    # Params:
    #   domain: Name of domain file; should be 'soko3/soko3/pddl'
    #   problem: Name of problem file encoding the level to be played, e.g. soko3/levelp3.pddl
    #   logfile: Name of file the trajectory should be written to; defaults to /dev/null
    #   verbose: If true, will write restarts, undoes, and failed moves to the trajectory file
    def __init__(self, domain, problem, logfile='/dev/null', verbose=False):
        # Parser
        self.parser = PDDL_Parser()
        self.parser.parse_domain(domain)
        self.parser.parse_problem(problem)
        # Parsed data
        self.state = self.parser.state
        self.goal_pos = self.parser.positive_goals
        self.goal_not = self.parser.negative_goals

        self.history = []
        self.movelog = []

        self.logfile = logfile
        self.verbose = verbose

        self.planner = Planner()
        # Do nothing
        if self.planner.applicable(self.state, self.goal_pos, self.goal_not):
            print('Puzzle is already solved! Double-check your problem file!')

    def parseCellName(self, cellName):
        _, x, y = cellName.split('-')
        # print(cellName)
        # print(out)
        return int(x), int(y)

    def findPlayer(self):
        for pred in self.state:
            if pred[0] == 'at' and pred[1] == 'player-01':
                return self.parseCellName(pred[2])
        raise ValueError('Player not found!')

    def formatPos(self, coords):
        return 'pos-{:02}-{:02}'.format(coords[0], coords[1])

    def groundAction(self, act, assignment):
        variables = []
        for v, _ in act.parameters:
            variables.append(v)
        pps = act.replace(act.positive_preconditions, variables, assignment)
        nps = act.replace(act.negative_preconditions, variables, assignment)
        aes = act.replace(act.add_effects, variables, assignment)
        des = act.replace(act.del_effects, variables, assignment)
        return Action(act.name, assignment, pps, nps, aes, des)

    def addVec(self, *vecs):
        x = 0
        y = 0
        for u, v in vecs:
            x += u
            y += v
        return (x, y)

    # act must already be grounded (e.g. by self.groundAction)
    def tryAction(self, act, log):
        # print(self.state)
        # print(act.positive_preconditions)
        # print(act.negative_preconditions)
        # print(self.planner.applicable(self.state, act.positive_preconditions, act.negative_preconditions))
        if self.planner.applicable(self.state, act.positive_preconditions, act.negative_preconditions):
            success = True
            suffix = ''
        else:
            success = False
            suffix = '-failed'
        if success or self.verbose:
            # log.write(str(self.state) + '\n')
            # log.write(str(act))
            print('Action: {} {}'.format(act.name, act.parameters))
            try:
                act_str = '(:action{} ({}))'.format(suffix, ' '.join([act.name, *act.parameters]))
                if success:
                    self.history.append(self.state)
                    self.state = self.planner.apply(self.state, act.add_effects, act.del_effects)
                # log.write(self.lispState() + '\n\n')
                self.movelog.append('{}\n\n{}\n\n'.format(act_str, self.lispState()))
            except TypeError:
                # Tried to move or push a boulder off the grid or into a wall (in sokoban-sequential, those are the same thing).
                # This can only be a failed action, but trying to log it crashes this script (hence this try-except block), and would cause problems for trajectory.py down the line.
                # So, don't attempt to log this action.
                # This might come back to bite me later, but I'll cross that bridge when I get there.
                pass
        return success

    def lookupAction(self, actName):
        for act in self.parser.actions:
            if act.name == actName:
                return act
        return None

    # Finds the next cell adjacent to curCell in direction direc
    def findNextCell(self, curCell, direc):
        for cell in self.parser.objects['location']:
            if self.planner.applicable(self.state, [['move-dir', curCell, cell, direc]], []):
                return cell
        return None

    def getStone(self, cell):
        for stone in self.parser.objects['stone']:
            if self.planner.applicable(self.state, [['at', stone, cell]], []):
                return stone
        return None

    def doMove(self, key, log):
        direc = None
        if key == 'u':
            if len(self.history) >= 1:
                self.state = self.history.pop()
                if self.verbose:
                    self.movelog.append('(:undo)\n\n{}\n\n'.format(self.lispState()))
                else:
                    self.movelog.pop()
            return True
        elif key == 'r':
            self.state = self.parser.state
            # self.history.append(self.state)
            self.history = [self.state]
            if self.verbose:
                self.movelog.append('(:restart)\n\n{}\n\n'.format(self.lispState()))
            else:
                self.movelog = []
            return True
        elif key == 'w':
            direc = 'dir-up'
        elif key == 's':
            direc = 'dir-down'
        elif key == 'a':
            direc = 'dir-left'
        elif key == 'd':
            direc = 'dir-right'
        else:
            # log.write('Unparseable input: {}\n\n'.format(key))
            return False
        # print(key, delta, actions)
        playerPos = self.findPlayer()
        # print(key, currentCell)

        # Put player's cell, next cell, and cell after in a list
        cells = [self.formatPos(playerPos)]
        cells.append(self.findNextCell(cells[0], direc))
        cells.append(self.findNextCell(cells[1], direc))

        # Try move action
        assignment = ['player-01']
        assignment.extend(cells[0:2])
        assignment.append(direc)
        gact = self.groundAction(self.lookupAction('move'), assignment)
        if self.tryAction(gact, log):
            return True
        # If that failed, try push-to-nongoal
        assignment.insert(1, self.getStone(cells[1]))
        assignment.insert(4, cells[2])
        gact = self.groundAction(self.lookupAction('push-to-goal'), assignment)
        if self.tryAction(gact, log):
            return True
        # And if that failed, try push-to-goal
        gact = self.groundAction(self.lookupAction('push-to-nongoal'), assignment)
        if self.tryAction(gact, log):
            return True
        return False

        # for act in self.parser.actions:
        #     currentCell = self.formatPos(playerPos)
        #     assignment = [key]
        #     while len(assignment) < len(act.parameters):
        #         assignment.append(currentCell)
        #         currentCell = self.findNextCell(currentCell, key)    # Having to do this for every cell parameter in every action is inefficient; maybe improve later?
        #     gact = self.groundAction(act, assignment)
        #     # print(gact)
        #     if self.tryAction(gact, log):
        #         return True
        # return False

        # nextCell = self.formatPos(self.addVec(playerPos, delta))
        # afterCell = self.formatPos(self.addVec(playerPos, delta, delta))
        # # print(playerPos, playerCell, nextCell, afterCell)
        # act = self.lookupAction(actions[0])
        # gact = self.groundAction(act, [playerCell, nextCell])
        # # print(gact)
        # if self.tryAction(gact, log):
        #     return True
        # else:
        #     act = self.lookupAction(actions[1])
        #     gact = self.groundAction(act, [playerCell, nextCell, afterCell])
        #     # print(gact)
        #     if self.tryAction(gact, log):
        #         return True
        # # log.write('Blocked move: {}\n\n'.format(actions))
        # return False

    predIDs = {'wall'   : 1,
            'player'    : 2,
            'ball'      : 4,
            'pit'       : 8,
            'goal'      : 16}

    tiles = {0: '  ',   # Floor
             1: '[]',   # Wall
             2: ':)',   # Player
             4: '()',   # Boulder
             8: '\/',   # Pit
            16: '//',   # Goal
            18: '%)',   # Goal and player
            20: '{}'}   # Goal and boulder

    nonwalls = set()

    def findNonWalls(self):
        for pred in self.state:
            # print('Checking {}'.format(pred))
            if pred[0] == 'move-dir':
                self.nonwalls.add(pred[1])
                self.nonwalls.add(pred[2])

    def renderCell(self, cell):
        if cell not in self.nonwalls:
            return '[]'
        elif self.formatPos(self.findPlayer()) == cell:
            if self.planner.applicable(self.state, [['is-goal', cell]], []):
                return '%)'
            else:
                return ':)'
        elif self.getStone(cell) is not None:
            if self.planner.applicable(self.state, [['is-goal', cell]], []):
                return '{}'
            else:
                return '()'
        else:
            if self.planner.applicable(self.state, [['is-goal', cell]], []):
                return '//'
            else:
                return '  '

    def render(self):
        w, h = 0, 0
        for cell in self.parser.objects['location']:
            x, y = self.parseCellName(cell)
            w = max(w, x+1)
            h = max(h, y+1)
        for y in range(1, h):
            for x in range(1, w):
                cell = self.formatPos((x, y))
                # code = 0
                # # print(cell)
                # # print(self.state)
                # for pred, pid in self.predIDs.items():
                #     if self.planner.applicable(self.state, [[pred, cell]], []):
                #         code += pid
                # if self.planner.applicable(self.goal_pos, [['ball', cell]], []):
                #     code += self.predIDs['goal']
                print(self.renderCell(cell), end='')
                # if self.planner.applicable(self.state, [['wall', cell]], []):
                #     code = -1
                # else:
                #     if self.planner.applicable(self.state, [['floor', cell]], []):
                #         code = 1
                #     if self.planner.applicable(self.state, [['ball', cell]], []):
                #         code += 2
                #     if self.planner.applicable(self.goal_pos, [['ball', cell]], []):
                #         code += 4
                #     if self.planner.applicable(self.state, [['player', cell]], []):
                #         code += 8
            print()

    def lispState(self, word=':state'):
        out = []
        out.append('({}'.format(word))
        for pred in self.state:
            out.append(' (')
            out.append(' '.join(pred))
            out.append(')')
        out.append(')')
        return ''.join(out)

    def gameloop(self):
        with open(self.logfile, 'w') as log:
            # log.write('{}\n\n'.format(datetime.datetime.now()))
            log.write('(trajectory\n\n')
            log.write('(:objects ')
            for t, os in self.parser.objects.items():
                for o in os:
                    log.write('{} -  {} '.format(o, t))
            log.write(')\n\n')
            log.write(self.lispState(':init'))
            log.write('\n\n')
            self.findNonWalls()
            while True:
                self.render()
                if self.planner.applicable(self.state, self.goal_pos, self.goal_not):
                    print('Winningness!')
                    log.write(''.join(self.movelog))
                    log.write(')')
                    return
                prevTime = time.time()
                key = input('Choose direction (wasdur, followed by Enter): ')
                # log.write('{}\n\n'.format(time.time() - prevTime))
                self.doMove(key, log)


# ==========================================
# Main
# ==========================================
if __name__ == '__main__':
    import sys, time
    start_time = time.time()
    domain = sys.argv[1]
    problem = sys.argv[2]
    try:
        logfile = sys.argv[3]
    except IndexError:
        logfile = '/dev/null'
    if len(sys.argv) > 4 and sys.argv[4] == '--verbose':
        verbose = True
    else:
        verbose = False
    engine = Engine(domain, problem, logfile, verbose=verbose)
    engine.gameloop()
    print('Time: ' + str(time.time() - start_time) + 's')
    # if plan:
    #     print('plan:')
    #     for act in plan:
    #         print(act)
    # else:
    #     print('No plan was found')



