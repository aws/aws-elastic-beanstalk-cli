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

from .baseinttest import BaseIntegrationTest

from ebcli.core import fileoperations
from ebcli.operations import commonops
from ebcli.resources.strings import prompts

from . import mockservice


class TestUpgrade(BaseIntegrationTest):

    def setUp(self):
        super(TestUpgrade, self).setUp()
        # Create all app stuff
        fileoperations.create_config_file('myEBCLItest', 'us-west-2',
                                          'my-stack-stack')
        commonops.set_environment_for_current_branch('my-env')

    def test_upgrade_standard(self):
        """
        Just make sure no errors are thrown
        """
        # Setup mock responses
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeConfigurationSettings',
                            describe_web_without_rolling())
        self.mock_input.return_value = 'my-env'

        self.run_command('upgrade')

    def test_upgrade_up_to_date(self):
        # Setup mock responses
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeConfigurationSettings',
                            describe_already_up_to_date())
        self.mock_input.return_value = 'my-env'

        self.run_command('upgrade')
        self.mock_warning.assert_not_called()
        self.mock_output.assert_called_with(prompts['upgrade.alreadylatest'])

    def test_upgrade_single(self):
        # Setup mock responses
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeConfigurationSettings',
                            describe_single_instance())
        self.mock_input.return_value = 'my-env'

        self.run_command('upgrade')
        self.mock_warning.assert_called_with(prompts['upgrade.singleinstance'])

    def test_upgrade_worker(self):
        # Setup mock responses
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeConfigurationSettings',
                            describe_worker())
        self.mock_input.return_value = 'my-env'

        self.run_command('upgrade')
        self.mock_warning.assert_any_call(prompts['upgrade.norollingapply'].format('Time'))

    def test_upgrade_noroll(self):
        # Setup mock responses
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeConfigurationSettings',
                            describe_web_without_rolling())
        self.mock_input.return_value = 'my-env'

        self.run_command('upgrade', '--noroll')
        self.mock_warning.assert_any_call(prompts['upgrade.norollingforce'])

    def test_upgrade_rolling_enabled(self):
        # Setup mock responses
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeConfigurationSettings',
                            describe_web_with_rolling())
        self.mock_input.return_value = 'my-env'

        self.run_command('upgrade')
        self.mock_warning.assert_called_with(prompts['upgrade.rollingupdate'])

    def test_upgrade_web_enable_rolling(self):
        # Setup mock responses
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeConfigurationSettings',
                            describe_web_without_rolling())
        self.mock_input.return_value = 'my-env'

        self.run_command('upgrade')
        self.mock_warning.assert_any_call(prompts['upgrade.norollingapply'].format('Health'))

    def test_upgrade_force(self):
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeConfigurationSettings',
                            describe_web_without_rolling())
        self.mock_input.return_value = 'my-env'

        self.run_command('upgrade')
        self.mock_warning.assert_called_with(prompts['upgrade.applyrolling'].format('Health'))
        self.mock_input.assert_called_with('To continue, type the environment name')
        self.assertEqual(self.mock_input.call_count, 1)

    def test_upgrade_force_worker(self):
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeConfigurationSettings',
                            describe_worker())
        self.mock_input.return_value = 'my-env'

        self.run_command('upgrade')
        self.mock_warning.assert_called_with(prompts['upgrade.applyrolling'].format('Time'))
        self.mock_input.assert_called_with('To continue, type the environment name')
        self.assertEqual(self.mock_input.call_count, 1)

    def test_upgrade_force_dont_apply(self):
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeConfigurationSettings',
                            describe_web_with_rolling())
        self.mock_input.return_value = 'my-env'

        self.run_command('upgrade')
        self.mock_warning.assert_called_with('This operation replaces your instances with minimal or zero downtime. ' +
                                             'You may cancel the upgrade after it has started by typing "eb abort".')
        self.assertEqual(self.mock_warning.call_count, 1)
        self.mock_input.assert_called_with('To continue, type the environment name')
        self.assertEqual(self.mock_input.call_count, 1)


def describe_worker():
    default = mockservice.standard_describe_configuration_settings()
    settings = default['ConfigurationSettings'][0]
    settings['SolutionStackName'] = '64bit Amazon Linux 2014.09 v1.1.0 running Python 2.7'
    settings['Tier'] = {u'Version': ' ', u'Type': 'HTTP/SQS', u'Name': 'Worker'}
    return default


def describe_single_instance():
    default = mockservice.standard_describe_configuration_settings()
    settings = default['ConfigurationSettings'][0]
    settings['SolutionStackName'] = '64bit Amazon Linux 2014.09 v1.1.0 running Python 2.7'
    option_settings = settings['OptionSettings']
    mockservice.replace_option_setting(
        'aws:elasticbeanstalk:environment',
        'EnvironmentType',
        'SingleInstance',
        option_settings
    )
    return default


def describe_web_without_rolling():
    default = mockservice.standard_describe_configuration_settings()
    settings = default['ConfigurationSettings'][0]
    settings['SolutionStackName'] = '64bit Amazon Linux 2014.09 v1.1.0 running Python 2.7'
    option_settings = settings['OptionSettings']
    mockservice.replace_option_setting(
        'aws:autoscaling:updatepolicy:rollingupdate',
        'RollingUpdateEnabled',
        'false',
        option_settings
    )
    mockservice.replace_option_setting(
        'aws:autoscaling:updatepolicy:rollingupdate',
        'RollingUpdateType',
        'Time',
        option_settings
    )
    return default


def describe_web_with_rolling():
    default = mockservice.standard_describe_configuration_settings()
    settings = default['ConfigurationSettings'][0]
    settings['SolutionStackName'] = '64bit Amazon Linux 2014.09 v1.1.0 running Python 2.7'
    option_settings = settings['OptionSettings']
    mockservice.replace_option_setting(
        'aws:autoscaling:updatepolicy:rollingupdate',
        'RollingUpdateEnabled',
        'true',
        option_settings
    )
    mockservice.replace_option_setting(
        'aws:autoscaling:updatepolicy:rollingupdate',
        'RollingUpdateType',
        'Health',
        option_settings
    )
    return default


def describe_already_up_to_date():
    latest = commonops.get_latest_solution_stack('Python 2.7')
    default = mockservice.standard_describe_configuration_settings()
    default['SolutionStackName'] = latest.name
    return default