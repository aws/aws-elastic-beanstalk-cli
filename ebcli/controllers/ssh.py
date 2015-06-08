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
from ..core import fileoperations, io
from ..lib import utils
from ..objects.exceptions import NoKeypairError, InvalidOptionsError
from ..operations import commonops, sshops


class SSHController(AbstractBaseController):
    class Meta:
        label = 'ssh'
        description = strings['ssh.info']
        usage = AbstractBaseController.Meta.usage.replace('{cmd}', label)
        arguments = AbstractBaseController.Meta.arguments + [
            (['-n', '--number'], dict(help=flag_text['ssh.number'], type=int)),
            (['-i', '--instance'], dict(help=flag_text['ssh.instance'])),
            (['-o', '--keep_open'], dict(
                action='store_true', help=flag_text['ssh.keepopen'])),
            (['--force'], dict(
                action='store_true', help=flag_text['ssh.force'])),
            (['--setup'], dict(
                action='store_true', help=flag_text['ssh.setup']))
        ]

    def do_command(self):
        app_name = self.get_app_name()
        number = self.app.pargs.number
        env_name = self.get_env_name()
        instance = self.app.pargs.instance
        keep_open = self.app.pargs.keep_open
        force = self.app.pargs.force
        setup = self.app.pargs.setup

        if setup:
            self.setup_ssh(env_name)
            return

        if instance and number:
            raise InvalidOptionsError(strings['ssh.instanceandnumber'])

        if not instance:
            instances = commonops.get_instance_ids(app_name, env_name)
            if number is not None:
                if number > len(instances) or number < 1:
                    raise InvalidOptionsError(
                        'Invalid index number (' + str(number) +
                        ') for environment with ' + str(len(instances)) +
                        ' instances')
                else:
                    instance = instances[number - 1]

            elif len(instances) == 1:
                instance = instances[0]
            else:
                io.echo()
                io.echo('Select an instance to ssh into')
                instance = utils.prompt_for_item_in_list(instances)

        try:
            sshops.ssh_into_instance(instance, keep_open=keep_open,
                                     force_open=force)
        except NoKeypairError:
            io.log_error(prompts['ssh.nokey'])

    def setup_ssh(self, env_name):
        # Instance does not have a keypair
        io.log_warning(prompts['ssh.setupwarn'].replace('{env-name}',
                                                        env_name))
        keyname = sshops.prompt_for_ec2_keyname(env_name=env_name)
        if keyname:
            options = [
                {'Namespace': 'aws:autoscaling:launchconfiguration',
                 'OptionName': 'EC2KeyName',
                 'Value': keyname}
            ]
            commonops.update_environment(env_name, options, False)

    def complete_command(self, commands):
        if not self.complete_region(commands):
            # Environment names are the second positional argument in this
            ## controller, so we only complete if its the second
            if len(commands) == 2 and commands[-1].startswith('-'):
                app_name = fileoperations.get_application_name()
                io.echo(commonops.get_env_names(app_name))