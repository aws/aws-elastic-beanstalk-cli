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

import os
import sys

# Add vendor directory to module search path
# Need this for docker-compose
def fix_path():
    parent_folder = os.path.dirname(__file__)
    parent_dir = os.path.abspath(parent_folder)
    while not parent_folder.endswith('ebcli'):
        # Keep going up until we get to the right folder
        parent_folder = os.path.dirname(parent_folder)
        parent_dir = os.path.abspath(parent_folder)

    vendor_dir = os.path.join(parent_dir, 'bundled')

    sys.path.insert(0, vendor_dir)
fix_path()

import logging
from argparse import SUPPRESS, ArgumentTypeError

from cement.core import foundation, handler, hook
from cement.utils.misc import init_defaults
from cement.core.exc import CaughtSignal
import botocore
from botocore.compat import six
iteritems = six.iteritems

from . import ebglobals, base, io, hooks
from ..controllers.initialize import InitController
from ..controllers.abort import AbortController
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
from ..controllers.swap import SwapController
from ..controllers.platform import PlatformController
from ..controllers.health import HealthController
from ..controllers.upgrade import UpgradeController
from ..core.completer import CompleterController
from ..controllers.local import LocalController, LocalRunController,\
        LocalLogsController, LocalOpenController, LocalStatusController
from ..objects.exceptions import *
from ..resources.strings import strings, flag_text
from ..labs.controller import LabsController
from ..controllers.codesource import CodeSourceController

class EB(foundation.CementApp):
    class Meta:
        label = 'eb'
        base_controller = base.EbBaseController
        defaults = init_defaults('eb', 'log.logging')
        defaults['log.logging']['level'] = 'WARN'
        config_defaults = defaults

    def setup(self):
        # Add hooks
        hook.register('post_argument_parsing', hooks.pre_run_hook)

        # Add controllers
        controllers = [
            InitController,
            CreateController,
            EventsController,
            LogsController,
            PrintEnvController,
            DeployController,
            StatusController,
            TerminateController,
            ConfigController,
            SwapController,
            OpenController,
            ConsoleController,
            ScaleController,
            SSHController,
            UseController,
            SetEnvController,
            ListController,
            PlatformController,
            CloneController,
            UpgradeController,
            AbortController,
            LabsController,
            LocalController,
            HealthController,
            CodeSourceController,
        ]

        # register all controllers
        for c in controllers:
            c._add_to_handler(handler)

        # Add special controllers
        handler.register(CompleterController)

        super(EB, self).setup()

        #Register global arguments
        self.add_arg('-v', '--verbose',
                     action='store_true', help=flag_text['base.verbose'])
        self.add_arg('--profile', help=flag_text['base.profile'])
        self.add_arg('-r', '--region', help=flag_text['base.region'])
        self.add_arg('--endpoint-url', help=SUPPRESS)
        self.add_arg('--no-verify-ssl',
                     action='store_true', help=flag_text['base.noverify'])
        self.add_arg('--debugboto',  # show debug info for botocore
                     action='store_true', help=SUPPRESS)

        ebglobals.app = self


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
    except ArgumentTypeError:
        io.log_error(strings['exit.argerror'])
        app.close(code=4)
    except EBCLIException as e:
        if app.pargs is None or not app.pargs.debug:
            raise

        message = next(io._convert_to_strings([e]))

        if app.pargs.verbose:
            io.log_error(e.__class__.__name__ + " - " + message)
        else:
            io.log_error(message)
        app.close(code=4)
    except Exception as e:
        # Generic catch all
        if app.pargs is None or not app.pargs.debug:
            raise

        message = next(io._convert_to_strings([e]))
        io.log_error(e.__class__.__name__ + " :: " + message)
        app.close(code=10)
    finally:
        app.close()
