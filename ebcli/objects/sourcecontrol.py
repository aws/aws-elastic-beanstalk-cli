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

import os
import zipfile

from cement.utils.misc import minimal_logger
from cement.utils.shell import exec_cmd

from ebcli.resources.strings import git_ignore
from ebcli.core.fileoperations import get_config_setting
from ebcli.objects.exceptions import NoSourceControlError

LOG = minimal_logger(__name__)


class SourceControl():
    def __init__(self):
        self.name = ''

    def get_current_branch(self):
        pass

    def do_zip(self):
        pass

    def set_up_ignore_file(self):
        pass

    @staticmethod
    def get_source_control():
        # First check for setting in config file
        git_installed = get_config_setting('global', 'git')

        if not git_installed:
            if Git().is_setup():
                return Git()
            else:
                return NoSC()


class NoSC(SourceControl):
    """
        No source control installed
    """
    def get_current_branch(self):
        return 'master'

    def _zipdir(self, path, zipf):
        for root, dirs, files in os.walk(path):
            for f in files:
                zipf.write(os.path.join(root, f))

    def do_zip(self):
        LOG.debug("Zipping with no source control is Not Supported")
        raise NoSourceControlError
        # zipf = zipfile.ZipFile('myApp.zip', 'w', zipfile.ZIP_DEFLATED)
        # self._zipdir('./', zipf)
        # zipf.close()

    def set_up_ignore_file(self):
        LOG.debug('No Source control installed')
        raise NoSourceControlError


class Git(SourceControl):
    """
        The user has git installed
        """

    def get_current_branch(self):
        pass

    def do_zip(self):
        stdout, stderr, exitcode = \
            exec_cmd(['git archive --format=zip '
                      '-o .elasticbeanstalk/eb-app.zip HEAD'], True)
        if exitcode != 0:
            raise Exception('error')

    def is_setup(self):
        #   does the current directory have git set-up
        stdout, stderr, exitcode = exec_cmd(['git status'], True)

        if exitcode == 0:
            return True
        if exitcode == 127 or exitcode == 128:
            # 127 = git not installed
            # 128 = current directory does not have a git root
            return False
        # Default to False just to be safe
        return False

    def set_up_ignore_file(self):
        with open('.gitignore', 'a') as f:
            f.write(os.linesep)
            for line in git_ignore:
                f.write(line + os.linesep)
