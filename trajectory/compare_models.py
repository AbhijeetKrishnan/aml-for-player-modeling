#! /usr/bin/env python3

# Usage: compare_models.py REFERENCE_MODEL TARGET_MODEL

import sys
from PDDL import PDDL_Parser

reference = sys.argv[1]
target = sys.argv[2]
ref_parser, tar_parser = PDDL_Parser(), PDDL_Parser()
ref_parser.parse_domain(reference)
tar_parser.parse_domain(target)

missing_preconditions = {}
extra_preconditions = {}  # This should only occur in stage 1
missing_effects = {}
# Extra effects should never occur unless there is a bug in the implementation
# Since the purpose of this script is not to debug the implementation, extra actions are not included
missing_actions = []


def canonicalize_params(ref_action, tar_action):
    param_map = {}
    ref_parameters = ref_action.parameters
    tar_parameters = tar_action.parameters

    for i in range(len(ref_parameters)):
        param_map[tar_parameters[i][0]] = ref_parameters[i][0]
    for pred_list in [tar_action.parameters, tar_action.positive_preconditions, tar_action.negative_preconditions,
                                             tar_action.add_effects, tar_action.del_effects]:
        for pred in pred_list:
            for idx, param in enumerate(pred):
                if param in param_map:
                    pred[idx] = param_map[param]


# Finds predicates in pred_list_1 that are not in pred_list_2
def predicate_diff(pred_list_1, pred_list_2):
    diff = []

    for pred1 in pred_list_1:
        found = False
        for pred2 in pred_list_2:
            if pred1 == pred2:
                found = True
                break

        if not found:
            diff.append(pred1)

    return diff


for ref_action in ref_parser.actions:
    ref_name = ref_action.name
    found = False
    for tar_action in tar_parser.actions:
        tar_name = tar_action.name
        if ref_name == tar_name:
            canonicalize_params(ref_action, tar_action)

            missing_pos_pre = predicate_diff(ref_action.positive_preconditions, tar_action.positive_preconditions)
            missing_neg_pre = predicate_diff(ref_action.negative_preconditions, tar_action.negative_preconditions)
            for pre in missing_neg_pre:
                pre.insert(0, '!')
            if len(missing_pos_pre) != 0 or len(missing_neg_pre) != 0:
                missing_preconditions[ref_name] = missing_pos_pre + missing_neg_pre

            extra_pos_pre = predicate_diff(tar_action.positive_preconditions, ref_action.positive_preconditions)
            extra_neg_pre = predicate_diff(tar_action.negative_preconditions, ref_action.negative_preconditions)
            for pre in extra_neg_pre:
                pre.insert(0, '!')
            if len(extra_pos_pre) != 0 or len(extra_neg_pre) != 0:
                extra_preconditions[ref_name] = extra_pos_pre + extra_neg_pre

            missing_pos_eff = predicate_diff(ref_action.add_effects, tar_action.add_effects)
            missing_neg_eff = predicate_diff(ref_action.del_effects, tar_action.del_effects)
            for pre in missing_neg_eff:
                pre.insert(0, '!')
            if len(missing_pos_eff) != 0 or len(missing_neg_eff) != 0:
                missing_effects[ref_name] = missing_pos_eff + missing_neg_eff

            found = True
            break

    if not found:
        missing_actions.append(ref_action)

print("The following preconditions are missing:")
for act in missing_preconditions:
    print("  In {}:".format(act))
    for pred in missing_preconditions[act]:
        if pred[0] == '!':
            print("    not {}({})".format(pred[1], ", ".join(pred[2:])))
        else:
            print("    {}({})".format(pred[0], ", ".join(pred[1:])))
print()

print("The following extraneous preconditions are present:")
for act in extra_preconditions:
    print("  In {}:".format(act))
    for pred in extra_preconditions[act]:
        if pred[0] == '!':
            print("    not {}({})".format(pred[1], ", ".join(pred[2:])))
        else:
            print("    {}({})".format(pred[0], ", ".join(pred[1:])))
print()

print("The following effects are missing:")
for act in missing_effects:
    print("  In {}:".format(act))
    for pred in missing_effects[act]:
        if pred[0] == '!':
            print("    not {}({})".format(pred[1], ", ".join(pred[2:])))
        else:
            print("    {}({})".format(pred[0], ", ".join(pred[1:])))
print()

print("The following actions are missing:")
for act in missing_actions:
    print(act.name)
print()
