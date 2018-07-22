# -*- coding: utf-8 -*-

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

import os

import sys
import shutil
import unittest

import mock
from pytest_socket import enable_socket, disable_socket

from ebcli.core import fileoperations
from ebcli.operations import initializeops


class TestInitializeOperations(unittest.TestCase):

    def setUp(self):
        disable_socket()
        # set up test directory
        if not os.path.exists('testDir'):
            os.makedirs('testDir')
        os.chdir('testDir')

        # set up mock elastic beanstalk directory
        if not os.path.exists(fileoperations.beanstalk_directory):
            os.makedirs(fileoperations.beanstalk_directory)

        # set up mock home dir
        if not os.path.exists('home'):
            os.makedirs('home')

        # change directory to mock home
        fileoperations.aws_config_folder = 'home' + os.path.sep
        fileoperations.aws_config_location \
            = fileoperations.aws_config_folder + 'config'

        # Create local
        fileoperations.create_config_file('ebcli-test', 'us-east-1',
                                          'my-solution-stack')

    def tearDown(self):
        enable_socket()
        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            if sys.platform.startswith('win'):
                os.system('rmdir /S /Q testDir')
            else:
                shutil.rmtree('testDir')


    @mock.patch('ebcli.operations.initializeops.codebuild')
    def test_get_codebuild_image_from_platform_that_exists(self, mock_codebuild):
        # Delcare variables local to this test
        expected_image = {u'name': u'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6',
                              u'description': u'Java 8 Running on Amazon Linux 64bit '}
        curated_images_response = [{u'name': u'aws/codebuild/eb-java-7-amazonlinux-64:2.1.6',
                              u'description': u'Java 7 Running on Amazon Linux 64bit '},
                             expected_image,
                             {u'name': u'aws/codebuild/eb-go-1.5-amazonlinux-64:2.1.6',
                              u'description': u'Go 1.5 Running on Amazon Linux 64bit '}]

        # Mock out methods
        mock_codebuild.list_curated_environment_images.return_value = curated_images_response

        # Make the actual call
        images_for_platform = initializeops.get_codebuild_image_from_platform("Java 8")

        # Assert methods were called with the right params and returned the correct values
        self.assertEqual(expected_image, images_for_platform,
                         "Expected '{0}' but got: {1}".format(expected_image, images_for_platform))

    @mock.patch('ebcli.operations.initializeops.codebuild')
    def test_get_codebuild_image_from_platform_that_does_not_match(self, mock_codebuild):
        # Delcare variables local to this test
        curated_images_response = [{u'name': u'aws/codebuild/eb-java-7-amazonlinux-64:2.1.6',
                                    u'description': u'Java 7 Running on Amazon Linux 64bit '},
                                   {u'name': u'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6',
                                    u'description': u'Java 8 Running on Amazon Linux 64bit '},
                                   {u'name': u'aws/codebuild/eb-go-1.5-amazonlinux-64:2.1.6',
                                    u'description': u'Go 1.5 Running on Amazon Linux 64bit '}]

        # Mock out methods
        mock_codebuild.list_curated_environment_images.return_value = curated_images_response

        # Make the actual call
        images_for_platform = initializeops.get_codebuild_image_from_platform(
            "64bit Amazon Linux 2016.09 v2.2.0 running Java 8")

        # Assert methods were called with the right params and returned the correct values
        self.assertEqual(curated_images_response, images_for_platform,
                         "Expected '{0}' but got: {1}".format(curated_images_response, images_for_platform))

    @mock.patch('ebcli.operations.initializeops.elasticbeanstalk.get_available_solution_stacks')
    def test_credentials_are_valid(
            self,
            get_available_solution_stacks_mock
    ):
        self.assertTrue(initializeops.credentials_are_valid())

    @mock.patch('ebcli.operations.initializeops.elasticbeanstalk.get_available_solution_stacks')
    def test_credentials_are_valid__credentials_error(
            self,
            get_available_solution_stacks_mock
    ):
        get_available_solution_stacks_mock.side_effect = initializeops.CredentialsError

        self.assertFalse(initializeops.credentials_are_valid())

    @mock.patch('ebcli.operations.initializeops.elasticbeanstalk.get_available_solution_stacks')
    @mock.patch('ebcli.operations.initializeops.io.log_error')
    def test_credentials_are_valid__not_authorized_error(
            self,
            log_error_mock,
            get_available_solution_stacks_mock
    ):
        get_available_solution_stacks_mock.side_effect = initializeops.NotAuthorizedError

        self.assertFalse(initializeops.credentials_are_valid())

        log_error_mock.assert_called_once_with(
            'The current user does not have the correct permissions. Reason: '
        )

    @mock.patch('ebcli.operations.initializeops.heuristics.has_tomcat_war_file')
    @mock.patch('ebcli.operations.initializeops.fileoperations.get_war_file_location')
    @mock.patch('ebcli.operations.initializeops.fileoperations.write_config_setting')
    @mock.patch('ebcli.operations.initializeops.setup_directory')
    @mock.patch('ebcli.operations.initializeops.setup_ignore_file')
    def test_setup__tomcat_special_case(
            self,
            setup_ignore_file_mock,
            setup_directory_mock,
            write_config_setting_mock,
            get_war_file_location_mock,
            has_tomcat_war_file_mock
    ):
        has_tomcat_war_file_mock.return_value = True
        get_war_file_location_mock.return_value = '/path/to/file'

        initializeops.setup(
            'my-application',
            'us-west-2',
            'tomcat',
            'application'
        )

        setup_directory_mock.assert_called_once_with(
            'my-application',
            'us-west-2',
            'tomcat',
            branch=None,
            dir_path=None,
            instance_profile=None,
            platform_name=None,
            platform_version=None,
            repository=None,
            workspace_type='application'
        )
        has_tomcat_war_file_mock.assert_called_once_with()
        write_config_setting_mock.assert_called_once_with(
            'deploy',
            'artifact',
            '/path/to/file'
        )
        setup_ignore_file_mock.assert_called_once_with()

    @mock.patch('ebcli.operations.initializeops.setup_directory')
    @mock.patch('ebcli.operations.initializeops.setup_ignore_file')
    def test_setup(
            self,
            setup_ignore_file_mock,
            setup_directory_mock,
    ):
        initializeops.setup(
            'my-application',
            'us-west-2',
            'php',
            'application'
        )

        setup_directory_mock.assert_called_once_with(
            'my-application',
            'us-west-2',
            'php',
            branch=None,
            dir_path=None,
            instance_profile=None,
            platform_name=None,
            platform_version=None,
            repository=None,
            workspace_type='application'
        )

        setup_ignore_file_mock.assert_called_once_with()

    @mock.patch('ebcli.operations.initializeops.io.echo')
    @mock.patch('ebcli.operations.initializeops.io.log_info')
    @mock.patch('ebcli.operations.initializeops.io.prompt')
    @mock.patch('ebcli.operations.initializeops.fileoperations.save_to_aws_config')
    @mock.patch('ebcli.operations.initializeops.fileoperations.touch_config_folder')
    @mock.patch('ebcli.operations.initializeops.fileoperations.write_config_setting')
    @mock.patch('ebcli.operations.initializeops.aws.set_session_creds')
    def test_setup_credentials(
            self,
            set_session_creds_mock,
            write_config_setting_mock,
            touch_config_folder_mock,
            save_to_aws_config_mock,
            prompt_mock,
            log_info_mock,
            echo_mock
    ):
        prompt_mock.side_effect = [
            'access-id',
            'secret-key'
        ]

        initializeops.setup_credentials()

        set_session_creds_mock.assert_called_once_with('access-id', 'secret-key')
        write_config_setting_mock.assert_called_once_with('global', 'profile', 'eb-cli')
        touch_config_folder_mock.assert_called_once_with()
        save_to_aws_config_mock.assert_called_once_with('access-id', 'secret-key')
        log_info_mock.assert_called_once_with('Setting up ~/aws/ directory with config file')
        echo_mock.assert_called_once_with(
            'You have not yet set up your credentials or your credentials are incorrect \nYou must provide your credentials.'
        )

    @mock.patch('ebcli.operations.initializeops.fileoperations.create_config_file')
    def test_setup_directory(
            self,
            create_confg_file_mock
    ):
        initializeops.setup_directory(
            'my-application',
            'us-west-2',
            'php',
            'application',
            None,
            None,
            None,
            dir_path=None,
            repository=None,
            branch=None,
        )

        create_confg_file_mock.assert_called_once_with(
            'my-application',
            'us-west-2',
            'php',
            'application',
            None,
            None,
            None,
            dir_path=None,
            repository=None,
            branch=None,
        )

    @mock.patch('ebcli.operations.initializeops.fileoperations.get_config_setting')
    @mock.patch('ebcli.operations.initializeops.SourceControl.get_source_control')
    def test_setup_ignore_file__no_source_control(
            self,
            get_source_control_mock,
            get_config_setting_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_name.return_value = 'git'
        get_source_control_mock.return_value = source_control_mock
        get_config_setting_mock.return_value = None

        initializeops.setup_ignore_file()

        get_config_setting_mock.assert_called_once_with('global', 'sc')

    @mock.patch('ebcli.operations.initializeops.fileoperations.get_config_setting')
    def test_setup_ignore_file__source_control_setup(
            self,
            get_config_setting_mock
    ):
        get_config_setting_mock.return_value = True

        initializeops.setup_ignore_file()
