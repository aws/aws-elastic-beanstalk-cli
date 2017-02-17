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

from ebcli.core import fileoperations, io
from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.core.fileoperations import write_config_setting
from ebcli.lib import iam
from ebcli.objects.exceptions import NotInitializedError, NotAuthorizedError, AlreadyExistsError
from ebcli.operations import platformops
from ebcli.operations.platformops import create_platform_version
from ebcli.resources.strings import strings, flag_text, prompts
from ebcli.resources.statics import iam_attributes, iam_documents


class GenericPlatformCreateController(AbstractBaseController):
    class Meta:
        description = strings['platformcreateversion.info']
        arguments = [
            (['version'], dict(action='store', nargs='?', default=None, help=flag_text['platformcreateversion.version'])),
            (['-M', '--major-increment'], dict(action='store_true', help=flag_text['platformcreateversion.major'])),
            (['-m', '--minor-increment'], dict(action='store_true', help=flag_text['platformcreateversion.minor'])),
            (['-p', '--patch-increment'], dict(action='store_true', help=flag_text['platformcreateversion.patch'])),
            (['-i', '--instance-type'], dict(help=flag_text['create.itype'])),
            (['-ip', '--instance_profile'], dict(action='store', help=flag_text['platformcreate.instanceprofile'])),
            (['--vpc.id'], dict(dest='vpc_id', help=flag_text['platformcreateversion.vpc.id'])),
            (['--vpc.subnets'], dict(dest='vpc_subnets', help=flag_text['platformcreateversion.vpc.subnets'])),
            (['--vpc.publicip'], dict(action='store_true', dest='vpc_publicip', help=flag_text['platformcreateversion.vpc.publicip']))
        ]
        epilog = strings['platformcreateversion.epilog']

        @classmethod
        def clone(cls):
            return type('Meta', cls.__bases__, dict(cls.__dict__))

    def do_command(self):
        self.get_instance_profile()

        create_platform_version(
            self.app.pargs.version,
            self.app.pargs.major_increment,
            self.app.pargs.minor_increment,
            self.app.pargs.patch_increment,
            self.app.pargs.instance_type,
            { 'id': self.app.pargs.vpc_id, 'subnets': self.app.pargs.vpc_subnets, 'publicip': self.app.pargs.vpc_publicip })

    # TODO: Merge into ebcli/lib/iam_role.py when the code has been merged in
    def get_instance_profile(self):
        # Check to see if it was specified on the command line
        profile = self.app.pargs.instance_profile

        if profile is None:
            try:
                # Check to see if it is associated with the workspace
                profile = fileoperations.get_instance_profile()
            except NotInitializedError:
                pass

        if profile is None:
            # Check to see if the default instance profile already exists
            try:
                existing_profiles = iam.get_instance_profile_names()
                if iam_attributes.DEFAULT_PLATFORM_BUILDER_ROLE in existing_profiles:
                    profile = iam_attributes.DEFAULT_PLATFORM_BUILDER_ROLE
            except NotAuthorizedError:
                io.log_warning(strings['platformcreateiamdescribeerror.info'])

        if profile is None:
            # We will now create the default role for the customer
            try:
                profile = iam_attributes.DEFAULT_PLATFORM_BUILDER_ROLE
                try:
                    iam.create_instance_profile(profile)
                    io.log_info(strings['platformcreateiamcreated.info'])
                except AlreadyExistsError:
                    pass

                document = iam_documents.EC2_ASSUME_ROLE_PERMISSION
                try:
                    # Create a role with the same name
                    iam.create_role(profile, document)

                    # Attach required custom platform builder permissions
                    iam.put_role_policy(
                        profile,
                        iam_attributes.PLATFORM_BUILDER_INLINE_POLICY_NAME,
                        iam_documents.CUSTOM_PLATFORM_BUILDER_INLINE_POLICY)
                    # Associate instance profile with the required role
                    iam.add_role_to_profile(profile, profile)
                    io.log_info(strings['platformcreateiampolicyadded.info'])
                except AlreadyExistsError:
                    # If the role exists then we leave it as is, we do not try to add or modify its policies
                    pass

            except NotAuthorizedError:
                io.log_warning(strings['platformcreateiamcreateerror.info'])

        # Save to disk
        write_config_setting('global', 'instance_profile', profile)


class PlatformCreateController(GenericPlatformCreateController):
    Meta = GenericPlatformCreateController.Meta.clone()
    Meta.label = 'platform create'
    Meta.aliases = ['create']
    Meta.aliases_only = True
    Meta.stacked_on = 'platform'
    Meta.stacked_type = 'nested'
    Meta.usage = 'eb platform create <version> [options...]'


class EBPCreateController(GenericPlatformCreateController):
    Meta = GenericPlatformCreateController.Meta.clone()
    Meta.label = 'create'
    Meta.usage = 'ebp create <version> [options...]'
