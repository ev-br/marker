from __future__ import division, print_function, absolute_import

from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
import logging
import datetime
import os
import contextlib

@contextlib.contextmanager
def use_folder(folder):
    """Step into an existing folder, then step back."""
    start_folder = os.getcwd()
    os.chdir(folder)
    yield
    os.chdir(start_folder)


def setup_logger(logger_name, log_file, level=logging.INFO):
    # http://stackoverflow.com/questions/17035077/python-logging-to-multiple-log-files-from-different-classes
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)


class Program(object):
    def __init__(self, folder, fname, logger, timeout=None, *args, **kwds):
        super(Program, self).__init__(*args, **kwds)

        self.workdir = os.path.abspath(folder)
        self.fname = fname

        self.timeout = timeout if timeout else 60
        self.cmd = None

    def compile(self, logger):
        """ Compile the code. Return True/False for success status.
        """
        # XXX: refactor the python-specific part to _compile.
        logger.info("Compiling %s ..." % self.fname)

        with use_folder(self.workdir):
            try:
                self.cmd = ["python", self.fname]
                success = True
                logger.info("compilation success!")
            except:
                logger.error("compilation failed.")
                success = False
        return success

    def run(self, logger, inp=None):
        """Run the program in a subprocess. Grab the output.
        """
        logger.info("running %s < %s" % (os.path.join(self.workdir, self.fname), inp))
        inp_ = str(inp) if inp is not None else ""
        with use_folder(self.workdir):
            try:
                inp_ = str(inp)
                p = Popen(self.cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                          universal_newlines=True)
                output, err = p.communicate(input=inp_, timeout=self.timeout)
            except TimeoutExpired:
                logger.error("Timeout!")
                p.kill()
                output, err = "", None
        return output, err


class Submission(object):
    """A student's submission. Given a folder, find an executable file.

    Attributes
    ----------
    folder : str
        The absolute path to the submission folder
    fname : str
        The name of the executable, relative to self.folder
    """
    def __init__(self, folder, kind='python', *args, **kwds):
        super(Submission, self).__init__(*args, **kwds)
        if not os.path.isdir(folder):
            raise ValueError("Expect a directory, got %s." % folder)
        self.folder = os.path.abspath(folder)

        # find the exectutable
        self.fname = None
        for f in os.listdir(self.folder):
            if self._is_executable(f):
                self.fname = f
                break
        else:
            # did not find it
            raise ValueError("Failed to find an executable in %s." % folder)

    def _is_executable(self, f):
        """Replace for non-python executables."""
        return f.endswith('.py')


class Excercise(object):
    def __init__(self, base_program, logger, timeout=60,
                 weights=None, inputs=None, *args, **kwds):
        super(Excercise, self).__init__(*args, **kwds)

        if isinstance(base_program, Program):
            self.base_program = base_program
            self.timeout = base_program.timeout
        else:
            self.base_program = Program('.', base_program, logger, timeout)  ## FIXME: paths
            self.timeout = timeout

        logger.info('Compiling the base_program.')
        s = self.base_program.compile(logger)
        if not s:
            raise ValueError("%s compile error" % self.base_program)

        if inputs is None:
            inputs = [""]
        if weights is None:
            weights = [20.0] + [80.0/len(inputs) for _ in inputs]
        if len(weights) != len(inputs) + 1:
            raise ValueError("Weights %s and inputs %s are inconsistent" %
                             (weights, inputs))
        self.weights, self.inputs = weights, inputs
        logger.info('Done setting up the Excercise.')

    def _check(self, inp, outp, base_outp):
        """ Compare the outputs given input. 

        Subclass and override this method if you want a different way of
        of checking correctness (e.g. np.allclose, etc).

        """
        return 1 if outp == base_outp else 0

    def mark(self, folder, logger, timeout=None):
        if timeout is None:
            timeout = self.timeout

        submission = Submission(folder)
        program = Program(submission.folder, submission.fname, logger, timeout)

        with use_folder(submission.folder):
            # start marking
            mark = 0

            # compile
            logger.info("Compiling the submission...")
            success = program.compile(logger)
            if success:
                mark = self.weights[0]
            else:
                logger.info("Compilation failed, done marking. Mark = %s." % mark)
                return mark
            logger.info("Compilation success, mark = %s." % mark)
                    
            for inp, weight in zip(self.inputs, self.weights[1:]):
                logger.info("Checking input = %s" % inp)
                outp, err = program.run(logger, inp)
                base_outp, base_err = self.base_program.run(logger, inp)

                if base_err and not err:
                    logger.error("base_stderr is %s " % base_err)
                    raise ValueError("base_err is %s for input %s " % (inp, base_err))
                if err:
                    logging.error("stderr is %s." % err)
                    continue

                result = self._check(inp, outp, base_outp) 
                mark += result * weight
                logger.info("result is %s, mark is %s out of %s." % (result,
                            mark, sum(self.weights)))
        logger.info("Done marking: %s out of %s" % (mark, sum(self.weights)))
        return mark


if __name__ == "__main__":

    setup_logger('root', log_file='root_log.log')
    root_logger = logging.getLogger('root')

    # Mark a single excercise
    fname = "fizzbuzz.py"
    exc = Excercise(fname, logger=root_logger, inputs=[21, ""])

    # mark a single student: here's the submission folder
    folder = "FB"

    # set up the per-student logger
    setup_logger(logger_name=folder, log_file=os.path.join(folder, 'log.log'))
    this_logger = logging.getLogger(folder)

    # mark
    mark = exc.mark('FB', this_logger)
    print("mark = ", mark)
