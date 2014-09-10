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
from ebcli.objects import region as regions
from ebcli.lib import utils, elasticbeanstalk

class InitController(AbstractBaseController):
    class Meta:
        label = 'init'
        help = 'blarg!!'
        description = strings['init.info']
        arguments = [
            (['-a', '--app'], dict(help='Application name')),
            (['-r', '--region'], dict(help='Default Region')),
            (['-s', '--solution'], dict(help='Solution stack')),
            (['-i', '--interactive'], dict(action='store_true',
                                           help='Force interactive mode'))
        ]
        usage = 'eb init [options ...]'
        epilog = strings['init.epilog']


    def do_command(self):
        # get arguments
        flag = False
        app_name = self.app.pargs.app
        region = self.app.pargs.region
        solution = self.app.pargs.solution
        interactive = self.app.pargs.interactive

        # Get app name from config file, if exists
        if not app_name:
            try:
                app_name = fileoperations.get_application_name(default=None)
            except NotInitializedError:
                app_name = None

        # Get region from config file, if exists
        if not region:
            try:
                region = fileoperations.get_default_region()
            except NotInitializedError:
                region = None

        # Get solution stack from config file, if exists
        if not solution:
            try:
                solution = fileoperations.get_default_solution_stack()
            except NotInitializedError:
                solution = None

        # If we still do not have app name, (or interactive mode) ask for it
        if not app_name or interactive:
            file_name = fileoperations.get_current_directory_name()
            io.echo('Enter Application Name')
            app_name = io.prompt('default is "' + file_name + '"',
                                 default=file_name)

        # If we still do not have region name, (or interactive mode) ask for it
        if not region or interactive:
            if not flag:
                io.echo('Select a default region')
                region_list = regions.get_all_regions()
                result = utils.prompt_for_item_in_list(region_list, default=3)
                region = result.name

        # If still no have solution stack, (or interactive mode) ask for it
        if interactive:
            solution = None

        #Do setup stuff
        operations.setup(app_name, region, solution)