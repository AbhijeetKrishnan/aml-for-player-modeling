#!/usr/bin/env python

class Evaluation:
    def __init__(self, reference, target):
        self.tp = 0
        self.tn = 0
        self.fp = 0
        self.fn = 0

        for ref_action in reference.actions:
            for tar_action in target.actions:
                if ref_action.name == tar_action.name:
                    self.__compare_predicate_list(ref_action.positive_preconditions, tar_action.positive_preconditions)
                    self.__compare_predicate_list(ref_action.negative_preconditions, tar_action.negative_preconditions)
                    self.__compare_predicate_list(ref_action.add_effects, tar_action.add_effects)
                    self.__compare_predicate_list(ref_action.del_effects, ref_action.del_effects)

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

    def __str__(self):
        return f"""         True False
Positive {self.tp:4} {self.fp:5}
Negative {self.tn:4} {self.fn:5}

Precision = {self.precision:.4f}
Recall = {self.recall:.4f}
F1-score = {self.f1:.4f}"""

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