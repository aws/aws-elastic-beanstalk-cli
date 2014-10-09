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
from ebcli.resources.strings import strings, prompts
from ebcli.core import fileoperations, io, operations
from ebcli.objects.exceptions import NotInitializedError, NotFoundError
from ebcli.objects import region as regions
from ebcli.lib import utils, elasticbeanstalk


class InitController(AbstractBaseController):
    class Meta:
        label = 'init'
        help = 'blarg!!'
        description = strings['init.info']
        arguments = [
            (['application_name'], dict(help='Application name',
                                        nargs='?', default=[])),
            (['-r', '--region'], dict(help='Default Region')),
            (['-s', '--solution'], dict(help='Default Solution stack')),
            (['-k', '--keyname'], dict(help='Default EC2 key name')),
            (['-i', '--interactive'], dict(action='store_true',
                                           help='Force interactive mode')),
            (['--nossh'], dict(action='store_true',
                               help='Dont  setup ssh'))
        ]
        usage = 'eb init [options ...]'
        epilog = strings['init.epilog']

    def do_command(self):
        # get arguments
        self.nossh = self.app.pargs.nossh
        self.interactive = self.app.pargs.interactive
        self.region = self.get_region()
        self.flag = False
        if self.app.pargs.application_name and self.app.pargs.solution:
            self.flag = True

        if not operations.credentials_are_valid(self.region):
            operations.setup_credentials()

        self.solution = self.get_solution_stack()
        self.app_name = self.get_app_name()

        if not self.solution or self.interactive:
            result = operations.prompt_for_solution_stack(self.region)
            self.solution = result.version

        self.keyname = self.get_keyname()

        operations.setup(self.app_name, self.region, self.solution,
                         self.keyname)

    def get_app_name(self):
        # Get app name from command line arguments
        app_name = self.app.pargs.application_name

        # Get app name from config file, if exists
        if not app_name:
            try:
                app_name = fileoperations.get_application_name(default=None)
            except NotInitializedError:
                app_name = None

        # Ask for app name
        if not app_name or self.interactive:
            app_name = _get_application_name_interactive(self.region)

        return app_name

    def get_region(self):
        # Get region from command line arguments
        region = self.app.pargs.region

        # Get region from config file
        if not region:
            try:
                region = fileoperations.get_default_region()
            except NotInitializedError:
                region = None

        # Ask for region
        if not region or self.interactive:
            io.echo()
            io.echo('Select a default region')
            region_list = regions.get_all_regions()
            result = utils.prompt_for_item_in_list(region_list, default=3)
            region = result.name

        return region

    def get_solution_stack(self):
        # Get solution stack from command line arguments
        solution_string = self.app.pargs.solution

        # Get solution stack from config file, if exists
        if not solution_string:
            try:
                solution_string = fileoperations.get_default_solution_stack()
            except NotInitializedError:
                solution_string = None

        if solution_string:
            operations.get_solution_stack(solution_string, self.region)

        return solution_string

    def get_keyname(self):
        if self.nossh:
            return None

        keyname = self.app.pargs.keyname

        # Get keyname from config file, if exists
        if not keyname:
            try:
                keyname = fileoperations.get_default_keyname()
            except NotInitializedError:
                keyname = None

        if self.flag and not self.interactive:
            return keyname

        if not keyname or self.interactive:
            # Prompt for one
            keyname = operations.prompt_for_ec2_keyname(self.region)

        return keyname

    def complete_command(self, commands):
        self.complete_region(commands)
        #Note, completing solution stacks is only going to work
        ## if they already have their keys set up with region
        if commands[-1] in ['-s', '--solution']:
            io.echo(*elasticbeanstalk.get_available_solution_stacks())


def _get_application_name_interactive(region):
    app_list = operations.get_application_names(region)
    new_app = False
    if len(app_list) > 0:
        io.echo()
        io.echo('Select an application to use')
        new_app_option = '[ Create new Application ]'
        app_list.append(new_app_option)
        app_name = utils.prompt_for_item_in_list(app_list,
                                                 default=len(app_list))
        if app_name == new_app_option:
            new_app = True

    if len(app_list) == 0 or new_app:
        file_name = fileoperations.get_current_directory_name()
        io.echo()
        io.echo('Enter Application Name')
        unique_name = utils.get_unique_name(file_name, app_list)
        app_name = io.prompt_for_unique_name(unique_name, app_list)

    return app_name