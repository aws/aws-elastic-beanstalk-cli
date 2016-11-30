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
import mock
import unittest

from ebcli.lib import codebuild


class TestCodeBuild(unittest.TestCase):
    expected_default_response = {'200'}

    def setUp(self):
        self.patcher_aws = mock.patch('ebcli.lib.codebuild.aws')
        self.mock_codebuild_aws = self.patcher_aws.start()

    def tearDown(self):
        self.patcher_aws.stop()

    def test_get_builds(self):
        # Set local variables
        build_ids = ['arn:aws:codebuild:us-east-1:123456789876:build/foo-test']

        # Mock out api calls
        self.mock_codebuild_aws.make_api_call.return_value = self.expected_default_response

        # Make actual call
        actual_response = codebuild.batch_get_builds(build_ids)

        # Assert methods were called with the right params and returned the correct values
        self.assertEqual(self.expected_default_response, actual_response,
                         "Expected: {0} but got: {1}".format(self.expected_default_response, actual_response))
        self.mock_codebuild_aws.make_api_call.assert_called_with('codebuild', 'batch_get_builds',
                                                                 ids=build_ids)


    def test_list_curated_environment_images(self):
        # Set local variables
        api_response = {u'platforms':
                            [{u'languages':
                                  [{u'images':
                                        [{u'name': u'aws/codebuild/eb-java-7-amazonlinux-64:2.1.3', u'description': u'AWS ElasticBeanstalk - Java 7 Running on Amazon Linux 64bit v2.1.3'},
                                         {u'name': u'aws/codebuild/eb-java-8-amazonlinux-64:2.1.3', u'description': u'AWS ElasticBeanstalk - Java 8 Running on Amazon Linux 64bit v2.1.3'},
                                         {u'name': u'aws/codebuild/eb-java-7-amazonlinux-64:2.1.6', u'description': u'AWS ElasticBeanstalk - Java 7 Running on Amazon Linux 64bit v2.1.6'},
                                         {u'name': u'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6', u'description': u'AWS ElasticBeanstalk - Java 8 Running on Amazon Linux 64bit v2.1.6'}],
                                        u'language': u'Java'},
                                   {u'images':
                                        [{u'name': u'aws/codebuild/eb-go-1.5-amazonlinux-64:2.1.3', u'description': u'AWS ElasticBeanstalk - Go 1.5 Running on Amazon Linux 64bit v2.1.3'},
                                         {u'name': u'aws/codebuild/eb-go-1.5-amazonlinux-64:2.1.6', u'description': u'AWS ElasticBeanstalk - Go 1.5 Running on Amazon Linux 64bit v2.1.6'}],
                                        u'language': u'Golang'},
                                   {u'images':
                                        [{u'name': u'aws/codebuild/android-java-6:24.4.1', u'description': u'AWS CodeBuild - Android 24.4.1 with java 6'},
                                         {u'name': u'aws/codebuild/android-java-7:24.4.1', u'description': u'AWS CodeBuild - Android 24.4.1 with java 7'},
                                         {u'name': u'aws/codebuild/android-java-8:24.4.1', u'description': u'AWS CodeBuild - Android 24.4.1 with java 8'}],
                                        u'language': u'Android'}
                                  ]
                              }],
                         'ResponseMetadata':
                             {'date': 'Tue, 22 Nov 2016 21:36:19 GMT',
                              'RetryAttempts': 0, 'HTTPStatusCode': 200,
                              'RequestId': 'b47ba2d1-b0fb-11e6-a6a7-6fc6c5a33aee'}}

        expected_response = [{u'name': u'aws/codebuild/eb-java-7-amazonlinux-64:2.1.6',
                              u'description': u'Java 7 Running on Amazon Linux 64bit '},
                             {u'name': u'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6',
                              u'description': u'Java 8 Running on Amazon Linux 64bit '},
                             {u'name': u'aws/codebuild/eb-go-1.5-amazonlinux-64:2.1.6',
                              u'description': u'Go 1.5 Running on Amazon Linux 64bit '}]

        # Mock out api calls
        self.mock_codebuild_aws.make_api_call.return_value = api_response

        # Make actual call
        actual_response = codebuild.list_curated_environment_images()

        # Assert methods were called with the right params and returned the correct values
        self.assertEqual(expected_response, actual_response,
                         "Expected response '{0}' but was: {1}".format(expected_response, actual_response))
        self.mock_codebuild_aws.make_api_call.assert_called_with('codebuild',
                                                                 'list_curated_environment_images')
