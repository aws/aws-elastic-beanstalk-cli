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

import sys

from ebcli.core import fileoperations, io
from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.lib import utils, aws
from ebcli.objects.exceptions import NotInitializedError
from ebcli.operations import platformops, initializeops
from ebcli.resources.strings import strings, flag_text, prompts
from ebcli.controllers.initialize import get_region, get_region_from_inputs, set_up_credentials
from ebcli.core.ebglobals import Constants
from ebcli.operations import commonops, sshops

KEYPAIR_NAMESPACE = 'aws:autoscaling:launchconfiguration'
KEYPAIR_OPTION = 'EC2KeyName'


class GenericPlatformInitController(AbstractBaseController):
    class Meta:
        arguments = [
            (['platform_name'], dict(help=flag_text['platforminit.name'], nargs='?', default=[])),
            (['-i', '--interactive'], dict(action='store_true', help=flag_text['init.interactive'])),
            (['-k', '--keyname'], dict(help=flag_text['init.keyname']))
        ]
        epilog = strings['platforminit.epilog']

        @classmethod
        def clone(cls):
            return type('Meta', cls.__bases__, dict(cls.__dict__))

    def do_command(self):
        fileoperations.touch_config_folder()

        self.interactive = self.app.pargs.interactive
        self.region = self.app.pargs.region

        if self.interactive:
            self.region = get_region(self.app.pargs.region, self.app.pargs.interactive)
        else:
            self.region = get_region_from_inputs(self.app.pargs.region)

        aws.set_region(self.region)

        self.region = set_up_credentials(self.app.pargs.profile, self.region, self.interactive)

        self.platform_name, version = self.get_platform_name_and_version()

        # If interactive mode, or explicit interactive due to missing platform_name
        if self.interactive or not self.platform_name:
            self.keyname = self.get_keyname(self.app.pargs.keyname)
        else:
            self.keyname = None

        if self.keyname == -1:
            self.keyname = None

        initializeops.setup(
            'Custom Platform Builder',
            self.region,
            None,
            workspace_type=Constants.WorkSpaceTypes.PLATFORM,
            platform_name=self.platform_name,
            platform_version=version)

        fileoperations.write_keyname(self.keyname)

        if version is None:
            platformops.set_workspace_to_latest()

    def get_keyname(self, keyname):
        # Get keyname from config file, if exists
        if not keyname:
            try:
                keyname = commonops.get_default_keyname()
            except NotInitializedError:
                keyname = None

        if keyname is None:
            # Prompt for one
            keyname = sshops.prompt_for_ec2_keyname(message=prompts['platforminit.ssh'])
        elif keyname != -1:
            commonops.upload_keypair_if_needed(keyname)

        return keyname

    def get_platform_name_and_version(self):
        # Get app name from command line arguments
        platform_name = self.app.pargs.platform_name
        interactive = self.app.pargs.interactive
        version = None

        # Get app name from config file, if exists
        if not platform_name:
            try:
                platform_name = fileoperations.get_platform_name(default=None)
                version = fileoperations.get_platform_version()
            except NotInitializedError:
                platform_name = None

        # Ask for app name
        if not platform_name or interactive:
            platform_name, version = platformops.get_platform_name_and_version_interactive()

        if sys.version_info[0] < 3 and isinstance(platform_name, unicode):
            try:
                platform_name.encode('utf8')
                platform_name = platform_name.encode('utf8')
            except UnicodeDecodeError:
                pass

        return platform_name, version


class PlatformInitController(GenericPlatformInitController):
    Meta = GenericPlatformInitController.Meta.clone()
    Meta.arguments = GenericPlatformInitController.Meta.arguments
    Meta.label = 'platform init'
    Meta.aliases = ['init']
    Meta.aliases_only = True
    Meta.stacked_on = 'platform'
    Meta.stacked_type = 'nested'
    Meta.description = strings['platforminit.info']
    Meta.usage = 'eb platform init <platform name> [options...]'


class EBPInitController(GenericPlatformInitController):
    Meta = GenericPlatformInitController.Meta.clone()
    Meta.arguments = GenericPlatformInitController.Meta.arguments
    Meta.label = 'init'
    Meta.description = strings['platforminit.info']
    Meta.usage = 'ebp init <platform name> [options...]'
