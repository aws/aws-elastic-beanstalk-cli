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

from cement.core import controller
from cement.utils.misc import init_defaults
from cement.ext.ext_logging import LoggingLogHandler

from ebcli.core import io, fileoperations, operations
from ebcli.objects.exceptions import NoEnvironmentForBranchError
from ebcli.resources.strings import strings


class AbstractBaseController(controller.CementBaseController):
    """
    This is an abstract base class that is useless on its own, but used
    by other classes to sub-class from and to share common commands and
    arguments.

    """
    class Meta:
        label = 'test'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['environment_name'], dict(action='store', nargs='?',
                                        default=[],
                                        help='Environment name')),
            (['-r', '--region'], dict(help='Region where environment lives')),
        ]
        epilog = ''
        usage = 'eb {cmd} <environment_name> [options ...]'

    def _setup(self, base_app):
        self.Meta.usage = 'eb ' + self.Meta.label + ' {stuff}'
        super(AbstractBaseController, self)._setup(base_app)
        self.my_shared_obj = dict()

    def do_command(self):
        pass

    @controller.expose(hide=True)
    def default(self):
        """
        This command will be shared within all controllers that sub-class
        from here.  It can also be overridden in the sub-class

        """
        if self.app.pargs.verbose:
            LoggingLogHandler.set_level(self.app.log, 'INFO')
        io.log_info("Verbose Mode On")
        self.do_command()

    def get_app_name(self):
        app_name = fileoperations.get_application_name()
        return app_name

    def get_env_name(self, cmd_example=None):
        env_name = self.app.pargs.environment_name
        if not env_name:
            #If env name not provided, grab branch default
            env_name = operations. \
                get_setting_from_current_branch('environment')

        if not env_name:
            # No default env, lets ask for one
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
