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
import datetime
import fileinput
import os
import sys

from cement.utils.misc import minimal_logger
from cement.utils.shell import exec_cmd

from ..core import fileoperations, io
from ..objects.exceptions import NoSourceControlError, CommandError, \
    NotInitializedError
from ..resources.strings import git_ignore, strings

LOG = minimal_logger(__name__)


class SourceControl():
    name = 'base'

    def __init__(self):
        self.name = ''

    def get_name(self):
        return None

    def get_current_branch(self):
        pass

    def do_zip(self, location, staged=False):
        pass

    def set_up_ignore_file(self):
        pass

    def get_version_label(self):
        pass

    def untracked_changes_exist(self):
        pass

    @staticmethod
    def get_source_control():
        # First check for setting in config file
        try:
            git_installed = fileoperations.get_config_setting('global', 'sc')
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

    def do_zip(self, location, staged=False):
        io.log_info('Creating zip using systems zip')
        fileoperations.zip_up_project(location)

    def get_message(self):
        return 'EB-CLI deploy'

    def is_setup(self):
        pass

    def set_up_ignore_file(self):
        Git().set_up_ignore_file()

    def clean_up_ignore_file(self):
        pass

    def untracked_changes_exist(self):
        return False


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
            self._run_cmd(['git', 'describe', '--always', '--abbrev=4'])

        version_label = 'app-{}-{:%y%m%d_%H%M%S}'.format(stdout, datetime.datetime.now())
        #Replace dots with underscores
        return version_label.replace('.', '_')

    def untracked_changes_exist(self):
        stdout, stderr, exitcode = self._run_cmd(['git', 'diff', '--numstat'])
        LOG.debug('git diff --numstat result: ' + stdout +
                  ' with errors: ' + stderr)
        if stdout:
            return True
        return False

    def get_current_branch(self):
        try:
            stdout, stderr, exitcode = self._run_cmd(['git', '--version'])
            LOG.debug('Git Version: ' + stdout)
        except:
            raise CommandError('Error getting "git --version".')

        stdout, stderr, exitcode = self._run_cmd(
            ['git', 'symbolic-ref', 'HEAD'], handle_exitcode=False)
        if exitcode != 0:
            io.log_warning('Git is in a detached head state. Using branch "default".')
            return 'default'
        else:
            self._handle_exitcode(exitcode, stderr)

        LOG.debug('git symbolic-ref result: ' + stdout)
        # Need to parse branch from ref manually because "--short" is
        # not supported on git < 1.8
        return stdout.split('/')[-1]

    def do_zip(self, location, staged=False):
        cwd = os.getcwd()
        try:
            # must be in project root for git archive to work.
            fileoperations._traverse_to_project_root()

            if staged:
                commit_id, stderr, exitcode = self._run_cmd(
                    ['git', 'write-tree'])
            else:
                commit_id = 'HEAD'
            io.log_info('creating zip using git archive HEAD')
            stdout, stderr, exitcode = self._run_cmd(
                ['git', 'archive', '-v', '--format=zip',
                 '-o', location, commit_id])
            io.log_info('git archive output: ' + stderr)
        finally:
            os.chdir(cwd)

    def get_message(self):
        stdout, stderr, exitcode = self._run_cmd(
            ['git', 'log', '--oneline', '-1'])
        return stdout.split(' ', 1)[1]

    def is_setup(self):
        if fileoperations.is_git_directory_present():
            # We know that the directory has git, but
            # is git on the path?
            if not fileoperations.program_is_installed('git'):
                raise CommandError(strings['sc.gitnotinstalled'])
            else:
                return True
        return False

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

    def _run_cmd(self, cmd, handle_exitcode=True):
        stdout, stderr, exitcode = exec_cmd(cmd)
        if sys.version_info[0] >= 3:
            stdout = stdout.decode('utf8')
            stderr = stderr.decode('utf8')
        stdout = stdout.strip()
        stderr = stderr.strip()
        if handle_exitcode:
            self._handle_exitcode(exitcode, stderr)
        return stdout, stderr, exitcode
