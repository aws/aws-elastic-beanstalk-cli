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

import time
from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.resources.strings import strings


class UpdateController(AbstractBaseController):
    class Meta:
        label = 'update'
        description = strings['update.info']
        arguments = [
            (['-e', '--environment'], dict(dest='env',
                                           help='Environment name')),
            ]

    def do_command(self):
        if not self.app.pargs.env:
            self.app.print_to_console('INFO: No environment has been given. '
                                      'Using branch default.')

        # update environment using a given config file

        self.app.print_to_console('...')
        time.sleep(1)

        self.app.print_to_console('Your Environment has been updated')