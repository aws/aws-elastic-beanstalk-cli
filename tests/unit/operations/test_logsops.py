# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import mock
from mock import ANY

from ebcli.operations import logsops
from ebcli.lib.aws import MaxRetriesError
from ebcli.objects.exceptions import InvalidStateError, ServiceError
from ebcli.resources.strings import prompts


class TestLogsOperations(unittest.TestCase):
    app_name = 'MyFooApp'
    env_name = 'MyFooEnv'
    instance_id = 'i-123456789'
    instance_id_alt = 'i-666666666'
    info_type_bundle = 'bundle'
    info_type_tail = 'tail'

    old_default_log_group = 'awseb-{0}-activity'.format(env_name)
    default_log_group = '/aws/elasticbeanstalk/{0}/test/activity.log'.format(env_name)
    specified_log_group = '/aws/elasticbeanstalk/{0}/specific/error.log'.format(env_name)

    request_id = '1234-5678-9098-7654'
    message = 'https://url.com'
    message_alt = 'https://url-two.com'
    log_msg = '[MSG]: logslogslogs'
    request_env_info_response = {'ResponseMetadata': {'RequestId': request_id}}
    retrieve_env_info_response = {'EnvironmentInfo': [{'Ec2InstanceId': instance_id, 'Message': message},
                                                      {'Ec2InstanceId': instance_id_alt, 'Message': message_alt}]}
    describe_log_streams_response = {'logStreams': [{'logStreamName': instance_id}, {'logStreamName': instance_id_alt}]}
    get_log_events_response = {'events': [{'message': log_msg}, {'message': log_msg}], 'nextForwardToken': 'fooToken'}

    logs_location = 'ebcli/env/logs/'
    zip_location = 'ebcli/env/tmp/'
    instance_folder = '{0}-{1}'.format(logs_location, instance_id)

    process = '111'

    def setUp(self):
        # Setup Patchers
        self.patcher_beanstalk = mock.patch('ebcli.operations.logsops.elasticbeanstalk')
        self.patcher_fileops = mock.patch('ebcli.operations.logsops.fileoperations')
        self.patcher_commonops = mock.patch('ebcli.operations.logsops.commonops')
        self.patcher_cloudwatch = mock.patch('ebcli.operations.logsops.cloudwatch')
        self.patcher_utils = mock.patch('ebcli.operations.logsops.utils')
        self.patcher_io = mock.patch('ebcli.operations.logsops.io')
        self.patcher_os = mock.patch('ebcli.operations.logsops.os')
        # Assign patchers
        self.mock_beanstalk = self.patcher_beanstalk.start()
        self.mock_fileops = self.patcher_fileops.start()
        self.mock_commonops = self.patcher_commonops.start()
        self.mock_cloudwatch = self.patcher_cloudwatch.start()
        self.mock_utils = self.patcher_utils.start()
        self.mock_io = self.patcher_io.start()
        self.mock_os = self.patcher_os.start()

    def tearDown(self):
        # Stop all active patchers
        self.patcher_beanstalk.stop()
        self.patcher_fileops.stop()
        self.patcher_commonops.stop()
        self.patcher_cloudwatch.stop()
        self.patcher_utils.stop()
        self.patcher_io.stop()
        self.patcher_os.stop()

    # TESTING logsops.logs()
    @mock.patch('ebcli.operations.logsops.get_logs')
    def test_basic_logs_call(self, mock_get_ops):
        # Mock out methods
        self.mock_beanstalk.request_environment_info.return_value = self.request_env_info_response

        # Make actual call
        logsops.retrieve_beanstalk_logs(self.env_name, self.info_type_bundle, do_zip=True, instance_id=self.instance_id)

        # Assert correct methods were called
        self.mock_beanstalk.request_environment_info.assert_called_with(self.env_name, self.info_type_bundle)
        self.mock_io.echo.assert_called_with(prompts['logs.retrieving'])
        self.mock_commonops.wait_for_success_events.assert_called_with(self.request_id, timeout_in_minutes=2, sleep_time=1, stream_events=False)
        mock_get_ops.assert_called_with(self.env_name, self.info_type_bundle, do_zip=True, instance_id=self.instance_id)

    # TESTING logsops.get_logs()
    def test_bundle_get_logs_call(self):
        # Mock out methods
        self.mock_beanstalk.retrieve_environment_info.return_value = self.retrieve_env_info_response
        self.mock_fileops.get_logs_location.return_value = self.logs_location
        self.mock_utils.save_file_from_url.return_value = self.zip_location
        self.mock_os.path.join.return_value = self.instance_folder
        self.mock_fileops.get_logs_location.return_value = self.logs_location

        # Make actual call
        logsops.get_logs(self.env_name, self.info_type_bundle)

        # Assert correct methods were called
        self.mock_beanstalk.retrieve_environment_info.assert_called_with(self.env_name, self.info_type_bundle)
        save_from_url_calls = [mock.call(self.message, self.logs_location, self.instance_id + '.zip'), mock.call(self.message_alt, self.logs_location, self.instance_id_alt + '.zip')]
        self.mock_utils.save_file_from_url.assert_has_calls(save_from_url_calls, any_order=True)

    def test_bundle_and_zip_get_logs_call(self):
        # Mock out methods
        self.mock_beanstalk.retrieve_environment_info.return_value = self.retrieve_env_info_response
        self.mock_fileops.get_logs_location.return_value = self.logs_location
        self.mock_utils.save_file_from_url.return_value = self.zip_location
        self.mock_os.path.join.return_value = self.instance_folder

        # Make actual call
        logsops.get_logs(self.env_name, self.info_type_bundle, do_zip=True, instance_id=self.instance_id)

        # Assert correct methods were called
        self.mock_beanstalk.retrieve_environment_info.assert_called_with(self.env_name, self.info_type_bundle)
        save_from_url_calls = [mock.call(self.message, self.logs_location, self.instance_id + '.zip')]
        self.mock_utils.save_file_from_url.assert_has_calls(save_from_url_calls,  any_order=True)
        self.mock_fileops.zup_up_folder(self.logs_location, self.logs_location + '.zip')
        self.mock_io.symlink.assert_not_called()

    def test_tail_get_logs_call(self):
        # Mock out methods
        self.mock_beanstalk.retrieve_environment_info.return_value = self.retrieve_env_info_response
        self.mock_utils.get_data_from_url.return_value = self.log_msg
        self.mock_os.linesep.join.return_value = self.log_msg

        # Make actual call
        logsops.get_logs(self.env_name, self.info_type_tail)

        # Assert correct methods were called
        self.mock_beanstalk.retrieve_environment_info.assert_called_with(self.env_name, self.info_type_tail)
        get_data_from_url_calls = [mock.call(self.message), mock.call(self.message_alt)]
        self.mock_utils.get_data_from_url.assert_has_calls(get_data_from_url_calls, any_order=True)
        self.mock_io.echo_with_pager.assert_called_with(self.log_msg)

    # TESTING logsops.stream_logs()
    @mock.patch('ebcli.operations.logsops.stream_single_stream')
    @mock.patch('ebcli.operations.logsops.get_log_name')
    @mock.patch('ebcli.operations.logsops.threading')
    @mock.patch('ebcli.operations.logsops.threading.Thread')
    @mock.patch('ebcli.core.io.EventStreamer')
    def test_stream_logs_with_log_group(self, mock_event_streamer, mock_thread, mock_threading, mock_get_log_name, mock_single_stream):
        # Mock out methods
        mock_get_log_name.return_value = self.default_log_group
        self.mock_io.get_event_streamer.return_value = mock_event_streamer
        self.mock_cloudwatch.get_all_stream_names.return_value = [self.instance_id, self.instance_id_alt]
        # NOTE: We have to throw this exception so we do not loop forever in the unit test
        mock_thread.start.side_effect = InvalidStateError("Forced stop")
        mock_threading.Thread.return_value = mock_thread

        # Make actual call
        self.assertRaises(InvalidStateError, logsops.stream_cloudwatch_logs, self.env_name, 2, self.default_log_group)

        # Assert correct methods were called
        self.mock_cloudwatch.get_all_stream_names.assert_called_with(self.default_log_group, None)
        mock_threading.Thread.assert_called_with(target=mock_single_stream, args=(self.default_log_group, self.instance_id, mock_event_streamer, 2))

    @mock.patch('ebcli.operations.logsops.stream_single_stream')
    @mock.patch('ebcli.operations.logsops.threading')
    @mock.patch('ebcli.operations.logsops.threading.Thread')
    @mock.patch('ebcli.core.io.EventStreamer')
    def test_stream_logs_call(self, mock_event_streamer, mock_thread, mock_threading, mock_single_stream):
        # Mock out methods
        self.mock_io.get_event_streamer.return_value = mock_event_streamer
        self.mock_cloudwatch.get_all_stream_names.return_value = [self.instance_id, self.instance_id_alt]
        # NOTE: We have to throw this exception so we do not loop forever in the unit test
        mock_thread.start.side_effect = InvalidStateError("Forced stop")
        mock_threading.Thread.return_value = mock_thread

        # Make actual call
        self.assertRaises(InvalidStateError, logsops.stream_cloudwatch_logs, self.env_name)

        # Assert correct methods were called
        self.mock_cloudwatch.get_all_stream_names.assert_called_with(self.old_default_log_group, None)
        mock_threading.Thread.assert_called_with(target=mock_single_stream, args=(self.old_default_log_group, self.instance_id, mock_event_streamer, 2))

    # TESTING logops.stream_single_stream
    @mock.patch('ebcli.core.io.EventStreamer')
    def test_stream_single_stream_call(self, mock_streamer):
        # Mock out methods
        self.mock_cloudwatch.get_log_events.side_effect = [self.get_log_events_response, Exception("Retry Me!"),
                                                           MaxRetriesError("Retry Me!"), ServiceError("Fail!")]

        # Make actual call
        logsops.stream_single_stream(self.specified_log_group, self.instance_id, mock_streamer)

        # Assert correct methods were called
        self.mock_cloudwatch.get_log_events.assert_called_with(self.specified_log_group, self.instance_id, next_token='fooToken')

    # TESTING logsops.cloudwatch_logs()
    @mock.patch('ebcli.operations.logsops.open')
    @mock.patch('ebcli.operations.logsops.get_cloudwatch_stream_logs')
    def test_cloudwatch_logs_call_with_bundle(self, mock_get_stream_logs, mock_open):
        # Mock out methods
        self.mock_cloudwatch.describe_log_streams.return_value = self.describe_log_streams_response
        self.mock_fileops.get_logs_location.return_value = self.logs_location
        mock_get_stream_logs.return_value = self.log_msg
        mock_open.return_value = mock_open
        self.mock_fileops.get_logs_location.return_value = self.logs_location

        # Make actual call
        logsops.retrieve_cloudwatch_logs(self.default_log_group, self.info_type_bundle)

        # Assert the correct methods were called
        self.mock_cloudwatch.describe_log_streams.assert_called_with(self.default_log_group, log_stream_name_prefix=None)
        get_logs_cloudwatch_calls = [mock.call(self.default_log_group, self.instance_id), mock.call(self.default_log_group, self.instance_id_alt)]
        mock_get_stream_logs.assert_has_calls(get_logs_cloudwatch_calls)
        self.mock_os.symlink.assert_called_with(self.logs_location, self.logs_location)

    @mock.patch('ebcli.operations.logsops.open')
    @mock.patch('ebcli.operations.logsops.get_cloudwatch_stream_logs')
    def test_cloudwatch_logs_call_with_bundle_and_zip(self, mock_get_stream_logs, mock_open):
        # Mock out methods
        self.mock_cloudwatch.describe_log_streams.return_value = self.describe_log_streams_response
        self.mock_fileops.get_logs_location.return_value = self.logs_location
        mock_get_stream_logs.return_value = self.log_msg
        mock_open.return_value = mock_open

        # Make actual call
        logsops.retrieve_cloudwatch_logs(self.default_log_group, self.info_type_bundle, do_zip=True)

        # Assert the correct methods were called
        self.mock_cloudwatch.describe_log_streams.assert_called_with(self.default_log_group,
                                                                     log_stream_name_prefix=None)
        get_logs_cloudwatch_calls = [mock.call(self.default_log_group, self.instance_id),
                                     mock.call(self.default_log_group, self.instance_id_alt)]
        mock_get_stream_logs.assert_has_calls(get_logs_cloudwatch_calls)
        self.mock_fileops.zup_up_folder(self.logs_location, self.logs_location + '.zip')
        self.mock_io.symlink.assert_not_called()

    @mock.patch('ebcli.operations.logsops.get_cloudwatch_stream_logs')
    def test_cloudwatch_logs_call_with_tail(self, mock_get_stream_logs):
        # Mock out methods
        self.mock_cloudwatch.describe_log_streams.return_value = self.describe_log_streams_response
        mock_get_stream_logs.return_value = self.log_msg

        # Make actual call
        logsops.retrieve_cloudwatch_logs(self.default_log_group, self.info_type_tail, instance_id=self.instance_id)

        # Assert the correct methods were called
        self.mock_cloudwatch.describe_log_streams.assert_called_with(self.default_log_group,
                                                                     log_stream_name_prefix=self.instance_id)
        get_logs_cloudwatch_calls = [mock.call(self.default_log_group, self.instance_id, num_log_events=logsops.TAIL_LOG_SIZE),
                                     mock.call(self.default_log_group, self.instance_id_alt, num_log_events=logsops.TAIL_LOG_SIZE)]
        mock_get_stream_logs.assert_has_calls(get_logs_cloudwatch_calls)
        self.mock_io.echo_with_pager.assert_called_once_with(ANY)

    # TESTING logsops.log_streaming_enabled()
    def test_get_logs_cloudwatch_call(self):
        # Mock out methods
        self.mock_cloudwatch.get_log_events.return_value = self.get_log_events_response

        # Make actual call
        actual_logs = logsops.get_cloudwatch_stream_logs(self.specified_log_group, self.instance_id)

        # Assert the correct methods were called and response returned
        self.mock_cloudwatch.get_log_events.assert_called_with(self.specified_log_group, self.instance_id, limit=None)
        expected_logs = '[{}] {}\n'.format(self.instance_id, self.log_msg)
        expected_logs += expected_logs
        self.assertEqual(expected_logs, actual_logs, "Expected logs to be: {0}. But were: {1}".format(expected_logs, actual_logs))

    def test_get_logs_cloudwatch_throws_service_error(self):
        # Mock out methods
        self.mock_cloudwatch.get_log_events.side_effect = ServiceError("Service is throwing an error!")

        # Make actual call
        logsops.get_cloudwatch_stream_logs(self.specified_log_group, self.instance_id_alt)

        # Assert the correct methods were called and response returned
        self.mock_cloudwatch.get_log_events.assert_called_with(self.specified_log_group, self.instance_id_alt, limit=None)

    def test_get_logs_cloudwatch_throws_unknown_exception(self):
        # Mock out methods
        self.mock_cloudwatch.get_log_events.side_effect = Exception("An unknown error appeared!")

        # Make actual call
        logsops.get_cloudwatch_stream_logs(self.specified_log_group, self.instance_id, num_log_events=50)

        # Assert the correct methods were called and response returned
        self.mock_cloudwatch.get_log_events.assert_called_with(self.specified_log_group, self.instance_id, limit=50)

    # TESTING logsops.log_streaming_enabled
    def test_log_streaming_enabled_is_true(self):
        meaningless_config = "doesn't matter"
        # Mock out methods
        self.mock_beanstalk.describe_configuration_settings.return_value = meaningless_config
        self.mock_beanstalk.get_specific_configuration.return_value = 'true'

        self.assertTrue(logsops.log_streaming_enabled(self.app_name, self.env_name), "Expected log streaming to be enabled")

    def test_log_streaming_enabled_is_false(self):
        meaningless_config = "doesn't matter"
        # Mock out methods
        self.mock_beanstalk.describe_configuration_settings.return_value = meaningless_config
        self.mock_beanstalk.get_specific_configuration.return_value = None

        self.assertFalse(logsops.log_streaming_enabled(self.app_name, self.env_name), "Expected log streaming to be disabled")

    # TESTING logsops.log_group_builder
    def test_log_group_builder_default(self):
        actual_log_group = logsops.beanstalk_log_group_builder(self.env_name)
        expected_log_group = '/aws/elasticbeanstalk/{0}/{1}'.format(self.env_name, logsops.DEFAULT_LOG_STREAMING_PATH)
        self.assertEqual(actual_log_group, expected_log_group, "Expected log group to be: {0} but got: {1}".format(expected_log_group, actual_log_group))

    def test_log_group_builder_with_full_filepath(self):
        actual_log_group = logsops.beanstalk_log_group_builder(self.env_name, self.specified_log_group)
        self.assertEqual(actual_log_group, self.specified_log_group, "Expected log group to be: {0} but got: {1}".format(self.specified_log_group, actual_log_group))

    def test_log_group_builder_with_partial_filepath(self):
        filepath = 'foo/specific/error.log'
        actual_log_group = logsops.beanstalk_log_group_builder(self.env_name, filepath)
        expected_log_group = '/aws/elasticbeanstalk/{0}/{1}'.format(self.env_name, filepath)
        self.assertEqual(actual_log_group, expected_log_group, "Expected log group to be: {0} but got: {1}".format(expected_log_group, actual_log_group))
