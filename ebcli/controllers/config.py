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

from cement.core import controller

from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.resources.strings import strings


class BranchController(AbstractBaseController):
    class Meta:
        label = 'branch'
        description = strings['branch.info']
        arguments = [
            (['-f', '--foo'], dict(help='notorious foo option')),
            ]

    def do_command(self):
        self.app.print_to_console('We are doing the branch stuff!')

    @controller.expose(help="stuff")
    def create(self):

        # Create a config template based on current environment

        # Store template somewhere?

        self.app.print_to_console('Creating config template')

    def update(self):
        # update a config template

        self.app.print_to_console('Updating config template')

    @controller.expose(help="dump the settings file")
    def dump(self):
        self.app.print_to_console('Dumping the optionsettings file')