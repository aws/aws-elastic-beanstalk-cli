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


class OpenController(AbstractBaseController):
    class Meta:
        label = 'open'
        description = strings['open.info']
        usage = AbstractBaseController.Meta.usage.replace('{cmd}', label)


    def do_command(self):
        region = self.app.pargs.region
        env_name = self.app.pargs.environment_name
        #load default region
        if not region:
            region = fileoperations.get_default_region()

        app_name = fileoperations.get_application_name()
        if not env_name:
            env_name = operations. \
                get_setting_from_current_branch('environment')

        if not env_name:
            # ask for environment name
            io.log_error(strings['branch.noenv'].replace('{cmd}', 'deploy'))
            return

        operations.open_app(app_name, env_name, region)