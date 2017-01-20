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

from ebcli.core.ebcore import EB
from ebcli.core import fileoperations

from .baseinttest import BaseIntegrationTest


class TestCreate(BaseIntegrationTest):

    def setUp(self):
        super(TestCreate, self).setUp()
        # Create all app stuff
        fileoperations.create_config_file('myEBCLItest', 'us-west-2',
                                          'my-stack-stack')

    def test_create_standard(self):
        """
                Testing for:
                1. Prompt for env-name
                2. Reads app name from file
                3. Ask for cname
                4. Ask for solution stack
                5. Ask for tier
                6. Create environment
                7. Message output environment name
        """
        # Setup mock responses


        # run cmd
        # EB.Meta.exit_on_close = False
        # self.app = EB(argv=['create'])
        # self.app.setup()
        # self.app.run()
        # self.app.close()