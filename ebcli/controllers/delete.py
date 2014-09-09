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
from ebcli.objects.exceptions import ServiceError

class DeleteController(AbstractBaseController):
    class Meta:
        label = 'delete'
        description = strings['delete.info']
        arguments = [
            (['-y'], dict(action='store_true',
                          help='answer yes to all questions')),
        ]

    def do_command(self):
        confirm = self.app.pargs.y
        # delete App
        app_name = fileoperations.get_application_name()
        region = fileoperations.get_default_region()
        operations.delete(app_name, region, confirm)