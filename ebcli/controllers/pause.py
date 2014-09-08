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
from ebcli.core import fileoperations, operations, io


class PauseController(AbstractBaseController):
    class Meta:
        label = 'pause'
        description = strings['delete.info']
        arguments = [
            (['stuff'], dict(action='store', nargs='*',
                                        default=[],
                                        help='stuff')),
        ]
        hide = True

    def do_command(self):
        stuff = self.app.pargs.stuff
        for s in stuff:
            io.echo(s)