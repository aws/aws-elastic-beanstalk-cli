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

from cement.utils.misc import minimal_logger

from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.resources.strings import strings, flag_text
from ebcli.operations import logsops
from ebcli.objects.exceptions import InvalidOptionsError, NotFoundError
from ebcli.core import io

LOG = minimal_logger(__name__)


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
            (['-g', '--log-group'], dict(help=flag_text['logs.instance'])),
            (['-cw', '--cloudwatch-logs'], dict(help=flag_text['logs.instance'], nargs='?',
                                                choices=['enable', 'disable'], type=str.lower, const='enable')),
            (['--stream'], dict(action='store_true',
                                help=flag_text['logs.stream'])),

        ]
        epilog = strings['logs.epilog']

    '''
        COMMAND LOGIC
    '''
    def do_command(self):
        self.env_name = self.get_env_name()
        self.app_name = self.get_app_name()
        self.log_group = self.app.pargs.log_group
        self.instance = self.app.pargs.instance
        self.all = self.app.pargs.all
        self.zip = self.app.pargs.zip

        # Enable or disable cloudwatch logs
        cloudwatch_logs_action = self.app.pargs.cloudwatch_logs
        if cloudwatch_logs_action is not None:
            self.modify_log_streaming(cloudwatch_logs_action)
            return

        # Workflow to stream the logs
        if self.app.pargs.stream:
            self.stream_cloudwatch_logs()
            return

        # This will get the logs to download or display in a pager
        self.get_logs()

    '''
        FLAG LOGIC
    '''
    def modify_log_streaming(self, cloudwatch_logs_action):
        """
            Either disables or enables native CloudWatch support for the current Beanstalk Environment.
            :param cloudwatch_logs_action: boolean
        """
        actions = ['enable', 'disable']
        enable = 0
        disable = 1
        log_streaming_enabled = logsops.log_streaming_enabled(self.app_name, self.env_name)
        if actions[enable] == cloudwatch_logs_action:
            if log_streaming_enabled:
                io.echo(strings['cloudwatch-logs.alreadyenabled'])
            else:
                logsops.enable_cloudwatch_logs(self.env_name)
        if actions[disable] == cloudwatch_logs_action:
            if not log_streaming_enabled:
                io.echo(strings['cloudwatch-logs.alreadydisabled'])
            else:
                logsops.disable_cloudwatch_logs(self.env_name)

    def stream_cloudwatch_logs(self):
        """
            Will stream cloudwatch logs from a specified log group, if there are multiple streams we will stream them
            all in different threads to the same terminal.
        """
        # If they have log streaming enabled use that stream
        if logsops.log_streaming_enabled(self.app_name, self.env_name):
            self.log_group = logsops.beanstalk_log_group_builder(self.env_name, self.log_group)
        logsops.stream_cloudwatch_logs(self.env_name, log_group=self.log_group, instance_id=self.instance)

    def get_logs(self):
        """
            Determines the type of logs to get and how to package them from the flags given to the command. The method
            will either zip or save the individual logs in '.elasticbeanstalk/logs/' directory OR return a pager that
            will allow the user to page through the tail logs.
        """
        if self.all and self.instance:
            raise InvalidOptionsError(strings['logs.allandinstance'])

        if self.zip:
            info_type = 'bundle'
            do_zip = True
        elif self.all:
            info_type = 'bundle'
            do_zip = False
        else:
            info_type = 'tail'
            do_zip = False

        if logsops.log_streaming_enabled(self.app_name, self.env_name):
            log_group = logsops.beanstalk_log_group_builder(self.env_name, self.log_group)
            try:
                logsops.retrieve_cloudwatch_logs(log_group, info_type, do_zip=do_zip, instance_id=self.instance)
            except NotFoundError:
                raise NotFoundError('The specified log group does not exist. "{0}"'.format(log_group))
        else:
            logsops.retrieve_beanstalk_logs(self.env_name, info_type, do_zip=do_zip, instance_id=self.instance)