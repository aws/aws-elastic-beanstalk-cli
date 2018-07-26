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
import datetime

from dateutil import tz
import mock
from pytest_socket import enable_socket, disable_socket
import unittest

from ebcli.operations import statusops
from ebcli.objects.environment import Environment
from ebcli.objects.platform import PlatformVersion
from ebcli.objects.tier import Tier

from .. import mock_responses


class TestStatusOps(unittest.TestCase):
    def setUp(self):
        disable_socket()

    def tearDown(self):
        enable_socket()

    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.operations.statusops.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    @mock.patch('ebcli.operations.statusops.io.echo')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_branch')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_repository')
    def test_status__non_verbose_mode__codecommit_setup__using_non_latest_platform(
            self,
            get_default_repository_mock,
            get_default_branch_mock,
            echo_mock,
            log_alert_mock,
            find_solution_stack_from_string_mock,
            get_environment_mock
    ):
        environment_object = Environment.json_to_environment_object(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments'][0]
        )
        environment_object.platform = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5')
        get_environment_mock.return_value = environment_object
        find_solution_stack_from_string_mock.return_value = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_default_branch_mock.return_value = 'branch'
        get_default_repository_mock.return_value = 'repository'

        statusops.status('my-application', 'environment-1', False)

        log_alert_mock.assert_called_once_with(
            'There is a newer version of the platform used by your environment. '
            'You can upgrade your environment to the most recent platform version by typing "eb upgrade".'
        )
        echo_mock.assert_has_calls(
            [
                mock.call('Environment details for:', 'environment-1'),
                mock.call('  Application name:', 'my-application'),
                mock.call('  Region:', 'us-west-2'),
                mock.call('  Deployed Version:', 'Sample Application'),
                mock.call('  Environment ID:', 'e-sfsdfsfasdads'),
                mock.call('  Platform:', PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5')),
                mock.call('  Tier:', Tier.from_raw_string('webserver')),
                mock.call('  CNAME:', 'environment-1.us-west-2.elasticbeanstalk.com'),
                mock.call('  Updated:', datetime.datetime(2018, 3, 27, 23, 47, 41, 830000, tzinfo=tz.tzutc())),
                mock.call('  Status:', 'Ready'),
                mock.call('  Health:', 'Green'),
                mock.call('Current CodeCommit settings:'),
                mock.call('  Repository: repository'),
                mock.call('  Branch: branch')
            ]
        )

    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.operations.statusops.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    @mock.patch('ebcli.operations.statusops.io.echo')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_branch')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_repository')
    def test_status__non_verbose_mode__codecommit_not_setup__using_non_latest_platform(
            self,
            get_default_repository_mock,
            get_default_branch_mock,
            echo_mock,
            log_alert_mock,
            find_solution_stack_from_string_mock,
            get_environment_mock
    ):
        environment_object = Environment.json_to_environment_object(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments'][0]
        )
        environment_object.platform = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5')
        get_environment_mock.return_value = environment_object
        get_environment_mock.platform = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5')
        find_solution_stack_from_string_mock.return_value = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_default_branch_mock.return_value = None
        get_default_repository_mock.return_value = None

        statusops.status('my-application', 'environment-1', False)

        log_alert_mock.assert_called_once_with(
            'There is a newer version of the platform used by your environment. '
            'You can upgrade your environment to the most recent platform version by typing "eb upgrade".'
        )
        echo_mock.assert_has_calls(
            [
                mock.call('Environment details for:', 'environment-1'),
                mock.call('  Application name:', 'my-application'),
                mock.call('  Region:', 'us-west-2'),
                mock.call('  Deployed Version:', 'Sample Application'),
                mock.call('  Environment ID:', 'e-sfsdfsfasdads'),
                mock.call('  Platform:', PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5')),
                mock.call('  Tier:', Tier.from_raw_string('webserver')),
                mock.call('  CNAME:', 'environment-1.us-west-2.elasticbeanstalk.com'),
                mock.call('  Updated:', datetime.datetime(2018, 3, 27, 23, 47, 41, 830000, tzinfo=tz.tzutc())),
                mock.call('  Status:', 'Ready'),
                mock.call('  Health:', 'Green')
            ]
        )

    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.operations.statusops.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    @mock.patch('ebcli.operations.statusops.io.echo')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_branch')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_repository')
    def test_status__non_verbose_mode__codecommit_setup__using_latest_platform(
            self,
            get_default_repository_mock,
            get_default_branch_mock,
            echo_mock,
            log_alert_mock,
            find_solution_stack_from_string_mock,
            get_environment_mock
    ):
        environment_object = Environment.json_to_environment_object(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments'][0]
        )
        environment_object.platform = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_environment_mock.return_value = environment_object
        find_solution_stack_from_string_mock.return_value = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_default_branch_mock.return_value = 'branch'
        get_default_repository_mock.return_value = 'repository'

        statusops.status('my-application', 'environment-1', False)

        log_alert_mock.assert_not_called()
        echo_mock.assert_has_calls(
            [
                mock.call('Environment details for:', 'environment-1'),
                mock.call('  Application name:', 'my-application'),
                mock.call('  Region:', 'us-west-2'),
                mock.call('  Deployed Version:', 'Sample Application'),
                mock.call('  Environment ID:', 'e-sfsdfsfasdads'),
                mock.call('  Platform:', PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')),
                mock.call('  Tier:', Tier.from_raw_string('webserver')),
                mock.call('  CNAME:', 'environment-1.us-west-2.elasticbeanstalk.com'),
                mock.call('  Updated:', datetime.datetime(2018, 3, 27, 23, 47, 41, 830000, tzinfo=tz.tzutc())),
                mock.call('  Status:', 'Ready'),
                mock.call('  Health:', 'Green'),
                mock.call('Current CodeCommit settings:'),
                mock.call('  Repository: repository'),
                mock.call('  Branch: branch')
            ]
        )

    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.operations.statusops.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    @mock.patch('ebcli.operations.statusops.io.echo')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_branch')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_repository')
    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environment_resources')
    @mock.patch('ebcli.operations.statusops.elbv2.get_target_groups_for_load_balancer')
    @mock.patch('ebcli.operations.statusops.elbv2.get_target_group_healths')
    def test_status__verbose_mode__elbv2(
            self,
            get_target_group_healths_mock,
            get_target_groups_for_load_balancer_mock,
            get_environment_resources_mock,
            get_default_repository_mock,
            get_default_branch_mock,
            echo_mock,
            log_alert_mock,
            find_solution_stack_from_string_mock,
            get_environment_mock
    ):
        environment_object = Environment.json_to_environment_object(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments'][0]
        )
        environment_object.platform = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_environment_mock.return_value = environment_object
        find_solution_stack_from_string_mock.return_value = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_default_branch_mock.return_value = 'branch'
        get_default_repository_mock.return_value = 'repository'
        get_environment_resources_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENT_RESOURCES_RESPONSE__ELBV2_ENVIRONMENT
        get_target_groups_for_load_balancer_mock.return_value = mock_responses.DESCRIBE_TARGET_GROUPS_RESPONSE['TargetGroups']
        get_target_group_healths_mock.return_value = {
            "arn:aws:elasticloadbalancing:us-west-2:123123123123:targetgroup/awseb-AWSEB-179V6JWWL9HI5/e57decc4139bfdd2": mock_responses.DESCRIBE_TARGET_HEALTH_RESPONSE
        }

        statusops.status('my-application', 'environment-1', True)

        log_alert_mock.assert_not_called()
        echo_mock.assert_has_calls(
            [
                mock.call('Environment details for:', 'environment-1'),
                mock.call('  Application name:', 'my-application'),
                mock.call('  Region:', 'us-west-2'),
                mock.call('  Deployed Version:', 'Sample Application'),
                mock.call('  Environment ID:', 'e-sfsdfsfasdads'),
                mock.call('  Platform:', PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')),
                mock.call('  Tier:', Tier.from_raw_string('webserver')),
                mock.call('  CNAME:', 'environment-1.us-west-2.elasticbeanstalk.com'),
                mock.call('  Updated:', datetime.datetime(2018, 3, 27, 23, 47, 41, 830000, tzinfo=tz.tzutc())),
                mock.call('  Status:', 'Ready'),
                mock.call('  Health:', 'Green'),
                mock.call('  Running instances:', 1),
                mock.call('          ', 'i-01641763db1c0cb47: healthy'),
                mock.call('Current CodeCommit settings:'),
                mock.call('  Repository: repository'),
                mock.call('  Branch: branch')
            ]
        )

    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.operations.statusops.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    @mock.patch('ebcli.operations.statusops.io.echo')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_branch')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_repository')
    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environment_resources')
    @mock.patch('ebcli.operations.statusops.elbv2.get_target_groups_for_load_balancer')
    @mock.patch('ebcli.operations.statusops.elbv2.get_target_group_healths')
    def test_status__verbose_mode__elbv2__elb_registration_in_progress__some_instances_are_not_registered_with_target_groups(
            self,
            get_target_group_healths_mock,
            get_target_groups_for_load_balancer_mock,
            get_environment_resources_mock,
            get_default_repository_mock,
            get_default_branch_mock,
            echo_mock,
            log_alert_mock,
            find_solution_stack_from_string_mock,
            get_environment_mock
    ):
        environment_object = Environment.json_to_environment_object(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments'][0]
        )
        environment_object.platform = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_environment_mock.return_value = environment_object
        find_solution_stack_from_string_mock.return_value = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_default_branch_mock.return_value = 'branch'
        get_default_repository_mock.return_value = 'repository'
        get_environment_resources_response = mock_responses.DESCRIBE_ENVIRONMENT_RESOURCES_RESPONSE__ELBV2_ENVIRONMENT
        get_environment_resources_response['EnvironmentResources']['Instances'].append(
            {
                "Id": "i-12141763d121c0cb47"
            }
        )
        get_environment_resources_mock.return_value = get_environment_resources_response
        get_target_groups_for_load_balancer_mock.return_value = mock_responses.DESCRIBE_TARGET_GROUPS_RESPONSE['TargetGroups']
        get_target_group_healths_mock.return_value = {
            "arn:aws:elasticloadbalancing:us-west-2:123123123123:targetgroup/awseb-AWSEB-179V6JWWL9HI5/e57decc4139bfdd2": mock_responses.DESCRIBE_TARGET_HEALTH_RESPONSE__REGISTRATION_IN_PROGRESS
        }

        statusops.status('my-application', 'environment-1', True)

        log_alert_mock.assert_not_called()
        echo_mock.assert_has_calls(
            [
                mock.call('Environment details for:', 'environment-1'),
                mock.call('  Application name:', 'my-application'),
                mock.call('  Region:', 'us-west-2'),
                mock.call('  Deployed Version:', 'Sample Application'),
                mock.call('  Environment ID:', 'e-sfsdfsfasdads'),
                mock.call('  Platform:', PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')),
                mock.call('  Tier:', Tier.from_raw_string('webserver')),
                mock.call('  CNAME:', 'environment-1.us-west-2.elasticbeanstalk.com'),
                mock.call('  Updated:', datetime.datetime(2018, 3, 27, 23, 47, 41, 830000, tzinfo=tz.tzutc())),
                mock.call('  Status:', 'Ready'),
                mock.call('  Health:', 'Green'),
                mock.call('  Running instances:', 2),
                mock.call('          ', 'i-01641763db1c0cb47: initial'),
                mock.call('               ', 'Description: Target registration is in progress'),
                mock.call('               ', 'Reason: Elb.RegistrationInProgress'),
                mock.call('          ', 'i-12141763d121c0cb47:', 'N/A (Not registered with Target Group)'),
                mock.call('Current CodeCommit settings:'),
                mock.call('  Repository: repository'),
                mock.call('  Branch: branch')
                ]
        )

    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.operations.statusops.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    @mock.patch('ebcli.operations.statusops.io.echo')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_branch')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_repository')
    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environment_resources')
    @mock.patch('ebcli.operations.statusops.elb.get_health_of_instances')
    def test_status__verbose_mode__elb(
            self,
            get_health_of_instances_mock,
            get_environment_resources_mock,
            get_default_repository_mock,
            get_default_branch_mock,
            echo_mock,
            log_alert_mock,
            find_solution_stack_from_string_mock,
            get_environment_mock
    ):
        environment_object = Environment.json_to_environment_object(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments'][0]
        )
        environment_object.platform = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_environment_mock.return_value = environment_object
        find_solution_stack_from_string_mock.return_value = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_default_branch_mock.return_value = 'branch'
        get_default_repository_mock.return_value = 'repository'
        get_environment_resources_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENT_RESOURCES_RESPONSE
        get_health_of_instances_mock.return_value = mock_responses.DESCRIBE_INSTANCE_HEALTH['InstanceStates']

        statusops.status('my-application', 'environment-1', True)

        log_alert_mock.assert_not_called()
        echo_mock.assert_has_calls(
            [
                mock.call('Environment details for:', 'environment-1'),
                mock.call('  Application name:', 'my-application'),
                mock.call('  Region:', 'us-west-2'),
                mock.call('  Deployed Version:', 'Sample Application'),
                mock.call('  Environment ID:', 'e-sfsdfsfasdads'),
                mock.call('  Platform:', PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')),
                mock.call('  Tier:', Tier.from_raw_string('webserver')),
                mock.call('  CNAME:', 'environment-1.us-west-2.elasticbeanstalk.com'),
                mock.call('  Updated:', datetime.datetime(2018, 3, 27, 23, 47, 41, 830000, tzinfo=tz.tzutc())),
                mock.call('  Status:', 'Ready'),
                mock.call('  Health:', 'Green'),
                mock.call('  Running instances:', 2),
                mock.call('     ', 'i-23452345346456566:', 'InService'),
                mock.call('     ', 'i-21312312312312312:', 'OutOfService'),
                mock.call('Current CodeCommit settings:'),
                mock.call('  Repository: repository'),
                mock.call('  Branch: branch')
            ]
        )

    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.operations.statusops.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    @mock.patch('ebcli.operations.statusops.io.echo')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_branch')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_repository')
    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environment_resources')
    def test_status__verbose_mode__non_load_balanced(
            self,
            get_environment_resources_mock,
            get_default_repository_mock,
            get_default_branch_mock,
            echo_mock,
            log_alert_mock,
            find_solution_stack_from_string_mock,
            get_environment_mock
    ):
        environment_object = Environment.json_to_environment_object(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments'][0]
        )
        environment_object.platform = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_environment_mock.return_value = environment_object
        find_solution_stack_from_string_mock.return_value = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_default_branch_mock.return_value = 'branch'
        get_default_repository_mock.return_value = 'repository'
        get_environment_resources_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENT_RESOURCES_RESPONSE__SINGLE_INSTANCE_ENVIRONMENT

        statusops.status('my-application', 'environment-1', True)

        log_alert_mock.assert_not_called()
        echo_mock.assert_has_calls(
            [
                mock.call('Environment details for:', 'environment-1'),
                mock.call('  Application name:', 'my-application'),
                mock.call('  Region:', 'us-west-2'),
                mock.call('  Deployed Version:', 'Sample Application'),
                mock.call('  Environment ID:', 'e-sfsdfsfasdads'),
                mock.call('  Platform:', PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')),
                mock.call('  Tier:', Tier.from_raw_string('webserver')),
                mock.call('  CNAME:', 'environment-1.us-west-2.elasticbeanstalk.com'),
                mock.call('  Updated:', datetime.datetime(2018, 3, 27, 23, 47, 41, 830000, tzinfo=tz.tzutc())),
                mock.call('  Status:', 'Ready'),
                mock.call('  Health:', 'Green'),
                mock.call('  Running instances:', 1),
                mock.call('Current CodeCommit settings:'),
                mock.call('  Repository: repository'),
                mock.call('  Branch: branch')
            ]
        )
