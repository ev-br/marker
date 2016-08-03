from __future__ import division, print_function, absolute_import

from subprocess import STDOUT, check_output, TimeoutExpired
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
            logger.error(">>> compilation failed.")
            return False
        logger.info(">>> compilation success!")
        return True

    def run(self,  logger, inp=None):
        """Run the program. Grab the output."""
        logger.info(">>> running %s " % (self.path,))
        try:
            output = check_output(self.cmd, stderr=STDOUT, timeout=self.timeout)
        except TimeoutExpired:
            logger.error(">>> Timeout!")
            return b""
        return output




if __name__ == "__main__":

    # main level
    logger = logging.getLogger('robo')
    logger.setLevel(logging.DEBUG)

    # single excercise, single student etc
    logfname = 'fb.log'
    if os.path.exists(logfname):
        os.remove(logfname)
    logger.handlers = []
    logger.addHandler(logging.FileHandler(logfname))
    logger.info('>> On %s' % datetime.datetime.now())

    fname = "fizzbuzz.py"
    program = Program(fname, logger, timeout=1)
    outp = program.run(logger=logger) 
    print(outp.decode('utf-8'))
