#!/usr/bin/env python

# Usage: ./evaluation.py [REFERENCE_MODEL] [TARGET_MODEL]
# e.g. ./evaluation.py ../reference-sokoban.pddl ../models-custom/model-2.pddl

def canonicalizeActionParameterNames(action):
    parMap = {}
    for idx, par in enumerate(action.parameters):
        parMap[par[0]] = '?{}'.format(idx + 1)
    for predList in [action.parameters, action.positive_preconditions, action.negative_preconditions, action.add_effects, action.del_effects]:
        # print('Canonicalizing', predList)
        for pred in predList:
            # print(pred)
            for idx, param in enumerate(pred):
                if param in parMap:
                    pred[idx] = parMap[param]
        # print('    Changed to', predList)

class ActionEvaluation:
    def __init__(self, ref_action, tar_action):
        self.tp = 0
        self.tn = 0
        self.fp = 0
        self.fn = 0
        self.name = ref_action.name

        canonicalizeActionParameterNames(ref_action)
        canonicalizeActionParameterNames(tar_action)

        self.__compare_predicate_list(ref_action.positive_preconditions, tar_action.positive_preconditions)
        self.__compare_predicate_list(ref_action.negative_preconditions, tar_action.negative_preconditions)
        self.__compare_predicate_list(ref_action.add_effects, tar_action.add_effects)
        self.__compare_predicate_list(ref_action.del_effects, tar_action.del_effects)

    def __compare_predicate_list(self, ref_pred_list, tar_pred_list):
        for ref_pred in ref_pred_list:
            found = False
            for tar_pred in tar_pred_list:
                if ref_pred[0] == tar_pred[0]:
                    self.tp += 1
                    found = True
                    break
            if not found:
                self.fn += 1
        
        for tar_pred in tar_pred_list:
            found = False
            for ref_pred in ref_pred_list:
                if ref_pred[0] == tar_pred[0]:
                    found = True
                    break
            if not found:
                self.fp += 1
    
    @property
    def precision(self):
        return self.tp / (self.tp + self.fp)
    
    @property
    def recall(self):
        return self.tp / (self.tp + self.fn)

    @property
    def f1(self):
        return 2 * self.precision * self.recall / (self.precision + self.recall)

    def __str__(self):
        return '{:15s} {:6.4f}   {:6.4f}   {:6.4f}'.format(self.name, self.f1, self.precision, self.recall,)
    

class Evaluation:
    def __init__(self, reference, target):
        self.action_evaluations = []
        for ref_action in reference.actions:
            for tar_action in target.actions:
                if ref_action.name == tar_action.name:
                    self.action_evaluations.append(ActionEvaluation(ref_action, tar_action))


    def __str__(self):
        return f"""Name           F1-score Precision Recall
{chr(10).join([str(action_evaluation) for action_evaluation in self.action_evaluations])}
"""

if __name__ == '__main__':
    import sys
    from PDDL import PDDL_Parser

    reference = sys.argv[1]
    target = sys.argv[2]
    ref_parser, tar_parser = PDDL_Parser(), PDDL_Parser()
    ref_parser.parse_domain(reference)
    tar_parser.parse_domain(target)
    evaluation = Evaluation(ref_parser, tar_parser)
    print(evaluation)
