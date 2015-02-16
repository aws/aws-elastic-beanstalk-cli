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

from cement.core.controller import expose

from ..core.abstractcontroller import AbstractBaseController
from ..resources.strings import strings, flag_text
from ..core import io, operations, fileoperations
from ..commands import saved_configs
from ..objects.exceptions import InvalidSyntaxError, NotFoundError
from ..lib import utils


class ConfigController(AbstractBaseController):
    class Meta:
        label = 'config'
        description = strings['config.info']
        usage = 'eb config < |save|get|put|list|delete> <name> [options ...]'
        arguments = [
            (['name'], dict(action='store', nargs='?',
                            default=[],
                            help='environment_name|template_name')),
            (['-nh', '--nohang'], dict(action='store_true',
                                       help=flag_text['config.nohang'])),
            (['--timeout'], dict(type=int, help=flag_text['general.timeout'])),
            (['--cfg'], dict(help='name of configuration'))
        ]
        epilog = strings['config.epilog']

    def do_command(self):
        region = self.get_region()
        env_name = self.get_env_name(varname='name')
        app_name = self.get_app_name()
        timeout = self.app.pargs.timeout
        nohang = self.app.pargs.nohang
        cfg = self.app.pargs.cfg

        # input_exists = False
        input_exists = not sys.stdin.isatty()
        if not cfg and not input_exists:
            # No input, run interactive editor
            operations.update_environment_configuration(app_name, env_name,
                                                        region, nohang,
                                                        timeout=timeout)
            return

        if cfg:
            cfg_name = saved_configs.resolve_config_name(app_name, cfg, region)
            saved_configs.update_environment_with_config_file(env_name,
                                                              cfg_name,
                                                              region, nohang,
                                                              timeout=timeout)
        elif input_exists:
            data = sys.stdin.read()
            saved_configs.update_environment_with_config_data(env_name, data,
                                                              region, nohang,
                                                              timeout=timeout)

    @expose(help='Save a configuration of the environment.')
    def save(self):
        cfg_name = self.app.pargs.cfg
        env_name = self.get_env_name(varname='name',
                                     cmd_example='eb config save')
        app_name = self.get_app_name()
        region = self.get_region()

        if not cfg_name:
            cfg_name = self._choose_cfg_name(app_name, env_name, region)

        saved_configs.create_config(app_name, env_name, cfg_name, region)

    @expose(help='Upload a configuration to S3.')
    def put(self):
        app_name = self.get_app_name()
        region = self.get_region()
        name = self._get_cfg_name('put')
        platform = fileoperations.get_default_solution_stack()
        platform = operations.get_solution_stack(platform, region)
        platform = platform.name

        saved_configs.update_config(app_name, name, region)
        saved_configs.validate_config_file(app_name, name, platform, region)

    @expose(help='Download a configuration from S3.')
    def get(self):
        app_name = self.get_app_name()
        region = self.get_region()
        name = self._get_cfg_name('get')

        try:
            saved_configs.download_config_from_s3(app_name, name, region)
        except NotFoundError:
            io.log_error(strings['config.notfound'].replace('{config-name}',
                                                            name))

    @expose(help='Delete a configuration.')
    def delete(self):
        name = self._get_cfg_name('delete')
        app_name = self.get_app_name()
        region = self.get_region()

        saved_configs.delete_config(app_name, name, region)

    @expose(help='List all configurations.')
    def list(self):
        app_name = self.get_app_name()
        region = self.get_region()

        for c in saved_configs.get_configurations(app_name, region):
            io.echo(c)

    def _get_cfg_name(self, cmd):
        name = self.app.pargs.name
        if not name:
            io.echo('usage: eb config', cmd, '[configuration_name]')
            raise InvalidSyntaxError('too few arguments')
        else:
            return name

    @staticmethod
    def _choose_cfg_name(app_name, env_name, region):
        configs = saved_configs.get_configurations(app_name, region)
        io.echo()
        io.echo('Enter desired name of configuration.')
        default = utils.get_unique_name(env_name + '-sc', configs)
        cfg_name = io.prompt_for_unique_name(default, configs)
        return cfg_name
