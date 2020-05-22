#!/usr/bin/env python

from PDDL import PDDL_Parser
import pprint

class trajectory:
    def parseObjects(self, objTokens):
        self.types2objs = {}    # Map of types -> objects; useful when you need to know what objects have a specified type
        self.objs2types = {}    # Map of objects -> types; useful when you want to know what the type of a specific object is
        objs = []
        isType = False
        for token in objTokens[1:]: # Throw out objTokens[0], which will be the string ':objects'
            if isType:
                if token not in self.types2objs:
                    self.types2objs[token] = []
                self.types2objs[token].extend(objs)
                for obj in objs:
                    self.objs2types[obj] = token
                objs = []
                isType = False
            elif token == '-':
                isType = True
            else:
                objs.append(token)

    # Parses the :init and :state blocks in the trajectory file, and also makes a dictionary of all the predicates that appear in the states, along with the types of their peremeters
    def parseStates(self, tokens):
        self.states = []
        self.predicates = {}
        for block in tokens:
            if block[0] == ':state' or block[0] == ':init':
                self.states.append(block[1:])
                for pred in block[1:]:
                    pName = pred[0]
                    pTypes = []
                    for arg in pred[1:]:
                        pTypes.append([self.objs2types[arg]])   # Predicate type lists are now lists of lists of strings- each inner list representing the types observed for one parameter
                    if pName in self.predicates:
                        for oldParamTypes, newType in zip(self.predicates[pName], pTypes):
                            if newType[0] not in oldParamTypes:
                                oldParamTypes.append(newType[0])
                        # if self.predicates[pName] != pTypes:
                            # raise TypeError('Predicate {} believed to have parameter types {}; inconsistent with observed parameters {}'.format(pName, self.predicates[pName], pTypes))
                    else:
                        self.predicates[pName] = pTypes

    def parseActions(self, tokens):
        self.actions = {}
        for block in tokens:
            if block[0] == ':action':
                act_in = block[1]
                # print('Parsing action {}'.format(act_in))
                parTypes = []
                for param in act_in[1:]:
                    parTypes.append(self.objs2types[param]) # Not doing list-of-lists here- that'll be handled in actionCandidate constructor
                if act_in[0] in self.actions:
                    # print ('Found action with same name: {}'.format(act_in[0]))
                    for oldTypes, newType in zip(self.actions[act_in[0]].parameterTypes, parTypes):
                        if newType not in oldTypes:
                            oldTypes.append(newType)
                    self.actions[act_in[0]].updateParameterTypes(parTypes)
                    # if act.parameterTypes != parTypes:
                    #     raise TypeError('Action {} found using parameters {}; inconsistent with earlier {}. Are you using type inheritance?'.format(act_in[0], parTypes, act.parameterTypes))
                else:
                    newAct = actionCandidate(act_in[0], parTypes, self)
                    self.actions[newAct.name] = newAct

    def refineActions(self, tokens):
        assignments = [((n - 1) // 2 - 1, block[1]) for (n, block) in enumerate(tokens) if block[0] == ':action']
        # pprint.pprint(assignments)
        for i, agmt in assignments:
            assignedTypes = [self.objs2types[par] for par in agmt[1:]]
            self.actions[agmt[0]].updateParameterTypes(assignedTypes)
        for act in self.actions.values():
            act.createPrecons(self)
        needsDoubleChecking = False
        for i, agmt in assignments:
            # print('State {}: {}'.format(i, self.states[i]))
            # print('Action {}: {}'.format(i, agmt))
            # print('State {}: {}'.format(i+1, self.states[i+1]))
            # print()
            act = self.actions[agmt[0]]
            assignment = agmt[1:]
            # assignedTypes = [self.objs2types[par] for par in assignment]
            act.prunePrecons(self.states[i], assignment)
            needsDoubleChecking |= act.updateEffects(self.states[i], assignment, self.states[i + 1])
        if needsDoubleChecking:
            # print('Double-checking action effects\n')
            needsDoubleChecking = False
            for i, agmt in assignments:
                act = self.actions[agmt[0]]
                assignment = agmt[1:]
                # assignedTypes = [self.objs2types[par] for par in assignment]
                needsDoubleChecking |= act.updateEffects(self.states[i], assignment, self.states[i + 1])
            if needsDoubleChecking:
                raise ValueError("Some actions still had unexpected effects during the second pass. This shouldn't be possible. If you see this message, please let me know. --SE")

    def genTypeclasses(self):   #TODO Add code to deal with deeper hierarchies
        classList = []
        for typesOuter in self.predicates.values():
            for types in typesOuter:
                # print(types)
                sorTypes = list(sorted(types))
                if sorTypes not in classList:
                    classList.append(sorTypes)
        for act in self.actions:
            for types in self.actions[act].parameterTypes:
                sorTypes = list(sorted(types))
                if sorTypes not in classList:
                    classList.append(sorTypes)
        # print(classList)
        self.typeclasses = {}
        for tclass in classList:
            self.typeclasses['_'.join(tclass)] = 'object'
        for typ in self.types2objs.keys():
            container = 'object'
            for tclass in classList:
                if typ in tclass and typ != '_'.join(tclass):
                    container = '_'.join(tclass)
            self.typeclasses[typ] = container

    def __init__(self, filename, domainName='reconstructed'):
        self.domainName = domainName
        self.parser = PDDL_Parser()
        self.tokens = self.parser.scan_tokens(filename)
        pprint.pprint(self.tokens)
        print('=== Objects ===')
        self.parseObjects(self.tokens[1])
        pprint.pprint(self.types2objs)
        print('=== States ===')
        self.parseStates(self.tokens)
        pprint.pprint(self.states)
        print('=== Predicates ===')
        pprint.pprint(self.predicates)
        print('=== Actions ===')
        self.parseActions(self.tokens)
        # print(self.tokens[3])
        # p, n = self.actions[0].assignPrecons(self.tokens[3][1][1:])
        # print('Grounded Positive preconditions')
        # print(p)
        # print('Grounded Negative preconditions')
        # print(n)
        # print('Before State')
        # print(self.states[0])
        # self.actions[0].prunePrecons(self.states[0], self.tokens[3][1][1:])
        # print(self.actions[0])
        self.refineActions(self.tokens)
        pprint.pprint(self.actions)
        self.genTypeclasses()

    def __repr__(self):
        fmtTypeclasses = ['{} - {}'.format(k, v) for k, v in self.typeclasses.items()]
        fmtPredicates = []
        for name, types in self.predicates.items():
            fmtParams = [name]
            for i, typ in enumerate(types):
                fmtParams.append('?{} - {}'.format(i, '_'.join(typ)))
            fmtPredicates.append('({})'.format(' '.join(fmtParams)))
        fmtActions = [str(act) for act in self.actions.values()]
        return '''(define (domain {})
(:requirements :typing :negative-preconditions)
(:types {})
(:predicates {})
{})
'''.format(self.domainName, ' '.join(fmtTypeclasses), ' '.join(fmtPredicates), ''.join(fmtActions))

# Given a list of lists, returns every possible result of taking one element from each sublist.
# Eg: explode([[1, 2], [3, 4]]) yields [1, 3], [1, 4], [2, 3], [2, 4]
def explode(params):
    # print('Input: {}'.format(params))
    if len(params) == 1:
        for elem in params[0]:
            # print('Base case: Yielding {}'.format([elem]))
            yield [elem]
    else:
        for elem in params[0]:
            # print('Recurring on {}'.format(params[1:]))
            for things in explode(params[1:]):
                # print('Recursion yielded {}'.format(things))
                toYield = [elem]
                toYield.extend(things)
                # print('From recursive branch: Yielding {}'.format(toYield))
                yield toYield

# Flatten a list of lists into a single set, removing duplicate entries in the process
def flattenNoRepeats(ll):
    out = set()
    for l in ll:
        out.update(l)
    return out

class actionCandidate:
    def __init__(self, name, parTypes, trajectory):
        self.name = name
        self.parameterTypes = []
        self.parNames = []
        self.types2pars = {}    # Map from types to the names of the action parameters names that could be that type
        for i, pType in enumerate(parTypes):
            self.parameterTypes.append([pType]) # Other observed types will be added later, during successive iterations of trajectory.parseActions
            parName = '?{}{}'.format(i, pType)   # Parameter name format is '?<parameter index><type of first object observed being passed to this parameter>'
            if pType not in self.types2pars:
                self.types2pars[pType] = []
            self.types2pars[pType].append(parName)
            self.parNames.append(parName)
        self.positivePreconditions = []
        self.negativePreconditions = []
        self.positiveEffects = set()
        self.negativeEffects = set()
        # print(self)

    def updateParameterTypes(self, parTypes):
        for parName, oldTypes, newType in zip(self.parNames, self.parameterTypes, parTypes):
            if newType not in oldTypes:
                oldTypes.append(newType)
            if parName not in self.types2pars[newType]:
                self.types2pars[newType].append(parName)

    def createPrecons(self, trajectory):
        # print('{} types2pars:'.format(self.name))
        # pprint.pprint(self.types2pars)
        for predName, predTypes in trajectory.predicates.items():
            # print(' Predicate: {} {}'.format(predName, predTypes))
            for typeOrdering in explode(predTypes):
                # print('  Type ordering: {}'.format(typeOrdering))
                toExplode = []
                canExplode = True
                for predType in typeOrdering:
                    # print('   Predicate parameter type: {}'.format(predType))
                    if predType in self.types2pars:
                        # print('    Keeping {}'.format(predType))
                        toExplode.append(self.types2pars[predType])
                    else:
                        canExplode = False
                        # print('    Dropping {}'.format(predType))
                if canExplode:
                    # print('  Will now explode {}'.format(toExplode))
                    # toExplode = [self.types2pars[predType] for predType in predTypes]
                    exploded = explode(toExplode)
                    # print('Recieved {}'.format(list(exploded)))
                    for ordering in exploded:
                        # print('   From explosion: {}'.format(ordering))
                        precon = [predName]
                        precon.extend(ordering)
                        self.positivePreconditions.append(precon)
                    self.negativePreconditions.append(precon)


    def assignPrecons(self, assignment):
        assignMap = dict(zip(self.parNames, assignment))
        # print(assignMap)
        pos_out = []
        neg_out = []
        for prec in self.positivePreconditions:
            grounded = [prec[0]]
            grounded.extend([assignMap[p] for p in prec[1:]])
            pos_out.append(grounded)
        for prec in self.negativePreconditions:
            grounded = [prec[0]]
            grounded.extend([assignMap[p] for p in prec[1:]])
            neg_out.append(grounded)
        return pos_out, neg_out

    def prunePrecons(self, before, assignment):
        pos, neg = self.assignPrecons(assignment)
        new_pos = []
        new_neg = []
        # print('Assignment to {}: {}'.format(self.name, assignment))
        # print('Negative preconditions: {}'.format(neg))
        # print('Before state: {}'.format(before))
        for grounded, pred in zip(pos, self.positivePreconditions):
            if grounded in before:      # If the predicate is in the before state, it could be a positive precondition
                new_pos.append(pred)    # so keep it; otherwise, don't
        for grounded, pred in zip(neg, self.negativePreconditions):
            if grounded not in before:  # If the predicate wasn't in the before state, it could be a negative precondition
                new_neg.append(pred)    # so keep it
            #     print('Keeping {}'.format(grounded))
            # else:
            #     print('Dropping {}'.format(grounded))
        self.positivePreconditions = new_pos
        self.negativePreconditions = new_neg
        # print('New negative preconditions: {}\n'.format(new_neg))

    def updateEffects(self, before, assignment, after):
        # Compute differences between before and after
        pos = [pred for pred in after if pred not in before]
        neg = [pred for pred in before if pred not in after]
        # print('Updating effects of {} {}'.format(self.name, assignment))
        # print('Added predicates: {}'.format(pos))
        # print('Removed predicates: {}'.format(neg))
        # Check that the parameters of the predicates in the difference are a subset of the objects in assignment
        for pred in pos + neg:
            for param in pred[1:]:
                if param not in assignment:
                    raise ValueError('Action {} seems to be affecting predicate {}, with parameters outside its assignment, {}! Are you using conditional effects or something?'.format(
                        self.name, pred, assignment))
        # Map predicate parameters to parNames
        assignMap = dict(zip(assignment, self.parNames))
        reverseMap = dict(zip(self.parNames, assignment))
        new_pos = set()
        new_neg = set()
        # print('Assignment map: {}'.format(assignMap))
        for pred in pos:
            new_pred = [pred[0]]
            new_pred.extend([assignMap[param] for param in pred[1:]])
            new_pos.add(tuple(new_pred))
        for pred in neg:
            new_pred = [pred[0]]
            new_pred.extend([assignMap[param] for param in pred[1:]])
            new_neg.add(tuple(new_pred))
        # Check that the result matches the effects from the last run
        # new_pos.sort()
        # new_neg.sort()
        # print('Sorted positive effects: {}'.format(new_pos))
        # print('Sorted negative effects: {}'.format(new_neg))
        # if len(self.positiveEffects) == 0:
        #     self.positiveEffects = new_pos
        # elif new_pos != self.positiveEffects:

        needsDoubleChecking = False
        # Find differences between new_pos and (old) self.positiveEffects
        # For each effect in new_pos but not in self.positive_effects:
        for novelEffect in new_pos - self.positiveEffects:
            # print('Novel positive effect: {}'.format(novelEffect))
            # These effects were observed for the first time just now.
                # Add them to self.positiveEffects
            self.positiveEffects.add(novelEffect)
            # They should have been present in both the before and after states of previous invocations of this action.
                # Double-check that... somehow.
            needsDoubleChecking = True
        # For each effect in self.positive_effects but not in new_pos:
        for missingEffect in self.positiveEffects - new_pos:
            # print('Missing positive effect: {}'.format(missingEffect))
            # These effects have been observed in the past, but did not manifest this time.
            # They should be present in both the before and after states of this action.
            # Check that they are present.
            predicateName = missingEffect[0]
            predicateParams = [reverseMap[p] for p in missingEffect[1:]]
            groundedEffect = [predicateName] + predicateParams
            if groundedEffect not in before or groundedEffect not in after:
                raise ValueError('Spurious lack of positive effect discovered in action {} {}!\nBefore: {}\nMissing effect: {}\nAfter:  {}'.format(self.name, assignment, before, groundedEffect, after))
            # raise ValueError('Positive effects of action {} seem inconsistent! Are you using conditional effects?\nObserved: {}\nNew:      {}'.format(self.name, self.positiveEffects, new_pos))

        # if len(self.negativeEffects) == 0:
        #     self.negativeEffects = new_neg
        # elif new_neg != self.negativeEffects:

        # Find differences between new_neg and (old) self.negativeEffects
        # For each effect in new_neg but not in self.negative_effects:
        for novelEffect in new_neg - self.negativeEffects:
            # print('Novel negative effect: {}'.format(novelEffect))
            # These effects were observed for the first time just now.
                # Add them to self.negativeEffects
            self.negativeEffects.add(novelEffect)
            # They should have been absent in both the before and after states of previous invocations of this action.
                # Double-check that... somehow.
            needsDoubleChecking = True
        # For each effect in self.negative_effects but not in new_neg:
        for missingEffect in self.negativeEffects - new_neg:
            # print('Missing negative effect: {}'.format(missingEffect))
            # These effects have been observed in the past, but did not manifest this time.
            # These predicates should be absent in both the before and after states of this action.
            # Check that they are absent.
            predicateName = missingEffect[0]
            predicateParams = [reverseMap[p] for p in missingEffect[1:]]
            groundedEffect = [predicateName] + predicateParams
            if groundedEffect in before or groundedEffect in after:
                raise ValueError('Spurious lack of negative effect discovered in action {} {}!\nBefore: {}\nMissing effect: {}\nAfter:  {}'.format(self.name, assignment, before, groundedEffect, after))
            # raise ValueError('Negative effects of action {} seem inconsistent! Are you using conditional effects?\nObserved: {}\nNew:      {}'.format(self.name, self.negativeEffects, new_neg))
        # print()
        return needsDoubleChecking

    def __repr__(self):
        return '''Action Candidate Name: {}
Parameters: {}
Positive preconditions: {}
Negative preconditions: {}
Positive effects: {}
Negative effects: {}
'''.format(self.name, self.types2pars, self.positivePreconditions, self.negativePreconditions, self.positiveEffects, self.negativeEffects)

    def __str__(self):
        params = ['{} - {}'.format(par, '_'.join(typ)) for par, typ in zip(self.parNames, self.parameterTypes)]
        posiPrecons = ['({})'.format(' '.join(pred)) for pred in self.positivePreconditions]
        negaPrecons = ['(not ({}))'.format(' '.join(pred)) for pred in self.negativePreconditions]
        posEffects = ['({})'.format(' '.join(pred)) for pred in self.positiveEffects]
        negEffects = ['(not ({}))'.format(' '.join(pred)) for pred in self.negativeEffects]
        return '''(:action {}
:parameters ({})
:precondition (and {}
{})
:effect (and {}
{}))
'''.format(self.name, ' '.join(params), ' '.join(posiPrecons), ' '.join(negaPrecons), ' '.join(posEffects), ' '.join(negEffects))



# Main
if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    if len(sys.argv) > 3:
        traj = trajectory(filename, sys.argv[3])
    else:
        traj = trajectory(filename)
    if len(sys.argv) > 2:
        fout = open(sys.argv[2], 'w')
    else:
        fout = sys.stdout
    fout.write(str(traj))


