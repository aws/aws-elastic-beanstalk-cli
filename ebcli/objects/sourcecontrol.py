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
import zipfile
import fileinput
import datetime

from cement.utils.misc import minimal_logger
from cement.utils.shell import exec_cmd

from ebcli.resources.strings import git_ignore
from ebcli.core.fileoperations import get_config_setting
from ebcli.objects.exceptions import NoSourceControlError, CommandError
from ebcli.core import fileoperations

LOG = minimal_logger(__name__)


class SourceControl():
    name = 'base'

    def __init__(self):
        self.name = ''

    def get_name(self):
        return None

    def get_current_branch(self):
        pass

    def do_zip(self):
        pass

    def set_up_ignore_file(self):
        pass

    def get_version_label(self):
        pass

    @staticmethod
    def get_source_control():
        # First check for setting in config file
        git_installed = get_config_setting('global', 'sc')

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

    def _zipdir(self, path, zipf):
        for root, dirs, files in os.walk(path):
            for f in files:
                zipf.write(os.path.join(root, f))

    def do_zip(self, location):
        zipf = zipfile.ZipFile(location, 'w', zipfile.ZIP_DEFLATED)
        self._zipdir('./', zipf)
        zipf.close()

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
        if exitcode == 127 or exitcode == 128:
            # 127 = git not installed
            # 128 = current directory does not have a git root
            raise NoSourceControlError

        # Something else happened
        LOG.error('An error occurred while handling git command.'
                  '\nError code: ' + str(exitcode) + ' Error: ' + stderr)
        raise CommandError

    def get_version_label(self):
        stdout, stderr, exitcode = \
            exec_cmd('git describe --always --abbrev=4', shell=True)
        self._handle_exitcode(exitcode, stderr)

        #Replace dots with underscores
        return stdout[:-1].replace('.', '_')

    def get_current_branch(self):
        stdout, stderr, exitcode = \
            exec_cmd(['git rev-parse --abbrev-ref HEAD'], shell=True)

        self._handle_exitcode(exitcode, stderr)
        return stdout.rstrip()

    def do_zip(self, location):
        stdout, stderr, exitcode = \
            exec_cmd(['git archive --format=zip '
                      '-o ' + location + ' HEAD'], shell=True)
        self._handle_exitcode(exitcode, stderr)

    def get_message(self):
        stdout, stderr, exitcode = \
            exec_cmd(['git log --oneline -1'], shell=True)
        self._handle_exitcode(exitcode, stderr)
        return stdout.rstrip()

    def is_setup(self):
        #   does the current directory have git set-up
        # ToDo: We should instead check for a .git directory at the
        ## same level as .elasticbeanstalk
        # We want to enforce the same level for various reasons
        # (i.e. git ignore) and a git command has potential to
        # fail if in a detached HEAD state
        stdout, stderr, exitcode = exec_cmd(['git status'], shell=True)

        try:
            self._handle_exitcode(exitcode, stderr)
        except NoSourceControlError:
            return False
        except CommandError:
            # Default to False to be safe
            return False

        return True

    def set_up_ignore_file(self):
        # if not os.path.exists('.gitignore')
        with open('.gitignore', 'w+') as f:
            for line in f:
                if line.strip() == git_ignore[0]:
                    return

            # Move to the end of the file:
            f.seek(0, 2)
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
