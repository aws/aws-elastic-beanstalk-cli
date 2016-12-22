8# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

from cement.utils.misc import minimal_logger

from ebcli.core import io
from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.lib import elasticbeanstalk as elasticbeanstalk
from ebcli.operations import appversionops, commonops
from ebcli.resources.strings import strings, flag_text


class AppVersionController(AbstractBaseController):
    class Meta(AbstractBaseController.Meta):
        label = 'appversion'
        description = strings['appversion.info']
        arguments = [
            (['--delete', '-d'], dict(action='store', help=flag_text['appversion.delete'], metavar='VERSION_LABEL'))
        ]
        usage = 'eb appversion <lifecycle> [options ...]'

    def do_command(self):
        self.app_name = self.get_app_name()
        # For appversion, it's fine if environment is not defined
        self.env_name = self.get_env_name(noerror=True)

        # if user passed in a app version label to delete
        if self.app.pargs.delete is not None:
            version_label_to_delete = self.app.pargs.delete
            appversionops.delete_app_version_label(self.app_name, version_label_to_delete)
            return

        # if none of above, enter interactive mode
        self.interactive_list_version()

    def interactive_list_version(self):
        """Interactive mode which allows user to see previous
        versions and allow a choice to:
        - deploy a different version.
        - delete a certain version
        Run when the user supplies no argument to the --delete flag.
        """
        app_versions = elasticbeanstalk.get_application_versions(self.app_name)['ApplicationVersions']
        appversionops.display_versions(self.app_name, self.env_name, app_versions)
