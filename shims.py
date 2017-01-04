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

import numpy as np

from marking import Exercise

import lab_1


class Ex1_7(Exercise):
    """Shim for Ex1.7: machine epsilon, zero, inf."""
    def __init__(self, *args, **kwds):
        super(Ex1_7, self).__init__(*args, **kwds)

    def _parse_output(self, inp, outp, this_logger):
        # _check expects a list of floats. Extract these floats from `outp`
        # (which comes from the student).
        split_outp = outp.replace(', ', ' ').split()
        split_outp = [float(_) for _ in split_outp]
        return split_outp

    def _check(self, inp, outp, base_outp, this_logger):
        eps, zero, inf = outp
        eps_ok = (eps > 0) and (1 + eps/2 == 1) and (1 + eps != 1)
        zero_ok = (zero > 0) and (zero/2 == 0)
        inf_ok = (inf < float('inf') and inf*4 == float('inf'))
        return 100 * (int(eps_ok) + int(zero_ok) + int(inf_ok)) / 3


def get_ex1_7(*args, **kwds):
    """Create an instance of Ex7 class with correct solve-func.
    """
    return Ex1_7(lab_1.Problem7().solve, *args, **kwds)



class ExQ(Exercise):
    """Quadratic equation."""
    def __init__(self, *args, **kwds):
        super(ExQ, self).__init__(*args, **kwds)

    def _prepare_input(self, inp):
        return str(inp['b']) + '\n' + str(inp['c'])

    def _parse_output(self, inp, outp, this_logger):
        # FIXME: copy-paste from Ex1_7: move to the superclass?
        #
        # _check expects a list of floats. Extract these floats from `outp`
        # (which comes from the student).
        outp = outp.rstrip()
        if outp.startswith('(') and outp.endswith(')'):
            outp = outp[1:-1]
        split_outp = outp.replace(', ', ' ').split()
        split_outp = [complex(_) for _ in split_outp]
        return split_outp

    def _check(self, inp, outp, base_outp, this_logger):
        # FIXME: sort based on... ?
        outp = sorted(outp, key=abs)
        base_outp = sorted(base_outp, key=abs)

        res1 = np.allclose(outp[0], base_outp[0])
        res2 = np.allclose(np.prod(outp), inp['c'])
        return 100 * int(res1 and res2)

def get_ex_q(*args, **kwds):
    """Create an instance of ExQ class with correct solve-func.
    """
    p = lab_1.ProblemQ()
    return ExQ(p.solve, inputs=p.variants, **kwds)


######### a toy example
def get_fizzbuzz(*args, **kwds):
    from fizzbuzz import fizzbuzz_check
    kwds.update({"inputs": [21, 11]})
    ex = Exercise(fizzbuzz_check, *args, **kwds)
    return ex
########################

