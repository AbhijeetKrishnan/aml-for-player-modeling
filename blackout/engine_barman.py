#! /usr/bin/env python3

from PDDL import PDDL_Parser
from planner import Planner
from action import Action


TYPE_OBJECT     = 'object'
TYPE_HAND       = 'hand'
TYPE_LEVEL      = 'level'
TYPE_BEVERAGE   = 'beverage'
TYPE_DISPENSER  = 'dispenser'
TYPE_CONTAINER  = 'container'
TYPE_INGREDIENT = 'ingredient'
TYPE_COCKTAIL   = 'cocktail'
TYPE_SHOT       = 'shot'
TYPE_SHAKER     = 'shaker'

PRED_ONTABLE            = 'ontable'
PRED_HOLDING            = 'holding'
PRED_HANDEMPTY          = 'handempty'
PRED_EMPTY              = 'empty'
PRED_CONTAINS           = 'contains'
PRED_CLEAN              = 'clean'
PRED_USED               = 'used'
PRED_DISPENES           = 'dispenses'
PRED_SHAKER_EMPTY_LEVEL = 'shaker-empty-level'
PRED_SHAKER_LEVEL       = 'shaker-level'
PRED_NEXT               = 'next'
PRED_UNSHAKED           = 'unshaked'
PRED_SHAKED             = 'shaked'
PRED_COCKTAIL_PART1     = 'cocktail-part1'
PRED_COCKTAIL_PART2     = 'cocktail-part2'

ACT_GRASP                     = 'grasp'
ACT_LEAVE                     = 'leave'
ACT_FILL_SHOT                 = 'fill-shot'
ACT_REFILL_SHOT               = 'refill-shot'
ACT_EMPTY_SHOT                = 'empty-shot'
ACT_CLEAN_SHOT                = 'clean-shot'
ACT_POUR_SHOT_TO_CLEAN_SHAKER = 'pour-shot-to-clean-shaker'
ACT_POUR_SHOT_TO_USED_SHAKER  = 'pour-shot-to-used-shaker'
ACT_EMPTY_SHAKER              = 'empty-shaker'
ACT_CLEAN_SHAKER              = 'clean-shaker'
ACT_SHAKE                     = 'shake'
ACT_POUR_SHAKER_TO_SHOT       = 'pour-shaker-to-shot'

OBJ_HAND_LEFT       = 'left'
OBJ_HAND_RIGHT      = 'right'
OBJ_LEVEL_L0        = 'l0'
OBJ_LEVEL_L1        = 'l1'
OBJ_LEVEL_L2        = 'l2'
OBJ_SHOT_SHOT1      = 'shot1'
OBJ_SHAKER_SHAKER1  = 'shaker1'
OBJ_STEM_INGREDIENT = 'ingredient'
OBJ_STEM_COCKTAIL   = 'cocktail'


"""
    This is an engine for running the Barman domain from IPC 2014.
    It is designed to result in many failed actions, in order to help the Blackout algorithm learn.
    While not exactly realistic, this is useful for proving a concept.
"""
class Engine:
    def __init__(self, domain, problem, logfile, verbose):
        self.parser = PDDL_Parser()
        self.parser.parse_domain(domain)
        self.parser.parse_problem(problem)

        self.state = self.parser.state
        self.goal_pos = self.parser.positive_goals
        self.goal_neg = self.parser.negative_goals

        self.history = []
        self.action_log = []

        self.logfile = logfile
        self.verbose = verbose

        self.planner = Planner()
        if self.planner.applicable(self.state, self.goal_pos, self.goal_neg):
            print("Puzzle is already solved.")

    def get_objects(self, obj_type: str):
        # Parser doesn't include parents, so hardcoding them
        if obj_type == TYPE_OBJECT:
            return self.parser.objects[TYPE_HAND] + \
                   self.parser.objects[TYPE_LEVEL] + \
                   self.parser.objects[TYPE_DISPENSER] + \
                   self.get_objects(TYPE_BEVERAGE) + \
                   self.get_objects(TYPE_CONTAINER)
        elif obj_type == TYPE_BEVERAGE:
            return self.parser.objects[TYPE_INGREDIENT] + self.parser.objects[TYPE_COCKTAIL]
        elif obj_type == TYPE_CONTAINER:
            return self.parser.objects[TYPE_SHOT] + self.parser.objects[TYPE_SHAKER]
        else:
            return self.parser.objects[obj_type]

    def predicate_holds(self, pred: str, *args):
        return self.planner.applicable(self.state, [[pred] + list(args)], [])

    def get_action(self, name: str):
        for act in self.parser.actions:
            if act.name == name:
                return act
        return None

    def game_loop(self):
        with open(self.logfile, 'w') as log:
            log.write('(trajectory\n\n')
            log.write('(:objects ')
            for t, os in self.parser.objects.items():
                for o in os:
                    log.write('{} -  {} '.format(o, t))
            log.write(')\n\n')
            log.write(self.print_state(':init'))
            log.write('\n\n')

            while True:
                self.render()
                if self.planner.applicable(self.state, self.goal_pos, self.goal_neg):
                    print("You're winner !")
                    log.write(''.join(self.action_log))
                    log.write(')')
                    return

                self.action()

    def print_state(self, word=':state'):
        out = ['({}'.format(word)]
        for pred in self.state:
            out.append(' (')
            out.append(' '.join(pred))
            out.append(')')
        out.append(')')
        return ''.join(out)

    def render(self):
        left = "Empty"
        right = "Empty"
        table = []
        containers = {}
        for cont in self.get_objects(TYPE_CONTAINER):
            if self.predicate_holds(PRED_HOLDING, OBJ_HAND_LEFT, cont):
                left = cont
            elif self.predicate_holds(PRED_HOLDING, OBJ_HAND_RIGHT, cont):
                right = cont
            else:
                table.append(cont)

            if self.predicate_holds(PRED_EMPTY, cont):
                if self.predicate_holds(PRED_CLEAN, cont):
                    containers[cont] = "Clean"
                else:
                    containers[cont] = "Used"
                    for bev in self.get_objects(TYPE_BEVERAGE):
                        if self.predicate_holds(PRED_USED, cont, bev):
                            containers[cont] += ", " + bev
            else:
                if self.predicate_holds(PRED_SHAKER_LEVEL, cont, OBJ_LEVEL_L1):
                    containers[cont] = "Filled 1"
                elif self.predicate_holds(PRED_SHAKER_LEVEL, cont, OBJ_LEVEL_L2):
                    containers[cont] = "Filled 2"
                else:
                    containers[cont] = "Filled"
                for bev in self.get_objects(TYPE_BEVERAGE):
                    if self.predicate_holds(PRED_CONTAINS, cont, bev):
                        containers[cont] += ", " + bev

        for shaker in self.get_objects(TYPE_SHAKER):
            if self.predicate_holds(PRED_SHAKED, shaker):
                containers[shaker] += ", shaked"
            else:
                containers[shaker] += ", unshaked"

        print("Left: {:<9}Right: {}".format(left, right))
        print("Table: " + ", ".join(table))

        for cont in containers:
            print("{:<8}: {}".format(cont, containers[cont]))

    def action(self):
        key = input("Choose action (q for help): ")
        key = key.lower()

        if key == 'r':
            self.right_grasp_leave()
        elif key == 'l':
            self.left_grasp_leave()
        elif key == 'f':
            self.fill_refill_shot()
        elif key == 'e':
            self.empty()
        elif key == 'c':
            self.clean()
        elif key == 'p':
            self.pour()
        elif key == 'h':
            self.shake()
        elif key == 'u':  # Undo
            if len(self.history) > 0:
                self.state = self.history.pop()
                if self.verbose:
                    self.action_log.append('(:undo)\n\n{}\n\n'.format(self.print_state()))
                else:
                    self.action_log.pop()
        elif key == 's':  # Reset
            self.state = self.parser.state
            self.history = [self.state]
            if self.verbose:
                self.action_log.append('(:restart)\n\n{}\n\n'.format(self.print_state()))
            else:
                self.action_log = []
        elif key == 'q':  # Help
            print("R - pick up/put down with right hand")
            print("L - pick up/put down with left hand")
            print("F - fill shot")
            print("E - empty container")
            print("C - clean container")
            print("P - pour")
            print("H - shake")
            print("U - undo")
            print("S - reset")

    def right_grasp_leave(self):
        hand = OBJ_HAND_RIGHT
        # If right hand is holding something, put it down
        if not self.predicate_holds(PRED_HANDEMPTY, OBJ_HAND_RIGHT):
            # Guess the container
            for cont in self.get_objects(TYPE_CONTAINER):
                if self.predicate_holds(PRED_HOLDING, hand, cont):  # TODO
                    assign = [hand, cont]
                    ground_act = self.ground_action(self.get_action(ACT_LEAVE), assign)
                    if self.try_action(ground_act):
                        return
            # We should never get here
            assert False

        # Else, right hand is empty, so pick something up
        containers = self.get_objects(TYPE_CONTAINER)
        for i in range(len(containers)):
            print("{:<2}: {}".format(i, containers[i]))
        idx = int(input("Choose container: "))
        cont = containers[idx]

        assign = [hand, cont]
        ground_act = self.ground_action(self.get_action(ACT_GRASP), assign)
        self.try_action(ground_act)

    def left_grasp_leave(self):
        hand = OBJ_HAND_LEFT
        # If left hand is holding something, put it down
        if not self.predicate_holds(PRED_HANDEMPTY, OBJ_HAND_LEFT):
            # Guess the container
            for cont in self.get_objects(TYPE_CONTAINER):
                if self.predicate_holds(PRED_HOLDING, hand, cont):  # TODO
                    assign = [hand, cont]
                    ground_act = self.ground_action(self.get_action(ACT_LEAVE), assign)
                    if self.try_action(ground_act):
                        return
            # We should never get here
            assert False

        # Else, right hand is empty, so pick something up
        containers = self.get_objects(TYPE_CONTAINER)
        for i in range(len(containers)):
            print("{:<2}: {}".format(i, containers[i]))
        idx = int(input("Choose container: "))
        cont = containers[idx]

        assign = [hand, cont]
        ground_act = self.ground_action(self.get_action(ACT_GRASP), assign)
        self.try_action(ground_act)

    def fill_refill_shot(self):
        shot = None
        hand1 = None
        hand2 = None
        # If there is only a shot in one hand, we will attempt to fill that one
        # If both hands are occupied, we will unsuccessfully attempt to fill an arbitrary shot
        # If no shot is held, we will likewise unsuccessully attempt to fill an arbitrary one
        for s in self.get_objects(TYPE_SHOT):
            # If there is a shot in the right hand, try to fill that one
            if self.predicate_holds(PRED_HOLDING, OBJ_HAND_RIGHT, s):
                shot = s
                hand1 = OBJ_HAND_RIGHT
                hand2 = OBJ_HAND_LEFT
                break
            # Else if there is a shot in the left hand, try to fill that one
            if self.predicate_holds(PRED_HOLDING, OBJ_HAND_LEFT, s):
                shot = s
                hand1 = OBJ_HAND_LEFT
                hand2 = OBJ_HAND_RIGHT
                break
        # If no shot is in hands, use an arbitrary shot and hand; this will fail
        if not shot:
            shot = OBJ_SHOT_SHOT1
            hand1 = OBJ_HAND_RIGHT
            hand2 = OBJ_HAND_LEFT

        idx = input("Choose ingredient: ")
        ingr = OBJ_STEM_INGREDIENT + idx

        # Guess the dispenser
        for disp in self.get_objects(TYPE_DISPENSER):
            if self.predicate_holds(PRED_DISPENES, disp, ingr):  # TODO
                assign = [shot, ingr, hand1, hand2, disp]
                ground_act = self.ground_action(self.get_action(ACT_FILL_SHOT), assign)
                if self.try_action(ground_act):
                    return

        # If we failed to fill the shot, it might be used, so try to refill it
        # Once again, guess the dispenser
        for disp in self.get_objects(TYPE_DISPENSER):
            if self.predicate_holds(PRED_DISPENES, disp, ingr):  # TODO
                assign = [shot, ingr, hand1, hand2, disp]
                ground_act = self.ground_action(self.get_action(ACT_REFILL_SHOT), assign)
                if self.try_action(ground_act):
                    return

    def empty(self):
        h = input("Choose hand (r/l): ")
        hand = OBJ_HAND_RIGHT if h == 'r' else OBJ_HAND_LEFT

        # First try empty-shot
        # Guess the shot and beverage
        for shot in self.get_objects(TYPE_SHOT):
            if self.predicate_holds(PRED_HOLDING, hand, shot):  # TODO
                for bev in self.get_objects(TYPE_BEVERAGE):
                    if self.predicate_holds(PRED_CONTAINS, shot, bev):  # TODO
                        assign = [hand, shot, bev]
                        ground_act = self.ground_action(self.get_action(ACT_EMPTY_SHOT), assign)
                        if self.try_action(ground_act):
                            return

        # Try empty-shaker
        # Guess the shaker, cocktail, and level
        for shaker in self.get_objects(TYPE_SHAKER):
            if self.predicate_holds(PRED_HOLDING, hand, shaker):  # TODO
                for cocktail in self.get_objects(TYPE_COCKTAIL):
                    if self.predicate_holds(PRED_CONTAINS, shaker, cocktail):  # TODO
                        # for level in self.get_objects(TYPE_LEVEL):
                            level = OBJ_LEVEL_L2 if self.predicate_holds(PRED_SHAKER_LEVEL, shaker, OBJ_LEVEL_L2) else OBJ_LEVEL_L1
                            assign = [hand, shaker, cocktail, level, OBJ_LEVEL_L0]
                            ground_act = self.ground_action(self.get_action(ACT_EMPTY_SHAKER), assign)
                            if self.try_action(ground_act):
                                return

    def clean(self):
        cont = None
        hand1 = None
        hand2 = None
        shaker = False
        # If there is only a container in one hand, we will attempt to clean that one
        # If both hands are occupied, we will unsuccessfully attempt to clean an arbitrary container
        # If no container is held, we will likewise unsuccessully attempt to clean an arbitrary one
        for c in self.get_objects(TYPE_SHOT):
            # If there is a container in the right hand, try to clean that one
            if self.predicate_holds(PRED_HOLDING, OBJ_HAND_RIGHT, c):
                cont = c
                hand1 = OBJ_HAND_RIGHT
                hand2 = OBJ_HAND_LEFT
                break
            # Else if there is a container in the left hand, try to clean that one
            if self.predicate_holds(PRED_HOLDING, OBJ_HAND_LEFT, c):
                cont = c
                hand1 = OBJ_HAND_LEFT
                hand2 = OBJ_HAND_RIGHT
                break
        for c in self.get_objects(TYPE_SHAKER):
            # If there is a container in the right hand, try to clean that one
            if self.predicate_holds(PRED_HOLDING, OBJ_HAND_RIGHT, c):
                cont = c
                shaker = True
                hand1 = OBJ_HAND_RIGHT
                hand2 = OBJ_HAND_LEFT
                break
            # Else if there is a container in the left hand, try to clean that one
            if self.predicate_holds(PRED_HOLDING, OBJ_HAND_LEFT, c):
                cont = c
                shaker = True
                hand1 = OBJ_HAND_LEFT
                hand2 = OBJ_HAND_RIGHT
                break
        # If no container is in hands, use an arbitrary shot and hand; this will fail
        if not cont:
            cont = OBJ_SHOT_SHOT1
            hand1 = OBJ_HAND_RIGHT
            hand2 = OBJ_HAND_LEFT

        if shaker:
            assign = [hand1, hand2, cont]
            ground_act = self.ground_action(self.get_action(ACT_CLEAN_SHAKER), assign)
            self.try_action(ground_act)
        else:
            # Guess the beverage
            for bev in self.get_objects(TYPE_BEVERAGE):
                if self.predicate_holds(PRED_USED, cont, bev):  # TODO
                    assign = [cont, bev, hand1, hand2]
                    ground_act = self.ground_action(self.get_action(ACT_CLEAN_SHOT), assign)
                    if self.try_action(ground_act):
                        return

    def pour(self):
        h = input("Choose hand (r/l): ")
        hand = OBJ_HAND_RIGHT if h == 'r' else OBJ_HAND_LEFT

        containers = self.get_objects(TYPE_CONTAINER)
        for i in range(len(containers)):
            print("{:<2}: {}".format(i, containers[i]))
        idx = int(input("Choose receptacle: "))
        dest = containers[idx]

        # Pouring to shaker
        if dest in self.get_objects(TYPE_SHAKER):
            # Guess the pouring shot
            for shot in self.get_objects(TYPE_SHOT):
                if self.predicate_holds(PRED_HOLDING, hand, shot):  # TODO
                    # Guess the ingredient and level
                    for ingr in self.get_objects(TYPE_INGREDIENT):
                        if self.predicate_holds(PRED_CONTAINS, shot, ingr):  # TODO
                            # Try level 0 to 1
                            assign = [shot, ingr, dest, hand, OBJ_LEVEL_L0, OBJ_LEVEL_L1]
                            # First try pour-shot-to-clean-shaker
                            ground_act = self.ground_action(self.get_action(ACT_POUR_SHOT_TO_CLEAN_SHAKER), assign)
                            if self.try_action(ground_act):
                                return
                            # Try pour-shot-to-used-shaker
                            ground_act = self.ground_action(self.get_action(ACT_POUR_SHOT_TO_USED_SHAKER), assign)
                            if self.try_action(ground_act):
                                return

                            # Try level 1 to 2
                            assign[4:6] = [OBJ_LEVEL_L1, OBJ_LEVEL_L2]
                            # First try pour-shot-to-clean-shaker
                            ground_act = self.ground_action(self.get_action(ACT_POUR_SHOT_TO_CLEAN_SHAKER), assign)
                            if self.try_action(ground_act):
                                return
                            # Try pour-shot-to-used-shaker
                            ground_act = self.ground_action(self.get_action(ACT_POUR_SHOT_TO_USED_SHAKER), assign)
                            if self.try_action(ground_act):
                                return

                            # Finally, try level 2 to 0; this will fail
                            assign[4:6] = [OBJ_LEVEL_L2, OBJ_LEVEL_L0]
                            ground_act = self.ground_action(self.get_action(ACT_POUR_SHOT_TO_CLEAN_SHAKER), assign)
                            self.try_action(ground_act)
        # Pouring to shot
        else:
            # Guess the pouring shaker
            for shaker in self.get_objects(TYPE_SHAKER):
                if self.predicate_holds(PRED_HOLDING, hand, shaker):  # TODO
                    # Guess the beverage and level
                    for bev in self.get_objects(TYPE_BEVERAGE):
                        if self.predicate_holds(PRED_CONTAINS, shaker, bev):  # TODO
                            # Try level 2 to 1
                            assign = [bev, dest, hand, shaker, OBJ_LEVEL_L2, OBJ_LEVEL_L1]
                            ground_act = self.ground_action(self.get_action(ACT_POUR_SHAKER_TO_SHOT), assign)
                            if self.try_action(ground_act):
                                return

                            # Try level 1 to 0
                            assign[4:6] = [OBJ_LEVEL_L1, OBJ_LEVEL_L0]
                            ground_act = self.ground_action(self.get_action(ACT_POUR_SHAKER_TO_SHOT), assign)
                            if self.try_action(ground_act):
                                return

                            # Try level 0 to 2; this will fail
                            assign[4:6] = [OBJ_LEVEL_L0, OBJ_LEVEL_L2]
                            ground_act = self.ground_action(self.get_action(ACT_POUR_SHAKER_TO_SHOT), assign)
                            self.try_action(ground_act)

    def shake(self):
        shaker = None
        hand1 = None
        hand2 = None
        # If there is only a shaker in one hand, we will attempt to shaker that one
        # If both hands are occupied, we will unsuccessfully attempt to shake an arbitrary shaker
        # If no shaker is held, we will likewise unsuccessully attempt to shake an arbitrary one
        for s in self.get_objects(TYPE_SHAKER):
            # If there is a shot in the right hand, try to clean that one
            if self.predicate_holds(PRED_HOLDING, OBJ_HAND_RIGHT, s):
                shaker = s
                hand1 = OBJ_HAND_RIGHT
                hand2 = OBJ_HAND_LEFT
                break
            # Else if there is a shot in the left hand, try to clean that one
            if self.predicate_holds(PRED_HOLDING, OBJ_HAND_LEFT, s):
                shaker = s
                hand1 = OBJ_HAND_LEFT
                hand2 = OBJ_HAND_RIGHT
                break
        # If no shot is in hands, use an arbitrary shot and hand; this will fail
        if not shaker:
            shaker = OBJ_SHAKER_SHAKER1
            hand1 = OBJ_HAND_RIGHT
            hand2 = OBJ_HAND_LEFT

        idx = input("Choose cocktail: ")
        cocktail = OBJ_STEM_COCKTAIL + idx

        # Guess ingredients
        for ingr1 in self.get_objects(TYPE_INGREDIENT):
            for ingr2 in self.get_objects(TYPE_INGREDIENT):
                if self.predicate_holds(PRED_CONTAINS, shaker, ingr1) and self.predicate_holds(PRED_CONTAINS, shaker, ingr2):  # TODO
                    assign = [cocktail, ingr1, ingr2, shaker, hand1, hand2]
                    ground_act = self.ground_action(self.get_action(ACT_SHAKE), assign)
                    if self.try_action(ground_act):
                        return

    def ground_action(self, act: Action, assign: list):
        variables = []
        for var, _ in act.parameters:
            variables.append(var)
        pos_pre = act.replace(act.positive_preconditions, variables, assign)
        neg_pre = act.replace(act.negative_preconditions, variables, assign)
        pos_eff = act.replace(act.add_effects, variables, assign)
        neg_eff = act.replace(act.del_effects, variables, assign)

        return Action(act.name, assign, pos_pre, neg_pre, pos_eff, neg_eff)

    def try_action(self, act: Action):
        if self.planner.applicable(self.state, act.positive_preconditions, act.negative_preconditions):
            success = True
        else:
            success = False

        # Log successful action
        if success:
            print("Action: {} {}".format(act.name, act.parameters))
            self.history.append(self.state)
            self.state = self.planner.apply(self.state, act.add_effects, act.del_effects)
            self.action_log.append("(:action ({}))\n\n{}\n\n".format(' '.join([act.name, *act.parameters]),
                                                                     self.print_state()))
        # In verbose mode, log failed actions
        elif self.verbose:
            self.action_log.append("(:action-failed ({}))\n\n{}\n\n".format(' '.join([act.name, *act.parameters]),
                                                                            self.print_state()))

        return success


if __name__ == "__main__":
    import sys
    import time

    start = time.time()
    domain = sys.argv[1]
    problem = sys.argv[2]
    if len(sys.argv) > 3:
        logfile = sys.argv[3]
    else:
        logfile = '/dev/null'
    if len(sys.argv) > 4 and sys.argv[4] == '--verbose':
        verbose = True
    else:
        verbose = False

    engine = Engine(domain, problem, logfile, verbose)
    engine.game_loop()
