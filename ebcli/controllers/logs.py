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
from ebcli.core import operations, io


class LogsController(AbstractBaseController):
    class Meta:
        label = 'logs'
        description = strings['logs.info']
        arguments = [
            (['environment_name'], dict(action='store', nargs='?',
                                        default=[],
                                        help='Environment name')),
            (['-r', '--region'], dict(help='Region where environment lives')),
        ]

    def do_command(self):
        region = self.app.pargs.region
        env_name = self.app.pargs.environment_name

        if not env_name:
            env_name = operations. \
                get_setting_from_current_branch('environment')

        if not env_name:
            # ask for environment name
            io.echo('No environment is registered with this branch. '
                    'You must specify an environment, i.e. eb logs envName')
            env_name = io.prompt_for_environment_name()

        operations.logs(env_name, region)