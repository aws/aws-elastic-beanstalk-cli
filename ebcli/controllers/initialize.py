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
            (['-r', '--region'], dict(help='Service region environments '
                                           'will be created in')),
            (['-a', '--app'], dict(help='Application name')),
            (['-e', '--environment'], dict(help='Environment name')),
            (['--worker'], dict(action='store_true',
                                help='Start environment as a worker tier')),
            (['-S', '--solution'], dict(help='Solution stack')),
            (['-s', '--single'], dict(action='store_true',
                                      help='Environment will use a Single '
                                           'Instance with no Load Balancer')),
            (['-D', '--defaults'], dict(action='store_true',
                                        help='Automatically revert to defaults'
                                             ' for unsupplied parameters')),
            (['-p', '--profile'], dict(help='Instance profile')),

        ]
        usage = 'this is a usage statement'
        epilog = 'this is an epilog'

    def do_command(self):


        # Read/create config file

        # check for creds file
           # prompt for them to create one
           # export $AWS_CREDENTIALS_FILE if needed

        # Set up Git stuff
            # DevTools Git stuff for aws.push

        # git ignore?


        self.app.print_to_console('We are doing the init stuff!')

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