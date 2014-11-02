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
import os
import shutil
import subprocess
import mock

from ebcli.objects import sourcecontrol


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
            shutil.rmtree('testDir')


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

        with open('myFile', 'w') as f:
            f.write('Hello')

        subprocess.call(['git', 'init'])
        subprocess.call(['git', 'add', 'myFile'])
        subprocess.call(['git', 'commit', '-m', 'Hello'])
        subprocess.call(['git', 'tag', '-a', 'v1', '-m', 'my version'])

        self.patcher_io = mock.patch('ebcli.objects.sourcecontrol.io')

        self.mock_input = self.patcher_io.start()

    def tearDown(self):
        self.patcher_io.stop()

        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            shutil.rmtree('testDir')

    def test_get_source_control(self):
        sc = sourcecontrol.SourceControl.get_source_control()
        self.assertIsInstance(sc, sourcecontrol.Git)

    def test_get_name(self):
        self.assertEqual(sourcecontrol.Git().get_name(), 'git')

    def test_get_current_branch(self):
        self.assertEqual(sourcecontrol.Git().get_current_branch(), 'master')

    def test_do_zip(self):
        #Just want to make sure no errors happen
        sourcecontrol.Git().do_zip(os.getcwd() + os.path.sep + 'file.zip')

    def test_get_message(self):
        self.assertTrue(sourcecontrol.Git().get_message().endswith(' Hello'))

    def test_get_version_label(self):
        self.assertEquals(sourcecontrol.Git().get_version_label(), 'v1')

    def test_set_up_ignore_no_file(self):
        self.assertFalse(os.path.isfile('.gitignore'))
        sourcecontrol.Git().set_up_ignore_file()
        self.assertTrue(os.path.isfile('.gitignore'))

