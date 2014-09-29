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
from ebcli.core import io, fileoperations, operations


class UpdateController(AbstractBaseController):
    class Meta:
        label = 'update'
        description = strings['update.info']
        usage = AbstractBaseController.Meta.usage.replace('{cmd}', label)
        arguments = AbstractBaseController.Meta.arguments + [
            (['-nh', '--nohang'], dict(action='store_true',
                                       help='Do not hang and wait for update '
                                            'to be completed'))
        ]


    def do_command(self):
        region = self.get_region()
        env_name = self.get_env_name()
        app_name = self.get_app_name()
        nohang = self.app.pargs.nohang

        operations.update_environment(app_name, env_name, region, nohang)