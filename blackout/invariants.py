#!/usr/bin/env python

# Okay... My goal here is to take the information available after execution of trajectory2, and generate a set of invariants.
# Rules about what predicates can and cannot coexist on what kinds of objects.
# As an example invariant, consider the "at-goal" and "at-nongoal" predicates in soko3.
# Every stone has exactly one of those predicates at any given time. Always one or the other; never both or neither. That's an invariant.
# And it's an invariant because that condition ("exactly one") is true in the initial state ov every soko3 level, and none of the soko3 actions can make it false if it wasn't true to begin with.
# Move doesn't change the predicates of any stone; push-to-goal adds at-goal and removes at-nongoal; and push-to-nongoal does the reverse.
# Another example would be the in-dir predicates in soko2, which cannot be added or removed by any action.

# So, I'm thinking I'll start by analyzing the action effects. I'll look for patterns like this:
# P and Q are always added together
# P and Q are always removed together
# P and Q are never both added at once
# P and Q are never both removed at once
# P is only added when Q is removed     ('only' meaning that there are no actions that add P without also removing Q, but there may be actions that remove Q without adding P)
# P is always added when Q is removed
# P is only removed when Q is added
# Etc
# Which I can condense into this:
# P is (only | always) (added | removed) when Q is (added | removed)
# So I could express the at-goal/at-nongoal invariant like this:
#       at-goal    is only   added   when at-nongoal is removed
#   AND at-goal    is always added   when at-nongoal is removed
#   AND at-nongoal is only   added   when at-goal    is removed
#   AND at-nongoal is always added   when at-goal    is removed
#   AND at-goal    is only   removed when at-nongoal is added
#   AND at-goal    is always removed when at-nongoal is added
#   AND at-nongoal is only   removed when at-goal    is added
#   AND at-nongoal is always removed when at-goal    is added
# There's some redundancy there, right?
# If P is always added when Q is removed, then that means that the only actions that remove Q are the ones that also add P.
# [P is always added when Q is removed] <==> [Q is only removed when P is added]
# So maybe I should find a way to give those two contrapositives the same representation in the data structures? Don't know how, though.
# Factoring that into the equality operator should be simple enough, though.
# Also, maybe I should consider invariants on a variable number of predicates? That'd cover the never-added, never-removed constants, and more complex things like "only one or two of these three",
#   but permitting consideration of arbitrary-length rules sounds like it'd get computationally intractable super fast.
# I'll deal with that mess later on, if I determine I need to.
# In the meantime, I'll separately consider constants and 2-predicate-one-object rules.

# Ooh, what about predicates that are only removed and never added? Like the pellets in Pacman.
# Maybe I'll just ignore length-1 rules entirely for now.

# And when should I look at the preconditions of the actions?
# This'd allow statements like "P is only added if Q is present"
# and "Q is never removed if P is present"
# their combination implying that objects with P and Q are a subset of those with only Q, and none can be created with only P
# But the whole purpose of this exercise is to give trajectory2 more accurate preconditions 
# (specifically to help it make up its mine on this like "Should the precondition for this action be is-goal or NOT is-nongoal?")
# so let's ignore this for now, too.

# Hmm...is-goal and is-nongoal are both constants. Maybe I should put some code into identifying those.

# Regardless, th next step is to combine the weak rules formatted above into stronger rules.
# How to represent these?
# Maybe with three booleans, indicating whether or not a given object can have zero, one, or two of the given predicates at the same time?
# So goal/nongoal would be [0 1 0], meaning that there can only ever be one of those predicates on an object at a time after it's been touched by an action; never none or both.
# And two predicates that are always added and removed together would be [1 0 1]
# What are all eight possibilities?
# [0 0 0] is flat-out impossible
# [1 0 0] means neither predicate ever shows up, so they may as well not even exist
# [0 1 0] means they're mutually exclusive and exhaustive, as previously discussed
# [1 1 0] means an object can have zero or one predicate: One or the other, or neother of them, but not both at one. "Mutually exclusive, but not exhaustive".
#   Recognizing this one would require elementary rules for "P is never added if Q present to begin with and not simultaneously being removed"
#   which I don't have plans for at the moment
# [0 0 1] means both always exist, and are never removed
# [1 0 1] means they're always added and removed together, as mentioned above
# [0 1 1] means one or two always exist, but neither can be removed if the other is already present
# [1 1 1] mwans each can exist with or without the other. Maybe there's restrictions on the order in which they can be added and removed, but they're pretty much independent.
# So... of those eight options, four are useless, and two of the rest require information that I'm currently not giving myself access to.
# Nonetheless, I think I'll stick with this representation until I think of something better.

# So... the next step would be to check the initial state, and see if conditions present there are maintained by the refined rules described above.
# Or, rather, if the refined rules described above maintain conditions that happen to be present in the initial state.
# This'd be real simple; for each "mutually exclusive and exhaustive" condition, check every object it could apply to in the initial state,
#   and if each object has exactly one of the associated predicates in the initial state, mark the rule as verified. A proper Invariant.
# And ditto for the "both or neither" rules.
# And for the "zero or one" and "one or two" rules. It shouldn't be hard to write code that'll work for all eight options.

# Then, once I've got the invariants sorted out, go back to trajectory2 (or, more likeky, go forward to trajectory3, which'll be a new trajectory script designed to take this info into account)
# and find a way for it to, well, account for this info.
# Look at the list of "I couldn't decide if some action failed because of this or that", look up 'this' and 'that' in the invariants,
# and if 'this' and 'that' turn out to be equivalent, then include both as preconditions.
# I'll include both, and not pick one at random, because that might give more information to code I may write in the future.
# And picking one arbitrarily seems wrong, somehow.

# I think that's about as far as I can get with this for now. I'll imlpement all that, then run it a few times and see what comes out.
# That'll help inform where I need to make improvements.

import pprint

def flattenEffects(act):
    for pos in act.positiveEffects:
        yield (pos, True)
    for neg in act.negativeEffects:
        yield (neg, False)

class invariants:
    def __init__(self, traj):
        print ('=== Candidate Primitive Rules ===')
        self.candidatePRs = {}
        self.PRs = set()
        self.mutablePredicates = set()
        for act in traj.actions.values():
            self.candidatePRs[act.name] = set()
            print('Action: {}'.format(act.name))
            for p, pAdds in flattenEffects(act):
                self.mutablePredicates.add(p[0])
                for q, qAdds in flattenEffects(act):
                    if p != q:
                        # At this point, p and q are two different effects of the same action.
                        # Should be, anyway.
                        # print(' {} {} and {} {}'.format(pAdds, p, qAdds, q))
                        for i, arg in enumerate(p[1:]):
                            try:
                                j = q.index(arg, 1) - 1
                                print(' {} {}[{}] and {} {}[{}] {}'.format(pAdds, p, i, qAdds, q, j, arg))
                                # Aight, here we're iterating through each pair of effects that share an argument
                                # So now we... what, write them down and then cross off the ones that aren't consistent across all the actions?
                                pr = primitiveRule(p[0], i, pAdds, q[0], j, qAdds)
                                self.candidatePRs[act.name].add(pr)
                                self.PRs.add(pr)
                            except ValueError:
                                continue
        for actL, rulesL in self.candidatePRs.items():
            for actR, rulesR in self.candidatePRs.items():
                if actL != actR:
                    # Here I'm iterating through each non-repeating ordered pair of actions, with the previously-computed rules of each available
                    for ruleL in rulesL:
                        if ruleL in rulesR:
                            # Both actions have this same rule, so it's still a candidate for that 'always' classification
                            continue
                        else:
                            # If any rules in rulesR match the 'q' part of ruleL (and we already know none of these also match the 'p' part), ruleL is not always true
                            ruleBroken = False
                            for ruleR in rulesR:
                                if ruleL.qname == ruleR.qname and ruleL.qarg == ruleR.qarg and ruleL.qadded == ruleR.qadded:
                                    ruleBroken = True
                                    break
                            if ruleBroken:
                                self.PRs.discard(ruleL)
        # Now, the things in self.PRs should only be the ones that are true for all actions
        print()
        print('=== Primitive Rules ===')
        for rule in self.PRs:
            print()
            print(rule)
            print(rule.matrix())
        # Now... I think I want to tackle constants next
        print()
        print('=== Constants ===')
        print()
        self.constants = set(traj.predicates.keys()).difference(self.mutablePredicates)
        print(self.constants)
        # Determine what invariant holds for each pair of constants
        initialState = traj.states[0]
        initialGroundedConstants = set()
        initialGroundedVariables = set()
        for pred in initialState:
            if pred[0] in self.constants:
                initialGroundedConstants.add(tuple(pred))
            else:
                initialGroundedVariables.add(tuple(pred))
        print('\nGrounded Constants:\n')
        pprint.pprint(initialGroundedConstants)
        print('\nGrounded Variables:\n')
        pprint.pprint(initialGroundedVariables)
        # For each constant
        # consideredConstants = self.constants.copy()
        # for p in self.constants:
        #     consideredConstants.remove(p)
        #     # For each other constant in that set listed after it
        #     for q in consideredConstants:
        #         print(p, q)
        #         # For each argument of the first constant
        #         for pi, parg in enumerate(traj.predicates[p]):
        #             # For each argument of the second
        #             for qi, qarg in enumerate(traj.predicates[q]):
        #                 print(parg, pi, ', ', qarg, qi)
        #                 # If the arguments have the same type list
        #                 if parg == qarg:
        #                     print(parg)
        #                     # For each object of any of those types
        #                     mat = ((False, False), (False, False))
        #                     for typ in parg:
        #                         for obj in traj.types2objs[typ]:
        #                             print(obj)
        #                             # Determine if the object has the first constant
        #                             hasP = any([pred[0] == p and pred[pi+1] == obj for pred in initialGroundedConstants])
        #                             # Determine if the object has the second constant
        #                             hasQ = any([pred[0] == q and pred[qi+1] == obj for pred in initialGroundedConstants])
        #                             # Note whether the first and second constants are present on it in the initial state in the form of a matrix
        #                             mat = matrixOr(mat, genSingletonMat(hasP, hasQ))
        #                     # OR all those matrices together
        #                     print(mat)
        #                     # Record an invariant using the OR'd matrix
        #                     print(invariant(p, pi, q, qi, mat))
        self.initialStateAnalysis = analyzeState(initialState, set(traj.predicates.keys()), traj)


        # Next, sort through those primitive rules, and find the ones that add up to a proper invariant
        print()
        print('=== Invariants ===')
        # OK, I've got my primitive rules, I've got my invariant data structure; how to get from one to the other?
        # The only invariant operators I can get from the info I have are XOR and XNOR
        # And those each require the same two predicates and the same two arguments in four separate primitive rules.
        # So that's what I'll look for.
        matchedPreds = []
        self.actionInvariants = []
        for p in self.PRs:
            if p not in matchedPreds:
                matches = [p]
                for q in self.PRs:
                    if q is not p and q not in matchedPreds:
                        if p.matches(q):
                            matches.append(q)
                print()
                if len(matches) == 4:
                    print('Found tetra-match!')
                    matchedPreds.extend(matches)
                    first = matches[0]
                    pname = first.pname
                    matrix = ((False, False), (False, False))
                    for m in matches:
                        for n in matches:
                            if n is not m:
                                if m.equalsReversed(n):
                                    tmp = m.matrix() if m.pname == pname else m.matrixTransposed()
                                    matrix = matrixOr(matrix, tmp)
                    inv = invariant(first.pname, first.parg, first.qname, first.qarg, matrix)
                    self.actionInvariants.append(inv)
                    for match in matches:
                        print(match)
                    for match in matches:
                        print(match.matrix())
                    print(inv)
                else:
                    print('Found set of {} matches'.format(len(matches)))
                    for match in matches:
                        print(match)
                    for match in matches:
                        print(match.matrix())
        # Compare the invariants divined from the action effects to those taken from the initial state
        self.invariantList = []
        for actInv in self.actionInvariants:
            for stateInv in self.initialStateAnalysis:
                modifiedStateInv = actInv.match(stateInv)
                if modifiedStateInv is not None:
                    print()
                    print('From action analysis: ', actInv)
                    print('From initial state analysis: ', modifiedStateInv)
                    inv = invariant(actInv.pname, actInv.parg, actInv.qname, actInv.qarg, matrixOr(actInv.op_tuple, modifiedStateInv.op_tuple))
                    print('Recording: ', inv)
                    self.invariantList.append(inv)
        # Filter the invariants from the initial state analysis for those that only describe constants
        for stateInv in self.initialStateAnalysis:
            if stateInv.pname in self.constants and stateInv.qname in self.constants:
                self.invariantList.append(stateInv)
        print('\n=========== Got The Invariants ==============\n')
        pprint.pprint(self.invariantList)

def analyzeState(state, preds, traj):
    out = []
    consideredPreds = preds.copy()
    for p in preds:
        consideredPreds.remove(p)
        # For each other constant in that set listed after it
        for q in consideredPreds:
            print(p, q)
            # For each argument of the first constant
            for pi, parg in enumerate(traj.predicates[p]):
                # For each argument of the second
                for qi, qarg in enumerate(traj.predicates[q]):
                    print(parg, pi, ', ', qarg, qi)
                    # If the arguments have the same type list
                    if parg == qarg:
                        print(parg)
                        # For each object of any of those types
                        mat = ((False, False), (False, False))
                        for typ in parg:
                            for obj in traj.types2objs[typ]:
                                # Determine if the object has the first constant
                                hasP = any([pred[0] == p and pred[pi+1] == obj for pred in state])
                                # Determine if the object has the second constant
                                hasQ = any([pred[0] == q and pred[qi+1] == obj for pred in state])
                                # Note whether the first and second constants are present on it in the initial state in the form of a matrix
                                newMat = genSingletonMat(hasP, hasQ)
                                mat = matrixOr(mat, newMat)
                                print(obj, hasP, hasQ)
                        # OR all those matrices together
                        print(mat)
                        # Record an invariant using the OR'd matrix
                        inv = invariant(p, pi, q, qi, mat)
                        print(inv)
                        out.append(inv)
    return out


def matrixOr(a, b):
    c = a[0][0] or b[0][0]
    d = a[0][1] or b[0][1]
    e = a[1][0] or b[1][0]
    f = a[1][1] or b[1][1]
    return ((c, d), (e, f))

def matrixTranspose(a):
    c = a[0][0]
    d = a[1][0]
    e = a[0][1]
    f = a[1][1]
    return ((c, d), (e, f))

def genSingletonMat(a, b):
    out = [[False, False], [False, False]]
    a = 1 if a else 0
    b = 1 if b else 0
    out[a][b] = True
    return tuple(map(tuple, out))

class primitiveRule:
    # Encodes statements like this:
    # P is (only | always) (added | removed) when Q is (added | removed)
    # Actually, since this is true:
    # [P is always added when Q is removed] <==> [Q is only removed when P is added]
    # I can drop the (only | always) bit, and just use 'always' for everything, since an 'only' can be turned into an 'always' by swapping the order of the predicates.
    # And I also need to specify what object the predicates are being added to or removed from.

    def __init__(self, pname, parg, padded, qname, qarg, qadded):
        self.pname = pname
        self.parg = parg
        self.padded = padded
        self.qname = qname
        self.qarg = qarg
        self.qadded = qadded

    def __str__(self):
        pverb = 'added to' if self.padded else 'removed from'
        qverb = 'added to' if self.qadded else 'removed from'
        return 'Predicate {} is always {} its {}th argument when {} is {} its {}th.'.format(self.pname, pverb, self.parg, self.qname, qverb, self.qarg)

    def __eq__(self, other):
        return (self.pname == other.pname
                and self.parg == other.parg
                and self.padded == other.padded
                and self.qname == other.qname
                and self.qarg == other.qarg
                and self.qadded == other.qadded)

    def __hash__(self):
        return hash((self.pname, self.parg, self.padded, self.qname, self.qarg, self.qadded))

    # Returns true iff self and other apply to the same arguments of the same predicates
    # Four primitive rules that mutually match by this function make an invariant
    def matches(self, other):
        return ((self.pname == other.pname and self.qname == other.qname
            and self.parg == other.parg and self.qarg == other.qarg)
            or (self.pname == other.qname and self.qname == other.pname
            and self.parg == other.qarg and self.qarg == other.parg))

    # Returns a pair of pairs of booleans; three False, one True; with the True representing the present/absent state of the two predicates
    # after an action conforming to this primitive rule is triggered
    # Format is the same as that used by invariant operators, as shown below
    def matrix(self):
        out = [[False, False], [False, False]]
        a = 1 if self.padded else 0
        b = 1 if self.qadded else 0
        out[a][b] = True
        return tuple(map(tuple, out))

    def matrixTransposed(self):
        out = [[False, False], [False, False]]
        a = 1 if self.padded else 0
        b = 1 if self.qadded else 0
        out[b][a] = True
        return tuple(map(tuple, out))

    # Return true iff this rule's p fields equal the other's q fields, and vice versa, meaning they together describe an "always and only" relationship
    def equalsReversed(self, other):
        return (self.pname == other.qname
                and self.parg == other.qarg
                and self.padded == other.qadded
                and self.qname == other.pname
                and self.qarg == other.parg
                and self.qadded == other.padded)


# ops[0][0]: Both absent
# ops[0][1]: Second present, first absent
# ops[1][0]: First present, second absent
# ops[1][1]: Both present

# [[AA, AP],[PA, PP]]

ops = {'NONE' : ((False, False), (False, False)),      #                       Neither predicate is allowed to be present or absent... which is impossible
        'AND'  : ((False, False), (False, True )),     # AND operator    &&    Both predicates must be present at all times, for all applicable objects
        'RNIM' : ((False, False), (True , False)),     # reversed NIMP   <-/-  First predicate must be present, second must be absent
        'FST'  : ((False, False), (True , True )),     #                       First predicate must be present, disregard second
        'NIMP' : ((False, True ), (False, False)),     # negated IMPLIES -/->  First predicate must be absent, second must be present
        'SEC'  : ((False, True ), (False, True )),     #                       Second predicate must be present, disregard first
        'XOR'  : ((False, True ), (True , False)),     # XOR operator    !=    Exactly one predicate must be present at all times, and not both
        'OR'   : ((False, True ), (True , True )),     # OR operator     ||    At least one predicate must be present at all times (or both)
        'NOR'  : ((True , False), (False, False)),     # NOR operator          Neither predicate is ever allowed to be present
        'XNOR' : ((True , False), (False, True )),     # XNOR operator   ==    Either both predicates are mresent, or both are absent
        'NSEC' : ((True , False), (True , False)),     #                       Second predicate must be absent; disregard first
        'REVI' : ((True , False), (True , True )),     # reversed IMPLIES <--  Like IMPL, but with the arguments reversed. If the second is present, the first must also be present.
        'NFST' : ((True , True ), (False, False)),     #                       First predicate must be absent, disregard second
        'IMPL' : ((True , True ), (False, True )),     # IMPLIES operator -->  If the first rpedicate is present, then the second must also be present (but if the first is absent, anything goes)
        'NAND' : ((True , True ), (True , False)),     # NAND operator         At least one predicate must always be absent (though the both can be at once)
        'ALL'  : ((True , True ), (True , True ))}     #                       Predicates are entirely independent of each other

rev_ops = {}
for k, v in ops.items():
    rev_ops[v] = k

inv_fmt = {'NONE' : "{0}[{1}] and {2}[{3}] are PARADOXICAL (meaning they're not allowed to be present, and they're not allowed to be absent... if you ever see this message, something's gone wrong)",
        'AND'  : '{0}[{1}] and {2}[{3}] are BOTH MANDATORY',
        'RNIM' : '{0}[{1}] is MANDATORY; {2}[{3}] is FORBIDDEN',
        'FST'  : '{0}[{1}] is MANDATORY; {2}[{3}] is IRRELEVANT',
        'NIMP' : '{0}[{1}] is FORBIDDEN; {2}[{3}] is MANDATORY',
        'SEC'  : '{0}[{1}] is IRRELEVANT; {2}[{3}] is MANDATORY',
        'XOR'  : '{0}[{1}] and {2}[{3}] are MUTUALLY EXCLUSIVE',
        'OR'   : 'AT LEAST ONE of {0}[{1}] and {2}[{3}] must be PRESENT',
        'NOR'  : '{0}[{1}] and {2}[{3}] are BOTH FORBIDDEN',
        'XNOR' : '{0}[{1}] and {2}[{3}] are EQUIVALENT',
        'NSEC' : '{0}[{1}] is IRRELEVANT; {2}[{3}] is FORBIDDEN',
        'REVI' : '{0}[{1}] IS IMPLIED BY {2}[{3}]',
        'NFST' : '{0}[{1}] is FORBIDDEN; {2}[{3}] is IRRELEVANT',
        'IMPL' : '{0}[{1}] IMPLIES {2}[{3}]',
        'NAND' : 'AT LEAST ONE of {0}[{1}] and {2}[{3}] must be ABSENT',
        'ALL'  : '{0}[{1}] and {2}[{3}] are INDEPENDENT'}

class invariant:
    # Not to be confused with the invariants class (note the plural), which analyzes invariants.
    # This class represents a single invariant.
    # Something like "any object of this type always has exactly one of these two predicates"
    # More generally, this class encodes what combinations of present and absent are permitted for two predicates attached to the same object.

    def __init__(self, pname, parg, qname, qarg, op):
        self.pname = pname
        self.qname = qname
        self.parg = parg
        self.qarg = qarg
        if op in ops:
            self.op_str = op
            self.op_tuple = ops[op]
        else:
            self.op_tuple = op
            self.op_str = rev_ops[op]

    # Apply this invariant's operator to two booleans
    def apply(self, p, q):
        a = 1 if p else 0
        b = 1 if q else 0
        return self.op_tuple[a][b]

    def match(self, other):
        if (self.pname == other.pname
                and self.parg == other.parg
                and self.qname == other.qname
                and self.qarg == other.qarg):
            return other
        elif (self.pname == other.qname
                and self.parg == other.qarg
                and self.qname == other.pname
                and self.qarg == other.parg):
            return invariant(other.qname, other.qarg, other.pname, other.parg, matrixTranspose(other.op_tuple))
        else:
            return None

    def __str__(self):
        return inv_fmt[self.op_str].format(self.pname, self.parg, self.qname, self.qarg)

    __repr__ = __str__

# Main
if __name__ == '__main__':
    import sys
    from blackout1 import trajectory
    filename = sys.argv[1]
    if len(sys.argv) > 3:
        traj = trajectory(filename, sys.argv[3])
    else:
        traj = trajectory(filename)
    invariants(traj)


