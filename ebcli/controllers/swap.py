# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
from ..resources.strings import strings, flag_text, prompts
from ..core import io
from ..objects.exceptions import NotSupportedError
from ..lib import utils
from ..operations import commonops, swapops


class SwapController(AbstractBaseController):
    class Meta:
        label = 'swap'
        description = strings['swap.info']
        arguments = [
            (['environment_name'], dict(action='store', nargs='?',
                                        help=flag_text['swap.env'])),
            (['-n', '--destination_name'], dict(help=flag_text['swap.name'])),
        ]
        usage = AbstractBaseController.Meta.usage.replace('{cmd}', label)

    def do_command(self):
        app_name = self.get_app_name()
        source_env = self.get_env_name()
        destination_env = self.app.pargs.destination_name

        if not destination_env:
            # Ask interactively for an env to swap with
            envs = commonops.get_env_names(app_name)
            if len(envs) < 2:
                raise NotSupportedError(strings['swap.unsupported'])

            # Filter out current env
            envs = [e for e in envs if e != source_env]
            if len(envs) == 1:
                # Don't ask for env, just swap with only other environment
                destination_env = envs[0]
            else:
                # Ask for env to swap with
                io.echo()
                io.echo(prompts['swap.envprompt'])
                destination_env = utils.prompt_for_item_in_list(envs)

        swapops.cname_swap(source_env, destination_env)
