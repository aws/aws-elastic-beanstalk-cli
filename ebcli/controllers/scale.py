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


class ScaleController(AbstractBaseController):
    class Meta:
        label = 'scale'
        description = strings['scale.info']
        usage = AbstractBaseController.Meta.usage.replace('{cmd}', label)
        arguments = [
            (['number'], dict(action='store', type=int,
                              help='Number of desired instances')),
            (['-f'], dict(action='store_true',
                          help='skip confirmation prompt')),
        ] + AbstractBaseController.Meta.arguments
        usage = 'eb scale {number} <environment_name> [options ...]'

    def do_command(self):
        app_name = self.get_app_name()
        region = self.get_region()
        number = self.app.pargs.number
        env_name = self.get_env_name(cmd_example='scale ' + str(number))
        confirm = self.app.pargs.f

        operations.scale(app_name, env_name, number, confirm, region)