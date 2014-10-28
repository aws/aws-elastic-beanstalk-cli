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

from ..core.abstractcontroller import AbstractBaseController
from ..resources.strings import strings, flag_text
from ..core import io, fileoperations, operations


class ConfigController(AbstractBaseController):
    class Meta:
        label = 'config'
        description = strings['config.info']
        usage = AbstractBaseController.Meta.usage.replace('{cmd}', label)
        arguments = AbstractBaseController.Meta.arguments + [
            (['-nh', '--nohang'], dict(action='store_true',
                                       help=flag_text['config.nohang']))
        ]


    def do_command(self):
        region = self.get_region()
        env_name = self.get_env_name()
        app_name = self.get_app_name()
        nohang = self.app.pargs.nohang

        operations.update_environment_configuration(app_name, env_name,
                                                    region, nohang)