# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
from ebcli.objects.exceptions import(
    CommandError,
    GitRemoteNotSetupError,
    NoSourceControlError
)


class TestNoSourceControl(unittest.TestCase):
    def setUp(self):
        if not os.path.exists('testDir{}'.format(os.path.sep)):
            os.makedirs('testDir{}'.format(os.path.sep))
        os.chdir('testDir')

        self.patcher_io = mock.patch('ebcli.objects.sourcecontrol.io')

        self.mock_input = self.patcher_io.start()

    def tearDown(self):
        self.patcher_io.stop()

        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            shutil.rmtree('testDir')

    @unittest.skipIf(fileoperations.program_is_installed('git'), "Skipped because git is installed")
    def test_get_source_control(self):
        sc = sourcecontrol.SourceControl.get_source_control()
        self.assertIsInstance(sc, sourcecontrol.NoSC)

    def test_get_name(self):
        self.assertEqual(sourcecontrol.NoSC().get_name(), None)

    def test_get_current_branch(self):
        self.assertEqual(sourcecontrol.NoSC().get_current_branch(), 'default')

    @mock.patch('ebcli.objects.sourcecontrol.fileoperations')
    def test_do_zip(self, mock_file):
        sourcecontrol.NoSC().do_zip('file.zip')
        mock_file.zip_up_project.assert_called_with('file.zip')


class TestGitSourceControl(unittest.TestCase):
    def setUp(self):
        if not os.path.exists('testDir{}'.format(os.path.sep)):
            os.makedirs('testDir{}'.format(os.path.sep))
        os.chdir('testDir')
        fileoperations.create_config_file('testapp', 'us-east-1', 'PHP')

        with open('myFile', 'w') as f:
            f.write('Hello')

        subprocess.call(['git', 'init'])
        subprocess.call(['git', 'config', '--local', 'user.email', 'abc@def.com'])
        subprocess.call(['git', 'config', '--local', 'user.name', 'abc def'])
        subprocess.call(['git', 'add', 'myFile'])
        subprocess.call(['git', 'commit', '-m', 'Initial'])

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
        subprocess.call(['git', 'checkout', 'HEAD^'])
        self.assertEqual(sourcecontrol.Git().get_current_branch(), 'default')

    @unittest.skipIf(not fileoperations.program_is_installed('git'), "Skipped because git is not installed")
    def test_do_zip(self):
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

    @mock.patch.object(sourcecontrol.Git, '_run_cmd')
    @mock.patch.object(sourcecontrol.Git, 'get_current_branch')
    def test_get_current_repository_git_cmd_succeeded(
        self,
        get_current_branch_mock,
        _run_cmd_mock,
    ):
        get_current_branch_mock.return_value = 'develop'
        _run_cmd_mock.return_value = 'develop-remote', '', 0
        actual = sourcecontrol.Git().get_current_repository()

        get_current_branch_mock.assert_called_once_with()
        _run_cmd_mock.assert_called_once_with(
            ['git', 'config', '--get', 'branch.develop.remote'],
            handle_exitcode=False)
        self.assertEqual('develop-remote', actual)

    @mock.patch.object(sourcecontrol.Git, '_run_cmd')
    @mock.patch.object(sourcecontrol.Git, 'get_current_branch')
    def test_get_current_repository__git_cmd_failed(
        self,
        get_current_branch_mock,
        _run_cmd_mock,
    ):
        get_current_branch_mock.return_value = 'develop'
        _run_cmd_mock.return_value = '', 'error message', 1
        actual = sourcecontrol.Git().get_current_repository()

        get_current_branch_mock.assert_called_once_with()
        _run_cmd_mock.assert_called_once_with(
            ['git', 'config', '--get', 'branch.develop.remote'],
            handle_exitcode=False)
        self.assertIsNone(actual)

    @unittest.skipIf(not fileoperations.program_is_installed('git'), "Skipped because git is not installed")
    def test_get_current_branch(self):
        self.assertEqual('master', sourcecontrol.Git().get_current_branch())

    @unittest.skipIf(not fileoperations.program_is_installed('git'), "Skipped because git is not installed")
    @mock.patch('ebcli.core.io.log_warning')
    def test_get_current_branch__detached_head_state(self, log_warning_mock):
        self.assertIsNotNone(sourcecontrol.Git().get_current_branch())

        p = subprocess.Popen(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE)
        stdout, _ = p.communicate()
        commit_of_head = stdout.decode().strip()

        p = subprocess.Popen(['git', 'checkout', commit_of_head], stdout=subprocess.PIPE)
        p.communicate()

        self.assertEqual('default', sourcecontrol.Git().get_current_branch())

    def test_verify_url_is_a_codecommit_url__valid_urls(self):
        valid_urls = [
            'https://git-codecommit.us-east-1.amazonaws.com',
            'https://git-codecommit.us-east-1.amazonaws.com/v1/repos/github-tests-test-1',
            'https://git-codecommit.us-east-1.amazonaws.com.cn/v1/repos/github-tests-test-1',
            'ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/github-tests-test-1',
            'git-codecommit..amazonaws.com',
            'git-codecommit.us-east-1.amazonaws.com/v1/repos/github-tests-test-1',
        ]

        for url in valid_urls:
            sourcecontrol.Git().verify_url_is_a_codecommit_url(url)

    def test_verify_url_is_a_codecommit_url__invalid_urls(self):
        invalid_urls = [
            'https://github.us-east-1.amazonaws.com',
            'ssh://git-codecommit.us-east-1.com/v1/repos/github-tests-test-1',
            'https://github.com/rahulrajaram/dummy_repository.git',
            'https://emmap1@bitbucket.org/tutorials/tutorials.git.bitbucket.org.git',
            'github..amazonaws.com',
        ]

        for url in invalid_urls:
            with self.assertRaises(NoSourceControlError) as context_manager:
                sourcecontrol.Git().verify_url_is_a_codecommit_url(url)

            self.assertEqual(
                'Could not connect to repository located at {}'.format(url),
                context_manager.exception.message
            )

    def test_credential_helper_command(self):
        self.assertEqual(
            '!aws codecommit credential-helper $@',
            sourcecontrol.credential_helper_command()
        )

    @mock.patch('ebcli.objects.sourcecontrol.Git._run_cmd')
    def test_setup_codecommit_cred_config__non_windows(
            self,
            _run_cmd_mock
    ):
        sourcecontrol.Git().setup_codecommit_cred_config()

        _run_cmd_mock.assert_has_calls(
            [
                mock.call(['git', 'config', '--local', '--replace-all', 'credential.UseHttpPath', 'true']),
                mock.call(
                    [
                        'git', 'config', '--local', '--replace-all',
                        'credential.helper', '!aws codecommit credential-helper $@'
                    ]
                )
            ])

    @mock.patch.object(sourcecontrol.Git, '_run_cmd')
    def test_fetch_remote_branches__git_cmd_succeded(self, _run_cmd_mock):
        _run_cmd_mock.return_value = '', '', 0
        actual = sourcecontrol.Git().fetch_remote_branches('develop')

        _run_cmd_mock.assert_called_once_with(
            ['git', 'fetch', 'develop'],
            handle_exitcode=False)
        self.assertTrue(actual)

    @mock.patch.object(sourcecontrol.Git, '_run_cmd')
    def test_fetch_remote_branches__git_cmd_failed(self, _run_cmd_mock):
        _run_cmd_mock.return_value = '', '', 1
        actual = sourcecontrol.Git().fetch_remote_branches('develop')

        _run_cmd_mock.assert_called_once_with(
            ['git', 'fetch', 'develop'],
            handle_exitcode=False)
        self.assertFalse(actual)
