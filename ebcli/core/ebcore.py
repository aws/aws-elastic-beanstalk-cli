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


from cement.core import foundation, handler
from cement.utils.misc import init_defaults

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
from ebcli.core.arghandler import ArgParseHandler
from ebcli.core import globals, base


class EB(foundation.CementApp):
    class Meta:
        label = 'eb'
        base_controller = base.EbBaseController
        defaults = init_defaults('eb', 'log')
        defaults['log']['level'] = 'WARN'
        config_defaults = defaults
        # argument_handler = ArgParseHandler
        # uncomment above if custom arg handler is needed

    def setup(self):
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

        super(EB, self).setup()

        #Register global arguments
        self.add_arg('--verbose', action='store_true',
                         help='verbose text')



defaults = init_defaults('ebapp', 'log')
defaults['log']['level'] = 'WARN'


def main():
    globals.app = EB()

    try:
        globals.app.setup()
        globals.app.run()

    finally:
        globals.app.close()