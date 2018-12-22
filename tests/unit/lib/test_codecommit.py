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

from ebcli.lib import codecommit

from .. import mock_responses


class TestCloudWatch(unittest.TestCase):
    def test_region_not_supported(self):
        region_supported = codecommit.region_supported('fake_region')
        self.assertFalse(region_supported)

    def test_region_supported(self):
        region_supported = codecommit.region_supported('us-east-1')
        self.assertTrue(region_supported)

    @mock.patch('ebcli.lib.codecommit.aws.make_api_call')
    def test_list_branches(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.LIST_BRANCHES_RESPONSE

        self.assertEqual(
            mock_responses.LIST_BRANCHES_RESPONSE,
            codecommit.list_branches(
                'my-repository',
                next_token='next-token'
            )
        )

        make_api_call_mock.assert_called_once_with(
            'codecommit',
            'list_branches',
            nextToken='next-token',
            repositoryName='my-repository'
        )

    @mock.patch('ebcli.lib.codecommit.aws.make_api_call')
    def test_list_repositories(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.LIST_REPOSITORIES_RESPONSE

        self.assertEqual(
            mock_responses.LIST_REPOSITORIES_RESPONSE,
            codecommit.list_repositories(next_token='next-token')
        )

        make_api_call_mock.assert_called_once_with(
            'codecommit',
            'list_repositories',
            nextToken='next-token',
            order='descending',
            sortBy='lastModifiedDate'
        )

    @mock.patch('ebcli.lib.codecommit.aws.make_api_call')
    def test_get_branch(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.GET_BRANCH_RESPONSE

        self.assertEqual(
            mock_responses.GET_BRANCH_RESPONSE,
            codecommit.get_branch('my-repository', 'my-branch')
        )

    @mock.patch('ebcli.lib.codecommit.aws.make_api_call')
    def test_get_repository(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.GET_REPOSITORY_RESPONSE

        self.assertEqual(
            mock_responses.GET_REPOSITORY_RESPONSE,
            codecommit.get_repository('my-repository')
        )

    @mock.patch('ebcli.lib.codecommit.aws.make_api_call')
    def test_create_branch(
            self,
            make_api_call_mock
    ):
        codecommit.create_branch(
            'my-repository',
            'my-branch',
            '068f60ebd5b7d9a0ad071b8a20ccdf8178491295'
        )

        make_api_call_mock.assert_called_once_with(
            'codecommit',
            'create_branch',
            branchName='my-branch',
            commitId='068f60ebd5b7d9a0ad071b8a20ccdf8178491295',
            repositoryName='my-repository'
        )

    @mock.patch('ebcli.lib.codecommit.aws.make_api_call')
    def test_create_repository(
            self,
            make_api_call_mock
    ):

        codecommit.create_repository(
            'my-repository',
            repo_description='my repository'
        )

        make_api_call_mock.assert_called_once_with(
            'codecommit',
            'create_repository',
            repositoryDescription='my repository',
            repositoryName='my-repository'
        )

    @mock.patch('ebcli.lib.codecommit.aws.make_api_call')
    @mock.patch('ebcli.lib.codecommit.io.echo')
    def test_make_api_call__access_denied(
            self,
            echo_mock,
            make_api_call_mock
    ):
        make_api_call_mock.side_effect = codecommit.aws.ServiceError(code='AccessDeniedException')

        with self.assertRaises(codecommit.ServiceError):
            codecommit._make_api_call('get-branch')

        echo_mock.assert_called_once_with(
            'EB CLI does not have the right permissions to access CodeCommit. '
            'List of IAM policies needed by EB CLI, please configure and try again.\n'
            ' codecommit:CreateRepository\n'
            ' codecommit:CreateBranch\n'
            ' codecommit:GetRepository\n'
            ' codecommit:ListRepositories\n'
            ' codecommit:ListBranches\n'
            'To learn more, see Docs: '
            'http://docs.aws.amazon.com/codecommit/latest/userguide/access-permissions.html'
        )
