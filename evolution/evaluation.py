from enum import Enum
from PDDL import PDDL_Parser
from statistics import mean

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
                if ref_pred == tar_pred:
                    self.tp += 1
                    found = True
                    break
            if not found:
                self.fn += 1
        
        for tar_pred in tar_pred_list:
            found = False
            for ref_pred in ref_pred_list:
                if ref_pred == tar_pred:
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
    

class Evaluation:
    def __init__(self, reference, target):
        self.action_evaluations = []
        for ref_action in reference.actions:
            for tar_action in target.actions:
                if ref_action.name == tar_action.name:
                    self.action_evaluations.append(ActionEvaluation(ref_action, tar_action))

    @property
    def avg_f1(self):
        return mean([act.f1 for act in self.action_evaluations])


def eval_f1(model):
    reference = "../reference-sokoban.pddl"
    ref_parser, tar_parser = PDDL_Parser(), PDDL_Parser()
    ref_parser.parse_domain(reference)
    tar_parser.parse_domain(model)
    evaluation = Evaluation(ref_parser, tar_parser)
    return evaluation.avg_f1

class Mode(Enum):
    POS_PRE = 0
    NEG_PRE = 1
    POS_EFF = 2
    NEG_EFF = 3

def eval_single_target(model, tar_act, tar_mode, tar_pred):
    parser = PDDL_Parser()
    parser.parse_domain(model)

    tar_pred = tar_pred.split(' ')

    for action in parser.actions:
        if action.name == tar_act:
            if tar_mode == Mode.POS_PRE:
                for pred in action.positive_preconditions:
                    if pred == tar_pred:
                        return 1
            elif tar_mode == Mode.NEG_PRE:
                for pred in action.negative_preconditions:
                    if pred == tar_pred:
                        return 1
            elif tar_mode == Mode.POS_EFF:
                for pred in action.add_effects:
                    if pred == tar_pred:
                        return 1
            elif tar_mode == Mode.NEG_EFF:
                for pred in action.del_effects:
                    if pred == tar_pred:
                        return 1

    return 0
