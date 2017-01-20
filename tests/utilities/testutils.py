# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
"""
Test utilities for the EB CLI.

This module includes various classes/functions that help in writing
CLI unit/integration tests.  This module should not be imported by
any module **except** for test code.
"""
import binascii
import contextlib
import json
import logging
import os
import platform
import shutil
import sys
import tempfile
import six
from subprocess import Popen, PIPE

try:
    import mock
except ImportError as e:
    # In the off chance something imports this module
    # that's not suppose to, we should not stop the CLI
    # by raising an ImportError.  Now if anything actually
    # *uses* this module that isn't suppose to, that's s
    # different story.
    mock = None
import botocore.loaders

# The unittest module got a significant overhaul
# in 2.7, so if we're in 2.6 we can use the backported
# version unittest2.
if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest


# In python 3, order matters when calling assertEqual to
# compare lists and dictionaries with lists. Therefore,
# assertItemsEqual needs to be used but it is renamed to
# assertCountEqual in python 3.
if six.PY2:
    unittest.TestCase.assertCountEqual = unittest.TestCase.assertItemsEqual


_LOADER = botocore.loaders.Loader()
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger('ebcli.tests.integration')
EB_CMD = None


def skip_if_windows(reason):
    """Decorator to skip tests that should not be run on windows.

    Example usage:

        @skip_if_windows("Not valid")
        def test_some_non_windows_stuff(self):
            self.assertEqual(...)

    """
    def decorator(func):
        return unittest.skipIf(
            platform.system() not in ['Darwin', 'Linux'], reason)(func)
    return decorator


def set_invalid_utime(path):
    """Helper function to set an invalid last modified time"""
    try:
        os.utime(path, (-1, -100000000000))
    except (OSError, OverflowError):
        # Some OS's such as Windows throws an error for trying to set a
        # last modified time of that size. So if an error is thrown, set it
        # to just a negative time which will trigger the warning as well for
        # Windows.
        os.utime(path, (-1, -1))


def get_eb_cmd():
    global EB_CMD
    import ebcli
    if EB_CMD is None:
        # Try <repo>/bin/eb
        repo_root = os.path.dirname(os.path.abspath(ebcli.__file__))
        eb_cmd = os.path.join(repo_root, 'bin', 'eb')
        if not os.path.isfile(eb_cmd):
            eb_cmd = _search_path_for_cmd('eb')
            if eb_cmd is None:
                raise ValueError('Could not find "eb" executable.  Either '
                                 'make sure it is on your PATH, or you can '
                                 'explicitly set this value using '
                                 '"set_eb_cmd()"')
        EB_CMD = eb_cmd
        LOG.info('Using eb command from: {0}'.format(EB_CMD))
    return EB_CMD


def _search_path_for_cmd(cmd_name):
    for path in os.environ.get('PATH', '').split(os.pathsep):
        full_cmd_path = os.path.join(path, cmd_name)
        if os.path.isfile(full_cmd_path):
            return full_cmd_path
    return None


def set_eb_cmd(aws_cmd):
    global EB_CMD
    EB_CMD = aws_cmd


@contextlib.contextmanager
def temporary_file(mode):
    """This is a cross platform temporary file creation.

    tempfile.NamedTemporary file on windows creates a secure temp file
    that can't be read by other processes and can't be opened a second time.

    For tests, we generally *want* them to be read multiple times.
    The test fixture writes the temp file contents, the test reads the
    temp file.

    """
    temporary_directory = tempfile.mkdtemp()
    basename = 'tmpfile-%s' % str(random_chars(8))
    full_filename = os.path.join(temporary_directory, basename)
    open(full_filename, 'w').close()
    try:
        with open(full_filename, mode) as f:
            yield f
    finally:
        shutil.rmtree(temporary_directory)


def random_chars(num_chars):
    """Returns random hex characters.

    Useful for creating resources with random names.

    """
    return binascii.hexlify(os.urandom(int(num_chars / 2))).decode('ascii')


class CapturedRenderer(object):
    def __init__(self):
        self.rendered_contents = ''

    def render(self, contents):
        self.rendered_contents = contents.decode('utf-8')


class CapturedOutput(object):
    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr


@contextlib.contextmanager
def capture_output():
    stderr = six.StringIO()
    stdout = six.StringIO()
    with mock.patch('sys.stderr', stderr):
        with mock.patch('sys.stdout', stdout):
            yield CapturedOutput(stdout, stderr)


@contextlib.contextmanager
def capture_input(input_bytes=b''):
    input_data = six.BytesIO(input_bytes)
    if six.PY3:
        mock_object = mock.Mock()
        mock_object.buffer = input_data
    else:
        mock_object = input_data

    with mock.patch('sys.stdin', mock_object):
        yield input_data


class FileCreator(object):
    def __init__(self):
        self.rootdir = tempfile.mkdtemp()

    def remove_all(self):
        shutil.rmtree(self.rootdir)

    def create_file(self, filename, contents, mtime=None, mode='w'):
        """Creates a file in a tmpdir

        ``filename`` should be a relative path, e.g. "foo/bar/baz.txt"
        It will be translated into a full path in a tmp dir.

        If the ``mtime`` argument is provided, then the file's
        mtime will be set to the provided value (must be an epoch time).
        Otherwise the mtime is left untouched.

        ``mode`` is the mode the file should be opened either as ``w`` or
        `wb``.

        Returns the full path to the file.

        """
        full_path = os.path.join(self.rootdir, filename)
        if not os.path.isdir(os.path.dirname(full_path)):
            os.makedirs(os.path.dirname(full_path))
        with open(full_path, mode) as f:
            f.write(contents)
        current_time = os.path.getmtime(full_path)
        # Subtract a few years off the last modification date.
        os.utime(full_path, (current_time, current_time - 100000000))
        if mtime is not None:
            os.utime(full_path, (mtime, mtime))
        return full_path

    def append_file(self, filename, contents):
        """Append contents to a file

        ``filename`` should be a relative path, e.g. "foo/bar/baz.txt"
        It will be translated into a full path in a tmp dir.

        Returns the full path to the file.
        """
        full_path = os.path.join(self.rootdir, filename)
        if not os.path.isdir(os.path.dirname(full_path)):
            os.makedirs(os.path.dirname(full_path))
        with open(full_path, 'a') as f:
            f.write(contents)
        return full_path

    def full_path(self, filename):
        """Translate relative path to full path in temp dir.

        f.full_path('foo/bar.txt') -> /tmp/asdfasd/foo/bar.txt
        """
        return os.path.join(self.rootdir, filename)


class ProcessTerminatedError(Exception):
    pass


class Result(object):
    def __init__(self, rc, stdout, stderr, memory_usage=None):
        self.rc = rc
        self.stdout = stdout
        self.stderr = stderr
        LOG.debug("rc: %s", rc)
        LOG.debug("stdout: %s", stdout)
        LOG.debug("stderr: %s", stderr)
        if memory_usage is None:
            memory_usage = []
        self.memory_usage = memory_usage

    @property
    def json(self):
        return json.loads(self.stdout)


def _escape_quotes(command):
    # For windows we have different rules for escaping.
    # First, double quotes must be escaped.
    command = command.replace('"', '\\"')
    # Second, single quotes do nothing, to quote a value we need
    # to use double quotes.
    command = command.replace("'", '"')
    return command


def eb(command, collect_memory=False, env_vars=None,
       wait_for_finish=True, input_data=None, input_file=None):
    """Run an aws command.

    This help function abstracts the differences of running the "aws"
    command on different platforms.

    If collect_memory is ``True`` the the Result object will have a list
    of memory usage taken at 2 second intervals.  The memory usage
    will be in bytes.

    If env_vars is None, this will set the environment variables
    to be used by the aws process.

    If wait_for_finish is False, then the Process object is returned
    to the caller.  It is then the caller's responsibility to ensure
    proper cleanup.  This can be useful if you want to test timeout's
    or how the CLI responds to various signals.

    :type input_data: string
    :param input_data: This string will be communicated to the process through
        the stdin of the process.  It essentially allows the user to
        avoid having to use a file handle to pass information to the process.
        Note that this string is not passed on creation of the process, but
        rather communicated to the process.

    :type input_file: a file handle
    :param input_file: This is a file handle that will act as the
        the stdin of the process immediately on creation.  Essentially
        any data written to the file will be read from stdin of the
        process. This is needed if you plan to stream data into stdin while
        collecting memory.
    """
    if platform.system() == 'Windows':
        command = _escape_quotes(command)
    eb_command = 'python {0}'.format(get_eb_cmd())
    full_command = '{0} {1}'.format(eb_command, command)
    stdout_encoding = get_stdout_encoding()
    if isinstance(full_command, six.text_type) and not six.PY3:
        full_command = full_command.encode(stdout_encoding)
    LOG.debug("Running command: %s", full_command)
    env = os.environ.copy()
    env['AWS_DEFAULT_REGION'] = "us-east-1"
    if env_vars is not None:
        env = env_vars
    if input_file is None:
        input_file = PIPE
    LOG.info("Running command: eb {0}".format(command))
    process = Popen(full_command, stdout=PIPE, stderr=PIPE, stdin=input_file,
                    shell=True, env=env)
    if not wait_for_finish:
        return process
    memory = None
    if not collect_memory:
        kwargs = {}
        if input_data:
            kwargs = {'input': input_data}
        stdout, stderr = process.communicate(**kwargs)
    else:
        stdout, stderr, memory = _wait_and_collect_mem(process)
    return Result(process.returncode,
                  stdout.decode(stdout_encoding),
                  stderr.decode(stdout_encoding),
                  memory)


def get_stdout_encoding():
    encoding = getattr(sys.__stdout__, 'encoding', None)
    if encoding is None:
        encoding = 'utf-8'
    return encoding


def _wait_and_collect_mem(process):
    # We only know how to collect memory on mac/linux.
    if platform.system() == 'Darwin':
        get_memory = _get_memory_with_ps
    elif platform.system() == 'Linux':
        get_memory = _get_memory_with_ps
    else:
        raise ValueError(
            "Can't collect memory for process on platform %s." %
            platform.system())
    memory = []
    while process.poll() is None:
        try:
            current = get_memory(process.pid)
        except ProcessTerminatedError:
            # It's possible the process terminated between .poll()
            # and get_memory().
            break
        memory.append(current)
    stdout, stderr = process.communicate()
    return stdout, stderr, memory


def _get_memory_with_ps(pid):
    # It's probably possible to do with proc_pidinfo and ctypes on a Mac,
    # but we'll do it the easy way with parsing ps output.
    command_list = 'ps u -p'.split()
    command_list.append(str(pid))
    p = Popen(command_list, stdout=PIPE)
    stdout = p.communicate()[0]
    if not p.returncode == 0:
        raise ProcessTerminatedError(str(pid))
    else:
        # Get the RSS from output that looks like this:
        # USER       PID  %CPU %MEM      VSZ    RSS   TT  STAT STARTED      TIME COMMAND
        # user     47102   0.0  0.1  2437000   4496 s002  S+    7:04PM   0:00.12 python2.6
        return int(stdout.splitlines()[1].split()[5]) * 1024


def process_output(process):
    return "stdout: {0}\nstderr: {1}".format(process.stdout, process.stderr)

class TestEventHandler(object):
    def __init__(self, handler=None):
        self._handler = handler
        self._called = False

    @property
    def called(self):
        return self._called

    def handler(self, **kwargs):
        self._called = True
        if self._handler is not None:
            self._handler(**kwargs)