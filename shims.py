"""
This collects shims between Problem/ProblemVariant classes (TheLibrary)
and Exercise runners.

For each Problem there is 
i) an Exercise subclass which specifies _parse_output and _check methods
ii) a factory function which creates an instance of the correct Exercise
    subclass *with* the correct solve-func, as defined by the Problem
    or standalone.

XXX: this all should be refactored at some point. On one hand, there's need for
subclassing because a Problem does not do e.g. _parse_output; OTOH, there an
Exercise instance needs to accept the solve-func in the constructor.
"""
from __future__ import division, print_function, absolute_import

from marking import Exercise

import lab_1


class Ex1_7(Exercise):
    def __init__(self, *args, **kwds):
        super(Ex1_7, self).__init__(*args, **kwds)

    def _parse_output(self, inp, outp, this_logger):
        # _check expects a list of floats. Extract these floats from `outp`
        # (which comes from the student).
        try:
            split_outp = outp.replace(', ', ' ').split()
            split_outp = [float(_) for _ in split_outp]
        except Exception as e:
            mesg = "Failed to parse the output: \n===\n %s\n===\n" % outp
            mesg += "Exception: %s " % e
            this_logger.error(mesg)
            return None
        return split_outp

    def _check(self, inp, outp, base_outp, this_logger):
        import numpy as np
        size = min(len(base_outp), len(outp))
        summ = sum(np.allclose(a, b) for a, b in zip(outp, base_outp))
        # TODO: more careful checks
        return 100 * summ / len(base_outp)

def get_ex1_7(*args, **kwds):
    """Create an instance of Ex7 class with correct solve-func.
    """
    return Ex1_7(lab_1.Problem7().solve, *args, **kwds)


######### a toy example
def get_fizzbuzz(*args, **kwds):
    from fizzbuzz import fizzbuzz_check
    kwds.update({"inputs": [21, 11]})
    ex = Exercise(fizzbuzz_check, *args, **kwds)
    return ex
########################

