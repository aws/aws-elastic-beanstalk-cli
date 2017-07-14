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

import unittest
import sys
import os
import shutil
import subprocess
import mock

from ebcli.objects import sourcecontrol
from ebcli.core import fileoperations
from ebcli.objects.exceptions import CommandError, NoSourceControlError


class TestNoSourceControl(unittest.TestCase):
    def setUp(self):
        # set up test directory
        if not os.path.exists('testDir/'):
            os.makedirs('testDir/')
        os.chdir('testDir')

        self.patcher_io = mock.patch('ebcli.objects.sourcecontrol.io')

        self.mock_input = self.patcher_io.start()

    def tearDown(self):
        self.patcher_io.stop()

        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            if sys.platform.startswith('win'):
                os.system('rmdir /S /Q testDir')
            else:
                shutil.rmtree('testDir')

    @unittest.skipIf(fileoperations.program_is_installed('git'), "Skipped because git is installed")
    def test_get_source_control(self):
        sc = sourcecontrol.SourceControl.get_source_control()
        self.assertIsInstance(sc, sourcecontrol.NoSC)

    def test_get_name(self):
        self.assertEqual(sourcecontrol.NoSC().get_name(), None)

    def test_get_current_branch(self):
        #Hardcoded, but should test for backwards compatibility
        self.assertEqual(sourcecontrol.NoSC().get_current_branch(), 'default')

    @mock.patch('ebcli.objects.sourcecontrol.fileoperations')
    def test_do_zip(self, mock_file):
        sourcecontrol.NoSC().do_zip('file.zip')
        mock_file.zip_up_project.assert_called_with('file.zip')

    def test_get_message(self):
        # Just a hardcoded string, dont really need to test
        pass


class TestGitSourceControl(unittest.TestCase):
    def setUp(self):
        # set up test directory
        if not os.path.exists('testDir/'):
            os.makedirs('testDir/')
        os.chdir('testDir')
        fileoperations.create_config_file('testapp', 'us-east-1', 'PHP')

        with open('myFile', 'w') as f:
            f.write('Hello')

        subprocess.call(['git', 'init'])
        subprocess.call(['git', 'add', 'myFile'])
        subprocess.call(['git', 'commit', '-m', 'Initial'])

        # Add a second commit
        with open('myFile2', 'w') as f:
            f.write('Hello There')
        subprocess.call(['git', 'add', 'myFile2'])
        subprocess.call(['git', 'commit', '-m', 'Hello'])


        subprocess.call(['git', 'tag', '-a', 'v1', '-m', 'my version'])

        self.patcher_io = mock.patch('ebcli.objects.sourcecontrol.io')

        self.mock_input = self.patcher_io.start()

    def tearDown(self):
        self.patcher_io.stop()

        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            if sys.platform.startswith('win'):
                os.system('rmdir /S /Q testDir')
            else:
                shutil.rmtree('testDir')

    @unittest.skipIf(not fileoperations.program_is_installed('git'), "Skipped because git is not installed")
    def test_get_source_control(self):
        sc = sourcecontrol.SourceControl.get_source_control()
        self.assertIsInstance(sc, sourcecontrol.Git)

    @unittest.skipIf(not fileoperations.program_is_installed('git'), "Skipped because git is not installed")
    def test_get_name(self):
        self.assertEqual(sourcecontrol.Git().get_name(), 'git')

    @unittest.skipIf(not fileoperations.program_is_installed('git'), "Skipped because git is not installed")
    def test_get_current_branch(self):
        self.assertEqual(sourcecontrol.Git().get_current_branch(), 'master')

    @unittest.skipIf(not fileoperations.program_is_installed('git'), "Skipped because git is not installed")
    def test_get_current_branch_detached_head(self):
        # Checkout a commit back to get us in detached head state
        subprocess.call(['git', 'checkout', 'HEAD^'])
        self.assertEqual(sourcecontrol.Git().get_current_branch(), 'default')

    @unittest.skipIf(not fileoperations.program_is_installed('git'), "Skipped because git is not installed")
    def test_do_zip(self):
        #Just want to make sure no errors happen
        sourcecontrol.Git().do_zip(os.getcwd() + os.path.sep + 'file.zip')

    @unittest.skipIf(not fileoperations.program_is_installed('git'), "Skipped because git is not installed")
    def test_get_message(self):
        self.assertEqual(sourcecontrol.Git().get_message(), 'Hello')

    @unittest.skipIf(not fileoperations.program_is_installed('git'), "Skipped because git is not installed")
    def test_get_version_label(self):
        self.assertTrue(sourcecontrol.Git().get_version_label().startswith('app-v1-'))

    @unittest.skipIf(not fileoperations.program_is_installed('git'), "Skipped because git is not installed")
    def test_set_up_ignore_no_file(self):
        self.assertFalse(os.path.isfile('.gitignore'))
        sourcecontrol.Git().set_up_ignore_file()
        self.assertTrue(os.path.isfile('.gitignore'))

    @unittest.skipIf(not fileoperations.program_is_installed('git'), "Skipped because git is not installed")
    def test_set_up_ignore_file_file_exists(self):
        with open('.gitignore', 'w') as f:
            f.write('line1\n')
            f.write('line2\n')

        sourcecontrol.Git().set_up_ignore_file()

        with open('.gitignore', 'r') as f:
            f = f.readlines()
            self.assertEqual(f[0], 'line1\n')
            self.assertEqual(f[1], 'line2\n')

    @unittest.skipIf(not fileoperations.program_is_installed('git'), "Skipped because git is not installed")
    @mock.patch('ebcli.objects.sourcecontrol.exec_cmd')
    def test_error_handler_for_exit_code_128(self, mock_exec_cmd):
        stdout = ""
        stderr = "Not a valid object name HEAD"
        exit_code = 128
        mock_exec_cmd.return_value = stdout, stderr, exit_code
        self.assertRaises(CommandError, sourcecontrol.Git().get_version_label)

    @unittest.skipIf(not fileoperations.program_is_installed('git'), "Skipped because git is not installed")
    @mock.patch('ebcli.objects.sourcecontrol.exec_cmd')
    def test_error_handler_for_exit_code_127(self, mock_exec_cmd):
        stdout = ""
        stderr = "git not installed"
        exit_code = 127
        mock_exec_cmd.return_value = stdout, stderr, exit_code
        self.assertRaises(NoSourceControlError, sourcecontrol.Git().get_version_label)

    @unittest.skipIf(not fileoperations.program_is_installed('git'), "Skipped because git is not installed")
    @mock.patch('ebcli.objects.sourcecontrol.exec_cmd')
    def test_error_handler_for_non_handled_exit_code(self, mock_exec_cmd):
        stdout = ""
        stderr = "git not installed"
        exit_code = 99999
        mock_exec_cmd.return_value = stdout, stderr, exit_code
        self.assertRaises(CommandError, sourcecontrol.Git().get_version_label)
