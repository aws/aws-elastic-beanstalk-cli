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

from ebcli.lib import elasticbeanstalk

class AWSTestCase(unittest.TestCase):

    @mock.patch('ebcli.lib.elasticbeanstalk.aws')
    def test_aws(self, mock_aws):
        mock_aws.make_api_call.return_value = {'Applications': 'test'}
        result = elasticbeanstalk.describe_applications()
        mock_aws.make_api_call.assert_called_with('elasticbeanstalk', 'describe-applications')
        print result