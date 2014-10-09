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

import time
from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.resources.strings import strings
from ebcli.core import operations, io
from ebcli.objects.exceptions import NotFoundError


class TerminateController(AbstractBaseController):
    class Meta:
        label = 'terminate'
        description = strings['terminate.info']
        arguments = AbstractBaseController.Meta.arguments + [
            (['--force'], dict(action='store_true',
                               help='skip confimation prompt')),
            (['--all'], dict(action='store_true',
                             help='Terminate everything'))
        ]
        usage = AbstractBaseController.Meta.usage.replace('{cmd}', label)


    def do_command(self):
        region = self.get_region()
        app_name = self.get_app_name()
        force = self.app.pargs.force
        all = self.app.pargs.all

        if all:
            operations.delete_app(app_name, region, force)

        else:
            env_name = self.get_env_name()
            if not force:
                # make sure env exists
                env_names = operations.get_env_names(app_name, region)
                if env_name not in env_names:
                    raise NotFoundError('Environment ' +
                                        env_name + ' not found')
                io.echo('You are about to terminate environment:', env_name)
                result = io.get_input('Enter environment name '
                                      'as shown to confirm')

                if result != env_name:
                    io.log_error('Names do not match. Exiting.')
                    return

            operations.terminate(env_name, region)