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
from ebcli.lib import elasticbeanstalk


class CreateController(AbstractBaseController):
    class Meta:
        label = 'create'
        description = strings['create.info']
        arguments = [

            (['-n', '--name'], dict(dest='env', help='Environment name')),
            (['-r', '--region'], dict(help='Region which environment '
                                           'will be created in')),
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

    def do_command(self):
        if not self.app.pargs.region:
            self.app.pargs.region = "us-east-1"

        if self.app.pargs.defaults:
            if not self.app.pargs.env:
                self.app.pargs.env = "myFirstEnvironment"
            if not self.app.pargs.solution:
                self.app.pargs.solution = 'PHP 5.5 on 64bit Amazon Linux 2014'

        if not self.app.pargs.env:
            self.app.pargs.env = self.app.prompt('environment name')
        if not self.app.pargs.solution:
            stacks = elasticbeanstalk.get_available_solution_stacks()
            print(stacks['SolutionStacks'])
            self.app.pargs.solution = self.app.prompt('solution stack')

        self.app.print_to_console('Creating environment..')
        self.app.print_to_console('...')
        time.sleep(1)

        self.app.print_to_console('The environment', self.app.pargs.env,
                                  'has been created.')
        self.app.print_to_console('Region:', self.app.pargs.region)
        self.app.print_to_console('Solution Stack:', self.app.pargs.solution)

        if self.app.pargs.single:
            self.app.print_to_console('Instance Type: Single Instance')
        else:
            self.app.print_to_console('Instance Type: Load Balanced')

        if self.app.pargs.worker:
            self.app.print_to_console('Tier: Worker')
        else:
            self.app.print_to_console('Tier: Web Server')



        #This command will probably go away
           #initialized a branch
            # sets up an environment for the branch

            # We should do this automagically when another command is called