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
# from ebcli.resources.constants import ParameterName


class ImportController(AbstractBaseController):
    class Meta:
        label = 'import'
        description = strings['import.info']
        arguments = [
            (['-f', '--file'], dict(help='location of project root')),
        ]

    def do_command(self):



        if not self.app.pargs.file:
            self.app.pargs.file = '.elasticbeanstalk'
        else:
            self.app.pargs.file += '/.elasticbeanstalk'

        self.app.print_to_console('Importing all project settings from ',
                                  self.app.pargs.file)


        # self.app.log.info('hello')
        # self.app.log.warn('hello')
        # self.app.args.joe = 'bob'
        # self.app.print_to_console(ParameterName.AwsAccessKeyId, 'hello', 1)
        # self.app.print_to_console('joe = ' + self.app.args.joe)
        # name = self.app.prompt('bobs name')
        # self.app.print_to_console('you entered \'' + str(name) + '\'')
        # self.app.print_to_console('We are doing the import stuff!')