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
# from ebcli.core import fileoperations


class InitController(AbstractBaseController):
    class Meta:
        label = 'init'
        description = strings['init.info']
        arguments = [
            (['-r', '--region'], dict(help='Default Service region which '
                                           'environments will be created in')),
            (['-a', '--app'], dict(help='Application name')),
            (['-D', '--defaults'], dict(action='store_true',
                                        help='Automatically revert to defaults'
                                             ' for unsupplied parameters')),
        ]
        usage = 'this is a usage statement'
        epilog = 'this is an epilog'

    def do_command(self):
        if self.app.pargs.defaults and not self.app.pargs.app:
            self.app.pargs.app = 'myFirstConsoleApp'

        if not self.app.pargs.region:
            self.app.pargs.region = "us-east-1"

        if not self.app.pargs.app:
            self.app.pargs.app = self.app.prompt('application name')

        self.app.print_to_console('Application', self.app.pargs.app,
                                  'has been created with default region of',
                                  self.app.pargs.region)

        # Create directory if it does not exist

        # Create app (?)

        # check for creds file
           # prompt for them to create one
           # export $AWS_CREDENTIALS_FILE if needed

        # Set up Git stuff
            # DevTools Git stuff for aws.push

        # git ignore?

        # queue.add(TryLoadEbConfigFileOperation(queue))
        # queue.add(ReadAwsCredentialFileOperation(queue))
        # queue.add(AskForConfigFileParameterOperation(queue))
        # queue.add(ValidateParameterOperation(queue))
        # queue.add(RotateOptionsettingFileOperation(queue))
        # queue.add(SanitizeBranchOperation(queue))
        # queue.add(UpdateAwsCredentialFileOperation(queue))
        # queue.add(SanitizeAppVersionNameOperation(queue))
        # queue.add(SaveEbConfigFileOperation(queue))
        # queue.add(UpdateDevToolsConfigOperation(queue))
        # queue.add(CheckGitIgnoreFileOperation(queue))