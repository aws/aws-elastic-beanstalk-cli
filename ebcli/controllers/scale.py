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

from ..core.abstractcontroller import AbstractBaseController
from ..resources.strings import strings, flag_text
from ..core import fileoperations, io
from ..lib import elasticbeanstalk
from ..operations import scaleops, commonops


class ScaleController(AbstractBaseController):
    class Meta:
        label = 'scale'
        description = strings['scale.info']
        arguments = [
            (['number'], dict(
                action='store', type=int, help=flag_text['scale.number'])),
            (['-f', '--force'], dict(
                action='store_true', help=flag_text['scale.force'])),
            (['--timeout'], dict(type=int, help=flag_text['general.timeout'])),
        ] + AbstractBaseController.Meta.arguments
        usage = 'eb scale {number} <environment_name> [options ...]'

    def do_command(self):
        app_name = self.get_app_name()
        number = self.app.pargs.number
        timeout = self.app.pargs.timeout
        env_name = self.get_env_name(cmd_example='scale ' + str(number))
        confirm = self.app.pargs.force

        scaleops.scale(app_name, env_name, number, confirm,
                         timeout=timeout)

    def complete_command(self, commands):
        if not self.complete_region(commands):
            # Environment names are the second positional argument in this
            ## controller, so we only complete if its the second
            if len(commands) == 2 and not commands[-1].startswith('-'):
                app_name = fileoperations.get_application_name()
                io.echo(*elasticbeanstalk.get_environment_names(app_name))