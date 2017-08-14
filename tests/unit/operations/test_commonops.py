# -*- coding: utf-8 -*-

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
import sys
import shutil
import json
import mock
import unittest
from collections import Counter

from botocore.compat import six
from mock import Mock

from ebcli.core import fileoperations
from ebcli.objects.exceptions import NotAuthorizedError
from ebcli.operations import commonops
from ebcli.lib.aws import InvalidParameterValueError
from ebcli.objects.buildconfiguration import BuildConfiguration
from ebcli.resources.strings import strings, responses
from ebcli.resources.statics import iam_documents, iam_attributes
from ebcli.objects.solutionstack import SolutionStack

class TestCommonOperations(unittest.TestCase):
    app_name = 'ebcli-app'
    app_version_name = 'ebcli-app-version'
    env_name = 'ebcli-env'
    description = 'ebcli testing app'
    s3_bucket = 'app_bucket'
    s3_key = 'app_bucket_key'

    repository = 'my-repo'
    branch = 'my-branch'
    commit_id = '123456789'

    image = 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.3'
    compute_type = 'BUILD_GENERAL1_SMALL'
    service_role = 'eb-test'
    service_role_arn = 'arn:testcli:eb-test'
    timeout = 60
    build_config = BuildConfiguration(image=image, compute_type=compute_type,
                                      service_role=service_role, timeout=timeout)


    def assertListsOfDictsEquivalent(self, ls1, ls2):
        return self.assertEqual(
            Counter(frozenset(six.iteritems(d)) for d in ls1),
            Counter(frozenset(six.iteritems(d)) for d in ls2))

    def setUp(self):
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
        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            if sys.platform.startswith('win'):
                os.system('rmdir /S /Q testDir')
            else:
                shutil.rmtree('testDir')

    def test_is_success_string(self):
        self.assertTrue(commonops._is_success_string('Environment health has been set to GREEN'))
        self.assertTrue(commonops._is_success_string('Successfully launched environment: my-env'))
        self.assertTrue(commonops._is_success_string('Pulled logs for environment instances.'))
        self.assertTrue(commonops._is_success_string('terminateEnvironment completed successfully.'))

    @mock.patch('ebcli.operations.commonops.SourceControl')
    def test_return_global_default_if_no_branch_default(self, mock):
        sc_mock = Mock()
        sc_mock.get_current_branch.return_value = 'none'
        mock.get_source_control.return_value = sc_mock

        result = commonops.get_config_setting_from_branch_or_default('default_region')
        assert sc_mock.get_current_branch.called, 'Should have been called'
        self.assertEqual(result, 'us-east-1')

        fileoperations.write_config_setting('global', 'default_region', 'brazil')
        fileoperations.write_config_setting('global', 'profile', 'monica')
        fileoperations.write_config_setting('global', 'moop', 'meep')
        fileoperations.write_config_setting('branch-defaults', 'my-branch', {'profile': 'chandler',
            'environment': 'my-env', 'boop': 'beep'})

        result = commonops.get_current_branch_environment()
        self.assertEqual(result, None)

        # get default profile name
        result = commonops.get_default_profile()
        self.assertEqual(result, 'monica')

        result = commonops.get_config_setting_from_branch_or_default('moop')
        self.assertEqual(result, 'meep')


    @mock.patch('ebcli.operations.commonops.SourceControl')
    def test_return_branch_default_if_set(self, mock):
        sc_mock = Mock()
        sc_mock.get_current_branch.return_value = 'my-branch'
        mock.get_source_control.return_value = sc_mock

        fileoperations.write_config_setting('global', 'default_region', 'brazil')
        fileoperations.write_config_setting('global', 'profile', 'monica')
        fileoperations.write_config_setting('global', 'moop', 'meep')
        fileoperations.write_config_setting('branch-defaults', 'my-branch', {'profile': 'chandler',
            'environment': 'my-env', 'boop': 'beep'})

        # get default region name
        result = commonops.get_default_region()
        self.assertEqual(result, 'brazil')

        # get branch-specific default environment name
        result = commonops.get_current_branch_environment()
        self.assertEqual(result, 'my-env')

        # get branch-specific default profile name
        result = commonops.get_default_profile()
        self.assertEqual(result, 'chandler')

        # get branch-specific generic default
        result = commonops.get_config_setting_from_branch_or_default('boop')
        self.assertEqual(result, 'beep')

    def test_create_envvars_list_empty(self):
        options, options_to_remove = commonops.create_envvars_list([])
        self.assertEqual(options, list())
        self.assertEqual(options_to_remove, list())

        options, options_to_remove = commonops.create_envvars_list(
            [], as_option_settings=False)
        self.assertEqual(options, dict())
        self.assertEqual(options_to_remove, set())

    def test_create_envvars_list_simple(self):
        namespace = 'aws:elasticbeanstalk:application:environment'

        options, options_to_remove = commonops.create_envvars_list(
            ['foo=bar'])
        self.assertListsOfDictsEquivalent(options, [
            dict(Namespace=namespace,
                 OptionName='foo',
                 Value='bar')])
        self.assertListEqual(options_to_remove, list())

        options, options_to_remove = commonops.create_envvars_list(
            ['foo=bar', 'fish=good'])
        self.assertListsOfDictsEquivalent(options, [
            dict(Namespace=namespace,
                 OptionName='foo',
                 Value='bar'),
            dict(Namespace=namespace,
                 OptionName='fish',
                 Value='good')])
        self.assertEqual(options_to_remove, list())

        options, options_to_remove = commonops.create_envvars_list(
            ['foo=bar', 'fish=good', 'trout=', 'baz='])
        self.assertListsOfDictsEquivalent(options, [
            dict(Namespace=namespace,
                 OptionName='foo',
                 Value='bar'),
            dict(Namespace=namespace,
                 OptionName='fish',
                 Value='good')])
        self.assertListsOfDictsEquivalent(options_to_remove, [
            dict(Namespace=namespace,
                 OptionName='trout'),
            dict(Namespace=namespace,
                 OptionName='baz')])

    def test_create_envvars_not_as_option_settings(self):
        options, options_to_remove = commonops.create_envvars_list(
            ['foo=bar'], as_option_settings=False)
        self.assertEqual(options, dict(foo='bar'))
        self.assertEqual(options_to_remove, set())

        options, options_to_remove = commonops.create_envvars_list(
            ['foo=bar', 'fish=good'], as_option_settings=False)
        self.assertDictEqual(options, dict(foo='bar', fish='good'))
        self.assertEqual(options_to_remove, set())

        options, options_to_remove = commonops.create_envvars_list(
            ['foo=bar', 'fish=good', 'trout=', 'baz='],
            as_option_settings=False)
        self.assertDictEqual(options, dict(foo='bar', fish='good'))
        self.assertEqual(options_to_remove, {'trout', 'baz'})

    def test_create_envvars_crazy_characters(self):
        string1 = 'http://some.url.com/?quer=true&othersutff=1'
        string2 = 'some other !@=:;#$%^&*() weird, key'

        options, options_to_remove = commonops.create_envvars_list(
            ['foo=' + string1,
             'wierd er value='+ string2], as_option_settings=False)
        self.assertEqual(options, {
            'foo': string1,
            'wierd er value': string2})
        self.assertEqual(options_to_remove, set())

    def test_create_envvars_not_bad_characters(self):
        strings = [
            '!hello',
            ',hello',
            '?hello',
            ';hello',
            '=hello',
            '$hello',
            '%hello',
            '😊'
        ]
        for s in strings:
            options, options_to_remove = commonops.create_envvars_list(
                ['foo=' + s], as_option_settings=False)
            self.assertEqual(options, {'foo': s})

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk')
    def test_create_application_version_wrapper(self, mock_beanstalk):
        # Make the actual call
        actual_return = commonops._create_application_version(self.app_name, self.app_version_name,
                                              self.description, self.s3_bucket, self.s3_key)

        # Assert return and methods were called for the correct workflow
        self.assertEqual(self.app_version_name, actual_return, "Expected {0} but got: {1}"
                         .format(self.app_version_name, actual_return))
        mock_beanstalk.create_application_version.assert_called_with(self.app_name, self.app_version_name,
                                                                     self.description, self.s3_bucket, self.s3_key,
                                                                     False, None, None, None)

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk')
    def test_create_application_version_wrapper_app_version_already_exists(self, mock_beanstalk):
        # Mock out methods
        mock_beanstalk.create_application_version.side_effect = InvalidParameterValueError('Application Version {0} already exists.'
                                                                .format(self.app_version_name))

        # Make the actual call
        actual_return = commonops._create_application_version(self.app_name, self.app_version_name,
                                              self.description, self.s3_bucket, self.s3_key)

        # Assert return and methods were called for the correct workflow
        self.assertEqual(self.app_version_name, actual_return, "Expected {0} but got: {1}"
                         .format(self.app_version_name, actual_return))
        mock_beanstalk.create_application_version.assert_called_with(self.app_name, self.app_version_name,
                                                                     self.description, self.s3_bucket, self.s3_key,
                                                                     False, None, None, None)

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk')
    @mock.patch('ebcli.operations.commonops.fileoperations')
    def test_create_application_version_wrapper_app_does_not_exist(self, mock_fileoperations, mock_beanstalk):
        # Mock out methods
        mock_beanstalk.create_application_version.side_effect = [InvalidParameterValueError(responses['app.notexists'].replace(
                                                                '{app-name}', '\'' + self.app_name + '\'')), None]

        with mock.patch('ebcli.objects.sourcecontrol.Git') as MockGitClass:
            mock_git_sourcecontrol = MockGitClass.return_value
            mock_git_sourcecontrol.get_current_branch.return_value = self.branch
            with mock.patch('ebcli.operations.commonops.SourceControl') as MockSourceControlClass:
                mock_sourcecontrol = MockSourceControlClass.return_value
                mock_sourcecontrol.get_source_control.return_value = mock_git_sourcecontrol

            # Make the actual call
            actual_return = commonops._create_application_version(self.app_name, self.app_version_name,
                                          self.description, self.s3_bucket, self.s3_key)

        # Assert return and methods were called for the correct workflow
        self.assertEqual(self.app_version_name, actual_return, "Expected {0} but got: {1}"
                         .format(self.app_version_name, actual_return))
        mock_beanstalk.create_application_version.assert_called_with(self.app_name, self.app_version_name,
                                                                     self.description, self.s3_bucket, self.s3_key,
                                                                     False, None, None, None)
        mock_beanstalk.create_application.assert_called_with(self.app_name, strings['app.description'])

        write_config_calls = [mock.call('branch-defaults', self.branch, {'environment': None}),
                             mock.call('branch-defaults', self.branch, {'group_suffix': None})]
        mock_fileoperations.write_config_setting.assert_has_calls(write_config_calls)

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk')
    def test_create_application_version_wrapper_app_version_throws_unknown_exception(self, mock_beanstalk):
        # Mock out methods
        mock_beanstalk.create_application_version.side_effect = Exception("FooException")

        # Make the actual call
        self.assertRaises(Exception, commonops._create_application_version, self.app_name, self.app_version_name,
                          self.description, self.s3_bucket, self.s3_key)

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk')
    def test_create_application_version_wrapper_with_build_config(self, mock_beanstalk):
        # Mock out methods
        with mock.patch('ebcli.lib.iam.get_roles') as mock_iam_get_roles:
            mock_iam_get_roles.return_value = [{'RoleName': self.service_role, 'Arn': self.service_role_arn},
                                               {'RoleName': self.service_role, 'Arn': self.service_role_arn}]

            # Make the actual call
            actual_return = commonops._create_application_version(self.app_name, self.app_version_name,
                                                  self.description, self.s3_bucket, self.s3_key, build_config=self.build_config)

        # Assert return and methods were called for the correct workflow
        self.assertEqual(self.app_version_name, actual_return, "Expected {0} but got: {1}"
                         .format(self.app_version_name, actual_return))
        mock_beanstalk.create_application_version.assert_called_with(self.app_name, self.app_version_name,
                                                                     self.description, self.s3_bucket, self.s3_key,
                                                                     False, None, None, self.build_config)

    @mock.patch('ebcli.operations.commonops.iam')
    @mock.patch('ebcli.operations.commonops.io')
    def test_create_default_instance_profile_successful(self, _, mock_iam):
        commonops.create_default_instance_profile()

        mock_iam.create_instance_profile.assert_called_once_with(iam_attributes.DEFAULT_ROLE_NAME)
        mock_iam.create_role_with_policy.assert_called_once_with(iam_attributes.DEFAULT_ROLE_NAME, iam_documents.EC2_ASSUME_ROLE_PERMISSION, iam_attributes.DEFAULT_ROLE_POLICIES)
        mock_iam.add_role_to_profile.assert_called_once_with(iam_attributes.DEFAULT_ROLE_NAME, iam_attributes.DEFAULT_ROLE_NAME)
        mock_iam.put_role_policy.assert_not_called()

    @mock.patch('ebcli.operations.commonops.iam')
    @mock.patch('ebcli.operations.commonops.io')
    def test_create_instance_profile_successful(self, _, mock_iam):
        commonops.create_instance_profile('pname', 'policies', 'rname')

        mock_iam.create_instance_profile.assert_called_once_with('pname')
        mock_iam.create_role_with_policy.assert_called_once_with('rname', iam_documents.EC2_ASSUME_ROLE_PERMISSION, 'policies')
        mock_iam.add_role_to_profile.assert_called_once_with('pname', 'rname')
        mock_iam.put_role_policy.assert_not_called()

    @mock.patch('ebcli.operations.commonops.iam')
    @mock.patch('ebcli.operations.commonops.io')
    def test_create_instance_profile_successful_with_inline_policy(self, _, mock_iam):
        commonops.create_instance_profile('pname', 'policies', role_name='rname', inline_policy_name='inline_name', inline_policy_doc='{inline_json}')

        mock_iam.create_instance_profile.assert_called_once_with('pname')
        mock_iam.create_role_with_policy.assert_called_once_with('rname', iam_documents.EC2_ASSUME_ROLE_PERMISSION, 'policies')
        mock_iam.put_role_policy.assert_called_once_with('rname', 'inline_name', '{inline_json}')
        mock_iam.add_role_to_profile.assert_called_once_with('pname', 'rname')

    @mock.patch('ebcli.operations.commonops.iam')
    @mock.patch('ebcli.operations.commonops.io')
    def test_create_instance_profile_successful_omitting_role_name(self, _, mock_iam):
        commonops.create_instance_profile('pname', ['policies'])

        mock_iam.create_instance_profile.assert_called_once_with('pname')
        mock_iam.create_role_with_policy.assert_called_once_with('pname', iam_documents.EC2_ASSUME_ROLE_PERMISSION, ['policies'])
        mock_iam.add_role_to_profile.assert_called_once_with('pname', 'pname')
        mock_iam.put_role_policy.assert_not_called()

    @mock.patch('ebcli.operations.commonops.iam')
    @mock.patch('ebcli.operations.commonops.io')
    def test_create_instance_profile_without_permission(self, mock_io, mock_iam):
        mock_iam.create_instance_profile.side_effect = NotAuthorizedError()
        commonops.create_instance_profile('pname', 'policies', 'rname')

        mock_iam.create_instance_profile.assert_called_once_with('pname')
        mock_iam.create_role_with_policy.assert_not_called()
        mock_iam.put_role_policy.assert_not_called()
        mock_iam.add_role_to_profile.assert_not_called()

        mock_io.log_warning.assert_called_once()

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk')
    def test_get_solution_stack(self, mock_beanstalk):
        solutions = {
            "solution_strings": [
                # EB platforms specified in the format displayed by `eb platform list`
                "docker-1.11.2",
                "docker-1.12.6",
                "docker-1.6.2",
                "docker-1.7.1",
                "docker-1.9.1",
                "docker-17.03.1-ce",
                "glassfish-4.0-java-7-(preconfigured-docker)",
                "glassfish-4.1-java-8-(preconfigured-docker)",
                "go-1.3-(preconfigured-docker)",
                "go-1.4",
                "go-1.4-(preconfigured-docker)",
                "go-1.5",
                "go-1.6",
                "go-1.8",
                "iis-10.0",
                "iis-7.5",
                "iis-8",
                "iis-8.5",
                "java-7",
                "java-8",
                "multi-container-docker-1.11.2-(generic)",
                "multi-container-docker-1.6.2-(generic)",
                "multi-container-docker-1.9.1-(generic)",
                "multi-container-docker-17.03.1-ce-(generic)",
                "node.js",
                "packer-1.0.0",
                "packer-1.0.3",
                "php-5.3",
                "php-5.4",
                "php-5.5",
                "php-5.6",
                "php-7.0",
                "python",
                "python-2.7",
                "python-3.4",
                "python-3.4-(preconfigured-docker)",
                "ruby-1.9.3",
                "ruby-2.0-(passenger-standalone)",
                "ruby-2.0-(puma)",
                "ruby-2.1-(passenger-standalone)",
                "ruby-2.1-(puma)",
                "ruby-2.2-(passenger-standalone)",
                "ruby-2.2-(puma)",
                "ruby-2.3-(passenger-standalone)",
                "ruby-2.3-(puma)",
                "tomcat-6",
                "tomcat-7",
                "tomcat-7-java-6",
                "tomcat-7-java-7",
                "tomcat-8-java-8",

                # EB environments listed in the full format
                '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0',
                '64bit Windows Server 2016 v1.2.0 running IIS 10.0',
                '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5',
                '64bit Windows Server 2012 R2 v1.2.0 running IIS 8.5',
                '64bit Windows Server 2012 v1.2.0 running IIS 8',
                '64bit Windows Server 2008 R2 v1.2.0 running IIS 7.5',
                '64bit Amazon Linux 2017.03 v2.5.3 running Java 8',
                '64bit Amazon Linux 2017.03 v2.5.3 running Java 7',
                '64bit Amazon Linux 2017.03 v4.2.1 running Node.js',
                '64bit Amazon Linux 2017.03 v4.2.0 running Node.js',
                '64bit Amazon Linux 2017.03 v4.1.1 running Node.js',
                '64bit Amazon Linux 2015.09 v2.0.8 running Node.js',
                '64bit Amazon Linux 2015.03 v1.4.6 running Node.js',
                '64bit Amazon Linux 2014.03 v1.1.0 running Node.js',
                '32bit Amazon Linux 2014.03 v1.1.0 running Node.js',
                '64bit Amazon Linux 2017.03 v2.4.3 running PHP 5.4',
                '64bit Amazon Linux 2017.03 v2.4.3 running PHP 5.5',
                '64bit Amazon Linux 2017.03 v2.4.3 running PHP 5.6',
                '64bit Amazon Linux 2017.03 v2.4.3 running PHP 7.0',
                '64bit Amazon Linux 2017.03 v2.4.2 running PHP 5.4',
                '64bit Amazon Linux 2017.03 v2.4.2 running PHP 5.6',
                '64bit Amazon Linux 2017.03 v2.4.2 running PHP 7.0',
                '64bit Amazon Linux 2017.03 v2.4.1 running PHP 5.6',
                '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.4',
                '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.5',
                '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.6',
                '64bit Amazon Linux 2016.03 v2.1.6 running PHP 7.0',
                '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.6',
                '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.5',
                '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.4',
                '64bit Amazon Linux 2014.03 v1.1.0 running PHP 5.5',
                '64bit Amazon Linux 2014.03 v1.1.0 running PHP 5.4',
                '32bit Amazon Linux 2014.03 v1.1.0 running PHP 5.5',
                '32bit Amazon Linux 2014.03 v1.1.0 running PHP 5.4',
                '64bit Amazon Linux running PHP 5.3',
                '32bit Amazon Linux running PHP 5.3',
                '64bit Amazon Linux 2017.03 v2.5.0 running Python 3.4',
                '64bit Amazon Linux 2017.03 v2.5.0 running Python',
                '64bit Amazon Linux 2017.03 v2.5.0 running Python 2.7',
                '64bit Amazon Linux 2015.03 v1.4.6 running Python 3.4',
                '64bit Amazon Linux 2015.03 v1.4.6 running Python 2.7',
                '64bit Amazon Linux 2015.03 v1.4.6 running Python',
                '64bit Amazon Linux 2014.03 v1.1.0 running Python 2.7',
                '64bit Amazon Linux 2014.03 v1.1.0 running Python',
                '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7',
                '32bit Amazon Linux 2014.03 v1.1.0 running Python',
                '64bit Amazon Linux running Python',
                '32bit Amazon Linux running Python',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.3 (Puma)',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.2 (Puma)',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.1 (Puma)',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.0 (Puma)',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.3 (Passenger Standalone)',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.2 (Passenger Standalone)',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.1 (Passenger Standalone)',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.0 (Passenger Standalone)',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 1.9.3',
                '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.2 (Puma)',
                '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.2 (Passenger Standalone)',
                '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.1 (Puma)',
                '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.1 (Passenger Standalone)',
                '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.0 (Puma)',
                '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.0 (Passenger Standalone)',
                '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 1.9.3',
                '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Puma)',
                '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Passenger Standalone)',
                '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Puma)',
                '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Passenger Standalone)',
                '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3',
                '32bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3',
                '64bit Amazon Linux 2017.03 v2.6.3 running Tomcat 8 Java 8',
                '64bit Amazon Linux 2017.03 v2.6.3 running Tomcat 7 Java 7',
                '64bit Amazon Linux 2017.03 v2.6.3 running Tomcat 7 Java 6',
                '64bit Amazon Linux 2017.03 v2.6.1 running Tomcat 8 Java 8',
                '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 8 Java 8',
                '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 7 Java 7',
                '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 7 Java 6',
                '64bit Amazon Linux 2015.03 v1.4.4 running Tomcat 7 Java 7',
                '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7',
                '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 6',
                '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7',
                '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 6',
                '64bit Amazon Linux running Tomcat 7',
                '64bit Amazon Linux running Tomcat 6',
                '32bit Amazon Linux running Tomcat 7',
                '32bit Amazon Linux running Tomcat 6',
                '64bit Windows Server Core 2012 R2 running IIS 8.5',
                '64bit Windows Server 2012 R2 running IIS 8.5',
                '64bit Windows Server 2012 running IIS 8',
                '64bit Windows Server 2008 R2 running IIS 7.5',
                '64bit Amazon Linux 2017.03 v2.7.2 running Docker 17.03.1-ce',
                '64bit Amazon Linux 2017.03 v2.7.1 running Docker 17.03.1-ce',
                '64bit Amazon Linux 2017.03 v2.6.0 running Docker 1.12.6',
                '64bit Amazon Linux 2016.09 v2.3.0 running Docker 1.11.2',
                '64bit Amazon Linux 2016.03 v2.1.6 running Docker 1.11.2',
                '64bit Amazon Linux 2016.03 v2.1.0 running Docker 1.9.1',
                '64bit Amazon Linux 2015.09 v2.0.6 running Docker 1.7.1',
                '64bit Amazon Linux 2015.03 v1.4.6 running Docker 1.6.2',
                '64bit Amazon Linux 2017.03 v2.7.3 running Multi-container Docker 17.03.1-ce (Generic)',
                '64bit Amazon Linux 2016.03 v2.1.6 running Multi-container Docker 1.11.2 (Generic)',
                '64bit Amazon Linux 2016.03 v2.1.0 running Multi-container Docker 1.9.1 (Generic)',
                '64bit Amazon Linux 2015.03 v1.4.6 running Multi-container Docker 1.6.2 (Generic)',
                '64bit Debian jessie v2.7.2 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
                '64bit Debian jessie v2.7.2 running GlassFish 4.0 Java 7 (Preconfigured - Docker)',
                '64bit Debian jessie v1.4.6 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
                '64bit Debian jessie v1.4.6 running GlassFish 4.0 Java 7 (Preconfigured - Docker)',
                '64bit Debian jessie v2.7.2 running Go 1.4 (Preconfigured - Docker)',
                '64bit Debian jessie v2.7.2 running Go 1.3 (Preconfigured - Docker)',
                '64bit Debian jessie v1.4.6 running Go 1.4 (Preconfigured - Docker)',
                '64bit Debian jessie v1.4.6 running Go 1.3 (Preconfigured - Docker)',
                '64bit Debian jessie v2.7.2 running Python 3.4 (Preconfigured - Docker)',
                '64bit Debian jessie v1.4.6 running Python 3.4 (Preconfigured - Docker)',
                '64bit Amazon Linux 2017.03 v2.5.1 running Go 1.8',
                '64bit Amazon Linux 2016.09 v2.3.3 running Go 1.6',
                '64bit Amazon Linux 2016.09 v2.3.0 running Go 1.5',
                '64bit Amazon Linux 2016.03 v2.1.0 running Go 1.4',
                '64bit Amazon Linux 2017.03 v2.3.1 running Packer 1.0.3',
                '64bit Amazon Linux 2017.03 v2.2.2 running Packer 1.0.0',

                # EB platforms specified in a format customers might specify
                "Node.js",
                "PHP 5.6",
                "PHP 5.3",
                "Python 3.4",
                "Python",
                "Ruby 2.3 (Puma)",
                "Ruby 2.3 (Passenger Standalone)",
                "Tomcat 8 Java 8",
                "Tomcat 7",
                "IIS 8.5",
                "IIS 8.5",
                "IIS 8",
                "Docker 1.12.6",
                "Multi-container Docker 17.03.1-ce (Generic)",
                "Multi-container Docker 1.11.2 (Generic)",
                "GlassFish 4.1 Java 8 (Preconfigured - Docker)",
                "Go 1.4 (Preconfigured - Docker)",
                "Python 3.4 (Preconfigured - Docker)",
                "Java 8",
                "Java 7",
                "Go 1.8",
                "Go 1.6",
                "Go 1.5",
                "Go 1.4",
                "Packer 1.0.0",

                # custom platform names in the non-ARN representation
                "nfs_test_1",
                "NodePlatform_AmazonLinux",
                "NodePlatform_Ubuntu"
            ],
            "solution_stacks": [
                '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0',
                '64bit Windows Server 2016 v1.2.0 running IIS 10.0',
                '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5',
                '64bit Windows Server 2012 R2 v1.2.0 running IIS 8.5',
                '64bit Windows Server 2012 v1.2.0 running IIS 8',
                '64bit Windows Server 2008 R2 v1.2.0 running IIS 7.5',
                '64bit Amazon Linux 2017.03 v2.5.3 running Java 8',
                '64bit Amazon Linux 2017.03 v2.5.3 running Java 7',
                '64bit Amazon Linux 2017.03 v4.2.1 running Node.js',
                '64bit Amazon Linux 2017.03 v4.2.0 running Node.js',
                '64bit Amazon Linux 2017.03 v4.1.1 running Node.js',
                '64bit Amazon Linux 2015.09 v2.0.8 running Node.js',
                '64bit Amazon Linux 2015.03 v1.4.6 running Node.js',
                '64bit Amazon Linux 2014.03 v1.1.0 running Node.js',
                '32bit Amazon Linux 2014.03 v1.1.0 running Node.js',
                '64bit Amazon Linux 2017.03 v2.4.3 running PHP 5.4',
                '64bit Amazon Linux 2017.03 v2.4.3 running PHP 5.5',
                '64bit Amazon Linux 2017.03 v2.4.3 running PHP 5.6',
                '64bit Amazon Linux 2017.03 v2.4.3 running PHP 7.0',
                '64bit Amazon Linux 2017.03 v2.4.2 running PHP 5.4',
                '64bit Amazon Linux 2017.03 v2.4.2 running PHP 5.6',
                '64bit Amazon Linux 2017.03 v2.4.2 running PHP 7.0',
                '64bit Amazon Linux 2017.03 v2.4.1 running PHP 5.6',
                '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.4',
                '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.5',
                '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.6',
                '64bit Amazon Linux 2016.03 v2.1.6 running PHP 7.0',
                '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.6',
                '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.5',
                '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.4',
                '64bit Amazon Linux 2014.03 v1.1.0 running PHP 5.5',
                '64bit Amazon Linux 2014.03 v1.1.0 running PHP 5.4',
                '32bit Amazon Linux 2014.03 v1.1.0 running PHP 5.5',
                '32bit Amazon Linux 2014.03 v1.1.0 running PHP 5.4',
                '64bit Amazon Linux running PHP 5.3',
                '32bit Amazon Linux running PHP 5.3',
                '64bit Amazon Linux 2017.03 v2.5.0 running Python 3.4',
                '64bit Amazon Linux 2017.03 v2.5.0 running Python',
                '64bit Amazon Linux 2017.03 v2.5.0 running Python 2.7',
                '64bit Amazon Linux 2015.03 v1.4.6 running Python 3.4',
                '64bit Amazon Linux 2015.03 v1.4.6 running Python 2.7',
                '64bit Amazon Linux 2015.03 v1.4.6 running Python',
                '64bit Amazon Linux 2014.03 v1.1.0 running Python 2.7',
                '64bit Amazon Linux 2014.03 v1.1.0 running Python',
                '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7',
                '32bit Amazon Linux 2014.03 v1.1.0 running Python',
                '64bit Amazon Linux running Python',
                '32bit Amazon Linux running Python',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.3 (Puma)',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.2 (Puma)',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.1 (Puma)',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.0 (Puma)',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.3 (Passenger Standalone)',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.2 (Passenger Standalone)',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.1 (Passenger Standalone)',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.0 (Passenger Standalone)',
                '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 1.9.3',
                '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.2 (Puma)',
                '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.2 (Passenger Standalone)',
                '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.1 (Puma)',
                '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.1 (Passenger Standalone)',
                '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.0 (Puma)',
                '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.0 (Passenger Standalone)',
                '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 1.9.3',
                '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Puma)',
                '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Passenger Standalone)',
                '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Puma)',
                '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Passenger Standalone)',
                '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3',
                '32bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3',
                '64bit Amazon Linux 2017.03 v2.6.3 running Tomcat 8 Java 8',
                '64bit Amazon Linux 2017.03 v2.6.3 running Tomcat 7 Java 7',
                '64bit Amazon Linux 2017.03 v2.6.3 running Tomcat 7 Java 6',
                '64bit Amazon Linux 2017.03 v2.6.1 running Tomcat 8 Java 8',
                '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 8 Java 8',
                '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 7 Java 7',
                '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 7 Java 6',
                '64bit Amazon Linux 2015.03 v1.4.4 running Tomcat 7 Java 7',
                '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7',
                '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 6',
                '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7',
                '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 6',
                '64bit Amazon Linux running Tomcat 7',
                '64bit Amazon Linux running Tomcat 6',
                '32bit Amazon Linux running Tomcat 7',
                '32bit Amazon Linux running Tomcat 6',
                '64bit Windows Server Core 2012 R2 running IIS 8.5',
                '64bit Windows Server 2012 R2 running IIS 8.5',
                '64bit Windows Server 2012 running IIS 8',
                '64bit Windows Server 2008 R2 running IIS 7.5',
                '64bit Amazon Linux 2017.03 v2.7.2 running Docker 17.03.1-ce',
                '64bit Amazon Linux 2017.03 v2.7.1 running Docker 17.03.1-ce',
                '64bit Amazon Linux 2017.03 v2.6.0 running Docker 1.12.6',
                '64bit Amazon Linux 2016.09 v2.3.0 running Docker 1.11.2',
                '64bit Amazon Linux 2016.03 v2.1.6 running Docker 1.11.2',
                '64bit Amazon Linux 2016.03 v2.1.0 running Docker 1.9.1',
                '64bit Amazon Linux 2015.09 v2.0.6 running Docker 1.7.1',
                '64bit Amazon Linux 2015.03 v1.4.6 running Docker 1.6.2',
                '64bit Amazon Linux 2017.03 v2.7.3 running Multi-container Docker 17.03.1-ce (Generic)',
                '64bit Amazon Linux 2016.03 v2.1.6 running Multi-container Docker 1.11.2 (Generic)',
                '64bit Amazon Linux 2016.03 v2.1.0 running Multi-container Docker 1.9.1 (Generic)',
                '64bit Amazon Linux 2015.03 v1.4.6 running Multi-container Docker 1.6.2 (Generic)',
                '64bit Debian jessie v2.7.2 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
                '64bit Debian jessie v2.7.2 running GlassFish 4.0 Java 7 (Preconfigured - Docker)',
                '64bit Debian jessie v1.4.6 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
                '64bit Debian jessie v1.4.6 running GlassFish 4.0 Java 7 (Preconfigured - Docker)',
                '64bit Debian jessie v2.7.2 running Go 1.4 (Preconfigured - Docker)',
                '64bit Debian jessie v2.7.2 running Go 1.3 (Preconfigured - Docker)',
                '64bit Debian jessie v1.4.6 running Go 1.4 (Preconfigured - Docker)',
                '64bit Debian jessie v1.4.6 running Go 1.3 (Preconfigured - Docker)',
                '64bit Debian jessie v2.7.2 running Python 3.4 (Preconfigured - Docker)',
                '64bit Debian jessie v1.4.6 running Python 3.4 (Preconfigured - Docker)',
                '64bit Amazon Linux 2017.03 v2.5.1 running Go 1.8',
                '64bit Amazon Linux 2016.09 v2.3.3 running Go 1.6',
                '64bit Amazon Linux 2016.09 v2.3.0 running Go 1.5',
                '64bit Amazon Linux 2016.03 v2.1.0 running Go 1.4',
                '64bit Amazon Linux 2017.03 v2.3.1 running Packer 1.0.3',
                '64bit Amazon Linux 2017.03 v2.2.2 running Packer 1.0.0',

                # custom platforms
                "arn:aws:elasticbeanstalk:us-west-2:12345678:platform/nfs_test_1/1.0.0",
                "arn:aws:elasticbeanstalk:us-west-2:12345678:platform/NodePlatform_AmazonLinux/1.0.3",
                "arn:aws:elasticbeanstalk:us-west-2:12345678:platform/NodePlatform_Ubuntu/1.0.0"
            ]
        }

        solution_stacks = [SolutionStack(solution_stack) for solution_stack in solutions['solution_stacks']]
        mock_beanstalk.get_available_solution_stacks = Mock(return_value=solution_stacks)

        for solution_string in solutions['solution_strings']:
            commonops.get_solution_stack(solution_string)
