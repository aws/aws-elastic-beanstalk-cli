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


from ebcli.core import fileoperations
from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.operations import solution_stack_ops
from ebcli.operations.platformops import set_platform, get_platform_name_and_version_interactive
from ebcli.resources.strings import strings, flag_text


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
        platform = solution_stack_ops.get_solution_stack_from_customer().name
        fileoperations.write_config_setting('global', 'default_platform', platform)


class GenericPlatformUseController(AbstractBaseController):
    class Meta:
        description = strings['platformworkspaceselectversion.info']
        arguments = [
            (['platform'], dict(action='store', nargs='?', default=None, help=flag_text['platformworkspace.platform'])),
        ]

        @classmethod
        def clone(cls):
            return type('Meta', cls.__bases__, dict(cls.__dict__))

    def do_command(self):
        platform_name = self.app.pargs.platform
        platform_version = None
        verify = True

        if platform_name is None:
            platform_name, platform_version = get_platform_name_and_version_interactive()
            # The platform has already been validated
            verify = False

        set_platform(platform_name, platform_version, verify)


class PlatformWorkspaceUseController(GenericPlatformUseController):
    Meta = GenericPlatformUseController.Meta.clone()
    Meta.label = 'platform use'
    Meta.aliases = ['use']
    Meta.aliases_only = True
    Meta.stacked_on = 'platform'
    Meta.stacked_type = 'nested'
    Meta.usage = 'eb platform use <platform> [options...]'


class EBPUseController(GenericPlatformUseController):
    Meta = GenericPlatformUseController.Meta.clone()
    Meta.label = 'use'
    Meta.usage = 'ebp use <platform> [options...]'
