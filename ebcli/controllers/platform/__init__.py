# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import io

from ebcli.core import fileoperations
from ebcli.core.ebglobals import Constants

from ebcli.core.abstractcontroller import AbstractBaseController

from ebcli.controllers.platform.list import PlatformListController, PlatformWorkspaceListController, EBPListController
from ebcli.controllers.platform.use import PlatformSelectController, PlatformWorkspaceUseController, EBPUseController
from ebcli.controllers.platform.status import PlatformShowController, PlatformWorkspaceStatusController, EBPStatusController
from ebcli.controllers.platform.create import PlatformCreateController, EBPCreateController
from ebcli.controllers.platform.delete import PlatformDeleteController, EBPDeleteController
from ebcli.controllers.platform.events import PlatformEventsController, EBPEventsController
from ebcli.controllers.platform.initialize import PlatformInitController, EBPInitController
from ebcli.controllers.platform.logs import PlatformLogsController, EBPLogsController
from ebcli.controllers.platform.initialize import PlatformInitController, EBPInitController

from ebcli.resources.strings import strings
from ebcli.operations import commonops, platformops, initializeops, solution_stack_ops

class PlatformController(AbstractBaseController):
    class Meta:
        label = 'platform'
        description = strings['platform.info']
        usage = 'eb platform <command> [options...]'
        arguments = []

    def do_command(self):
        self.app.args.print_help()

    @classmethod
    def _add_to_handler(cls, handler):
        workspace_type = fileoperations.get_workspace_type(Constants.WorkSpaceTypes.APPLICATION)

        handler.register(cls)

        # Only load this if the the directory has not ben intialized or if it is a platform workspace
        if not fileoperations.get_workspace_type(None) or Constants.WorkSpaceTypes.PLATFORM == workspace_type:
            handler.register(PlatformInitController)

        # Environment specific sub commands
        if Constants.WorkSpaceTypes.APPLICATION == workspace_type:
            handler.register(PlatformListController)
            handler.register(PlatformShowController)
            handler.register(PlatformSelectController)
        # Platform specific controllers
        elif Constants.WorkSpaceTypes.PLATFORM == workspace_type:
            handler.register(PlatformWorkspaceListController)
            handler.register(PlatformWorkspaceStatusController)
            handler.register(PlatformWorkspaceUseController)
            handler.register(PlatformCreateController)
            handler.register(PlatformDeleteController)
            handler.register(PlatformEventsController)
            handler.register(PlatformLogsController)

    def complete_command(self, commands):
        workspace_type = fileoperations.get_workspace_type(Constants.WorkSpaceTypes.APPLICATION)

        # We only care about regions
        if len(commands) == 1:
            # They only have the main command so far
            # lets complete for next level command
            if Constants.WorkSpaceTypes.APPLICATION == workspace_type:
                io.echo(*['list', 'use', 'status'])
            elif Constants.WorkSpaceTypes.PLATFORM == workspace_type:
                io.echo(*['create', 'delete', 'events', 'init', 'list', 'status', 'use'])
        elif len(commands) > 1:
            pass
