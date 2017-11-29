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
from botocore.credentials import Credentials
import mock
import unittest

from ebcli.objects.solutionstack import SolutionStack
from ebcli.lib import codecommit


class TestCodeCommit(unittest.TestCase):
    solution = SolutionStack('64bit Amazon Linux 2015.03 v2.0.6 running PHP 5.5')
    app_name = 'ebcli-intTest-app'

    def setUp(self):
        self.patcher_io = mock.patch('ebcli.controllers.codesource.io')
        self.patcher_aws = mock.patch('ebcli.lib.codecommit.aws')
        self.mock_io = self.patcher_io.start()
        self.mock_codecommit_aws = self.patcher_aws.start()

    def tearDown(self):
        self.patcher_io.stop()
        self.patcher_aws.stop()


    def test_region_not_supported(self):
        region_supported = codecommit.region_supported('fake_region')
        self.assertFalse(region_supported, "Expected fake region to not be supported, but it was")

    def test_region_supported(self):
        region_supported = codecommit.region_supported('us-east-1')
        self.assertTrue(region_supported, "Expected us-east-1 to be supported but it's not")
