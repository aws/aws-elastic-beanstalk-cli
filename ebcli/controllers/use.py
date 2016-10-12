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
from ..lib import utils

from ..objects.exceptions import NotFoundError

from ..objects.sourcecontrol import SourceControl

from ..core.abstractcontroller import AbstractBaseController
from ..resources.strings import strings, flag_text
from ..operations import useops, gitops


class UseController(AbstractBaseController):
    class Meta:
        label = 'use'
        description = strings['use.info']
        arguments = [
            (['environment_name'], dict(action='store', nargs=1,
                                    help=flag_text['use.env'])),
            (['--source'], dict(type=utils.check_source, help=flag_text['deploy.source'])),
        ]
        usage = 'eb use [environment_name] [options ...]'

    def do_command(self):
        self.source = self.app.pargs.source
        app_name = self.get_app_name()
        env_name = self.app.pargs.environment_name[0]

        useops.switch_default_environment(app_name, env_name)

        if self.source is not None:
            repo, branch = utils.parse_source(self.source)

            source_control = SourceControl.get_source_control()
            source_control.is_setup()

            if repo is None:
                repo = gitops.get_default_repository()

            useops.switch_default_repo_and_branch(repo, branch)
            successfully_checked_out_branch = source_control.checkout_branch(branch)
            if not successfully_checked_out_branch:
                raise NotFoundError("Could not checkout branch {0}.".format(branch))

        # If source is not set attempt to change branch to the environment default
        else:
            source_control = SourceControl.get_source_control()
            default_branch = gitops.get_branch_default_for_current_environment()
            if default_branch is not None:
                source_control.checkout_branch(default_branch)