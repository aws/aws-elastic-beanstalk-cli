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

import sys

from cement.core import foundation, handler
from cement.utils.misc import init_defaults
from cement.core.exc import CaughtSignal

from ebcli.controllers.initialize import InitController
from ebcli.controllers.create import CreateController
from ebcli.controllers.delete import DeleteController
from ebcli.controllers.events import EventsController
from ebcli.controllers.logs import LogsController
from ebcli.controllers.deploy import DeployController
from ebcli.controllers.status import StatusController
from ebcli.controllers.terminate import TerminateController
from ebcli.controllers.update import UpdateController
from ebcli.controllers.pause import PauseController
from ebcli.controllers.config import ConfigController
from ebcli.controllers.sync import SyncController
from ebcli.core import globals, base, io
from ebcli.objects.exceptions import NotInitializedError, \
    NoSourceControlError, NoRegionError, EBCLIException
from ebcli.resources.strings import strings


class EB(foundation.CementApp):
    class Meta:
        label = 'eb'
        base_controller = base.EbBaseController
        defaults = init_defaults('eb', 'log')
        # ToDo: Verbose mode by default for development, uncomment below to fix
        # defaults['log']['level'] = 'WARN'
        config_defaults = defaults
        # argument_handler = ArgParseHandler
        # uncomment above if custom arg handler is needed

    def setup(self):
        # register all controllers
        handler.register(InitController)
        handler.register(CreateController)
        handler.register(DeleteController)
        handler.register(EventsController)
        handler.register(LogsController)
        handler.register(DeployController)
        handler.register(StatusController)
        handler.register(TerminateController)
        handler.register(UpdateController)
        handler.register(SyncController)
        handler.register(PauseController)
        # handler.register(ConfigController)  # Do we want this command?

        super(EB, self).setup()

        #Register global arguments
        self.add_arg('--verbose', action='store_true',
                         help='toggle verbose ouput')

        globals.app = self


def main():
    app = EB()

    try:
        app.setup()
        app.run()

    # Handle General Exceptions

    # ToDo: the safer way of closing would be
    # app.close(129) rather than sys.exit(129)
    # But this is not currently available in the current version of cement
    # A patch has been submitted and excepted
    # The fix needs to be changed once the next release of cement is out
    except CaughtSignal:
        io.echo()
        sys.exit(1)
    except NotInitializedError:
        io.log_error(strings['exit.notsetup'])
        sys.exit(128)
    except NoSourceControlError:
        io.log_error(strings['git.notfound'])
        sys.exit(129)
    except NoRegionError:
        io.log_error(strings['exit.noregion'])
        sys.exit(130)
    except EBCLIException as e:
        io.log_error(e.__class__.__name__ + ": " + e.message)
    finally:
        app.close()