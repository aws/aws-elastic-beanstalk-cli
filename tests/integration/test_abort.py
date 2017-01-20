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
from tests.utilities.testutils import eb, process_output

from tests.integration.baseintegrationtest import BaseIntegrationTest
from tests.utilities.beanstalkutils import EnvStatus


class TestAbortCommand(BaseIntegrationTest):
    def test_abort_help(self):
        p = eb('abort --help')
        self.assertEqual(p.rc, 0, process_output(p))
        self.assertIn('usage: eb abort', p.stdout)

    def test_abort_with_update(self):
        p = eb('deploy {0} --nohang'.format(self.env_name))
        self.assertEqual(p.rc, 0, process_output(p))

        # Assert that the environment is updating
        self.assertTrue(self.beanstalk_utils.check_env_status(EnvStatus.Updating))

        # Abort the command
        p = eb('abort {0}'.format(self.env_name))
        self.assertEqual(p.rc, 0, process_output(p))

        # Assert the env is ready again
        self.assertTrue(self.beanstalk_utils.check_env_status(EnvStatus.Ready, timeout=30))

    def test_abort_with_no_update(self):
        # Abort the command
        p = eb('abort {0}'.format(self.env_name))
        self.assertEqual(p.rc, 4, process_output(p))
        self.assertIn('invalid state for this operation', p.stdout)
