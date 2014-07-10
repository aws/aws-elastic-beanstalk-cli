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
from ebcli.objects.notfoundexception import NotFoundException


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
        args = self.app.pargs
        if not args.region:
            args.region = "us-east-1"

        if args.defaults:
            if not args.env:
                args.env = "myFirstEnvironment"
            if not args.solution:
                args.solution = 'php-5.5-64bit-v1.0.4'

        if not args.env:
            args.env = self.app.prompt('environment name')
        if not args.solution:
            args.solution = elasticbeanstalk.select_solution_stack()

        try:
            solution = elasticbeanstalk.get_solution_stack(args.solution)
        except NotFoundException:
            self.app.log.error('Could not find specified solution stack')
            return

        self.app.print_to_console('Creating environment..')
        self.app.print_to_console('...')



        time.sleep(1)

        self.app.print_to_console('The environment', args.env,
                                  'has been created.')
        self.app.print_to_console('Region:', args.region)
        self.app.print_to_console('Solution Stack Name:', solution.string)
        self.app.print_to_console('Solution Stack Description:', solution.name)


        if args.single:
            self.app.print_to_console('Instance Type: Single Instance')
        else:
            self.app.print_to_console('Instance Type: Load Balanced')

        if args.worker:
            self.app.print_to_console('Tier: Worker')
        else:
            self.app.print_to_console('Tier: Web Server')



        #This command will probably go away
           #initialized a branch
            # sets up an environment for the branch

            # We should do this automagically when another command is called