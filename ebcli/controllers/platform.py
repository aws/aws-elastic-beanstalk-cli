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

import os

from ..core import fileoperations, io
from ..core.abstractcontroller import AbstractBaseController
from ..operations import commonops, platformops
from ..resources.strings import strings, prompts


class PlatformController(AbstractBaseController):
    class Meta:
        label = 'platform'
        description = strings['platform.info']
        usage = 'eb platform <list|select|show> [options...]'
        arguments = []

    def do_command(self):
        self.app.args.print_help()

    @classmethod
    def _add_to_handler(cls, handler):
        handler.register(cls)
        # Register child controllers
        handler.register(PlatformShowController)
        handler.register(PlatformListController)
        handler.register(PlatformSelectController)

    def complete_command(self, commands):
        # We only care about regions
        if len(commands) == 1:
            # They only have the main command so far
            # lets complete for next level command
            io.echo(*['list', 'select', 'show'])
        elif len(commands) > 1:
            # TODO pass to next level controller
            pass


class PlatformShowController(AbstractBaseController):
    class Meta:
        label = 'platform show'
        aliases = ['show']
        aliases_only = True
        stacked_on = 'platform'
        stacked_type = 'nested'
        description = strings['platformshow.info']
        usage = AbstractBaseController.Meta.usage.format(cmd='platform show')

    def do_command(self):
        app_name = self.get_app_name()
        env_name = self.get_env_name(noerror=True)
        config_platform = commonops.get_default_solution_stack()
        full_platform = commonops.get_solution_stack(config_platform)

        io.echo('Current default platform:', config_platform)
        if config_platform.lower() == full_platform.name.lower():
            latest = commonops.get_latest_solution_stack(full_platform.version)
            io.echo('Most recent platform:    ', latest.name)
        else:
            io.echo('New environments will be running: ', full_platform)

        if env_name:
            platform = platformops.get_environment_platform(app_name, env_name)
            latest = commonops.get_latest_solution_stack(platform.version)
            io.echo()
            io.echo('Platform info for environment "{env_name}":'
                    .format(env_name=env_name))
            io.echo('Current:', platform)
            io.echo('Latest: ', latest)

            if latest != platform:
                io.echo(prompts['platformsshow.upgrade'])


class PlatformListController(AbstractBaseController):
    class Meta:
        label = 'platform list'
        aliases = ['list']
        aliases_only = True
        stacked_on = 'platform'
        stacked_type = 'nested'
        description = strings['platformlist.info']
        usage = 'eb platform list [options...]'
        arguments = []
        epilog = strings['platformlist.epilog']

    def do_command(self):
        verbose = self.app.pargs.verbose
        solution_stacks = platformops.get_all_platforms()
        if verbose:
            lst = [s.name for s in solution_stacks]
        else:
            lst = sorted(set([s.pythonify() for s in solution_stacks]))
        if len(lst) > 20:
            io.echo_with_pager(os.linesep.join(lst))
        else:
            io.echo(*lst, sep=os.linesep)


class PlatformSelectController(AbstractBaseController):
    class Meta:
        label = 'platform select'
        aliases = ['select']
        aliases_only = True
        stacked_on = 'platform'
        stacked_type = 'nested'
        description = strings['platformselect.info']
        usage = 'eb platform select [options...]'
        arguments = []
        epilog = strings['platformselect.epilog']

    def do_command(self):
        app_name = self.get_app_name()
        platform = commonops.prompt_for_solution_stack()
        fileoperations.write_config_setting('global', 'default_platform',
                                            platform.version)