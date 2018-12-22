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

from ebcli.lib import codebuild

from .. import mock_responses


class TestCloudWatch(unittest.TestCase):
    @mock.patch('ebcli.lib.codebuild.aws.make_api_call')
    def test_batch_get_builds(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.BATCH_GET_BUILDS

        build_ids = [
            'Elastic-Beanstalk-my-web-app-app-170706_000919-uUTqM:3362ef1d-584d-48c1-800a-c1c695b71562',
            'Elastic-Beanstalk-my-web-app-app-170706_001032-OYjRZ:a4db9491-91ba-4614-b5e4-3f8d9e994a19',
            'bad-batch-id-170706_001032-OYjRZ:a4db9491-91ba-4614-b5e4-3f8d9e994a19'
        ]

        self.assertEqual(
            mock_responses.BATCH_GET_BUILDS,
            codebuild.batch_get_builds(build_ids)
        )

    @mock.patch('ebcli.lib.codebuild.aws.make_api_call')
    @mock.patch('ebcli.lib.codebuild.io.echo')
    def test_batch_get_builds__service_error_raised(
            self,
            echo_mock,
            make_api_call_mock
    ):
        make_api_call_mock.side_effect = codebuild.aws.ServiceError(
            code='AccessDeniedException'
        )

        with self.assertRaises(codebuild.ServiceError):
            codebuild.batch_get_builds(['some-build-id'])

        echo_mock.assert_called_once_with(
            'EB CLI does not have the right permissions to access CodeBuild.\n'
            'To learn more, see Docs: '
            'https://docs-aws.amazon.com/codebuild/latest/userguide/auth-and-access-control-permissions-reference.html'
        )

    @mock.patch('ebcli.lib.codebuild.aws.make_api_call')
    def test_batch_get_builds__end_point_connection_error_raised(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.side_effect = codebuild.EndpointConnectionError(endpoint_url='www.codebuild.non-existent-region.com')

        with self.assertRaises(codebuild.ServiceError) as context_manager:
            codebuild.batch_get_builds(['some-build-id'])

        self.assertEqual(
            'Elastic Beanstalk does not support AWS CodeBuild in this region.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.lib.codebuild.aws.make_api_call')
    def test_list_curated_environment_images(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.LIST_CURATED_ENVIRONMENT_IMAGES_RESPONSE

        self.assertEqual(
            [
                {
                    'name': 'aws/codebuild/eb-java-7-amazonlinux-64:2.1.6',
                    'description': 'Java 7 Running on Amazon Linux 64bit '
                },
                {
                    'name': 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6',
                    'description': 'Java 8 Running on Amazon Linux 64bit '
                },
                {
                    'name': 'aws/codebuild/eb-go-1.5-amazonlinux-64:2.1.6',
                    'description': 'Go 1.5 Running on Amazon Linux 64bit '
                }
            ],
            codebuild.list_curated_environment_images()
        )
