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
from copy import deepcopy

import mock
import unittest

from ebcli.operations import sshops

from .. import mock_responses


class TestSSHOps(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')
        os.chdir('testDir')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

    @mock.patch('ebcli.operations.sshops.io.prompt')
    @mock.patch('ebcli.operations.sshops.subprocess.call')
    @mock.patch('ebcli.operations.sshops.commonops.upload_keypair_if_needed')
    def test_generate_and_upload_keypair__exit_code_0(
            self,
            upload_keypair_if_needed_mock,
            call_mock,
            prompt_mock
    ):
        prompt_mock.return_value = 'aws-eb-us-west-2'
        call_mock.return_value = 0
        self.assertEqual(
            'aws-eb-us-west-2',
            sshops._generate_and_upload_keypair(['aws-eb', 'aws-eb-us-east-2'])
        )
        upload_keypair_if_needed_mock.assert_called_once_with('aws-eb-us-west-2')
        call_mock.assert_called_once_with(
            [
                'ssh-keygen',
                '-f',
                os.path.expanduser('~') + '{0}.ssh{0}aws-eb-us-west-2'.format(os.path.sep),
                '-C',
                'aws-eb-us-west-2'
            ]
        )

    @mock.patch('ebcli.operations.sshops.io.prompt')
    @mock.patch('ebcli.operations.sshops.subprocess.call')
    @mock.patch('ebcli.operations.sshops.commonops.upload_keypair_if_needed')
    def test_generate_and_upload_keypair__exit_code_1(
            self,
            upload_keypair_if_needed_mock,
            call_mock,
            prompt_mock
    ):
        prompt_mock.return_value = 'aws-eb-us-west-2'
        call_mock.return_value = 1
        self.assertEqual(
            'aws-eb-us-west-2',
            sshops._generate_and_upload_keypair(['aws-eb', 'aws-eb-us-east-2'])
        )
        upload_keypair_if_needed_mock.assert_called_once_with('aws-eb-us-west-2')
        call_mock.assert_called_once_with(
            [
                'ssh-keygen',
                '-f',
                os.path.expanduser('~') + '{0}.ssh{0}aws-eb-us-west-2'.format(os.path.sep),
                '-C',
                'aws-eb-us-west-2'
            ]
        )

    @mock.patch('ebcli.operations.sshops.io.prompt')
    @mock.patch('ebcli.operations.sshops.subprocess.call')
    def test_generate_and_upload_keypair__exit_code_is_other_than_1_and_0(
            self,
            call_mock,
            prompt_mock
    ):
        prompt_mock.return_value = 'aws-eb-us-west-2'
        call_mock.return_value = 2
        with self.assertRaises(sshops.CommandError) as context_manager:
            sshops._generate_and_upload_keypair(['aws-eb', 'aws-eb-us-east-2'])
        self.assertEqual(
            'An error occurred while running ssh-keygen.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.sshops.io.prompt')
    @mock.patch('ebcli.operations.sshops.subprocess.call')
    def test_generate_and_upload_keypair__ssh_keygen_not_present(
            self,
            call_mock,
            prompt_mock
    ):
        prompt_mock.return_value = 'aws-eb-us-west-2'
        call_mock.sideeffect = OSError

        with self.assertRaises(sshops.CommandError) as context_manager:
            sshops._generate_and_upload_keypair(['aws-eb', 'aws-eb-us-east-2'])
        self.assertEqual(
            'An error occurred while running ssh-keygen.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.sshops.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.operations.sshops._generate_and_upload_keypair')
    @mock.patch('ebcli.operations.sshops.ec2.get_key_pairs')
    @mock.patch('ebcli.operations.sshops.io.validate_action')
    def test_prompt_for_ec2_keyname(
            self,
            validate_action_mock,
            get_key_pairs_mock,
            generate_and_upload_keypair_mock,
            prompt_for_item_in_list_mock
    ):
        get_key_pairs_mock.return_value = mock_responses.DESCRIBE_KEY_PAIRS_RESPONSE['KeyPairs']
        prompt_for_item_in_list_mock.return_value = '[ Create new KeyPair ]'

        sshops.prompt_for_ec2_keyname('my-environment')

        validate_action_mock.assert_called_once_with('To confirm, type the environment name', 'my-environment')
        generate_and_upload_keypair_mock.assert_called_once_with(['key_pair_1', 'key_pair_2', '[ Create new KeyPair ]'])

    @mock.patch('ebcli.operations.sshops.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.operations.sshops._generate_and_upload_keypair')
    @mock.patch('ebcli.operations.sshops.ec2.get_key_pairs')
    @mock.patch('ebcli.operations.sshops.io.validate_action')
    def test_prompt_for_ec2_keyname__choose_existing_key(
            self,
            validate_action_mock,
            get_key_pairs_mock,
            generate_and_upload_keypair_mock,
            prompt_for_item_in_list_mock
    ):
        get_key_pairs_mock.return_value = mock_responses.DESCRIBE_KEY_PAIRS_RESPONSE['KeyPairs']
        prompt_for_item_in_list_mock.return_value = 'key_pair_2'

        sshops.prompt_for_ec2_keyname('my-environment')

        validate_action_mock.assert_called_once_with('To confirm, type the environment name', 'my-environment')
        generate_and_upload_keypair_mock.assert_not_called()

    @mock.patch('ebcli.operations.sshops.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.operations.sshops._generate_and_upload_keypair')
    @mock.patch('ebcli.operations.sshops.ec2.get_key_pairs')
    @mock.patch('ebcli.operations.sshops.io.get_boolean_response')
    def test_prompt_for_ec2_keyname__get_boolean_response_to_confirm_termination(
            self,
            get_boolean_response_mock,
            get_key_pairs_mock,
            generate_and_upload_keypair_mock,
            prompt_for_item_in_list_mock
    ):
        get_key_pairs_mock.return_value = mock_responses.DESCRIBE_KEY_PAIRS_RESPONSE['KeyPairs']
        prompt_for_item_in_list_mock.return_value = 'key_pair_2'
        get_boolean_response_mock.return_value = True

        sshops.prompt_for_ec2_keyname()

        generate_and_upload_keypair_mock.assert_not_called()

    @mock.patch('ebcli.operations.sshops._generate_and_upload_keypair')
    @mock.patch('ebcli.operations.sshops.ec2.get_key_pairs')
    @mock.patch('ebcli.operations.sshops.io.validate_action')
    @mock.patch('ebcli.operations.sshops.io.get_boolean_response')
    def test_prompt_for_ec2_keyname__no_keys_exist(
            self,
            get_boolean_response_mock,
            validate_action_mock,
            get_key_pairs_mock,
            generate_and_upload_keypair_mock
    ):
        get_key_pairs_mock.return_value = []
        get_boolean_response_mock.return_value = True

        sshops.prompt_for_ec2_keyname('my-environment')

        generate_and_upload_keypair_mock.assert_called_once_with([])
        validate_action_mock.assert_called_once()

    @mock.patch('ebcli.operations.sshops.fileoperations.get_ssh_folder')
    def test_get_ssh_file(
            self,
            get_ssh_folder_mock
    ):
        open('aws-eb-us-west-2', 'w').close()
        get_ssh_folder_mock.return_value = os.getcwd() + os.path.sep
        sshops._get_ssh_file('aws-eb-us-west-2').endswith('testDir{}aws-eb-us-west-2'.format(os.pathsep))

    @mock.patch('ebcli.operations.sshops.fileoperations.get_ssh_folder')
    def test_get_ssh_file__file_present_as_pem(
            self,
            get_ssh_folder_mock
    ):
        open('aws-eb-us-west-2.pem', 'w').close()
        get_ssh_folder_mock.return_value = os.getcwd() + os.path.sep
        sshops._get_ssh_file('aws-eb-us-west-2').endswith('testDir{}aws-eb-us-west-2.pem'.format(os.pathsep))

    @mock.patch('ebcli.operations.sshops.fileoperations.get_ssh_folder')
    def test_get_ssh_file__file_absent(
            self,
            get_ssh_folder_mock
    ):
        open('aws-eb-us-west-2.pem', 'w').close()
        get_ssh_folder_mock.return_value = os.getcwd() + os.path.sep
        with self.assertRaises(sshops.NotFoundError) as context_manager:
            sshops._get_ssh_file('absent_file').endswith('testDir{}aws-eb-us-west-2.pem'.format(os.pathsep))
        self.assertEqual(
            'The EB CLI cannot find your SSH key file for keyname "absent_file". '
            'Your SSH key file must be located in the .ssh folder in your home directory.',
            str(context_manager.exception))

    @mock.patch('ebcli.operations.sshops.ec2.describe_instance')
    def test_ssh_into_instance__no_key_pair(
            self,
            describe_instance_mock
    ):
        describe_instance_mock.return_value = dict()
        with self.assertRaises(sshops.NoKeypairError):
            sshops.ssh_into_instance('some-instance-id')

    @mock.patch('ebcli.operations.sshops.ec2.describe_instance')
    @mock.patch('ebcli.operations.sshops.ec2.describe_security_group')
    @mock.patch('ebcli.operations.sshops.ec2.authorize_ssh')
    @mock.patch('ebcli.operations.sshops._get_ssh_file')
    @mock.patch('ebcli.operations.sshops.subprocess.call')
    def test_ssh_into_instance(
            self,
            call_mock,
            _get_ssh_file_mock,
            authorize_ssh_mock,
            describe_security_group_mock,
            describe_instance_mock
    ):
        describe_instance_mock.return_value = mock_responses.DESCRIBE_INSTANCES_RESPONSE['Reservations'][0]['Instances'][0]
        describe_security_group_mock.return_value = mock_responses.DESCRIBE_SECURITY_GROUPS_RESPONSE['SecurityGroups'][0]
        _get_ssh_file_mock.return_value = 'aws-eb-us-west-2'
        call_mock.return_value = 0

        sshops.ssh_into_instance('instance-id')

    @mock.patch('ebcli.operations.sshops.ec2.describe_instance')
    @mock.patch('ebcli.operations.sshops.ec2.describe_security_group')
    @mock.patch('ebcli.operations.sshops.ec2.authorize_ssh')
    @mock.patch('ebcli.operations.sshops._get_ssh_file')
    @mock.patch('ebcli.operations.sshops.subprocess.call')
    def test_ssh_into_instance__ssh_fails(
            self,
            call_mock,
            _get_ssh_file_mock,
            authorize_ssh_mock,
            describe_security_group_mock,
            describe_instance_mock
    ):
        describe_instance_mock.return_value = mock_responses.DESCRIBE_INSTANCES_RESPONSE['Reservations'][0]['Instances'][0]
        describe_security_group_mock.return_value = mock_responses.DESCRIBE_SECURITY_GROUPS_RESPONSE['SecurityGroups'][0]
        _get_ssh_file_mock.return_value = 'aws-eb-us-west-2'
        call_mock.return_value = 1

        with self.assertRaises(sshops.CommandError) as context_manager:
            sshops.ssh_into_instance('instance-id')
        self.assertEqual(
            'An error occurred while running: ssh.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.sshops.ec2.describe_instance')
    @mock.patch('ebcli.operations.sshops._get_ssh_file')
    @mock.patch('ebcli.operations.sshops.subprocess.call')
    def test_ssh_into_instance__neither_public_nor_private_ip_found(
            self,
            call_mock,
            _get_ssh_file_mock,
            describe_instance_mock
    ):
        describe_instance_response = deepcopy(mock_responses.DESCRIBE_INSTANCES_RESPONSE['Reservations'][0]['Instances'][0])
        del describe_instance_response['PublicIpAddress']
        del describe_instance_response['PrivateIpAddress']
        describe_instance_mock.return_value = describe_instance_response
        _get_ssh_file_mock.return_value = 'aws-eb-us-west-2'
        call_mock.return_value = 0

        with self.assertRaises(sshops.NotFoundError):
            sshops.ssh_into_instance('instance-id')

    @mock.patch('ebcli.operations.sshops.ec2.describe_instance')
    @mock.patch('ebcli.operations.sshops.ec2.describe_security_group')
    @mock.patch('ebcli.operations.sshops.ec2.authorize_ssh')
    @mock.patch('ebcli.operations.sshops._get_ssh_file')
    @mock.patch('ebcli.operations.sshops.subprocess.call')
    def test_ssh_into_instance__uses_private_address(
            self,
            call_mock,
            _get_ssh_file_mock,
            authorize_ssh_mock,
            describe_security_group_mock,
            describe_instance_mock
    ):
        describe_instance_response = deepcopy(mock_responses.DESCRIBE_INSTANCES_RESPONSE['Reservations'][0]['Instances'][0])
        del describe_instance_response['PublicIpAddress']
        describe_instance_mock.return_value = describe_instance_response
        describe_security_group_mock.return_value = mock_responses.DESCRIBE_SECURITY_GROUPS_RESPONSE['SecurityGroups'][0]
        _get_ssh_file_mock.return_value = 'aws-eb-us-west-2'
        call_mock.return_value = 0

        sshops.ssh_into_instance('instance-id')
        call_mock.assert_called_once_with(['ssh', '-i', 'aws-eb-us-west-2', 'ec2-user@172.31.35.210'])

    @mock.patch('ebcli.operations.sshops.ec2.describe_instance')
    @mock.patch('ebcli.operations.sshops.ec2.describe_security_group')
    @mock.patch('ebcli.operations.sshops.ec2.revoke_ssh')
    @mock.patch('ebcli.operations.sshops.ec2.authorize_ssh')
    @mock.patch('ebcli.operations.sshops._get_ssh_file')
    @mock.patch('ebcli.operations.sshops.subprocess.call')
    def test_ssh_into_instance__ssh_rule_exists(
            self,
            call_mock,
            _get_ssh_file_mock,
            authorize_ssh_mock,
            revoke_ssh_mock,
            describe_security_group_mock,
            describe_instance_mock
    ):
        describe_instance_response = deepcopy(mock_responses.DESCRIBE_INSTANCES_RESPONSE['Reservations'][0]['Instances'][0])
        describe_instance_mock.return_value = describe_instance_response
        describe_security_group_mock.return_value = mock_responses.DESCRIBE_SECURITY_GROUPS_RESPONSE['SecurityGroups'][0]
        _get_ssh_file_mock.return_value = 'aws-eb-us-west-2'
        call_mock.return_value = 0

        sshops.ssh_into_instance('instance-id')
        authorize_ssh_mock.assert_not_called()
        revoke_ssh_mock.assert_not_called()
        call_mock.assert_called_once_with(['ssh', '-i', 'aws-eb-us-west-2', 'ec2-user@54.218.96.238'])

    @mock.patch('ebcli.operations.sshops.ec2.describe_instance')
    @mock.patch('ebcli.operations.sshops.ec2.describe_security_group')
    @mock.patch('ebcli.operations.sshops.ec2.revoke_ssh')
    @mock.patch('ebcli.operations.sshops.ec2.authorize_ssh')
    @mock.patch('ebcli.operations.sshops._get_ssh_file')
    @mock.patch('ebcli.operations.sshops.subprocess.call')
    def test_ssh_into_instance__no_ssh_rule_exists(
            self,
            call_mock,
            _get_ssh_file_mock,
            authorize_ssh_mock,
            revoke_ssh_mock,
            describe_security_group_mock,
            describe_instance_mock
    ):
        describe_instance_response = deepcopy(mock_responses.DESCRIBE_INSTANCES_RESPONSE['Reservations'][0]['Instances'][0])
        describe_instance_mock.return_value = describe_instance_response
        describe_security_group_mock.return_value = mock_responses.DESCRIBE_SECURITY_GROUPS_RESPONSE['SecurityGroups'][1]
        _get_ssh_file_mock.return_value = 'aws-eb-us-west-2'
        call_mock.return_value = 0

        sshops.ssh_into_instance('instance-id')
        authorize_ssh_mock.assert_called_once_with('sg-12312313')
        revoke_ssh_mock.assert_called_once_with('sg-12312313')
        call_mock.assert_called_once_with(['ssh', '-i', 'aws-eb-us-west-2', 'ec2-user@54.218.96.238'])

    @mock.patch('ebcli.operations.sshops.prompt_for_ec2_keyname')
    @mock.patch('ebcli.operations.sshops.commonops.update_environment')
    def test_setup_ssh(
            self,
            update_environment_mock,
            prompt_for_ec2_keyname_mock
    ):
        prompt_for_ec2_keyname_mock.return_value = 'aws-eb-us-west-2'

        sshops.setup_ssh('my-environment', 'aws-eb-us-west-2')

        update_environment_mock.assert_called_once_with(
            'my-environment',
            [
                {
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'EC2KeyName',
                    'Value': 'aws-eb-us-west-2'
                }
            ],
            False,
            timeout=5
        )

    @mock.patch('ebcli.operations.sshops.prompt_for_ec2_keyname')
    @mock.patch('ebcli.operations.sshops.commonops.update_environment')
    def test_setup_ssh__keyname_not_entered(
            self,
            update_environment_mock,
            prompt_for_ec2_keyname_mock
    ):
        prompt_for_ec2_keyname_mock.return_value = None

        sshops.setup_ssh('my-environment', 'aws-eb-us-west-2')

        update_environment_mock.assert_not_called()

    @mock.patch('ebcli.operations.sshops.setup_ssh')
    def test_prepare_for_ssh(
            self,
            setup_ssh_mock
    ):
        sshops.prepare_for_ssh(
            'my-environment',
            'instance',
            False,
            False,
            True,
            None
        )
        setup_ssh_mock.assert_called_once_with('my-environment', None, timeout=None)

    def test_prepare_for_ssh__instance_and_number(self):
        with self.assertRaises(sshops.InvalidOptionsError) as context_manager:
            sshops.prepare_for_ssh(
                'my-environment',
                'instance',
                False,
                False,
                False,
                1
            )
        self.assertEqual(
            'You cannot use the "--instance" and "--number" options together.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.sshops.commonops.get_instance_ids')
    @mock.patch('ebcli.operations.sshops.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.operations.sshops.ssh_into_instance')
    def test_prepare_for_ssh__choose_instance_to_ssh_into(
            self,
            ssh_into_instance_mock,
            prompt_for_item_in_list_mock,
            get_instance_ids_mock
    ):
        get_instance_ids_mock.return_value = [
            'i-123123123123',
            'i-234234234424',
            'i-353454535434',
        ]
        prompt_for_item_in_list_mock.return_value = 'i-353454535434'

        sshops.prepare_for_ssh(
            'my-environment',
            None,
            False,
            False,
            False,
            None
        )

        ssh_into_instance_mock.assert_called_once_with(
            'i-353454535434',
            command=None,
            custom_ssh=None,
            force_open=False,
            keep_open=False
        )

    @mock.patch('ebcli.operations.sshops.commonops.get_instance_ids')
    @mock.patch('ebcli.operations.sshops.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.operations.sshops.ssh_into_instance')
    def test_prepare_for_ssh__choose_instance_to_ssh_into(
            self,
            ssh_into_instance_mock,
            prompt_for_item_in_list_mock,
            get_instance_ids_mock
    ):
        get_instance_ids_mock.return_value = [
            'i-123123123123',
        ]
        prompt_for_item_in_list_mock.return_value = 'i-353454535434'

        sshops.prepare_for_ssh(
            'my-environment',
            None,
            False,
            False,
            False,
            None
        )

        ssh_into_instance_mock.assert_called_once_with(
            'i-123123123123',
            command=None,
            custom_ssh=None,
            force_open=False,
            keep_open=False
        )

    @mock.patch('ebcli.operations.sshops.commonops.get_instance_ids')
    @mock.patch('ebcli.operations.sshops.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.operations.sshops.ssh_into_instance')
    def test_prepare_for_ssh__number_of_instance_specified(
            self,
            ssh_into_instance_mock,
            prompt_for_item_in_list_mock,
            get_instance_ids_mock
    ):
        get_instance_ids_mock.return_value = [
            'i-123123123123',
            'i-234234234424',
            'i-353454535434',
        ]
        prompt_for_item_in_list_mock.return_value = 'i-353454535434'

        sshops.prepare_for_ssh(
            'my-environment',
            None,
            False,
            False,
            False,
            2
        )

        ssh_into_instance_mock.assert_called_once_with(
            'i-234234234424',
            command=None,
            custom_ssh=None,
            force_open=False,
            keep_open=False
        )

    @mock.patch('ebcli.operations.sshops.commonops.get_instance_ids')
    @mock.patch('ebcli.operations.sshops.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.operations.sshops.ssh_into_instance')
    @mock.patch('ebcli.operations.sshops.io.log_error')
    def test_prepare_for_ssh__ssh_into_instance_fails(
            self,
            log_error_mock,
            ssh_into_instance_mock,
            prompt_for_item_in_list_mock,
            get_instance_ids_mock
    ):
        get_instance_ids_mock.return_value = [
            'i-123123123123',
            'i-234234234424',
            'i-353454535434',
        ]
        prompt_for_item_in_list_mock.return_value = 'i-353454535434'
        ssh_into_instance_mock.side_effect = sshops.NoKeypairError

        sshops.prepare_for_ssh(
            'my-environment',
            None,
            False,
            False,
            False,
            2
        )

        ssh_into_instance_mock.assert_called_once_with(
            'i-234234234424',
            command=None,
            custom_ssh=None,
            force_open=False,
            keep_open=False
        )
        log_error_mock.assert_called_once_with(
            'This environment is not set up for SSH. Use "eb ssh --setup" to set up SSH for the environment.'
        )
