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
from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.resources.strings import strings, prompts, flag_text
from ebcli.core import io
from ebcli.operations import terminateops


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
        force = self.app.pargs.force
        delete_application_and_resources = self.app.pargs.all
        ignore_links = self.app.pargs.ignore_links
        timeout = self.app.pargs.timeout
        nohang = self.app.pargs.nohang

        if delete_application_and_resources:
            app_name = self.get_app_name()
            cleanup = not self.app.pargs.region
            terminateops.delete_app(
                app_name,
                force,
                nohang=nohang,
                cleanup=cleanup,
                timeout=timeout
            )

        else:
            env_name = self.get_env_name()

            if not force:
                io.echo(prompts['terminate.confirm'].format(env_name=env_name))
                io.validate_action(prompts['terminate.validate'], env_name)

            terminateops.terminate(
                env_name,
                force_terminate=ignore_links,
                nohang=nohang,
                timeout=timeout
            )
