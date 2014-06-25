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
import sys
import gettext


class ImportController(AbstractBaseController):
    class Meta:
        label = 'import'
        description = strings['import.info']
        arguments = [
            (['-f', '--foo'], dict(help='notorious foo option')),
        ]

    def do_command(self):
        self.app.args.joe = 'bob'
        self.app.print_to_console('joe = ' + self.app.args.joe)
        name = self.app.prompt('enter bobs name')
        self.app.print_to_console('you entered \'' + str(name) + '\'')
        self.app.print_to_console('We are doing the import stuff!')