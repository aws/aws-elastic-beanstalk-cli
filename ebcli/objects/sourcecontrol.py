# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from __future__ import print_function
import os
import fileinput
import datetime
import sys

from cement.utils.misc import minimal_logger
from cement.utils.shell import exec_cmd

from ..resources.strings import git_ignore
from ..core.fileoperations import get_config_setting
from ..objects.exceptions import NoSourceControlError, CommandError, \
    NotInitializedError
from ..core import fileoperations, io

LOG = minimal_logger(__name__)


class SourceControl():
    name = 'base'

    def __init__(self):
        self.name = ''

    def get_name(self):
        return None

    def get_current_branch(self):
        pass

    def do_zip(self, location):
        pass

    def set_up_ignore_file(self):
        pass

    def get_version_label(self):
        pass

    @staticmethod
    def get_source_control():
        # First check for setting in config file
        try:
            git_installed = get_config_setting('global', 'sc')
        except NotInitializedError:
            git_installed = False

        if not git_installed:
            if Git().is_setup():
                return Git()
            else:
                return NoSC()

        return Git()


class NoSC(SourceControl):
    """
        No source control installed
    """
    def get_name(self):
        return None

    def get_version_label(self):
        # use timestamp as version
        suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        return 'app-' + suffix

    def get_current_branch(self):
        return 'default'

    def do_zip(self, location):
        io.log_info('Creating zip using systems zip')
        fileoperations.zip_up_project(location)

    def get_message(self):
        return 'EB-CLI deploy'

    def is_setup(self):
        pass

    def set_up_ignore_file(self):
        LOG.debug('No Source control installed')
        raise NoSourceControlError

    def clean_up_ignore_file(self):
        pass


class Git(SourceControl):
    """
        The user has git installed
        """

    def get_name(self):
        return 'git'

    def _handle_exitcode(self, exitcode, stderr):
        if exitcode == 0:
            return
        if exitcode == 127:
            # 127 = git not installed
            raise NoSourceControlError

        # Something else happened
        raise CommandError('An error occurred while handling git command.'
                           '\nError code: ' + str(exitcode) + ' Error: ' +
                           stderr)

    def get_version_label(self):
        io.log_info('Getting version label from git with git-describe')
        stdout, stderr, exitcode = \
            exec_cmd(['git', 'describe', '--always', '--abbrev=4'])
        if sys.version_info[0] >= 3:
            stdout = stdout.decode('utf8')
            stderr = stderr.decode('utf8')

        self._handle_exitcode(exitcode, stderr)

        #Replace dots with underscores
        return stdout[:-1].replace('.', '_')

    def get_current_branch(self):
        stdout, stderr, exitcode = \
            exec_cmd(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])

        if sys.version_info[0] >= 3:
            stdout = stdout.decode('utf8')
            stderr = stderr.decode('utf8')
        stdout = stdout.rstrip()
        self._handle_exitcode(exitcode, stderr)
        LOG.debug('git current-branch result: ' + stdout)
        return stdout

    def do_zip(self, location):
        io.log_info('creating zip using git archive HEAD')
        stdout, stderr, exitcode = \
            exec_cmd(['git', 'archive', '-v', '--format=zip',
                      '-o', location, 'HEAD'])
        if sys.version_info[0] >= 3:
            stderr = stderr.decode('utf8')
        self._handle_exitcode(exitcode, stderr)
        io.log_info('git archive output: ' + stderr)

    def get_message(self):
        stdout, stderr, exitcode = \
            exec_cmd(['git', 'log', '--oneline', '-1'])
        if sys.version_info[0] >= 3:
            stdout = stdout.decode('utf8')
            stderr = stderr.decode('utf8')
        self._handle_exitcode(exitcode, stderr)
        return stdout.rstrip().split(' ', 1)[1]

    def is_setup(self):
        return fileoperations.is_git_directory_present()

    def set_up_ignore_file(self):
        if not os.path.exists('.gitignore'):
            open('.gitignore', 'w')
        else:
            with open('.gitignore', 'r') as f:
                for line in f:
                    if line.strip() == git_ignore[0]:
                        return

        with open('.gitignore', 'a') as f:
            f.write(os.linesep)
            for line in git_ignore:
                f.write(line + os.linesep)

    def clean_up_ignore_file(self):
        cwd = os.getcwd()
        try:
            fileoperations._traverse_to_project_root()

            in_section = False
            for line in fileinput.input('.gitignore', inplace=True):
                if line.startswith(git_ignore[0]):
                    in_section = True
                if not line.strip():
                    in_section = False

                if not in_section:
                    print(line, end='')

        finally:
            os.chdir(cwd)
