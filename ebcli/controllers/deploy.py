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
from os import path, chdir, getcwd, listdir

from ..core.abstractcontroller import AbstractBaseController
from ..resources.strings import strings, flag_text
from ..core import fileoperations
from ..objects.exceptions import NoEnvironmentForBranchError, \
    InvalidOptionsError
from ..core import io, hooks
from ..operations import commonops, deployops, composeops


class DeployController(AbstractBaseController):
    class Meta(AbstractBaseController.Meta):
        label = 'deploy'
        description = strings['deploy.info']
        arguments = [
            (['environment_name'], dict(
                action='store', nargs='?', default=[],
                help=flag_text['deploy.env'])),
            (['--modules'], dict(help=flag_text['deploy.modules'], nargs='*')),
            (['-g', '--env-group-suffix'], dict(help=flag_text['deploy.group_suffix'])),
            (['--version'], dict(help=flag_text['deploy.version'])),
            (['-l', '--label'], dict(help=flag_text['deploy.label'])),
            (['-m', '--message'], dict(help=flag_text['deploy.message'])),
            (['-nh', '--nohang'], dict(
                action='store_true', help=flag_text['deploy.nohang'])),
            (['--staged'], dict(
                action='store_true', help=flag_text['deploy.staged'])),
            (['--timeout'], dict(type=int, help=flag_text['general.timeout'])),
            ]
        usage = AbstractBaseController.Meta.usage.replace('{cmd}', label)

    def do_command(self):
        self.message = self.app.pargs.message
        self.staged = self.app.pargs.staged
        self.timeout = self.app.pargs.timeout
        self.modules = self.app.pargs.modules

        if self.modules and len(self.modules) > 0:
            self.multiple_app_deploy()
            return

        self.app_name = self.get_app_name()
        self.env_name = self.app.pargs.environment_name
        self.version = self.app.pargs.version
        self.label = self.app.pargs.label
        group_name = self.app.pargs.env_group_suffix

        if self.version and (self.message or self.label):
            raise InvalidOptionsError(strings['deploy.invalidoptions'])

        if not self.env_name:
            self.env_name = \
                commonops.get_current_branch_environment()

        if not self.env_name:
            self.message = strings['branch.noenv'].replace('eb {cmd}',
                                                      self.Meta.label)
            io.log_error(self.message)
            raise NoEnvironmentForBranchError()

        # ToDo add support for deploying to multiples?
        # for arg in self.app.pargs.environment_name:
        #     # deploy to every environment listed
        #     ## Right now you can only list one

        process_app_versions = fileoperations.env_yaml_exists()

        deployops.deploy(self.app_name, self.env_name, self.version, self.label,
                         self.message, group_name=group_name, process_app_versions=process_app_versions,
                         staged=self.staged, timeout=self.timeout)

    def complete_command(self, commands):
        #ToDo, edit this if we ever support multiple env deploys
        super(DeployController, self).complete_command(commands)

        ## versionlabels on --version
        cmd = commands[-1]
        if cmd in ['--version']:
            app_name = fileoperations.get_application_name()
            io.echo(*commonops.get_app_version_labels(app_name))


    def multiple_app_deploy(self):
        missing_env_yaml = []
        top_dir = getcwd()

        for module in self.modules:
            if not path.isdir(path.join(top_dir, module)):
                continue

            chdir(path.join(top_dir, module))

            if not fileoperations.env_yaml_exists():
                missing_env_yaml.append(module)

            chdir(top_dir)

        # We currently do not want to support multiple deploys when some of the
        # modules do not contain env.yaml files
        if len(missing_env_yaml) > 0:
            module_list = ''
            for module_name in missing_env_yaml:
                module_list = module_list + module_name + ', '
            io.echo(strings['deploy.modulemissingenvyaml'].replace('{modules}',
                                                                   module_list[:-2]))
            return

        self.compose_deploy()
        return

    def compose_deploy(self):
        app_name = None
        modules = self.app.pargs.modules
        group_name = self.app.pargs.env_group_suffix

        env_names = []
        stages_version_labels = {}
        stages_env_names = {}

        top_dir = getcwd()
        for module in modules:
            if not path.isdir(path.join(top_dir, module)):
                io.log_error(strings['deploy.notadirectory'].replace('{module}', module))
                continue

            chdir(path.join(top_dir, module))

            if not group_name:
                group_name = commonops.get_current_branch_group_suffix()
            if group_name not in stages_version_labels.keys():
                stages_version_labels[group_name] = []
                stages_env_names[group_name] = []

            if not app_name:
                app_name = self.get_app_name()

            io.echo('--- Creating application version for module: {0} ---'.format(module))

            # Re-run hooks to get values from .elasticbeanstalk folders of apps
            hooks.set_region(None)
            hooks.set_ssl(None)
            hooks.set_profile(None)

            if not app_name:
                app_name = self.get_app_name()
            process_app_version = fileoperations.env_yaml_exists()
            version_label = commonops.create_app_version(app_name, process=process_app_version)

            stages_version_labels[group_name].append(version_label)

            environment_name = fileoperations.get_env_name_from_env_yaml()
            if environment_name is not None:
                commonops.set_environment_for_current_branch(environment_name.
                                                             replace('+', '-{0}'.
                                                                     format(group_name)))

                env_name = commonops.get_current_branch_environment()
                stages_env_names[group_name].append(env_name)
                env_names.append(env_name)
            else:
                io.echo(strings['deploy.noenvname'].replace('{module}', module))
                stages_version_labels[group_name].pop(version_label)

            chdir(top_dir)

        if len(stages_version_labels) > 0:
            for stage in stages_version_labels.keys():
                composeops.compose_no_events(app_name, stages_version_labels[stage],
                                             group_name=stage)
            commonops.wait_for_compose_events(app_name, env_names, self.timeout)
        else:
            io.log_warning(strings['compose.novalidmodules'])
