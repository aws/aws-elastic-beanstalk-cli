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

from cement.core import foundation, controller, handler
from ebcli.core.outputHandler import OutputHandler

from ebcli.controllers.initialize import InitController
from ebcli.controllers.branch import BranchController
from ebcli.controllers.delete import DeleteController
from ebcli.controllers.events import EventsController
from ebcli.controllers.importation import ImportController
from ebcli.controllers.logs import LogsController
from ebcli.controllers.push import PushController
from ebcli.controllers.start import StartController
from ebcli.controllers.status import StatusController
from ebcli.controllers.stop import StopController
from ebcli.controllers.update import UpdateController


class EbBaseController(controller.CementBaseController):
    """
    This is the application base controller.
    It handles eb when no sub-commands are given
    """
    class Meta:
        label = 'base'
        description = 'Welcome to EB. Please see below for a list of available commands.'

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()


class EB(foundation.CementApp):
    class Meta:
        label = 'eb'
        base_controller = EbBaseController
        output_handler = OutputHandler

    def print_to_console(self, data):
        self.output.print_to_console(data)


def main():
    app = EB()

    try:
        # register non-base controller handlers
        handler.register(InitController)
        handler.register(BranchController)
        handler.register(DeleteController)
        handler.register(EventsController)
        handler.register(ImportController)
        handler.register(LogsController)
        handler.register(PushController)
        handler.register(StartController)
        handler.register(StatusController)
        handler.register(StopController)
        handler.register(UpdateController)

        app.setup()
        app.run()

    finally:
        app.close()