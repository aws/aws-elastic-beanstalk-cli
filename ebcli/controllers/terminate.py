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
from ..resources.strings import strings, prompts, flag_text
from ..core import io
from ..objects.exceptions import NotFoundError, NoEnvironmentForBranchError
from ..operations import commonops, terminateops


class TerminateController(AbstractBaseController):
    class Meta:
        label = 'terminate'
        description = strings['terminate.info']
        arguments = AbstractBaseController.Meta.arguments + [
            (['--force'], dict(action='store_true',
                               help=flag_text['terminate.force'])),
            (['--ignore-links'], dict(action='store_true',
                                      help=flag_text['terminate.ignorelinks'])),
            (['--all'], dict(action='store_true',
                             help=flag_text['terminate.all'])),
            (['-nh', '--nohang'], dict(action='store_true',
                                       help=flag_text['terminate.nohang'])),
            (['--timeout'], dict(type=int, help=flag_text['general.timeout'])),
        ]
        usage = AbstractBaseController.Meta.usage.replace('{cmd}', label)
        epilog = strings['terminate.epilog']

    def do_command(self):
        app_name = self.get_app_name()
        force = self.app.pargs.force
        all = self.app.pargs.all
        ignore_links = self.app.pargs.ignore_links
        timeout = self.app.pargs.timeout
        nohang = self.app.pargs.nohang

        if all:
            cleanup = False if self.app.pargs.region else True
            terminateops.delete_app(app_name, force, nohang=nohang,
                                    cleanup=cleanup, timeout=timeout)

        else:
            try:
                env_name = self.get_env_name()
            except NoEnvironmentForBranchError as e:
                io.echo(strings['terminate.noenv'])
                raise e

            if not force:
                # make sure env exists
                env_names = commonops.get_env_names(app_name)
                if env_name not in env_names:
                    raise NotFoundError('Environment ' +
                                        env_name + ' not found')
                io.echo(prompts['terminate.confirm'].replace('{env-name}',
                                                             env_name))
                io.validate_action(prompts['terminate.validate'], env_name)

            if ignore_links:
                terminateops.terminate(env_name, ignore_links, nohang=nohang,
                                       timeout=timeout)
            else:
                terminateops.terminate(env_name, nohang=nohang,
                                       timeout=timeout)