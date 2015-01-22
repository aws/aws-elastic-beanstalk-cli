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
from ..resources.strings import strings, flag_text
from ..core import operations, fileoperations
from ..objects.exceptions import NoEnvironmentForBranchError, \
    InvalidOptionsError
from ..core import io


class DeployController(AbstractBaseController):
    class Meta(AbstractBaseController.Meta):
        label = 'deploy'
        description = strings['deploy.info']
        arguments = [
            (['environment_name'], dict(
                action='store', nargs='?', default=[],
                help=flag_text['deploy.env'])),
            (['--version'], dict(help=flag_text['deploy.version'])),
            (['-l', '--label'], dict(help=flag_text['deploy.label'])),
            (['-m', '--message'], dict(help=flag_text['deploy.message'])),
            (['-nh', '--nohang'], dict(
                action='store_true', help=flag_text['deploy.nohang'])),
            (['--timeout'], dict(type=int, help=flag_text['general.timeout'])),
            ]
        usage = AbstractBaseController.Meta.usage.replace('{cmd}', label)

    def do_command(self):
        app_name = self.get_app_name()
        region = self.get_region()
        env_name = self.app.pargs.environment_name
        version = self.app.pargs.version
        label = self.app.pargs.label
        timeout = self.app.pargs.timeout
        message = self.app.pargs.message

        if version and (message or label):
            raise InvalidOptionsError(strings['deploy.invalidoptions'])

        if not env_name:
            env_name = \
                operations.get_current_branch_environment()

        if not env_name:
            message = strings['branch.noenv'].replace('eb {cmd}',
                                                      self.Meta.label)
            io.log_error(message)
            raise NoEnvironmentForBranchError()

        # ToDo add support for deploying to multiples?
        # for arg in self.app.pargs.environment_name:
        #     # deploy to every environment listed
        #     ## Right now you can only list one

        operations.deploy(app_name, env_name, region, version, label, message,
                          timeout=timeout)

    def complete_command(self, commands):
        #ToDo, edit this if we ever support multiple env deploys
        super(DeployController, self).complete_command(commands)

        ## versionlabels on --version
        cmd = commands[-1]
        if cmd in ['--version']:
            region = fileoperations.get_default_region()
            app_name = fileoperations.get_application_name()
            io.echo(*operations.get_app_version_labels(app_name, region))