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
from ebcli.core import io, fileoperations
from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.core.ebglobals import Constants
from ebcli.objects.platform import PlatformVersion
from ebcli.operations import platformops
from ebcli.resources.strings import strings, flag_text


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
            platform_arns = platformops.list_custom_platform_versions()
            lst = [s.name for s in solution_stacks]
            lst.extend(platform_arns)
        else:
            platform_arns = platformops.list_custom_platform_versions(platform_version='latest')
            lst = sorted(set([s.pythonify() for s in solution_stacks]))
            lst.extend([PlatformVersion.get_platform_name(arn) for arn in platform_arns])

        if len(lst) > 20:
            io.echo_with_pager(os.linesep.join(lst))
        else:
            io.echo(*lst, sep=os.linesep)


class GenericPlatformListController(AbstractBaseController):
    class Meta:
        description = strings['platformlistversions.info']
        arguments = [
            (['-a', '--all-platforms'], dict(action='store_true', help=flag_text['platformlist.all'])),
            (['-s', '--status'], dict(action='store', help=flag_text['platformlist.status'])),
        ]
        epilog = strings['platformlistversions.epilog']

        @classmethod
        def clone(cls):
            return type('Meta', cls.__bases__, dict(cls.__dict__))

    def do_command(self):
        all_platforms = self.app.pargs.all_platforms
        status = self.app.pargs.status

        if not all_platforms:
            platform_name = fileoperations.get_platform_name()
        else:
            platform_name = None

        versions = platformops.list_custom_platform_versions(
            platform_name=platform_name,
            status=status,
            show_status=True
        )

        if len(versions) > 20:
            io.echo_with_pager(os.linesep.join(versions))
        else:
            io.echo(*versions, sep=os.linesep)


class PlatformWorkspaceListController(GenericPlatformListController):
    Meta = GenericPlatformListController.Meta.clone()
    Meta.label = 'platform list'
    Meta.aliases = ['list']
    Meta.aliases_only = True
    Meta.stacked_on = 'platform'
    Meta.stacked_type = 'nested'
    Meta.usage = 'eb platform list [options...]'


class EBPListController(GenericPlatformListController):
    Meta = GenericPlatformListController.Meta.clone()
    Meta.label = 'list'
    Meta.usage = 'ebp list [options...]'