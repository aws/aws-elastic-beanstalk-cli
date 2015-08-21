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

import argparse

from ..core.abstractcontroller import AbstractBaseController
from ..resources.strings import strings, flag_text
from ..operations import logsops
from ..objects.exceptions import InvalidOptionsError, NotFoundError


class LogsController(AbstractBaseController):
    class Meta:
        label = 'logs'
        description = strings['logs.info']
        usage = AbstractBaseController.Meta.usage.replace('{cmd}', label)
        arguments = AbstractBaseController.Meta.arguments + [
            (['-a', '--all'], dict(
                action='store_true', help=flag_text['logs.all'])),
            (['-z', '--zip'], dict(
                action='store_true', help=flag_text['logs.zip'])),
            (['-i', '--instance'], dict(help=flag_text['logs.instance'])),
            (['--stream'], dict(action='store_true',
                                help=flag_text['logs.stream'])),

        ]
        epilog = strings['logs.epilog']

    def do_command(self):
        env_name = self.get_env_name()
        if self.app.pargs.stream:
            try:
                return logsops.stream_logs(env_name)
            except NotFoundError:
                raise NotFoundError(strings['cloudwatch-stream.notsetup'])


        all = self.app.pargs.all
        instance = self.app.pargs.instance
        zip = self.app.pargs.zip

        if all and instance:
            raise InvalidOptionsError(strings['logs.allandinstance'])

        if zip:
            info_type = 'bundle'
            do_zip = True
        elif all:
            info_type = 'bundle'
            do_zip = False
        else:
            info_type = 'tail'
            do_zip = False

        logsops.logs(env_name, info_type, do_zip=do_zip,
                        instance_id=instance)