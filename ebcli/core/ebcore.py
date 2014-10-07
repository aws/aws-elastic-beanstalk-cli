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
from ebcli.controllers.events import EventsController
from ebcli.controllers.logs import LogsController
from ebcli.controllers.deploy import DeployController
from ebcli.controllers.status import StatusController
from ebcli.controllers.terminate import TerminateController
from ebcli.controllers.update import UpdateController
from ebcli.controllers.open import OpenController
from ebcli.controllers.console import ConsoleController
from ebcli.controllers.scale import ScaleController
from ebcli.controllers.ssh import SSHController
from ebcli.controllers.setenv import SetEnvController
from ebcli.controllers.list import ListController
from ebcli.controllers.clone import CloneController
from ebcli.core.completer import CompleterController
from ebcli.core import globals, base, io
from ebcli.objects.exceptions import *
from ebcli.resources.strings import strings


class EB(foundation.CementApp):
    class Meta:
        label = 'eb'
        base_controller = base.EbBaseController
        defaults = init_defaults('eb', 'log.logging')
        defaults['log.logging']['level'] = 'WARN'
        config_defaults = defaults

    def setup(self):
        # register all controllers
        handler.register(InitController)
        handler.register(CreateController)
        handler.register(EventsController)
        handler.register(LogsController)
        handler.register(DeployController)
        handler.register(StatusController)
        handler.register(TerminateController)
        handler.register(UpdateController)
        handler.register(OpenController)
        handler.register(ConsoleController)
        handler.register(ScaleController)
        handler.register(SSHController)
        handler.register(SetEnvController)
        handler.register(ListController)
        # Clone not yet ready
        # handler.register(CloneController)
        handler.register(CompleterController)

        super(EB, self).setup()

        #Register global arguments
        self.add_arg('-v', '--verbose',
                     action='store_true', help='toggle verbose output')
        self.add_arg('--profile', help='Use a specific profile '
                                       'from your credential file')

        globals.app = self


def main():
    app = EB()

    try:
        app.setup()
        app.run()

    # Handle General Exceptions

    # ToDo: the safer way of closing would be
    # app.close(129) rather than app.close(129)
    # But this is not currently available in the current version of cement
    # A patch has been submitted and excepted
    # The fix needs to be changed once the next release of cement is out
    except CaughtSignal:
        io.echo()
        app.close(130)
    except NoEnvironmentForBranchError:
        pass
    except InvalidStateError:
        io.log_error(strings['exit.invalidstate'])
        app.close(1)
    except NotFoundError as e:
        io.log_error(e.message)
        app.close(1)
    except AlreadyExistsError as e:
        io.log_error(e.message)
        app.close(1)
    except NotInitializedError:
        io.log_error(strings['exit.notsetup'])
        app.close(126)
    except NoSourceControlError:
        io.log_error(strings['git.notfound'])
        app.close(1)
    except NoRegionError:
        io.log_error(strings['exit.noregion'])
        app.close(1)
    except EBCLIException as e:
        io.log_error(e.__class__.__name__ + ": " + e.message)
    finally:
        app.close()