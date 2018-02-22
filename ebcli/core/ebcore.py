#!/usr/bin/env python
# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import ebcli.core.ebrun as ebrun

# Add vendor directory to module search path
# Need this for docker-compose
from ebcli.core import fileoperations
from ebcli.core.ebglobals import Constants

import logging
from argparse import SUPPRESS, ArgumentTypeError

from cement.core import foundation, handler, hook
from cement.utils.misc import init_defaults
from cement.core.exc import CaughtSignal
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
from ..controllers.local import LocalController
from ..objects.exceptions import *
from ..resources.strings import strings, flag_text
from ..labs.controller import LabsController
from ..controllers.codesource import CodeSourceController
from ..controllers.restore import RestoreController
from ..controllers.appversion import AppVersionController
from ..controllers.lifecycle import LifecycleController
from ..controllers.tags import TagsController


class EB(foundation.CementApp):
    class Meta:
        label = 'eb'
        base_controller = base.EbBaseController
        defaults = init_defaults('eb', 'log.logging')
        defaults['log.logging']['level'] = 'WARN'
        config_defaults = defaults
        exit_on_close = True

    def setup(self):
        ebglobals.app = self

        # Add hooks
        hook.register('post_argument_parsing', hooks.pre_run_hook)

        environment_controllers = [
            InitController,
            PlatformController,
            LogsController,
            SSHController,
            ConfigController,
            CreateController,
            EventsController,
            PrintEnvController,
            StatusController,
            TerminateController,
            DeployController,
            SwapController,
            OpenController,
            ConsoleController,
            ScaleController,
            UseController,
            SetEnvController,
            ListController,
            CloneController,
            UpgradeController,
            AbortController,
            LabsController,
            LocalController,
            HealthController,
            CodeSourceController,
            RestoreController,
            AppVersionController,
            LifecycleController,
            TagsController,
        ]

        # eb <foo> commands supported in platform workspaces
        platform_controllers = [
            ConfigController,
            ConsoleController,
            EventsController,
            ListController,
            LogsController,
            HealthController,
            SSHController,
            StatusController,
            TerminateController,
            PlatformController,
            UpgradeController,
        ]

        if "--modules" in self.argv:
            for c in environment_controllers:
                c._add_to_handler(handler)

        else:
            workspace_type = fileoperations.get_workspace_type(Constants.WorkSpaceTypes.APPLICATION)

            if Constants.WorkSpaceTypes.APPLICATION == workspace_type:
                for c in environment_controllers:
                    c._add_to_handler(handler)
            elif Constants.WorkSpaceTypes.PLATFORM == workspace_type:
                for c in platform_controllers:
                    c._add_to_handler(handler)

        # Add special controllers
        handler.register(CompleterController)

        super(EB, self).setup()

        # Register global arguments
        self.add_arg('-v', '--verbose',
                     action='store_true', help=flag_text['base.verbose'])
        self.add_arg('--profile', help=flag_text['base.profile'])
        self.add_arg('-r', '--region', help=flag_text['base.region'])
        self.add_arg('--endpoint-url', help=SUPPRESS)
        self.add_arg('--no-verify-ssl',
                     action='store_true', help=flag_text['base.noverify'])
        self.add_arg('--debugboto',  # show debug info for botocore
                     action='store_true', help=SUPPRESS)


def main():
    app = EB()
    ebrun.run_app(app)
