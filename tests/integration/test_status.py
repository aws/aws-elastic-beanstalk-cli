# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from tests.integration.baseintegrationtest import BaseIntegrationTest
from tests.utilities.testutils import eb


class TestStatusCommand(BaseIntegrationTest):
    def test_status_help(self):
        p = eb('status --help')
        self.assertEqual(p.rc, 0)
        self.assertIn('usage: eb status', p.stdout)

    def test_status(self):
        p = eb('status {0}'.format(self.env_name))
        self.assertEqual(p.rc, 0)
        self.assertIn('Environment details for: {0}'.format(self.env_name), p.stdout)