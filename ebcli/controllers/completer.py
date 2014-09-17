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
from ebcli.core import fileoperations, operations, io


class CompleterController(AbstractBaseController):
    class Meta:
        label = 'completer'
        description = 'auto-completer: hidden command'
        arguments = [
            (['commands'], dict(action='store', nargs='*',
                             default=[],
                             help='commands so far')),
            (['--cmplt'], dict(help='Word to complete')),
        ]
        hide = True

    def do_command(self):
        commands = self.app.pargs.commands
        word = self.app.pargs.cmplt

        # for c in commands:
        #     io.echo(c)
        # io.echo(word)
        #Hardcode a couple for testing
        io.echo('one two three')
