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
import mock
import unittest

from ebcli.objects.platform import PlatformBranch
from ebcli.operations import platform_branch_ops


class TestPlatformBranchOperations(unittest.TestCase):
    def test_collect_families_from_branches(
        self,
    ):
        branches = [
            {"BranchName": "Docker running on 64bit Amazon Linux",
                "LifecycleState": "Supported", "PlatformName": "Docker"},
            {"BranchName": "Go 1 running on 64bit Amazon Linux",
                "LifecycleState": "Supported", "PlatformName": "Golang"},
            {"BranchName": "Multi-container Docker running on 64bit Amazon Linux",
                "LifecycleState": "Supported", "PlatformName": "Docker"},
            {"BranchName": "Python 3.6 running on 64bit Amazon Linux",
                "LifecycleState": "Supported", "PlatformName": "Python"},
        ]
        expected = ['Docker', 'Golang', 'Python']

        result = platform_branch_ops.collect_families_from_branches(branches)

        self.assertEqual(expected.sort(), result.sort())

    
    @mock.patch('ebcli.operations.platform_branch_ops.PlatformVersion.is_valid_arn')
    @mock.patch('ebcli.operations.platform_branch_ops.get_platform_branch_by_name')
    def test_is_platform_branch_name__with_branch_name(
        self,
        get_platform_branch_by_name_mock,
        is_valid_arn_mock,
    ):
        branch_name = 'PHP 7.1 running on 64bit Amazon Linux'
        is_valid_arn_mock.return_value = False
        get_platform_branch_by_name_mock.return_value = {
            'BranchName': branch_name
        }

        result = platform_branch_ops.is_platform_branch_name(branch_name)

        is_valid_arn_mock.assert_called_once_with(branch_name)
        get_platform_branch_by_name_mock.assert_called_once_with(branch_name)
        self.assertTrue(result)

    @mock.patch('ebcli.operations.platform_branch_ops.PlatformVersion.is_valid_arn')
    @mock.patch('ebcli.operations.platform_branch_ops.get_platform_branch_by_name')
    def test_is_platform_branch_name__with_arn(
        self,
        get_platform_branch_by_name_mock,
        is_valid_arn_mock,
    ):
        branch_name = 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.1'
        is_valid_arn_mock.return_value = True

        result = platform_branch_ops.is_platform_branch_name(branch_name)

        is_valid_arn_mock.assert_called_once_with(branch_name)
        get_platform_branch_by_name_mock.assert_not_called()
        self.assertFalse(result)

    @mock.patch('ebcli.operations.platform_branch_ops.PlatformVersion.is_valid_arn')
    @mock.patch('ebcli.operations.platform_branch_ops.get_platform_branch_by_name')
    def test_is_platform_branch_name__with_non_branch_name(
        self,
        get_platform_branch_by_name_mock,
        is_valid_arn_mock,
    ):
        branch_name = 'PHP 7.1'
        is_valid_arn_mock.return_value = False
        get_platform_branch_by_name_mock.return_value = None

        result = platform_branch_ops.is_platform_branch_name(branch_name)

        is_valid_arn_mock.assert_called_once_with(branch_name)
        get_platform_branch_by_name_mock.assert_called_once_with(branch_name)
        self.assertFalse(result)

    @mock.patch('ebcli.operations.platform_branch_ops._resolve_conflicting_platform_branches')
    @mock.patch('ebcli.operations.platform_branch_ops.elasticbeanstalk.list_platform_branches')
    def test_get_platform_branch_by_name(
        self,
        list_platform_branches_mock,
        _resolve_conflicting_platform_branches_mock,
    ):
        branch_name = 'PHP 7.1 running on 64bit Amazon Linux'
        list_results = [
            { 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.1' },
        ]

        list_platform_branches_mock.return_value = list_results

        expected_filters = [
            {
                'Attribute': 'BranchName',
                'Operator': '=',
                'Values': [branch_name],
            }
        ]

        result = platform_branch_ops.get_platform_branch_by_name(branch_name)

        list_platform_branches_mock.assert_called_once_with(filters=expected_filters)
        _resolve_conflicting_platform_branches_mock.assert_not_called()
        self.assertEqual(list_results[0], result)

    @mock.patch('ebcli.operations.platform_branch_ops._resolve_conflicting_platform_branches')
    @mock.patch('ebcli.operations.platform_branch_ops.elasticbeanstalk.list_platform_branches')
    def test_get_platform_branch_by_name__multiple_results(
        self,
        list_platform_branches_mock,
        _resolve_conflicting_platform_branches_mock,
    ):
        branch_name = 'PHP 7.1 running on 64bit Amazon Linux'
        list_results = [
            { 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.1' },
            { 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.2.1' },
            { 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.4' },
        ]

        list_platform_branches_mock.return_value = list_results
        _resolve_conflicting_platform_branches_mock.return_value = list_results[1]

        expected_filters = [
            {
                'Attribute': 'BranchName',
                'Operator': '=',
                'Values': [branch_name],
            }
        ]

        result = platform_branch_ops.get_platform_branch_by_name(branch_name)

        list_platform_branches_mock.assert_called_once_with(filters=expected_filters)
        _resolve_conflicting_platform_branches_mock.assert_called_once_with(list_results)
        self.assertEqual(list_results[1], result)

    @mock.patch('ebcli.operations.platform_branch_ops._resolve_conflicting_platform_branches')
    @mock.patch('ebcli.operations.platform_branch_ops.elasticbeanstalk.list_platform_branches')
    def test_get_platform_branch_by_name__no_results(
        self,
        list_platform_branches_mock,
        _resolve_conflicting_platform_branches_mock,
    ):
        branch_name = 'PHP 7.1 running on 64bit Amazon Linux'
        list_results = []

        list_platform_branches_mock.return_value = list_results

        expected_filters = [
            {
                'Attribute': 'BranchName',
                'Operator': '=',
                'Values': [branch_name],
            }
        ]

        result = platform_branch_ops.get_platform_branch_by_name(branch_name)

        list_platform_branches_mock.assert_called_once_with(filters=expected_filters)
        _resolve_conflicting_platform_branches_mock.assert_not_called()
        self.assertEqual(None, result)

    @mock.patch('ebcli.operations.platform_branch_ops._non_retired_platform_branches_cache', None)
    @mock.patch('ebcli.operations.platform_branch_ops.elasticbeanstalk.list_platform_branches')
    def test_list_nonretired_platform_branches(
        self,
        list_platform_branches_mock,
    ):
        expected_filters = [{
            'Attribute': 'LifecycleState',
            'Operator': '!=',
            'Values': ['Retired']
        }]
        platform_branches = [
            {'PlatformName': 'Corretto',
                'BranchName': '(BETA) Corretto 11 running on 64bit Amazon Linux 2', 'LifecycleState': 'Beta'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
                'LifecycleState': 'Supported'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.4 running on 64bit Amazon Linux',
                'LifecycleState': 'Deprecated'},
        ]
        list_platform_branches_mock.return_value = platform_branches

        result = platform_branch_ops.list_nonretired_platform_branches()

        list_platform_branches_mock.assert_called_once_with(filters=expected_filters)
        self.assertEqual(platform_branches, result)

    @mock.patch('ebcli.operations.platform_branch_ops._non_retired_platform_branches_cache', None)
    @mock.patch('ebcli.operations.platform_branch_ops.elasticbeanstalk.list_platform_branches')
    def test_list_nonretired_platform_branches__multiple_calls(
        self,
        list_platform_branches_mock,
    ):
        expected_filters = [{
            'Attribute': 'LifecycleState',
            'Operator': '!=',
            'Values': ['Retired']
        }]
        platform_branches = [
            {'PlatformName': 'Corretto',
                'BranchName': '(BETA) Corretto 11 running on 64bit Amazon Linux 2', 'LifecycleState': 'Beta'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
                'LifecycleState': 'Supported'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.4 running on 64bit Amazon Linux',
                'LifecycleState': 'Deprecated'},
        ]
        list_platform_branches_mock.return_value = platform_branches

        results = [
            platform_branch_ops.list_nonretired_platform_branches(),
            platform_branch_ops.list_nonretired_platform_branches(),
        ]

        list_platform_branches_mock.assert_called_once_with(filters=expected_filters)
        self.assertEqual(platform_branches, results[0])
        self.assertEqual(platform_branches, results[1])

    def test__resolve_conflicting_platform_branches(self):
        branches = [
            {
                'BranchName': 'PHP 7.1',
                'LifecycleState': 'Deprecated',
            },
            {
                'BranchName': 'PHP 7.3',
                'LifecycleState': 'Supported',
            },
            {
                'BranchName': 'PHP 7.2',
                'LifecycleState': 'Deprecated',
            },
        ]
        expected = branches[1]

        result = platform_branch_ops._resolve_conflicting_platform_branches(branches)

        self.assertEqual(expected, result)

    def test__resolve_conflicting_platform_branches__single_supported(self):
        branches = [
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux', 'LifecycleState': 'Retired'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux', 'LifecycleState': 'Beta'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
                'LifecycleState': 'Deprecated'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
                'LifecycleState': 'Supported'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
                'LifecycleState': 'Deprecated'},
        ]
        expected = branches[3]

        result = platform_branch_ops._resolve_conflicting_platform_branches(branches)

        self.assertEqual(result, expected)

    def test__resolve_conflicting_platform_branches__multi_supported(self):
        branches = [
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux', 'LifecycleState': 'Retired'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux', 'LifecycleState': 'Beta'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
                'LifecycleState': 'Deprecated'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
                'LifecycleState': 'Supported'},
            {'PlatformName': 'OtherFamily', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
                'LifecycleState': 'Supported'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
                'LifecycleState': 'Deprecated'},
        ]
        expected = branches[3]

        result = platform_branch_ops._resolve_conflicting_platform_branches(branches)

        self.assertEqual(result, expected)

    def test__resolve_conflicting_platform_branches__single_beta(self):
        branches = [
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux', 'LifecycleState': 'Retired'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux', 'LifecycleState': 'Beta'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
                'LifecycleState': 'Deprecated'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
                'LifecycleState': 'Deprecated'},
        ]
        expected = branches[1]

        result = platform_branch_ops._resolve_conflicting_platform_branches(branches)

        self.assertEqual(result, expected)

    def test__resolve_conflicting_platform_branches__multi_beta(self):
        branches = [
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux', 'LifecycleState': 'Retired'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux', 'LifecycleState': 'Beta'},
            {'PlatformName': 'OtherFamily', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux', 'LifecycleState': 'Beta'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
                'LifecycleState': 'Deprecated'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
                'LifecycleState': 'Deprecated'},
        ]
        expected = branches[1]

        result = platform_branch_ops._resolve_conflicting_platform_branches(branches)

        self.assertEqual(result, expected)

    def test__resolve_conflicting_platform_branches__single_deprecated(self):
        branches = [
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux', 'LifecycleState': 'Retired'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
                'LifecycleState': 'Deprecated'},
        ]
        expected = branches[1]

        result = platform_branch_ops._resolve_conflicting_platform_branches(branches)

        self.assertEqual(result, expected)

    def test__resolve_conflicting_platform_branches__multi_deprecated(self):
        branches = [
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux', 'LifecycleState': 'Retired'},
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
                'LifecycleState': 'Deprecated'},
            {'PlatformName': 'OtherFamily', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
                'LifecycleState': 'Deprecated'},
        ]
        expected = branches[1]

        result = platform_branch_ops._resolve_conflicting_platform_branches(branches)

        self.assertEqual(result, expected)

    def test__resolve_conflicting_platform_branches__only_retired(self):
        branches = [
            {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux', 'LifecycleState': 'Retired'},
        ]
        expected = branches[0]

        result = platform_branch_ops._resolve_conflicting_platform_branches(branches)

        self.assertEqual(result, expected)
