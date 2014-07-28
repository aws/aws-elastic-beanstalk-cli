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


class ConfigController(AbstractBaseController):
    class Meta:
        label = 'config'
        description = strings['config.info']
        arguments = [
            (['-f', '--file'], dict(help='file to load from/save to')),
            (['-g', '--global'], dict(help='Make configuration file global'))
            ]

    def do_command(self):
        self.app.print_to_console('Error: Missing arguments. '
                                  'Please type --help for a list of '
                                  'available commands')

    @controller.expose(help="create a new configuration")
    def create(self):
        if not self.app.pargs.file:
            self.app.pargs.file = '.elasticbeanstalk/config-1'

        # Interactive create

        # Store template somewhere?

        self.app.print_to_console('Creating config template at',
                                  self.app.pargs.file)

    @controller.expose(help='Update an existing configuration')
    def update(self):
        if not self.app.pargs.file:
            self.app.pargs.file = '.elasticbeanstalk/config-1'
        # update a config template

        self.app.print_to_console('Updating config template',
                                  self.app.pargs.file)

    @controller.expose(help='Load a settings file')
    def load(self):
        if not self.app.pargs.file:
            self.app.pargs.file = '.elasticbeanstalk/config-1'

        self.app.print_to_console('Loaded file into your environment',
                                  self.app.pargs.file)

    @controller.expose(help='Save current environment settings to a file')
    def save(self):
        if not self.app.pargs.file:
            self.app.pargs.file = '.elasticbeanstalk/config-1'

        self.app.print_to_console('Saved environment configuration at',
                                  self.app.pargs.file)