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

import ebcli
from cement.core import foundation, controller, handler
from cement.utils.misc import init_defaults
from ebcli.core.outputhandler import OutputHandler
from ebcli.controllers.initialize import InitController
from ebcli.controllers.create import CreateController
from ebcli.controllers.delete import DeleteController
from ebcli.controllers.events import EventsController
from ebcli.controllers.importation import ImportController
from ebcli.controllers.logs import LogsController
from ebcli.controllers.deploy import DeployController
from ebcli.controllers.status import StatusController
from ebcli.controllers.terminate import TerminateController
from ebcli.controllers.update import UpdateController
from ebcli.controllers.config import ConfigController
from ebcli.resources.strings import strings
from ebcli.core import globals


class EbBaseController(controller.CementBaseController):
    """
    This is the application base controller.
    It handles eb when no sub-commands are given
    """
    class Meta:
        label = 'base'
        description = strings['base.info']
        arguments = [
            (['-v', '--version'], dict(action='store_true',
                                       help='show application/version info')),
        ]

    @controller.expose(hide=True)
    def default(self):
        if self.app.pargs.version:
            self.app.print_to_console(strings['app.version_message'],
                                      ebcli.__version__)
        else:
            self.app.args.print_help()


class EB(foundation.CementApp):
    class Meta:
        label = 'eb'
        base_controller = EbBaseController
        output_handler = OutputHandler
        defaults = init_defaults('eb', 'log')
        defaults['log']['level'] = 'WARN'
        config_defaults = defaults

    def print_to_console(self, *data):
        self.output.print_to_console(*data)

    @staticmethod
    def get_input(output):
        try:
            input = raw_input
        except NameError:
            pass
        return input(output + ': ')

    @staticmethod
    def prompt(output):
        return EB.get_input('(' + output + ')')


defaults = init_defaults('ebapp', 'log')
defaults['log']['level'] = 'WARN'


def main():
    globals.app = EB()

    try:
        # register all controllers
        handler.register(InitController)
        handler.register(CreateController)
        handler.register(DeleteController)
        handler.register(EventsController)
        handler.register(ImportController)
        handler.register(LogsController)
        handler.register(DeployController)
        handler.register(StatusController)
        handler.register(TerminateController)
        handler.register(UpdateController)
        handler.register(ConfigController)

        globals.app.setup()
        globals.app.run()

    finally:
        globals.app.close()