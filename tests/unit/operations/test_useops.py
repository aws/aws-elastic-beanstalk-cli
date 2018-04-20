# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import shutil

import unittest
import mock

from ebcli.core import fileoperations
from ebcli.operations import gitops, useops
from ebcli.objects.exceptions import NotFoundError, ServiceError


class TestUseOps(unittest.TestCase):
	def setUp(self):
		self.root_dir = os.getcwd()
		if not os.path.exists('testDir'):
			os.mkdir('testDir')

		os.chdir('testDir')

		fileoperations.create_config_file(
			app_name='my-app',
			region='us-west-2',
			solution_stack='64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5',

		)

	def tearDown(self):
		os.chdir(self.root_dir)
		shutil.rmtree('testDir')

	@mock.patch('ebcli.operations.useops.elasticbeanstalk.get_environment')
	def test_switch_default_environment__environment_found(
			self,
			get_environment_mock
	):
		fileoperations.write_config_setting(
			'branch-defaults',
			'default',
			{
				'environment': 'my-old-env'
			}
		)

		get_environment_mock.return_value = mock.MagicMock('some-environment')

		useops.switch_default_environment('my-new-env')

		branch_defaults = fileoperations.get_config_setting('branch-defaults', 'default')
		self.assertEqual('my-new-env', branch_defaults['environment'])

	@mock.patch('ebcli.operations.useops.elasticbeanstalk.get_environment')
	def test_switch_default_environment__redundantly_switch_to_present_environment(
			self,
			get_environment_mock
	):
		fileoperations.write_config_setting(
			'branch-defaults',
			'default',
			{
				'environment': 'my-old-env'
			}
		)

		get_environment_mock.return_value = mock.MagicMock('some-environment')

		useops.switch_default_environment('my-old-env')

		branch_defaults = fileoperations.get_config_setting('branch-defaults', 'default')
		self.assertEqual('my-old-env', branch_defaults['environment'])

	@mock.patch('ebcli.operations.useops.elasticbeanstalk.get_environment')
	def test_switch_default_environment__environment_not_found(
			self,
			get_environment_mock
	):
		fileoperations.write_config_setting(
			'branch-defaults',
			'default',
			{
				'environment': 'my-old-env'
			}
		)

		get_environment_mock.side_effect = NotFoundError('Environment "my-new-env" not Found.')

		with self.assertRaises(NotFoundError):
			useops.switch_default_environment('my-new-env')

		branch_defaults = fileoperations.get_config_setting('branch-defaults', 'default')
		self.assertEqual('my-old-env', branch_defaults['environment'])

	@mock.patch('ebcli.operations.useops.codecommit.get_branch')
	def test_switch_default_repo_and_branch__default_branch_environment_are_absent__writes_new(
			self,
			get_branch_mock
	):
		fileoperations.write_config_setting(
			'branch-defaults',
			'default',
			{
				'environment': 'my-old-env'
			}
		)

		get_branch_mock.return_value = mock.MagicMock('new-codecommit-branch')

		useops.switch_default_repo_and_branch(
			repo_name='new-codecommit-repository',
			branch_name='new-codecommit-branch',
		)

		environment_defaults = fileoperations.get_config_setting('environment-defaults', 'my-old-env')

		self.assertEqual('new-codecommit-branch', environment_defaults['branch'])
		self.assertEqual('new-codecommit-repository', environment_defaults['repository'])

	@mock.patch('ebcli.operations.useops.codecommit.get_branch')
	def test_switch_default_repo_and_branch__default_branch_environment_exists__overwrites_existing_environment_defaults(
			self,
			get_branch_mock
	):
		fileoperations.write_config_setting(
			'branch-defaults',
			'default',
			{
				'environment': 'my-old-env'
			}
		)
		gitops.write_setting_to_current_environment_or_default('branch', 'old-codecommit-branch')
		gitops.write_setting_to_current_environment_or_default('repository', 'old-codecommit-repository')

		get_branch_mock.return_value = mock.MagicMock('new-codecommit-branch')

		useops.switch_default_repo_and_branch(
			repo_name='new-codecommit-repository',
			branch_name='new-codecommit-branch',
		)

		environment_defaults = fileoperations.get_config_setting('environment-defaults', 'my-old-env')
		self.assertEqual('new-codecommit-branch', environment_defaults['branch'])
		self.assertEqual('new-codecommit-repository', environment_defaults['repository'])

	@mock.patch('ebcli.operations.useops.codecommit.get_branch')
	def test_switch_default_repo_and_branch__default_branch_environment_is_absent__branch_and_repository_name_are_stored_as_global_parameters(
			self,
			get_branch_mock
	):
		get_branch_mock.return_value = mock.MagicMock('new-codecommit-branch')

		useops.switch_default_repo_and_branch(
			repo_name='new-codecommit-repository',
			branch_name='new-codecommit-branch',
		)

		self.assertEqual('new-codecommit-branch', fileoperations.get_config_setting('global', 'branch'))
		self.assertEqual('new-codecommit-repository', fileoperations.get_config_setting('global', 'repository'))

	@mock.patch('ebcli.operations.useops.codecommit.get_branch')
	def test_switch_default_repo_and_branch__default_branch_environment_is_absent__branch_and_repository_name_are_stored_as_global_parameters(
			self,
			get_branch_mock
	):
		get_branch_mock.return_value = mock.MagicMock('new-codecommit-branch')

		useops.switch_default_repo_and_branch(
			repo_name='new-codecommit-repository',
			branch_name='new-codecommit-branch',
		)

		self.assertEqual('new-codecommit-branch', fileoperations.get_config_setting('global', 'branch'))
		self.assertEqual('new-codecommit-repository', fileoperations.get_config_setting('global', 'repository'))

	@mock.patch('ebcli.operations.useops.codecommit.get_branch')
	def test_switch_default_repo_and_branch__remote_codecommit_repository_absent__exception_is_raised__present_values_left_intact(
			self,
			get_branch_mock
	):
		get_branch_mock.side_effect = ServiceError
		fileoperations.write_config_setting(
			'branch-defaults',
			'default',
			{
				'environment': 'my-old-env'
			}
		)
		gitops.write_setting_to_current_environment_or_default('branch', 'old-codecommit-branch')
		gitops.write_setting_to_current_environment_or_default('repository', 'old-codecommit-repository')

		with self.assertRaises(NotFoundError):
			useops.switch_default_repo_and_branch(
				repo_name='nonexistent-codecommit-repository',
				branch_name='nonexistent-codecommit-branch',
			)

		environment_defaults = fileoperations.get_config_setting('environment-defaults', 'my-old-env')
		self.assertEqual('old-codecommit-branch', environment_defaults['branch'])
		self.assertEqual('old-codecommit-repository', environment_defaults['repository'])
