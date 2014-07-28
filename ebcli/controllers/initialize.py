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

from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.resources.strings import strings
from ebcli.core import fileoperations, io, operations
from ebcli.objects.exceptions import NotInitializedError


class InitController(AbstractBaseController):
    class Meta:
        label = 'init'
        description = strings['init.info']
        arguments = [
            (['-a', '--app'], dict(help='Application name')),
            (['-D', '--defaults'], dict(action='store_true',
                                        help='Automatically revert to defaults'
                                             ' for unsupplied parameters')),
        ]
        usage = 'this is a usage statement'
        epilog = 'this is an epilog'

    def do_command(self):
        # Get app name from config file, if exists
        try:
            app_name = fileoperations.get_application_name()
        except NotInitializedError:
            app_name = None

        if app_name and not self.app.pargs.app:
            self.app.pargs.app = app_name

        if self.app.pargs.defaults and not self.app.pargs.app:
            if not app_name:
                self.app.pargs.app = app_name
            self.app.pargs.app = 'myFirstConsoleApp'

        if not self.app.pargs.app:
            self.app.pargs.app = io.prompt('application name')

        #Do setup stuff
        operations.setup(self.app.pargs.app)