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

from ..core import io
from ..core.abstractcontroller import AbstractBaseController
from ..docker import container_factory as factory
from ..docker import log, compat
from ..docker.container_viewmodel import ContainerViewModel
from ..operations import localops
from ..resources.strings import strings, flag_text


class LocalController(AbstractBaseController):
    class Meta:
        label = 'local'
        description = strings['local.info']
        usage = 'eb local (sub-commands ...) [options ...]'
        arguments = []

    def do_command(self):
        self.app.args.print_help()


    @classmethod
    def _add_to_handler(cls, handler):
        handler.register(cls)
        # Register child controllers
        handler.register(LocalLogsController)
        handler.register(LocalRunController)
        handler.register(LocalOpenController)
        handler.register(LocalStatusController)


    def complete_command(self, commands):
        if len(commands) == 1:
            io.echo('logs', 'open', 'run', 'status')



class LocalRunController(AbstractBaseController):
    class Meta:
        label = 'local_run'
        description = strings['local.run.info']
        aliases = ['run']
        aliases_only = True
        stacked_on = 'local'
        stacked_type = 'nested'
        usage = 'eb local run [options ...]'
        arguments = [(['--envvars'], dict(help=flag_text['local.run.envvars'])),
                     (['--port'],
                         dict(type=int, help=flag_text['local.run.hostport']))]

    def do_command(self):
        compat.setup()
        cnt = factory.make_container(self.app.pargs.envvars,
                                     self.app.pargs.port)
        cnt.validate()
        cnt.start()


class LocalLogsController(AbstractBaseController):
    class Meta:
        # Workaround since labels must be unique and 'logs' is already taken
        label = 'local_logs'
        description = strings['local.logs.info']
        aliases = ['logs']
        aliases_only = True
        stacked_on = 'local'
        stacked_type = 'nested'
        usage = 'eb local logs [options ...]'
        arguments = []

    def do_command(self):
        log.print_logs()


class LocalOpenController(AbstractBaseController):
    class Meta:
        label = 'local_open'
        description = strings['local.open.info']
        aliases = ['open']
        aliases_only = True
        stacked_on = 'local'
        stacked_type = 'nested'
        usage = 'eb local open [options ...]'
        arguments = []

    def do_command(self):
        compat.setup()
        cnt = factory.make_container()
        cnt_viewmodel = ContainerViewModel.from_container(cnt)
        localops.open_webpage(cnt_viewmodel)


class LocalStatusController(AbstractBaseController):
    class Meta:
        label = 'local_status'
        description = strings['local.status.info']
        aliases = ['status']
        aliases_only = True
        stacked_on = 'local'
        stacked_type = 'nested'
        usage = 'eb local status [options ...]'
        arguments = []

    def do_command(self):
        compat.setup()
        cnt = factory.make_container()
        cnt_viewmodel = ContainerViewModel.from_container(cnt)
        localops.print_container_details(cnt_viewmodel)
