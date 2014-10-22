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
from ..resources.strings import strings
from ..core import operations, io
from ..objects.exceptions import InvalidOptionsError


class LogsController(AbstractBaseController):
    class Meta:
        label = 'logs'
        description = strings['logs.info']
        usage = AbstractBaseController.Meta.usage.replace('{cmd}', label)
        arguments = AbstractBaseController.Meta.arguments + [
            (['-a', '--all'], dict(action='store_true',
                                      help='Retrieve all logs')),
            (['-z', '--all_zip'], dict(action='store_true',
                                          help='Retrieve all logs as .zip')),
            (['-i', '--instance'], dict(help='Instance id')),
        ]
        epilog = strings['logs.epilog']

    def do_command(self):
        region = self.get_region()
        env_name = self.get_env_name()
        all = self.app.pargs.all
        instance = self.app.pargs.instance
        all_zip = self.app.pargs.all_zip

        if all and all_zip:
            raise InvalidOptionsError(strings['logs.allandzip'])

        if all and instance:
            raise InvalidOptionsError(strings['logs.allandinstance'])

        if all:
            info_type = 'bundle'
            do_zip = False
        elif all_zip:
            info_type = 'bundle'
            do_zip = True
        else:
            info_type = 'tail'
            do_zip = False

        operations.logs(env_name, info_type, region, do_zip=do_zip,
                        instance_id=instance)