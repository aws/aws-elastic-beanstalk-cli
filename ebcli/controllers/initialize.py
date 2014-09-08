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
from ebcli.lib import utils

class InitController(AbstractBaseController):
    class Meta:
        label = 'init'
        description = strings['init.info']
        arguments = [
            (['-a', '--app'], dict(help='Application name')),
            (['-r', '--region'], dict(help='Default Region')),
        ]
        usage = 'this is a usage statement'
        epilog = 'this is an epilog'

    def do_command(self):
        # get arguments
        flag = False
        app_name = self.app.pargs.app
        region = self.app.pargs.region

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

        # If we still do not have app name, ask for it
        if not app_name:
            file_name = fileoperations.get_current_directory_name()
            io.echo('Enter Application Name')
            app_name = io.prompt('default is "' + file_name + '"',
                                 default=file_name)

        # If we still do not have region name, ask for it
        if not region:
            if not flag:
                io.echo('Set a default region'
                        ' (if no, we will use us-west-2)')
                response = operations.get_boolean_response()
            else:
                response = False

            if response:
                region_list = regions.get_all_regions()
                result = utils.prompt_for_item_in_list(region_list)
                region = result.name
            else:
                region = 'us-west-2'

        #Do setup stuff
        operations.setup(app_name, region)