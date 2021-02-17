#!/usr/bin/env python

from PDDL import PDDL_Parser
import pprint
import sys
import time
import blackout2
import invariants

class trajectory3(blackout2.trajectoryRevised):


    def __init__(self, filename, domain='reconstructed'):
        super().__init__(filename, domain)  # Run all the code from my previous trajectory scripts
        self.times['wallclock_stage3_start'] = time.time_ns()
        self.times['process_stage3_start'] = time.process_time_ns()
        print('\n=========== Compute Invariants ==============\n')
        self.invariantsObject = invariants.invariants(self)
        self.invariantsList = self.invariantsObject.invariantList
        print('\n=========== Those Ambiguous Failed Actions Again ==============\n')
        pprint.pprint(self.ambiguities)
        print('\n=========== Find invariants that apply those ambiguities ==============\n')
        for actName, posCan, negCan in self.ambiguities:
            act = self.actions[actName]
            print('Analyzing action', actName)
            # posCan and negCan are sets of tuples, formatted as (predName, arg0, arg1...), where the arguments are formatted as action parameter names (e.g. ?4location).
            # Translate the two sets of tuples into a list of triples, formatted like this: (predName, isPresent, (arg0, arg1...)) where isPresent is a boolean
            # describing whether the predicate was present in the game state before the action was attempted.
            # posCan is a set of candidates for the positive precondition which caused the action to fail, i.e. predicates ABSENT in the before state
            # thus, that boolean in the second entry in the tuple is False
            candidates = [(p[0], False, p[1:]) for p in posCan]
            # conversely, for negCan, the boolean should be True
            candidates.extend([(p[0], True, p[1:]) for p in negCan])
            # Now, for every pair of different predicates in this combined candidates list
            for i in range(len(candidates)):
                for j in tuple(range(i)) + tuple(range(i+1, len(candidates))):
                    pname, ppresent, pargs = candidates[i]
                    qname, qpresent, qargs = candidates[j]
                    # For each argument of each of these predicates:
                    for parg, pargName in enumerate(pargs):
                        for qarg, qargName in enumerate(qargs):
                            print("  Analyzing ", pname, ppresent, parg, pargName, "with", qname, qpresent, qarg, qargName)
                            # If the chosen arguments refer to the same object (equivalently, they refer to the same parameter to the action on the same invocation of that action)
                            if pargName == qargName:
                                # Determine if there's an invariant that relates the selected predicates and arguments
                                for invariant in self.invariantsList:
                                    if (invariant.pname == pname
                                            and invariant.parg == parg
                                            and invariant.qname == qname
                                            and invariant.qarg == qarg):
                                        print("    Found matching invariant! ", invariant)
                                        # Now, what the heck do I do with this invariant?
                                        # The MUTUALLY EXCLUSIVE op_tuple ((False, True ), (True , False)) indicates that both-preds-present and both-preds-absent are forbidden states
                                        # I've got two candidates for a precondition, one saying "this predicate should be present" and the other saying "that predicate should be absent"
                                        # and I know that at least one of them must be factual, but I don't know which
                                        # Since the predicates are mutually exclusive, the presence of one implies the absence of the other
                                        # therefore, "this predicate is present" is equivalent to "that predicate is absent"
                                        # thus, either or both candidate preconditions could be included in the reconstructed domain file, and it would work the same
                                        # How to generalize?
                                        # I'll figure out how to handle each case individually, then look for a pattern
                                    # 'NONE' : ((False, False), (False, False)) don't worry about this one; throw error
                                    # 'AND'  : ((False, False), (False, True )) uninformative and probably impossible if the original domain was configured sensibly; throw error
                                    # 'RNIM' : ((False, False), (True , False)) similarly unlikely; throw error
                                    # 'FST'  : ((False, False), (True , True )) first predicate is irrelevant; confirm second precondition
                                    # 'NIMP' : ((False, True ), (False, False)) throw error
                                    # 'SEC'  : ((False, True ), (False, True )) second predicate is irrelevant; confirm first precondition
                                    # 'XOR'  : ((False, True ), (True , False)) mutually exclusive; can only occur w/ one posCan and one negCan; confirm both preconditions
                                    # 'OR'   : ((False, True ), (True , True ))
                                    # 'NOR'  : ((True , False), (False, False)) throw error
                                    # 'XNOR' : ((True , False), (False, True )) predicates are equivalent; confirm both preconditions
                                    # 'NSEC' : ((True , False), (True , False)) second predicate is irrelevant; confirm first precondition
                                    # 'REVI' : ((True , False), (True , True ))
                                    # 'NFST' : ((True , True ), (False, False)) first predicate is irrelevant; confirm second precondition
                                    # 'IMPL' : ((True , True ), (False, True ))
                                    # 'NAND' : ((True , True ), (True , False))
                                    # 'ALL'  : ((True , True ), (True , True )) no correlation; must let ambiguity continue; print warning
                                        # IMPL and its rotations are gonna take some more thought.
                                        # There are four cases when the invariant A ---> B appears:
                                        # A         B
                                        # present   present     one must be a negative precondition
                                        # present   absent      impossible; ignore
                                        # absent    present     either A is a positive precon, or B is a negative
                                        # absent    absent      one must be a positive precondition
                                        # ... This is going nowhere.
                                        # Need more what-if cases.
                                        # Aprecon   Bprecon     Astatus Bstatus OK? A-->B   ok&True bad&True
                                        # Required  Required    Present Present OK  True    Yes
                                        # Required  Required    Present Absent  bad
                                        # Required  Required    Absent  Present bad True            Yes
                                        # Required  Required    Absent  Absent  bad True            Yes
                                        # Required              Present Present OK  True    Yes
                                        # Required              Present Absent  OK
                                        # Required              Absent  Present bad True            Yes
                                        # Required              Absent  Absent  bad True            Yes
                                        # Required  Forbidden   Present Present bad True            Yes
                                        # Required  Forbidden   Present Absent  OK
                                        # Required  Forbidden   Absent  Present bad True            Yes
                                        # Required  Forbidden   Absent  Absent  bad True            Yes
                                        #           Required    Present Present OK  True    Yes
                                        #           Required    Present Absent  bad
                                        #           Required    Absent  Present OK  True    Yes
                                        #           Required    Absent  Absent  bad True            Yes
                                        #                       Present Present OK  True    Yes
                                        #                       Present Absent  OK
                                        #                       Absent  Present OK  True    Yes
                                        #                       Absent  Absent  OK  True    Yes
                                        #           Forbidden   Present Present bad True            Yes
                                        #           Forbidden   Present Absent  OK
                                        #           Forbidden   Absent  Present bad True            Yes
                                        #           Forbidden   Absent  Absent  OK  True    Yes
                                        # Forbidden Required    Present Present bad True            Yes
                                        # Forbidden Required    Present Absent  bad
                                        # Forbidden Required    Absent  Present OK  True    Yes
                                        # Forbidden Required    Absent  Absent  bad True            Yes
                                        # Forbidden             Present Present bad True            Yes
                                        # Forbidden             Present Absent  bad
                                        # Forbidden             Absent  Present OK  True    Yes
                                        # Forbidden             Absent  Absent  OK  True    Yes
                                        # Forbidden Forbidden   Present Present bad True            Yes
                                        # Forbidden Forbidden   Present Absent  bad
                                        # Forbidden Forbidden   Absent  Present bad True            Yes
                                        # Forbidden Forbidden   Absent  Absent  OK  True    Yes
                                        # ... Okay, if I'm at this point in the code, and I have an IMPLIES invariant
                                        # then I have to be in one of the rown with a True in the second-tolast column.
                                        # I also know what Astatus and Bstatus are. So let's make another table with the four possibilities for those.
                                        # Astatus   Bstatus Aprecon     Bprecon
                                        # Present   Present R_          R_
                                        # Present   Absent
                                        # Absent    Present _F          R_
                                        # Absent    Absent  _F          _F
                                        # ... So, what's this mean?
                                        # If both predicates are present, and the action succeeded, then neither precivate can be forbidden.
                                        # But I don't care about the times when the action succeeded.
                                        # So, let's do the same thing with the last column.
                                        # Astatus   Bstatus Aprecon     Bprecon
                                        # Present   Present R_F         R_F
                                        # Present   Absent
                                        # Absent    Present R_F         R_F
                                        # Absent    Absent  R_F         R_F
                                        # ... So the presence or absence of the predicates prior to the failed action tells me NOTHING AT ALL!
                                        # I've just wasted an hour and a half proving to myself that disambiguating three-True invariant matrices is totally impossible. Great. Just fantastic.
                                        # So there's just six cases I actually need to worry about:
                                        # XOR, XNOR, FST, NFST, SEC, NSEC
                                        toAdd = set()
                                        if invariant.op_str in {'XOR', 'XNOR'}:
                                            print('    Confirming both precondition candidates')
                                            toAdd.add(candidates[i])
                                            toAdd.add(candidates[j])
                                        elif invariant.op_str in {'FST', 'NFST'}:
                                            # print('    Confirming second precondition candidate')
                                            # toAdd.add(candidates[j])
                                            print('    First precondition candidate encodes no information; cannot confirm either candidate')
                                        elif invariant.op_str in {'SEC', 'NSEC'}:
                                            # print('    Confirming first precondition candidate')
                                            # toAdd.add(candidates[i])
                                            print('    Second precondition candidate encodes no information; cannot confirm either candidate')
                                        elif invariant.op_str in {'NONE', 'AND', 'RNIM', 'NIMP', 'NOR'}:
                                            print('    Before-state appears to break invariant; this is probably an error')
                                        elif invariant.op_str in {'OR', 'REVI', 'IMPL', 'NAND', 'ALL'}:
                                            print("    Cannot confirm either precondition because the predicates aren't sufficiently tightly correlated with each other")
                                        else:
                                            print('    Invariant operator code did not match any on file; this is definitely an error')
                                        for name, present, args in toAdd:
                                            precon = (name,) + args
                                            if not present:
                                                # If the predicate was absent, and the action failed, then it must be a positive precondition
                                                print('      Confirming positive precondition:', precon)
                                                act.defPosPrecons.add(precon)
                                            else:
                                                print('      Confirming negative precondition:', precon)
                                                act.defNegPrecons.add(precon)
        self.times['wallclock_stage3_end'] = time.time_ns()
        self.times['process_stage3_end'] = time.process_time_ns()
        self.times['wallclock_global_end'] = time.time_ns()
        self.times['process_global_end'] = time.process_time_ns()
        sys.stderr.write('\nStage 1 wall-clock time: {:,} nanoseconds\n'.format(self.times['wallclock_stage1_end'] - self.times['wallclock_stage1_start']))
        sys.stderr.write('Stage 1 process time:    {:,} nanoseconds\n'.format(self.times['process_stage1_end'] - self.times['process_stage1_start']))
        sys.stderr.write('Stage 2 wall-clock time: {:,} nanoseconds\n'.format(self.times['wallclock_stage2_end'] - self.times['wallclock_stage2_start']))
        sys.stderr.write('Stage 2 process time:    {:,} nanoseconds\n'.format(self.times['process_stage2_end'] - self.times['process_stage2_start']))
        sys.stderr.write('Stage 3 wall-clock time: {:,} nanoseconds\n'.format(self.times['wallclock_stage3_end'] - self.times['wallclock_stage3_start']))
        sys.stderr.write('Stage 3 process time:    {:,} nanoseconds\n'.format(self.times['process_stage3_end'] - self.times['process_stage3_start']))
        sys.stderr.write('Total   wall-clock time: {:,} nanoseconds\n'.format(self.times['wallclock_global_end'] - self.times['wallclock_global_start']))
        sys.stderr.write('Total   process time:    {:,} nanoseconds\n'.format(self.times['process_global_end'] - self.times['process_global_start']))



# Main
if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    if len(sys.argv) > 3:
        traj = trajectory3(filename, sys.argv[3])
    else:
        traj = trajectory3(filename)
    if len(sys.argv) > 2:
        fout = open(sys.argv[2], 'w')
    else:
        print('\n=========== Reconstructed PDDL Domain ==============\n')
        fout = sys.stdout
        print()
    fout.write(str(traj))


