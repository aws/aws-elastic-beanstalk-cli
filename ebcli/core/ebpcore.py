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

import ebcli.core.ebrun as ebrun

from ebcli.controllers.platform import EBPCreateController, \
    EBPEventsController, EBPListController, \
    EBPStatusController, EBPUseController, EBPDeleteController, \
    EBPInitController, EBPLogsController
from ebcli.core import fileoperations
from ebcli.core.ebglobals import Constants

import logging
from argparse import SUPPRESS

from cement.core import foundation, handler, hook
from cement.utils.misc import init_defaults
from cement.core.exc import CaughtSignal
import botocore
from botocore.compat import six
iteritems = six.iteritems

from . import ebglobals, base, io, hooks
from ..core.completer import CompleterController
from ..objects.exceptions import *
from ..resources.strings import flag_text, strings


class EBP(foundation.CementApp):
    class Meta:
        label = 'ebp'
        base_controller = base.EbBaseController
        defaults = init_defaults('ebp', 'log.logging')
        defaults['log.logging']['level'] = 'WARN'
        config_defaults = defaults
        base_controller.Meta.description = strings['ebpbase.info']
        base_controller.Meta.epilog = strings['ebpbase.epilog']

    def setup(self):
        ebglobals.app = self

        # Add hooks
        hook.register('post_argument_parsing', hooks.pre_run_hook)

        platform_controllers = [
            EBPEventsController,
            EBPListController,
            EBPStatusController,
            EBPUseController,
            EBPCreateController,
            EBPDeleteController,
            EBPLogsController,
        ]

        workspace_type = fileoperations.get_workspace_type(None)

        # Only load this if the the directory has not ben intialized or if it is a platform workspace
        if not fileoperations.get_workspace_type(None) or Constants.WorkSpaceTypes.PLATFORM == workspace_type:
            EBPInitController._add_to_handler(handler)

        if Constants.WorkSpaceTypes.APPLICATION == workspace_type:
            raise ApplicationWorkspaceNotSupportedError(strings['exit.applicationworkspacenotsupported'])
            # raise RuntimeError("Foo")
        elif Constants.WorkSpaceTypes.PLATFORM == workspace_type:
            for c in platform_controllers:
                c._add_to_handler(handler)
                pass

        # Add special controllers
        handler.register(CompleterController)

        super(EBP, self).setup()

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


def main():
    app = EBP()
    ebrun.run_app(app)
