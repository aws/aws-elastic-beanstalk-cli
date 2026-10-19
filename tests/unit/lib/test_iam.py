# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import mock
import unittest

from ebcli.lib import iam
from ebcli.objects.exceptions import AlreadyExistsError, NotAuthorizedError, NotAuthorizedInRegionError
from ebcli.resources.statics import iam_documents

from .. import mock_responses


class TestIAM(unittest.TestCase):
    @mock.patch('ebcli.lib.sns.aws.make_api_call')
    def test_account_id(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.GET_USER_RESPONSE

        self.assertEqual('123123123123', iam.account_id())

        make_api_call_mock.assert_called_once_with('iam', 'get_user')

    @mock.patch('ebcli.lib.iam.get_roles')
    def test_role_exists(self, get_roles_mock):
        # Mock the get_roles function to return a sample list of roles
        mock_roles = [
            {'RoleName': 'aws-elasticbeanstalk-ec2-role'},
            {'RoleName': 'aws-elasticbeanstalk-service-role'}
        ]
        get_roles_mock.return_value = mock_roles

        # Test for a role that exists
        self.assertTrue(iam.role_exists('aws-elasticbeanstalk-ec2-role'))

        # Test for a role that doesn't exist
        self.assertFalse(iam.role_exists('SomeRandomIAMRole'))

        self.assertEqual(get_roles_mock.call_count, 2)



class TestCreateRoleWithPolicyExistingRole(unittest.TestCase):
    EXPECTED = ('{"Version": "2008-10-17", "Statement": [{"Action": "sts:AssumeRole",'
                ' "Principal": {"Service": "ec2.amazonaws.com"}, "Effect": "Allow"}]}')
    EC2 = {'Effect': 'Allow', 'Principal': {'Service': 'ec2.amazonaws.com'}}
    OTHER = {'Effect': 'Allow', 'Principal': {'AWS': 'arn:aws:iam::123456789012:root'}}

    def _run(self, trust=None, attached=(), role_exists=True, get_role_error=None):
        def api(operation, **kwargs):
            if operation == 'create_role' and role_exists:
                raise AlreadyExistsError
            if operation == 'list_attached_role_policies':
                return {'AttachedPolicies': [{'PolicyArn': arn} for arn in attached]}
            return {}

        with mock.patch('ebcli.lib.iam._make_api_call', side_effect=api), \
                mock.patch('ebcli.lib.iam.attach_role_policy') as attach, \
                mock.patch('ebcli.lib.iam.get_role') as get_role, \
                mock.patch('ebcli.lib.iam.io') as io:
            if get_role_error:
                get_role.side_effect = get_role_error
            else:
                get_role.return_value = {'AssumeRolePolicyDocument':
                                         {'Statement': list(trust or [])}}
            iam.create_role_with_policy('role', self.EXPECTED, ['p1', 'p2'])
            return [c[0][1] for c in attach.call_args_list], get_role, io

    def test_new_role_gets_all_policies_without_trust_lookup(self):
        attached, get_role, _ = self._run(role_exists=False)

        self.assertEqual(['p1', 'p2'], attached)
        get_role.assert_not_called()

    def test_fully_provisioned_role_is_not_inspected(self):
        """Extra principals on a working role must not matter on repeat runs."""
        attached, get_role, io = self._run(attached=['p1', 'p2'])

        self.assertEqual([], attached)
        get_role.assert_not_called()
        io.log_warning.assert_not_called()

    def test_trusted_role_gets_only_missing_policies(self):
        attached, _, io = self._run(trust=[self.EC2], attached=['p1'])

        self.assertEqual(['p2'], attached)
        io.log_warning.assert_not_called()

    def test_role_trusting_another_principal_gets_nothing_and_warns(self):
        attached, _, io = self._run(trust=[self.OTHER])

        self.assertEqual([], attached)
        io.log_warning.assert_called_once()

    def test_role_trusting_expected_service_and_another_principal_gets_nothing(self):
        attached, _, _ = self._run(trust=[self.EC2, self.OTHER])

        self.assertEqual([], attached)

    def test_not_principal_is_treated_as_everyone(self):
        attached, _, _ = self._run(
            trust=[{'Effect': 'Allow', 'NotPrincipal': {'Service': 'ec2.amazonaws.com'}}])

        self.assertEqual([], attached)

    def test_china_service_principal_is_trusted(self):
        with mock.patch.object(self, 'EXPECTED', iam_documents.EC2_ASSUME_ROLE_PERMISSION_CN):
            attached, _, _ = self._run(
                trust=[{'Effect': 'Allow', 'Principal': {'Service': ['ec2.amazonaws.com.cn']}}])

        self.assertEqual(['p1', 'p2'], attached)

    def test_unreadable_role_in_beijing_gets_nothing_and_warns(self):
        """cn-north-1 raises a different exception for the same 403."""
        attached, _, io = self._run(get_role_error=NotAuthorizedInRegionError)

        self.assertEqual([], attached)
        io.log_warning.assert_called_once()

    def test_unreadable_role_gets_nothing_and_warns(self):
        attached, _, io = self._run(get_role_error=NotAuthorizedError)

        self.assertEqual([], attached)
        io.log_warning.assert_called_once()
