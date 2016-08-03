from __future__ import division, print_function, absolute_import

from subprocess import STDOUT, check_output, TimeoutExpired
from subprocess import Popen, PIPE
import logging
import datetime
import os


class Program(object):
    def __init__(self, path, logger, timeout=None, *args, **kwds):
        super(Program, self).__init__(*args, **kwds)
        self.path = path
        self.timeout = timeout if timeout else 60
        comp = self.compile(path, logger)
        if not comp:
            raise RuntimeError("Compilation failed.")

    def compile(self, path, logger):
        """ Compile the code at `path`. Return True/False for success status.
        """
        # FIXME: change w.dir, refactor the python-specific part to _compile.
        logger.info(">>> Compiling %s ..." % path)

        try:
            self.cmd = ["python", self.path]
        except:
            logger.error("compilation failed.")
            return False
        logger.info("compilation success!")
        return True

    def run(self,  logger, inp=None):
        """Run the program in a subprocess. Grab the output.
        """
        logger.info("running %s < %s" % (self.path, inp))
        inp_ = str(inp) if inp is not None else ""
        try:
            inp_ = str(inp)
            p = Popen(self.cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                      universal_newlines=True)
            output, err = p.communicate(input=inp_, timeout=self.timeout)
        except TimeoutExpired:
            logger.error("Timeout!")
            p.kill()
            output, err = "", None
        return output



if __name__ == "__main__":

    # main level
    logger = logging.getLogger('robo')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    # single excercise, single student etc
    logfname = 'fb.log'
    if os.path.exists(logfname):
        os.remove(logfname)
 ##   logger.handlers = []

    handler = logging.FileHandler(logfname)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    fname = "fizzbuzz.py"
    program = Program(fname, logger, timeout=1)
    outp = program.run(logger=logger, inp=21)
    print(outp)
