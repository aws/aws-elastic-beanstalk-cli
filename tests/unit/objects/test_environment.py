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
import unittest

from ebcli.objects.environment import Environment


class TestCFNStack(unittest.TestCase):
    def test_is_valid_arn(self):
        self.assertTrue(
            Environment.is_valid_arn(
                'arn:aws:elasticbeanstalk:us-west-2:123123123123:environment/my-application/environment-1'
            )
        )

    def test_is_valid_arn__cn_region(self):
        self.assertTrue(
            Environment.is_valid_arn(
                'arn:aws-cn:elasticbeanstalk:us-west-2:123123123123:environment/my-application/environment-1'
            )
        )

    def test_is_valid_arn__invalid_arns(self):
        invalid_inputs = [
            'an:aws:elasticbeanstalk:us-west-2:123123123123:environment/my-application/environment-1',
            'arn:ws:elasticbeanstalk:us-west-2:123123123123:environment/my-application/environment-1',
            'arn:aws:elasticbeanstlk:us-west-2:123123123123:environment/my-application/environment-1',
            'arn:aws:elasticbeanstlk:us-west-2:123123123123://',
            'arn:aws:elasticbeanstalk::123123123123:/environment-1',
        ]

        for string in invalid_inputs:
            self.assertFalse(Environment.is_valid_arn(string))
