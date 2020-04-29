#!/usr/bin/env python

from PDDL import PDDL_Parser
from action import Action
from planner import Planner

class Trajectory:

    def __init__(self, domain_filename=None, problem_filename=None, solution_filename=None):
        self.states = []
        self.actions = []
        self.objects = []

        if domain_filename and problem_filename and solution_filename:
            parser = PDDL_Parser()
            parser.parse_domain(domain_filename)
            parser.parse_problem(problem_filename)
            parser.parse_solution(solution_filename)

            self.states.append(parser.state) 
            self.objects = parser.objects
            planner = Planner()
            state = parser.state
            if not planner.applicable(state, parser.positive_goals, parser.negative_goals):
                for grounded_action in parser.solution:
                    if planner.applicable(state, grounded_action.positive_preconditions, grounded_action.negative_preconditions):
                        state = planner.apply(state, grounded_action.add_effects, grounded_action.del_effects)
                        self.states.append(state)
                        self.actions.append(grounded_action)

    def __get_state_actions(self):
            states = []
            for state in self.states[1:]:
                states.append('(:state ' + ' '.join(['(' + ' '.join(predicate) + ')' for predicate in state]) + ')')
            actions = []
            for action in self.actions:
                actions.append('(:action (' + ' '.join([action.name] + list(action.parameters)) + '))')
            return '\n\n'.join([state + '\n\n' + action for state, action in zip(states, actions)])
    
    def __str__(self):
        return f"""(trajectory

(:objects {' '.join([' '.join([f'{value} - {key}' for value in values]) for key, values in self.objects.items()])})

(:init {' '.join(['(' + ' '.join(predicate) + ')' for predicate in self.states[0]])})

{self.__get_state_actions()}

)"""

if __name__ == '__main__':
    import sys
    parser = PDDL_Parser()
    domain = sys.argv[1]
    problem = sys.argv[2]
    solution = sys.argv[3]
    trajectory = Trajectory(domain, problem, solution)
    print(trajectory)
