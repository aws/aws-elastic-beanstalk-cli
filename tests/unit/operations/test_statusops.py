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
import unittest

from ebcli.operations import statusops
from ebcli.objects.environment import Environment
from ebcli.objects.platform import PlatformBranch, PlatformVersion
from ebcli.objects.tier import Tier

from .. import mock_responses


class TestStatusOps(unittest.TestCase):

    @mock.patch('ebcli.operations.statusops.alert_platform_status')
    def test_alert_environment_status(
        self,
        alert_platform_status_mock,
    ):
        platform_version = PlatformVersion('arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/2.9.2')
        environment = Environment(
            platform=platform_version
        )

        statusops.alert_environment_status(environment)

        alert_platform_status_mock.assert_called_once_with(
            environment.platform,
            platform_old_alert='The platform version that your environment is using '
                'isn\'t up to date. There\'s a newer version. Type '
                '"eb upgrade" to upgrade your environment to the '
                'latest platform version.',
            platform_not_recommended_alert="The platform version that your environment "
                "is using isn't recommended. There's a "
                "recommended version in the same platform "
                "branch.",
            branch_deprecated_alert='Your environment is using a deprecated '
                'platform branch. It might not be '
                'supported in the future.',
            branch_retired_alert="Your environment is using a retired "
                "platform branch. It's no longer supported.",
        )

    @mock.patch('ebcli.operations.statusops.platform_branch_ops.get_platform_branch_by_name')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    def test_alert_platform_branch_status__supported(
        self,
        log_alert_mock,
        get_platform_branch_by_name_mock,
    ):
        branch = PlatformBranch('PHP 7.1 running on 64bit Amazon Linux')
        branch_summary = {
            'BranchName': 'PHP 7.1 running on 64bit Amazon Linux',
            'LifecycleState': 'Supported',
        }

        get_platform_branch_by_name_mock.return_value = branch_summary

        statusops.alert_platform_branch_status(branch)

        get_platform_branch_by_name_mock.assert_called_once_with(branch.branch_name)
        log_alert_mock.assert_not_called()

    @mock.patch('ebcli.operations.statusops.platform_branch_ops.get_platform_branch_by_name')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    def test_alert_platform_branch_status__supported_given_branch_name(
        self,
        log_alert_mock,
        get_platform_branch_by_name_mock,
    ):
        branch = 'PHP 7.1 running on 64bit Amazon Linux'
        branch_summary = {
            'BranchName': 'PHP 7.1 running on 64bit Amazon Linux',
            'LifecycleState': 'Supported',
        }

        get_platform_branch_by_name_mock.return_value = branch_summary

        statusops.alert_platform_branch_status(branch)

        get_platform_branch_by_name_mock.assert_called_once_with(branch)
        log_alert_mock.assert_not_called()

    @mock.patch('ebcli.operations.statusops.platform_branch_ops.get_platform_branch_by_name')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    def test_alert_platform_branch_status__deprecated(
        self,
        log_alert_mock,
        get_platform_branch_by_name_mock,
    ):
        branch = PlatformBranch('PHP 7.1 running on 64bit Amazon Linux')
        branch_summary = {
            'BranchName': 'PHP 7.1 running on 64bit Amazon Linux',
            'LifecycleState': 'Deprecated',
        }

        get_platform_branch_by_name_mock.return_value = branch_summary

        statusops.alert_platform_branch_status(branch)
        
        get_platform_branch_by_name_mock.assert_called_once_with(branch.branch_name)
        log_alert_mock.assert_called_once_with(
            'You chose a deprecated platform branch. It '
            'might not be supported in the future.\n')

    @mock.patch('ebcli.operations.statusops.platform_branch_ops.get_platform_branch_by_name')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    def test_alert_platform_branch_status__deprecated_given_custom_alert(
        self,
        log_alert_mock,
        get_platform_branch_by_name_mock,
    ):
        branch = 'PHP 7.1 running on 64bit Amazon Linux'
        branch_summary = {
            'BranchName': 'PHP 7.1 running on 64bit Amazon Linux',
            'LifecycleState': 'Deprecated',
        }

        get_platform_branch_by_name_mock.return_value = branch_summary

        statusops.alert_platform_branch_status(branch)

        get_platform_branch_by_name_mock.assert_called_once_with(branch)
        log_alert_mock.assert_called_once_with(
            'The platform you chose is deprecated and may not be supported in the future.\n')

    @mock.patch('ebcli.operations.statusops.platform_branch_ops.get_platform_branch_by_name')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    def test_alert_platform_branch_status__deprecated_given_custom_alert(
        self,
        log_alert_mock,
        get_platform_branch_by_name_mock,
    ):
        branch = PlatformBranch('PHP 7.1 running on 64bit Amazon Linux')
        custom_alert = 'This is a custom alert'
        branch_summary = {
            'BranchName': 'PHP 7.1 running on 64bit Amazon Linux',
            'LifecycleState': 'Deprecated',
        }

        get_platform_branch_by_name_mock.return_value = branch_summary

        statusops.alert_platform_branch_status(
            branch,
            branch_deprecated_alert=custom_alert
        )
        
        get_platform_branch_by_name_mock.assert_called_once_with(branch.branch_name)
        log_alert_mock.assert_called_once_with(custom_alert + '\n')

    @mock.patch('ebcli.operations.statusops.platform_branch_ops.get_platform_branch_by_name')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    def test_alert_platform_branch_status__retired(
        self,
        log_alert_mock,
        get_platform_branch_by_name_mock,
    ):
        branch = PlatformBranch('PHP 7.1 running on 64bit Amazon Linux')
        branch_summary = {
            'BranchName': 'PHP 7.1 running on 64bit Amazon Linux',
            'LifecycleState': 'Retired',
        }

        get_platform_branch_by_name_mock.return_value = branch_summary

        statusops.alert_platform_branch_status(branch)
        
        get_platform_branch_by_name_mock.assert_called_once_with(branch.branch_name)
        log_alert_mock.assert_called_once_with(
            "You chose a retired platform branch. It's no "
            "longer supported.\n")

    @mock.patch('ebcli.operations.statusops.platform_branch_ops.get_platform_branch_by_name')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    def test_alert_platform_branch_status__retired_given_branch_name(
        self,
        log_alert_mock,
        get_platform_branch_by_name_mock,
    ):
        branch = 'PHP 7.1 running on 64bit Amazon Linux'
        branch_summary = {
            'BranchName': 'PHP 7.1 running on 64bit Amazon Linux',
            'LifecycleState': 'Retired',
        }

        get_platform_branch_by_name_mock.return_value = branch_summary

        statusops.alert_platform_branch_status(branch)

        get_platform_branch_by_name_mock.assert_called_once_with(branch)
        log_alert_mock.assert_called_once_with(
            "You chose a retired platform branch. It's no "
            "longer supported.\n")

    @mock.patch('ebcli.operations.statusops.platform_branch_ops.get_platform_branch_by_name')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    def test_alert_platform_branch_status__retired_given_custom_alert(
        self,
        log_alert_mock,
        get_platform_branch_by_name_mock,
    ):
        branch = PlatformBranch('PHP 7.1 running on 64bit Amazon Linux')
        custom_alert = 'This is a custom alert'
        branch_summary = {
            'BranchName': 'PHP 7.1 running on 64bit Amazon Linux',
            'LifecycleState': 'Retired',
        }

        get_platform_branch_by_name_mock.return_value = branch_summary

        statusops.alert_platform_branch_status(
            branch,
            branch_retired_alert=custom_alert
        )
        
        get_platform_branch_by_name_mock.assert_called_once_with(branch.branch_name)
        log_alert_mock.assert_called_once_with(custom_alert + '\n')

    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.describe_platform_version')
    @mock.patch('ebcli.operations.statusops._alert_eb_managed_platform_version_status')
    @mock.patch('ebcli.operations.statusops._alert_custom_platform_version_status')
    def test_alert_platform_version_status__custom_platform(
        self,
        _alert_custom_platform_version_status_mock,
        _alert_eb_managed_platform_version_status_mock,
        describe_platform_version_mock,
    ):
        platform_version = PlatformVersion('arn:aws:elasticbeanstalk:us-east-1:123456789012:platform/PHP 7.1 running on 64bit Amazon Linux/2.9.2')
        platform_version_description = {}
        describe_platform_version_mock.return_value = platform_version_description

        statusops.alert_platform_version_status(platform_version)

        describe_platform_version_mock.assert_called_once_with(platform_version.platform_arn)
        _alert_eb_managed_platform_version_status_mock.assert_not_called()
        _alert_custom_platform_version_status_mock.assert_called_once_with(
            platform_version,
            "The platform version you chose isn't up to date. There's "
            "a newer version.",
        )

    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.describe_platform_version')
    @mock.patch('ebcli.operations.statusops.alert_platform_branch_status')
    @mock.patch('ebcli.operations.statusops.alert_platform_version_status')
    def test_alert_platform_status__eb_managed(
        self,
        alert_platform_version_status_mock,
        alert_platform_branch_status_mock,
        describe_platform_version_mock,
    ):
        platform_version = PlatformVersion('arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/2.9.2')
        platform_version_description = {
            'PlatformBranchName': 'PHP 7.1 running on 64bit Amazon Linux',
        }
        describe_platform_version_mock.return_value = platform_version_description

        statusops.alert_platform_status(platform_version)

        describe_platform_version_mock.assert_called_once_with(platform_version.arn)
        statusops.alert_platform_branch_status.assert_called_once_with(
            'PHP 7.1 running on 64bit Amazon Linux',
            branch_deprecated_alert='You chose a deprecated platform branch. It '
            'might not be supported in the future.',
            branch_retired_alert="You chose a retired platform branch. It's no "
            "longer supported.",
        )
        alert_platform_version_status_mock.assert_called_once_with(
            platform_version,
            platform_old_alert="The platform version you chose isn't up to date. There's "
            "a newer version.",
            platform_not_recommended_alert="The platform version you chose isn't "
            "recommended. There's a recommended version in "
            "the same platform branch.",
        )

    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.describe_platform_version')
    @mock.patch('ebcli.operations.statusops.alert_platform_branch_status')
    @mock.patch('ebcli.operations.statusops.alert_platform_version_status')
    def test_alert_platform_status__eb_managed_with_custom_alerts(
        self,
        alert_platform_version_status_mock,
        alert_platform_branch_status_mock,
        describe_platform_version_mock,
    ):
        platform_version = PlatformVersion('arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/2.9.2')
        platform_version_description = {
            'PlatformBranchName': 'PHP 7.1 running on 64bit Amazon Linux',
        }
        platform_old_alert = 'custom alert 1'
        platform_not_recommended_alert = 'custom alert 2'
        branch_deprecated_alert = 'custom alert 3'
        branch_retired_alert = 'custom alert 4'
        describe_platform_version_mock.return_value = platform_version_description

        statusops.alert_platform_status(
            platform_version,
            platform_old_alert=platform_old_alert,
            platform_not_recommended_alert=platform_not_recommended_alert,
            branch_deprecated_alert=branch_deprecated_alert,
            branch_retired_alert=branch_retired_alert,
        )

        describe_platform_version_mock.assert_called_once_with(platform_version.arn)
        statusops.alert_platform_branch_status.assert_called_once_with(
            'PHP 7.1 running on 64bit Amazon Linux',
            branch_deprecated_alert=branch_deprecated_alert,
            branch_retired_alert=branch_retired_alert,
        )
        alert_platform_version_status_mock.assert_called_once_with(
            platform_version,
            platform_old_alert=platform_old_alert,
            platform_not_recommended_alert=platform_not_recommended_alert,
        )

    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.describe_platform_version')
    @mock.patch('ebcli.operations.statusops.alert_platform_branch_status')
    @mock.patch('ebcli.operations.statusops.alert_platform_version_status')
    def test_alert_platform_status__custom_platform(
        self,
        alert_platform_version_status_mock,
        alert_platform_branch_status_mock,
        describe_platform_version_mock,
    ):
        platform_version = PlatformVersion('arn:aws:elasticbeanstalk:us-east-1:123456789012:platform/PHP 7.1 running on 64bit Amazon Linux/2.9.2')
        platform_version_description = {}
        describe_platform_version_mock.return_value = platform_version_description

        statusops.alert_platform_status(platform_version)

        describe_platform_version_mock.assert_called_once_with(platform_version.arn)
        statusops.alert_platform_branch_status.assert_not_called()
        alert_platform_version_status_mock.assert_called_once_with(
            platform_version,
            platform_old_alert="The platform version you chose isn't up to "
            "date. There's a newer version.",
            platform_not_recommended_alert="The platform version you chose isn't "
            "recommended. There's a recommended version in "
            "the same platform branch.",
        )

    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.describe_platform_version')
    @mock.patch('ebcli.operations.statusops.alert_platform_branch_status')
    @mock.patch('ebcli.operations.statusops.alert_platform_version_status')
    def test_alert_platform_status__custom_platform_with_custom_alerts(
        self,
        alert_platform_version_status_mock,
        alert_platform_branch_status_mock,
        describe_platform_version_mock,
    ):
        platform_version = PlatformVersion('arn:aws:elasticbeanstalk:us-east-1:123456789012:platform/PHP 7.1 running on 64bit Amazon Linux/2.9.2')
        platform_version_description = {}
        platform_old_alert = 'custom alert 1'
        platform_not_recommended_alert = 'custom alert 2'
        describe_platform_version_mock.return_value = platform_version_description

        statusops.alert_platform_status(
            platform_version,
            platform_old_alert=platform_old_alert,
            platform_not_recommended_alert=platform_not_recommended_alert,
        )

        describe_platform_version_mock.assert_called_once_with(platform_version.arn)
        statusops.alert_platform_branch_status.assert_not_called()
        alert_platform_version_status_mock.assert_called_once_with(
            platform_version,
            platform_old_alert=platform_old_alert,
            platform_not_recommended_alert=platform_not_recommended_alert,
        )

    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.operations.statusops.io.echo')
    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environments')
    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environment_resources')
    @mock.patch('ebcli.operations.statusops._print_information_about_elb_and_instances')
    @mock.patch('ebcli.operations.statusops.alert_environment_status')
    @mock.patch('ebcli.operations.statusops._print_codecommit_repositories')
    def test_status(
        self,
        _print_codecommit_repositories_mock,
        alert_environment_status_mock,
        _print_information_about_elb_and_instances_mock,
        get_environment_resources_mock,
        get_environments_mock,
        echo_mock,
        get_environment_mock,
    ):
        app_name = '<app-name>'
        env_name = '<env-name>'
        verbose = False
        environment = Environment()

        with mock.patch.object(environment, 'print_env_details'):
            environment.print_env_details.return_value = None
            get_environment_mock.return_value = environment

            statusops.status(app_name, env_name, verbose)

            get_environment_mock.assert_called_once_with(
                app_name=app_name, env_name=env_name)
            environment.print_env_details.assert_called_once_with(
                echo_mock,
                get_environments_mock,
                get_environment_resources_mock,
                health=True)
            _print_information_about_elb_and_instances_mock.assert_not_called()
            alert_environment_status_mock.assert_called_once_with(environment)
            _print_codecommit_repositories_mock.assert_called_once_with()

    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.operations.statusops.io.echo')
    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environments')
    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environment_resources')
    @mock.patch('ebcli.operations.statusops._print_information_about_elb_and_instances')
    @mock.patch('ebcli.operations.statusops.alert_environment_status')
    @mock.patch('ebcli.operations.statusops._print_codecommit_repositories')
    def test_status__verbose(
        self,
        _print_codecommit_repositories_mock,
        alert_environment_status_mock,
        _print_information_about_elb_and_instances_mock,
        get_environment_resources_mock,
        get_environments_mock,
        echo_mock,
        get_environment_mock,
    ):
        app_name = '<app-name>'
        env_name = '<env-name>'
        verbose = True
        environment = Environment()

        with mock.patch.object(environment, 'print_env_details'):
            environment.print_env_details.return_value = None
            get_environment_mock.return_value = environment

            statusops.status(app_name, env_name, verbose)

            get_environment_mock.assert_called_once_with(
                app_name=app_name, env_name=env_name)
            environment.print_env_details.assert_called_once_with(
                echo_mock,
                get_environments_mock,
                get_environment_resources_mock,
                health=True)
            _print_information_about_elb_and_instances_mock.assert_called_once_with(env_name)
            alert_environment_status_mock.assert_called_once_with(environment)
            _print_codecommit_repositories_mock.assert_called_once_with()

    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.list_platform_versions')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    def test__alert_custom_platform_version_status__no_newer_versions(
        self,
        log_alert_mock,
        list_platform_versions_mock,
    ):
        alert_message = 'alert message'
        platform_version = PlatformVersion(
            platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/2.9.2',
            platform_name='PHP 7.1 running on 64bit Amazon Linux',
            platform_version='2.9.2')
        platform_version_siblings = [
            {'PlatformVersion': '2.9.1', 'PlatformName': 'PHP 7.1 running on 64bit Amazon Linux'},
            {'PlatformVersion': '2.9.0', 'PlatformName': 'PHP 7.1 running on 64bit Amazon Linux'},
        ]
        expected_filters = [{
            'Operator': '=',
            'Type': 'PlatformName',
            'Values': [platform_version.platform_name]
        }]

        list_platform_versions_mock.return_value = platform_version_siblings

        statusops._alert_custom_platform_version_status(platform_version, alert_message)

        list_platform_versions_mock.assert_called_once_with(filters=expected_filters)
        log_alert_mock.assert_not_called()

    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.list_platform_versions')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    def test__alert_custom_platform_version_status__with_newer_versions(
        self,
        log_alert_mock,
        list_platform_versions_mock,
    ):
        alert_message = 'alert message'
        platform_version = PlatformVersion(
            platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/2.9.2',
            platform_name='PHP 7.1 running on 64bit Amazon Linux',
            platform_version='2.9.2')
        platform_version_siblings = [
            {'PlatformVersion': '2.9.3', 'PlatformName': 'PHP 7.1 running on 64bit Amazon Linux'},
            {'PlatformVersion': '2.9.1', 'PlatformName': 'PHP 7.1 running on 64bit Amazon Linux'},
        ]
        expected_filters = [{
            'Operator': '=',
            'Type': 'PlatformName',
            'Values': [platform_version.platform_name]
        }]

        list_platform_versions_mock.return_value = platform_version_siblings

        statusops._alert_custom_platform_version_status(platform_version, alert_message)

        list_platform_versions_mock.assert_called_once_with(filters=expected_filters)
        log_alert_mock.assert_called_once_with(alert_message + '\n')

    @mock.patch('ebcli.operations.statusops.platform_version_ops.get_preferred_platform_version_for_branch')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    def test__alert_eb_managed_platform_version_status__recommended_version_available(
        self,
        log_alert_mock,
        get_preferred_platform_version_for_branch_mock,
    ):
        platform_not_recommended_alert = 'not recommended alert'
        old_alert = 'old_alert'
        platform_version = PlatformVersion(
            platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/2.9.1',
            platform_branch_name='PHP 7.1 running on 64bit Amazon Linux',
            platform_lifecycle_state=None)
        preferred_platform_version = PlatformVersion(
            platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/2.9.2',
            platform_branch_name='PHP 7.1 running on 64bit Amazon Linux',
            platform_lifecycle_state='Recommended')

        get_preferred_platform_version_for_branch_mock.return_value = preferred_platform_version

        statusops._alert_eb_managed_platform_version_status(
            platform_version,
            platform_not_recommended_alert,
            old_alert)

        get_preferred_platform_version_for_branch_mock.assert_called_once_with('PHP 7.1 running on 64bit Amazon Linux')
        log_alert_mock.assert_called_once_with(platform_not_recommended_alert + '\n')

    @mock.patch('ebcli.operations.statusops.platform_version_ops.get_preferred_platform_version_for_branch')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    def test__alert_eb_managed_platform_version_status__platform_version_is_recommended(
        self,
        log_alert_mock,
        get_preferred_platform_version_for_branch_mock,
    ):
        platform_not_recommended_alert = 'not recommended alert'
        old_alert = 'old_alert'
        platform_version = PlatformVersion(
            platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/2.9.1',
            platform_branch_name='PHP 7.1 running on 64bit Amazon Linux',
            platform_lifecycle_state='Recommended')

        statusops._alert_eb_managed_platform_version_status(
            platform_version,
            platform_not_recommended_alert,
            old_alert)

        get_preferred_platform_version_for_branch_mock.assert_not_called()
        log_alert_mock.assert_not_called()

    @mock.patch('ebcli.operations.statusops.platform_version_ops.get_preferred_platform_version_for_branch')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    def test__alert_eb_managed_platform_version_status__platform_version_is_preferred(
        self,
        log_alert_mock,
        get_preferred_platform_version_for_branch_mock,
    ):
        platform_not_recommended_alert = 'not recommended alert'
        old_alert = 'old_alert'
        platform_version = PlatformVersion(
            platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/2.9.1',
            platform_branch_name='PHP 7.1 running on 64bit Amazon Linux',
            platform_lifecycle_state=None)
        preferred_platform_version = platform_version

        get_preferred_platform_version_for_branch_mock.return_value = preferred_platform_version

        statusops._alert_eb_managed_platform_version_status(
            platform_version,
            platform_not_recommended_alert,
            old_alert)

        get_preferred_platform_version_for_branch_mock.assert_called_once_with('PHP 7.1 running on 64bit Amazon Linux')
        log_alert_mock.assert_not_called()

    @mock.patch('ebcli.operations.statusops.platform_version_ops.get_preferred_platform_version_for_branch')
    @mock.patch('ebcli.operations.statusops.io.log_alert')
    def test__alert_eb_managed_platform_version_status__newer_version_available(
        self,
        log_alert_mock,
        get_preferred_platform_version_for_branch_mock,
    ):
        platform_not_recommended_alert = 'not recommended alert'
        old_alert = 'old_alert'
        platform_version = PlatformVersion(
            platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/2.9.1',
            platform_branch_name='PHP 7.1 running on 64bit Amazon Linux',
            platform_lifecycle_state=None)
        preferred_platform_version = PlatformVersion(
            platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/2.9.2',
            platform_branch_name='PHP 7.1 running on 64bit Amazon Linux',
            platform_lifecycle_state=None)

        get_preferred_platform_version_for_branch_mock.return_value = preferred_platform_version

        statusops._alert_eb_managed_platform_version_status(
            platform_version,
            platform_not_recommended_alert,
            old_alert)

        get_preferred_platform_version_for_branch_mock.assert_called_once_with('PHP 7.1 running on 64bit Amazon Linux')
        log_alert_mock.assert_called_once_with(old_alert + '\n')


    @mock.patch('ebcli.operations.statusops.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.operations.statusops.alert_environment_status')
    @mock.patch('ebcli.operations.statusops.io.echo')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_branch')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_repository')
    def test_status__non_verbose_mode__codecommit_setup__using_non_latest_platform(
            self,
            get_default_repository_mock,
            get_default_branch_mock,
            echo_mock,
            alert_environment_status_mock,
            get_environment_mock,
    ):
        environment_object = Environment.json_to_environment_object(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments'][0]
        )
        environment_object.platform = PlatformVersion(
            platform_arn='arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5',
            platform_branch_name='PHP 7.1 running on 64bit Amazon Linux')
        get_environment_mock.return_value = environment_object
        get_default_branch_mock.return_value = 'branch'
        get_default_repository_mock.return_value = 'repository'

        statusops.status('my-application', 'environment-1', False)

        alert_environment_status_mock.assert_called_once_with(environment_object)
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
    @mock.patch('ebcli.operations.statusops.alert_environment_status')
    @mock.patch('ebcli.operations.statusops.io.echo')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_branch')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_repository')
    def test_status__non_verbose_mode__codecommit_not_setup__using_non_latest_platform(
            self,
            get_default_repository_mock,
            get_default_branch_mock,
            echo_mock,
            alert_environment_status_mock,
            get_environment_mock
    ):
        environment_object = Environment.json_to_environment_object(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments'][0]
        )
        environment_object.platform = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5')
        get_environment_mock.return_value = environment_object
        get_environment_mock.platform = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5')
        get_default_branch_mock.return_value = None
        get_default_repository_mock.return_value = None

        statusops.status('my-application', 'environment-1', False)

        alert_environment_status_mock.assert_called_once_with(environment_object)
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
    @mock.patch('ebcli.operations.statusops.alert_environment_status')
    @mock.patch('ebcli.operations.statusops.io.echo')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_branch')
    @mock.patch('ebcli.operations.statusops.gitops.get_default_repository')
    def test_status__non_verbose_mode__codecommit_setup__using_latest_platform(
            self,
            get_default_repository_mock,
            get_default_branch_mock,
            echo_mock,
            alert_environment_status_mock,
            get_environment_mock
    ):
        environment_object = Environment.json_to_environment_object(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments'][0]
        )
        environment_object.platform = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_environment_mock.return_value = environment_object
        get_default_branch_mock.return_value = 'branch'
        get_default_repository_mock.return_value = 'repository'

        statusops.status('my-application', 'environment-1', False)

        alert_environment_status_mock.assert_called_once_with(environment_object)
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
    @mock.patch('ebcli.operations.statusops.alert_environment_status')
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
            alert_environment_status_mock,
            get_environment_mock,
    ):
        environment_object = Environment.json_to_environment_object(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments'][0]
        )
        environment_object.platform = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_environment_mock.return_value = environment_object
        get_default_branch_mock.return_value = 'branch'
        get_default_repository_mock.return_value = 'repository'
        get_environment_resources_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENT_RESOURCES_RESPONSE__ELBV2_ENVIRONMENT
        get_target_groups_for_load_balancer_mock.return_value = mock_responses.DESCRIBE_TARGET_GROUPS_RESPONSE['TargetGroups']
        get_target_group_healths_mock.return_value = {
            "arn:aws:elasticloadbalancing:us-west-2:123123123123:targetgroup/awseb-AWSEB-179V6JWWL9HI5/e57decc4139bfdd2": mock_responses.DESCRIBE_TARGET_HEALTH_RESPONSE
        }

        statusops.status('my-application', 'environment-1', True)

        alert_environment_status_mock.assert_called_once_with(environment_object)
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
    @mock.patch('ebcli.operations.statusops.alert_environment_status')
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
            alert_environment_status_mock,
            get_environment_mock
    ):
        environment_object = Environment.json_to_environment_object(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments'][0]
        )
        environment_object.platform = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_environment_mock.return_value = environment_object
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

        alert_environment_status_mock.assert_called_once_with(environment_object)
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
    @mock.patch('ebcli.operations.statusops.alert_environment_status')
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
            alert_environment_status_mock,
            get_environment_mock
    ):
        environment_object = Environment.json_to_environment_object(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments'][0]
        )
        environment_object.platform = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_environment_mock.return_value = environment_object
        get_default_branch_mock.return_value = 'branch'
        get_default_repository_mock.return_value = 'repository'
        get_environment_resources_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENT_RESOURCES_RESPONSE
        get_health_of_instances_mock.return_value = mock_responses.DESCRIBE_INSTANCE_HEALTH['InstanceStates']

        statusops.status('my-application', 'environment-1', True)

        alert_environment_status_mock.assert_called_once_with(environment_object)
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
    @mock.patch('ebcli.operations.statusops.alert_environment_status')
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
            alert_environment_status_mock,
            get_environment_mock,
    ):
        environment_object = Environment.json_to_environment_object(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments'][0]
        )
        environment_object.platform = PlatformVersion('arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.6')
        get_environment_mock.return_value = environment_object
        get_default_branch_mock.return_value = 'branch'
        get_default_repository_mock.return_value = 'repository'
        get_environment_resources_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENT_RESOURCES_RESPONSE__SINGLE_INSTANCE_ENVIRONMENT

        statusops.status('my-application', 'environment-1', True)

        alert_environment_status_mock.assert_called_once_with(environment_object)
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
