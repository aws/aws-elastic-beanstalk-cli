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

from ..core.abstractcontroller import AbstractBaseController
from ..resources.strings import strings
from ..core import io
from .quicklink import QuicklinkController
from .download import DownloadController
from .convertdockerrun import ConvertDockerrunController


class LabsController(AbstractBaseController):
    class Meta:
        label = 'labs'
        description = strings['labs.info']
        usage = AbstractBaseController.Meta.usage.\
            replace('{cmd}', 'labs <download|quicklink|convert-dockerrun>')
        arguments = []

    def do_command(self):
        self.app.args.print_help()

    def complete_command(self, commands):
        # We only care about regions
        if len(commands) == 1:
            # They only have the main command so far
            # lets complete for next level command
            io.echo(*['quicklink', 'download', 'convert-dockerrun'])
        elif len(commands) > 1:
            # TODO pass to next level controller
            pass

    @classmethod
    def _add_to_handler(cls, handler):
        handler.register(cls)
        # Register child controllers
        handler.register(QuicklinkController)
        handler.register(DownloadController)
        handler.register(ConvertDockerrunController)
