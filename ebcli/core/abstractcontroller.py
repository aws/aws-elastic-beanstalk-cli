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
import logging

from cement.core import controller
from cement.ext.ext_logging import LoggingLogHandler

from ebcli import __version__
from ..core import io, fileoperations, operations
from ..objects.exceptions import NoEnvironmentForBranchError
from ..resources.strings import strings, flag_text
from ..objects import region
from ..lib import aws


class AbstractBaseController(controller.CementBaseController):
    """
    This is an abstract base class that is useless on its own, but used
    by other classes to sub-class from and to share common commands and
    arguments.

    """
    class Meta:
        label = 'abstract'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['environment_name'], dict(action='store', nargs='?',
                                        default=[],
                                        help=flag_text['general.env'])),
        ]
        epilog = ''
        usage = 'eb {cmd} <environment_name> [options ...]'

    def do_command(self):
        pass

    @controller.expose(hide=True)
    def default(self):
        """
        This command will be shared within all controllers that sub-class
        from here.  It can also be overridden in the sub-class

        """
        if self.app.pargs.debug:
            io.echo('-- EBCLI Version:', __version__)
            io.echo('-- Python Version:', sys.version)

        if self.app.pargs.verbose:
            LoggingLogHandler.set_level(self.app.log, 'INFO')
        self.set_profile()
        self.do_command()

    def get_app_name(self):
        app_name = fileoperations.get_application_name()
        return app_name

    def get_env_name(self, cmd_example=None, noerror=False):
        env_name = self.app.pargs.environment_name
        if not env_name:
            #If env name not provided, grab branch default
            env_name = operations. \
                get_current_branch_environment()

        if not env_name:
            # No default env, lets ask for one
            if noerror:
                return None

            if not cmd_example:
                message = strings['branch.noenv'].replace('{cmd}',
                                                          self.Meta.label)
            else:
                message = strings['branch.noenv'].replace('eb {cmd}',
                                                          cmd_example)
            io.log_error(message)
            raise NoEnvironmentForBranchError()

        return env_name

    def get_region(self):
        region = self.app.pargs.region
        if not region:
            region = fileoperations.get_default_region()
        return region

    def set_profile(self):
        profile = self.app.pargs.profile
        if profile:
            aws.set_profile_override(profile)
        else:
            profile = fileoperations.get_default_profile()
            if profile:
                aws.set_profile(profile)

    def complete_command(self, commands):
        if not self.complete_region(commands):
            if len(commands) == 1:  # They only have the main command so far
                # lets complete for positional args
                region = fileoperations.get_default_region()
                app_name = fileoperations.get_application_name()
                io.echo(*operations.get_env_names(app_name, region))

    def complete_region(self, commands):
        # we only care about top command
        cmd = commands[-1]
        if cmd == '-r' or cmd == '--region':
            io.echo(*[r.name for r in region.get_all_regions()])
            return True
        return False