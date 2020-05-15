#!/usr/bin/env python

from collections import defaultdict

class PDDL_Problem:

    def __init__(self, level_file):
        self.problem_name = f'{level_file}'
        self.domain_name = 'sokoban-sequential'
        self.objects = defaultdict(list)
        self.state = []
        self.positive_goals = []
        self.negative_goals = []
        self.grid = None

        self.objects['direction'] = ['dir-down', 'dir-left', 'dir-right', 'dir-up']

        player_cnt = 1 # never more than 1 player in practice, but kept to be similar to stone_cnt
        stone_cnt = 1

        with open(level_file) as level:
            grid = []
            lines = level.readlines()
            for row in lines:
                row = row.strip('\n')
                if row and row[0] != ';': # ignore empty lines (only '\n') and comments
                    grid.append([row[i:i+1] for i in range(0, len(row), 1)])
            width, height = len(grid[0]), len(grid)
            self.grid = grid

            for j in range(height):
                for i in range(width):
                    symbol = grid[j][i]
                    pos = f'pos-{i+1:02}-{j+1:02}' # rows and cols are 1-indexed
                    self.objects['location'].append(pos)
                    if symbol == '#': # wall
                        self.state.append(['IS-NONGOAL', pos])
                    elif symbol == '.': # goal
                        self.state.append(['IS-GOAL', pos])
                        self.state.append(['clear', pos])
                    elif symbol == '*': # stone on goal
                        stone = f'stone-{stone_cnt:02}'
                        self.objects['stone'].append(stone)
                        self.state.append(['IS-GOAL', pos])
                        self.state.append(['at', stone, pos])
                        self.state.append(['at-goal', stone])
                        stone_cnt += 1
                    elif symbol == '$': # stone
                        stone = f'stone-{stone_cnt:02}'
                        self.objects['stone'].append(stone)
                        self.state.append(['IS-NONGOAL', pos])
                        self.state.append(['at', stone, pos])
                        stone_cnt += 1
                    elif symbol == '@': # player
                        player = f'player-{player_cnt:02}'
                        self.objects['player'].append(player)
                        self.state.append(['IS-NONGOAL', pos])
                        self.state.append(['at', player, pos])
                        player_cnt += 1
                    elif symbol == '%': # player on goal
                        player = f'player-{player_cnt:02}'
                        self.objects['player'].append(player)
                        self.state.append(['at', player, pos])
                        self.state.append(['IS-GOAL', pos])
                        player_cnt += 1
                    else:
                        self.state.append(['IS-NONGOAL', pos])
                        self.state.append(['clear', pos])

            for j in range(height):
                for i in range(width):
                    old_pos = f'pos-{i+1:02}-{j+1:02}'
                    for del_j, del_i, dir in [(1, 0, 'dir-down'), (0, -1, 'dir-left'), (0, 1, 'dir-right'), (-1, 0, 'dir-up')]:
                        new_i, new_j = i + del_i, j + del_j
                        if 0 <= new_i < width and 0 <= new_j < height and grid[j][i] != '#' and grid[new_j][new_i] != '#':
                            new_pos = f'pos-{new_i+1:02}-{new_j+1:02}'
                            self.state.append(['MOVE-DIR', old_pos, new_pos, dir])
            for i in range(1, stone_cnt):
                self.positive_goals.append(['at-goal', f'stone-{i:02}'])

    def __str__(self):
        NL = '\n' # '\' not permitted in f-strings
        NL_IND = '\n    '
        return f"""{NL.join([';; ' + ''.join(row) for row in self.grid])}

(define (problem {self.problem_name})
  (:domain {self.domain_name})

  (:objects 
    {NL_IND.join([NL_IND.join([f'{value} - {key}' for value in values]) for key, values in self.objects.items()])}
  )
  
  (:init 
    {NL_IND.join(['(' + ' '.join(predicate) + ')' for predicate in sorted(self.state)])}
  )

  (:goal (and
    {NL_IND.join(['(' + ' '.join(predicate) + ')' for predicate in self.positive_goals + self.negative_goals])}
  ))
)"""

if __name__ == '__main__':
    import sys
    level = sys.argv[1]
    problem = PDDL_Problem(level)
    print(problem)