from __future__ import division, print_function, absolute_import

from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
import logging
import datetime
import sys
import os
import contextlib
import argparse

@contextlib.contextmanager
def use_folder(folder):
    """Step into an existing folder, then step back."""
    start_folder = os.getcwd()
    os.chdir(folder)
    yield
    os.chdir(start_folder)


def name_from_path(path):
    # XXX: check on Windows?
    if path.endswith('/'):
        path = path[:-1]
    head, tail = os.path.split(path)
    return tail.replace(' ', '_')


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
    return l


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
                self.cmd = [sys.executable, self.fname]
                success = True
            except Exception as e:
                logger.error("Compilation failed. Exception %s " % e)
                success = False
        return success

    def run(self, logger, inp=None):
        """Run the program in a subprocess. Grab the output.
        """
        logger.info("running %s < %s" % (self.fname, inp))
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


class FakeProgram(object):
    """Wrap a callable `func` into a Program-compatible interface."""
    def __init__(self, func, timeout):
        self.func = func
        self.timeout = timeout

    def compile(self, logger):
        return True

    def run(self, logger, inp=None):
        logger.info("calling %s < %s" % (self.func, inp))
        return self.func(inp), None


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


class Exercise(object):
    """An Exercise, a list of tasks with their weights.

    Each task is defined by an input and a weighting. `self.inputs` is a list
    of inputs for each task. `self.weights` gives weighting of each task, plus
    a possible mark allocation for the program to compile, out of 100 in total.
    That is, ``len(self.weights) == len(self.inputs) + 1``, with ``weights[0]``
    being the mark allocation for compilation. Total weight is 100.

    To construct an Exercise, construct an instance of `Exercise` with
    either a `base_program` (which can be either a path to a file or a Program
    instance), or a callable with the signature ``func(input)``.

    By default, the output is checked by literal comparison of the output with
    the ground truth. If this is not desired, subclass Exercise and redefine
    the `_check` method.

    To mark an Exercise use the `mark` method which returns the numeric mark.

    """
    def __init__(self, base_program, logger, timeout=60,
                 weights=None, inputs=None, *args, **kwds):
        super(Exercise, self).__init__(*args, **kwds)

        logger.info('Setting up exercise with base_program %s' % base_program)

        if callable(base_program):
            self.base_program = FakeProgram(base_program, timeout)
            self.timeout = timeout 
        elif isinstance(base_program, Program):
            self.base_program = base_program
            self.timeout = base_program.timeout
        else:
            raise NotImplementedError("what is it?")
            self.base_program = Program('.', base_program, logger, timeout)  ## FIXME: paths
            self.timeout = timeout

        logger.info('Compiling the base_program.')
        s = self.base_program.compile(logger)
        if not s:
            raise ValueError("%s compile error" % self.base_program)

        self._set_up_weights(inputs, weights, logger)
        logger.info('Done setting up the exercise.')

    def _set_up_weights(self, inputs, weights, logger):
        if inputs is None:
            inputs = [""]
        if weights is None:
            weights = [20.0] + [80.0/len(inputs) for _ in inputs]
        if len(weights) != len(inputs) + 1:
            mesg = "Weights %s and inputs %s are inconsistent" % (weights, inputs)
            logger.error(mesg)
            raise ValueError(mesg)
        self.weights, self.inputs = weights, inputs

    def _check(self, inp, outp, base_outp):
        """ Compare the outputs given input. 

        Subclass and override this method if you want a different way of
        of checking correctness (e.g. np.allclose, etc).

        """
        return 1 if outp.splitlines() == base_outp.splitlines() else 0

    def mark(self, folder, logger, timeout=None):
        logger.info("*** Marking %s ***" % folder)

        if timeout is None:
            timeout = self.timeout

        submission = Submission(folder)
        program = Program(submission.folder, submission.fname, logger, timeout)

        with use_folder(submission.folder):
            # start marking
            mark = 0

            # compile
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

    def grade(self, *args, **kwds):
        """An alias for `mark`."""
        return self.mark(*args, **kwds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path",
                        help="Path to exercise folder or a single exercise.")
    parser.add_argument("--only", action="store_true",
                        help="Only mark a single exercise at path.")
    args = parser.parse_args()

    a_path = os.path.abspath(args.path)
    if not os.path.exists(a_path):
        raise ValueError("Path %s does not exist" % args.path)

    # figure out the root folder:
    #    if marking a single submission, root is os.getcwd()
    root_dir = args.path
    if args.only:
        root_dir = os.getcwd()

    # set up the root logger
    root_logger = setup_logger('root',
                               log_file=os.path.join(root_dir, 'root_log.log'))

    # XXX: select the correct exercise
    from fizzbuzz import fizzbuzz_check
    ex = Exercise(fizzbuzz_check, logger=root_logger, inputs=[21, 11])

    if args.only:
        # set up the per-student logger
        path = args.path
        name = name_from_path(path)
        this_logger = setup_logger(logger_name=name,
                                   log_file=os.path.join(path, name + '.log'))

        root_logger.info("Marking.. %s." % path)
        try:
            mark = ex.mark(path, this_logger)
        except Exception as e:
            root_logger.error("Unknown exception %s." % e)
        root_logger.info("Done, mark = %s." % mark)

    else:
        # walk: **Use abspaths, see os.walk docstring's last line**
        # root folder is path
        # The structure is 
        # root_dir
        #    - student_1
        #    - student_2
        #    - student_3
        # where each student_# is a directory with an executable. 
        root_path, dirs, fnames = next(os.walk(root_dir))
        for folder in dirs:
            ppath = os.path.join(root_path, folder)
            name = name_from_path(ppath)
            this_logger = setup_logger(logger_name=name,
                                       log_file=os.path.join(ppath, name + '.log'))

            root_logger.info("Marking.. %s." % ppath)
            try:
                mark = ex.mark(ppath, this_logger)
            except Exception as e:
                root_logger.error("Unknown exception %s." % e)
            root_logger.info("Done, mark = %s." % mark)

