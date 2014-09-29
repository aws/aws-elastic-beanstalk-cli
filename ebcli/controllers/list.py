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


class ListController(AbstractBaseController):
    class Meta:
        label = 'list'
        description = strings['list.info']
        usage = AbstractBaseController.Meta.usage.replace('{cmd}', label)
        arguments = [
            (['-r', '--region'], dict(help='Region where environment lives')),
        ]

    def do_command(self):
        app_name = self.get_app_name()
        region = self.get_region()

        operations.list_env_names(app_name, region)

    def complete_command(self, commands):
        # We only care about regions
        self.complete_region(commands)