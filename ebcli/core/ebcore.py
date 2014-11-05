#!/usr/bin/env python
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

import logging
from argparse import SUPPRESS

from cement.core import foundation, handler
from cement.utils.misc import init_defaults
from cement.core.exc import CaughtSignal
from six import iteritems

from ..controllers.initialize import InitController
from ..controllers.create import CreateController
from ..controllers.events import EventsController
from ..controllers.logs import LogsController
from ..controllers.deploy import DeployController
from ..controllers.status import StatusController
from ..controllers.terminate import TerminateController
from ..controllers.config import ConfigController
from ..controllers.open import OpenController
from ..controllers.console import ConsoleController
from ..controllers.use import UseController
from ..controllers.scale import ScaleController
from ..controllers.ssh import SSHController
from ..controllers.setenv import SetEnvController
from ..controllers.list import ListController
from ..controllers.printenv import PrintEnvController
from ..controllers.clone import CloneController
from ..core.completer import CompleterController
from ..core import globals, base, io
from ..objects.exceptions import *
from ..resources.strings import strings, flag_text


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
        handler.register(ConfigController)
        handler.register(OpenController)
        handler.register(ConsoleController)
        handler.register(ScaleController)
        handler.register(SSHController)
        handler.register(UseController)
        handler.register(SetEnvController)
        handler.register(PrintEnvController)
        handler.register(ListController)
        handler.register(CloneController)
        handler.register(CompleterController)

        super(EB, self).setup()

        #Register global arguments
        self.add_arg('-v', '--verbose',
                     action='store_true', help=flag_text['base.verbose'])
        self.add_arg('--profile', help=flag_text['base.profile'])
        self.add_arg('-r', '--region', help=flag_text['base.region'])
        self.add_arg('--endpoint-url', help=SUPPRESS)

        globals.app = self


def main():
    # Squash cement logging
    ######
    for d, k in iteritems(logging.Logger.manager.loggerDict):
        if d.startswith('cement') and isinstance(k, logging.Logger):
            k.setLevel('ERROR')
    #######

    app = EB()

    try:
        app.setup()
        app.run()

    # Handle General Exceptions
    except CaughtSignal:
        io.echo()
        app.close(code=5)
    except NoEnvironmentForBranchError:
        pass
    except InvalidStateError:
        io.log_error(strings['exit.invalidstate'])
        app.close(code=3)
    except NotInitializedError:
        io.log_error(strings['exit.notsetup'])
        app.close(code=126)
    except NoSourceControlError:
        io.log_error(strings['sc.notfound'])
        app.close(code=3)
    except NoRegionError:
        io.log_error(strings['exit.noregion'])
        app.close(code=3)
    except ConnectionError:
        io.log_error(strings['connection.error'])
        app.close(code=2)
    except EBCLIException as e:
        if app.pargs.debug:
            raise

        message = next(io._convert_to_strings([e]))

        if app.pargs.verbose:
            io.log_error(e.__class__.__name__ + " - " + message)
        else:
            io.log_error(message)
        app.close(code=4)
    except Exception as e:
        #Generic catch all
        if app.pargs.debug:
            raise

        message = next(io._convert_to_strings([e]))
        io.log_error(e.__class__.__name__ + " :: " + message)
        app.close(code=10)
    finally:
        app.close()