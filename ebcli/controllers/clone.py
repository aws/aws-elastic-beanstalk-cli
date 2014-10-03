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
from ebcli.lib import utils
from ebcli.controllers.create import get_cname


class CloneController(AbstractBaseController):
    class Meta(AbstractBaseController.Meta):
        label = 'clone'
        description = strings['clone.info']
        arguments = [
            (['environment_name'], dict(action='store', nargs='?',
                                            help='Name of environment '
                                                 'to clone')),
            (['-n', '--clone_name'], dict(help='Desired name for environment'
                                               ' clone')),
            (['-c', '--cname'], dict(help='Cname prefix')),
            (['-r', '--region'], dict(help='Region where environment lives')),
            (['-nh', '--nohang'], dict(action='store_true',
                                       help='Do not hang and wait for create '
                                            'to be completed')),
        ]
        usage = 'eb clone <environment_name> (-n CLONE_NAME) [options ...]'

    def do_command(self):
        app_name = self.get_app_name()
        region = self.get_region()
        env_name = self.get_env_name()
        clone_name = self.app.pargs.clone_name
        cname = self.app.pargs.cname
        nohang = self.app.pargs.nohang
        provided_clone_name = clone_name is not None

        if not clone_name:
            if len(env_name) < 16:
                unique_name = env_name + '-clone'
            else:
                unique_name = 'my-cloned-env'

            env_list = operations.get_env_names(app_name, region)

            unique_name = utils.get_unique_name(unique_name, env_list)

            clone_name = io.prompt_for_environment_name(
                default_name=unique_name,
                prompt_text='Enter name for Environment Clone'
            )

        if not cname and not provided_clone_name:
            cname = get_cname(region)

        operations.make_cloned_env(app_name, env_name, clone_name, cname,
                             region, nohang)

    def complete_command(self, commands):
        super(CloneController, self).complete_command(commands)