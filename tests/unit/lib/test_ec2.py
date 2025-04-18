# Copyright 2025 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import socket
import urllib.error
import urllib.request

import unittest
import mock

from ebcli.lib import ec2
from ebcli.objects.exceptions import NotAnEC2Instance


class TestEC2(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'testDir'
        self.ebcli_root = os.getcwd()

        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.ebcli_root)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @mock.patch('ebcli.lib.ec2.get_instance_metadata')
    @mock.patch('ebcli.lib.ec2.describe_instance')
    @mock.patch('ebcli.lib.ec2.ensure_vpc_exists')
    @mock.patch('ebcli.lib.ec2.aws.set_region')
    @mock.patch('ebcli.lib.ec2.fileoperations.write_config_setting')
    @mock.patch('ebcli.lib.ec2.instance_tags')
    def test_get_current_instance_details_success(
        self,
        instance_tags_mock,
        write_config_setting_mock,
        set_region_mock,
        ensure_vpc_exists_mock,
        describe_instance_mock,
        get_instance_metadata_mock
    ):
        # Setup mocks
        get_instance_metadata_mock.side_effect = [
            'i-1234567890abcdef0',  # instance-id
            'us-west-2a',           # availability-zone
            '0a:1b:2c:3d:4e:5f',    # mac
            'vpc-12345678',         # vpc-id
            'subnet-12345678'       # subnet-id
        ]
        
        describe_instance_mock.return_value = {
            'InstanceId': 'i-1234567890abcdef0',
            'SecurityGroups': [
                {'GroupId': 'sg-12345678'},
                {'GroupId': 'sg-87654321'}
            ]
        }
        
        instance_tags_mock.return_value = [
            {'Key': 'Name', 'Value': 'test-instance'},
            {'Key': 'Environment', 'Value': 'test'}
        ]
        
        # Call the function
        result = ec2.get_current_instance_details()
        
        # Verify results
        self.assertEqual('i-1234567890abcdef0', result['InstanceId'])
        self.assertEqual('vpc-12345678', result['VpcId'])
        self.assertEqual('subnet-12345678', result['SubnetId'])
        self.assertEqual(['sg-12345678', 'sg-87654321'], result['SecurityGroupIds'])
        self.assertEqual('us-west-2', result['Region'])
        self.assertEqual([
            {'Key': 'Name', 'Value': 'test-instance'},
            {'Key': 'Environment', 'Value': 'test'}
        ], result['Tags'])
        
        # Verify mock calls
        get_instance_metadata_mock.assert_any_call('instance-id')
        get_instance_metadata_mock.assert_any_call('placement/availability-zone')
        get_instance_metadata_mock.assert_any_call('mac')
        get_instance_metadata_mock.assert_any_call('network/interfaces/macs/0a:1b:2c:3d:4e:5f/vpc-id')
        get_instance_metadata_mock.assert_any_call('network/interfaces/macs/0a:1b:2c:3d:4e:5f/subnet-id')
        
        set_region_mock.assert_called_once_with('us-west-2')
        write_config_setting_mock.assert_called_once_with('global', 'default_region', 'us-west-2')
        ensure_vpc_exists_mock.assert_called_once_with('vpc-12345678')
        describe_instance_mock.assert_called_once_with(instance_id='i-1234567890abcdef0')
        instance_tags_mock.assert_called_once_with('i-1234567890abcdef0')

    @mock.patch('ebcli.lib.ec2.get_instance_metadata')
    @mock.patch('ebcli.lib.ec2.describe_instance')
    @mock.patch('ebcli.lib.ec2.ensure_vpc_exists')
    @mock.patch('ebcli.lib.ec2.aws.set_region')
    @mock.patch('ebcli.lib.ec2.fileoperations.write_config_setting')
    @mock.patch('ebcli.lib.ec2.io.log_warning')
    def test_get_current_instance_details_vpc_not_found(
        self,
        log_warning_mock,
        write_config_setting_mock,
        set_region_mock,
        ensure_vpc_exists_mock,
        describe_instance_mock,
        get_instance_metadata_mock
    ):
        # Setup mocks
        get_instance_metadata_mock.side_effect = [
            'i-1234567890abcdef0',  # instance-id
            'us-west-2a',           # availability-zone
            '0a:1b:2c:3d:4e:5f',    # mac
            'vpc-12345678',         # vpc-id
            'subnet-12345678'       # subnet-id
        ]
        
        # Simulate VPC not found error
        ensure_vpc_exists_mock.side_effect = Exception("InvalidVpcID.NotFound")
        
        # Call the function
        result = ec2.get_current_instance_details()
        
        # Verify results
        self.assertIsNone(result['InstanceId'])
        self.assertIsNone(result['VpcId'])
        self.assertIsNone(result['SubnetId'])
        self.assertEqual([], result['SecurityGroupIds'])
        self.assertEqual('us-west-2', result['Region'])
        self.assertEqual([], result['Tags'])
        
        # Verify warning was logged
        log_warning_mock.assert_called_once_with('Unable to retrieve details of VPC, vpc-12345678')
        
        # Verify describe_instance was not called
        describe_instance_mock.assert_not_called()

    @mock.patch('ebcli.lib.ec2.get_instance_metadata')
    @mock.patch('ebcli.lib.ec2.describe_instance')
    @mock.patch('ebcli.lib.ec2.ensure_vpc_exists')
    @mock.patch('ebcli.lib.ec2.aws.set_region')
    @mock.patch('ebcli.lib.ec2.fileoperations.write_config_setting')
    @mock.patch('ebcli.lib.ec2.io.log_warning')
    def test_get_current_instance_details_instance_not_found(
        self,
        log_warning_mock,
        write_config_setting_mock,
        set_region_mock,
        ensure_vpc_exists_mock,
        describe_instance_mock,
        get_instance_metadata_mock
    ):
        # Setup mocks
        instance_id = 'i-1234567890abcdef0'
        get_instance_metadata_mock.side_effect = [
            instance_id,            # instance-id
            'us-west-2a',           # availability-zone
            '0a:1b:2c:3d:4e:5f',    # mac
            'vpc-12345678',         # vpc-id
            'subnet-12345678'       # subnet-id
        ]
        
        # Simulate instance not found error
        describe_instance_mock.side_effect = Exception("InvalidInstanceID.NotFound")
        
        # Call the function
        result = ec2.get_current_instance_details()
        
        # Verify results
        self.assertIsNone(result['InstanceId'])
        self.assertIsNone(result['VpcId'])
        self.assertIsNone(result['SubnetId'])
        self.assertEqual([], result['SecurityGroupIds'])
        self.assertEqual('us-west-2', result['Region'])
        self.assertEqual([], result['Tags'])
        
        # Verify warning was logged - use the actual message from the code
        log_warning_mock.assert_called_once_with('Unable to retrieve details of instance, None')

    @mock.patch('ebcli.lib.ec2.get_instance_metadata')
    @mock.patch('ebcli.lib.ec2.describe_instance')
    @mock.patch('ebcli.lib.ec2.ensure_vpc_exists')
    @mock.patch('ebcli.lib.ec2.aws.set_region')
    @mock.patch('ebcli.lib.ec2.fileoperations.write_config_setting')
    @mock.patch('ebcli.lib.ec2.instance_tags')
    def test_get_current_instance_details_tags_exception(
        self,
        instance_tags_mock,
        write_config_setting_mock,
        set_region_mock,
        ensure_vpc_exists_mock,
        describe_instance_mock,
        get_instance_metadata_mock
    ):
        # Setup mocks
        get_instance_metadata_mock.side_effect = [
            'i-1234567890abcdef0',  # instance-id
            'us-west-2a',           # availability-zone
            '0a:1b:2c:3d:4e:5f',    # mac
            'vpc-12345678',         # vpc-id
            'subnet-12345678'       # subnet-id
        ]
        
        describe_instance_mock.return_value = {
            'InstanceId': 'i-1234567890abcdef0',
            'SecurityGroups': [
                {'GroupId': 'sg-12345678'}
            ]
        }
        
        # Simulate exception when getting tags
        instance_tags_mock.side_effect = Exception("Client error")
        
        # Call the function
        result = ec2.get_current_instance_details()
        
        # Verify results
        self.assertEqual('i-1234567890abcdef0', result['InstanceId'])
        self.assertEqual('vpc-12345678', result['VpcId'])
        self.assertEqual('subnet-12345678', result['SubnetId'])
        self.assertEqual(['sg-12345678'], result['SecurityGroupIds'])
        self.assertEqual('us-west-2', result['Region'])
        self.assertEqual([], result['Tags'])  # Tags should be empty due to exception

    @mock.patch('ebcli.lib.ec2.get_instance_metadata')
    def test_get_current_instance_details_not_an_ec2_instance(
        self,
        get_instance_metadata_mock
    ):
        # Simulate not being on an EC2 instance
        get_instance_metadata_mock.side_effect = NotAnEC2Instance("Not an EC2 instance")
        
        # Call the function and expect exception
        with self.assertRaises(NotAnEC2Instance):
            ec2.get_current_instance_details()

    @mock.patch('ebcli.lib.ec2.urllib.request.Request')
    @mock.patch('ebcli.lib.ec2.urllib.request.urlopen')
    def test_get_instance_metadata_success(
        self,
        urlopen_mock,
        request_mock
    ):
        # Setup mocks for successful metadata retrieval
        token_response_mock = mock.MagicMock()
        token_response_mock.read.return_value = b'mock-token'
        token_response_mock.__enter__.return_value = token_response_mock
        
        metadata_response_mock = mock.MagicMock()
        metadata_response_mock.read.return_value = b'metadata-value'
        metadata_response_mock.__enter__.return_value = metadata_response_mock
        
        urlopen_mock.side_effect = [token_response_mock, metadata_response_mock]
        
        # Call the function
        result = ec2.get_instance_metadata('instance-id')
        
        # Verify result
        self.assertEqual('metadata-value', result)
        
        # Verify request creation
        request_mock.assert_any_call('http://169.254.169.254/latest/api/token', method="PUT")
        request_mock.assert_any_call('http://169.254.169.254/latest/meta-data/instance-id')

    @mock.patch('ebcli.lib.ec2.urllib.request.Request')
    @mock.patch('ebcli.lib.ec2.urllib.request.urlopen')
    @mock.patch('ebcli.lib.ec2._is_timeout_exception')
    def test_get_instance_metadata_timeout(
        self,
        is_timeout_exception_mock,
        urlopen_mock,
        request_mock
    ):
        # Setup mock for timeout
        timeout_error = socket.timeout("Timed out")
        urlopen_mock.side_effect = timeout_error
        is_timeout_exception_mock.return_value = True
        
        # Call the function and expect exception
        with self.assertRaises(NotAnEC2Instance):
            ec2.get_instance_metadata('instance-id')

    @mock.patch('ebcli.lib.ec2.urllib.request.Request')
    @mock.patch('ebcli.lib.ec2.urllib.request.urlopen')
    def test_get_instance_metadata_url_error_timeout(
        self,
        urlopen_mock,
        request_mock
    ):
        # Setup mock for URLError with timeout reason
        url_error = urllib.error.URLError("URL error")
        url_error.reason = TimeoutError("Timed out")
        urlopen_mock.side_effect = url_error
        
        # Call the function and expect exception
        with self.assertRaises(NotAnEC2Instance):
            ec2.get_instance_metadata('instance-id')

    @mock.patch('ebcli.lib.ec2.urllib.request.Request')
    @mock.patch('ebcli.lib.ec2.urllib.request.urlopen')
    def test_get_instance_metadata_url_error_with_timeout_string(
        self,
        urlopen_mock,
        request_mock
    ):
        # Setup mock for URLError with timeout in string
        url_error = urllib.error.URLError("timed out")
        urlopen_mock.side_effect = url_error
        
        # Call the function and expect exception
        with self.assertRaises(NotAnEC2Instance):
            ec2.get_instance_metadata('instance-id')

    @mock.patch('ebcli.lib.ec2.urllib.request.Request')
    @mock.patch('ebcli.lib.ec2.urllib.request.urlopen')
    def test_get_instance_metadata_connection_error(
        self,
        urlopen_mock,
        request_mock
    ):
        # Setup mock for ConnectionError
        urlopen_mock.side_effect = ConnectionError("Connection refused")
        
        # Call the function and expect exception
        with self.assertRaises(ConnectionError):
            ec2.get_instance_metadata('instance-id')

    def test_is_timeout_exception_with_timeout_error(self):
        # Create a URLError with TimeoutError reason
        url_error = urllib.error.URLError("URL error")
        url_error.reason = TimeoutError("Timed out")
        
        # Verify it's detected as a timeout
        self.assertTrue(ec2._is_timeout_exception(url_error))

    def test_is_timeout_exception_with_timeout_string(self):
        # Create a URLError with "timed out" in the string
        url_error = urllib.error.URLError("Connection timed out")
        
        # Verify it's detected as a timeout
        self.assertTrue(ec2._is_timeout_exception(url_error))

    def test_is_timeout_exception_not_timeout(self):
        # Create a URLError without timeout indication
        url_error = urllib.error.URLError("Connection refused")
        
        # Verify it's not detected as a timeout
        self.assertFalse(ec2._is_timeout_exception(url_error))
