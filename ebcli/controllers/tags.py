# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

from ebcli.core import io
from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.objects.exceptions import InvalidOptionsError, NoEnvironmentForBranchError
from ebcli.operations import commonops
from ebcli.operations.tagops.tagops import TagOps
from ebcli.resources.strings import strings, flag_text

from cement.utils.misc import minimal_logger

LOG = minimal_logger(__name__)


class TagsController(AbstractBaseController):

    class Meta:
        label = 'tags'
        description = flag_text['tags.info']
        arguments = [
            (['environment_name'], dict(action='store', nargs='?',
                                        help=flag_text['tags.env'])),
            (['-l', '--list'], dict(action='store_true', help=flag_text['tags.list'])),
            (['-a', '--add'], dict(metavar='key1=value1[,key2=value2,...]', help=flag_text['tags.add'])),
            (['-d', '--delete'], dict(metavar='key1[,key2,...]', help=flag_text['tags.delete'])),
            (['-u', '--update'], dict(metavar='key1=value1[,key2=value2,...]', help=flag_text['tags.update']))
        ]
        usage = 'eb tags [<environment_name>] option [options ...]'

    def do_command(self):
        self.environment_name = self.env_name()

        self.list_argument = self.app.pargs.list

        self.add_arguments = self.app.pargs.add
        self.delete_arguments = self.app.pargs.delete
        self.update_arguments = self.app.pargs.update

        self.verbose = self.app.pargs.verbose

        tagops = TagOps(self.environment_name, self.verbose)

        self.__assert_list_argument_xor_modifier_arguments_specified()

        if self.list_argument:
            tagops.list_tags()

            return

        tagops.handle_addition_string(self.add_arguments) if self.add_arguments else None
        tagops.handle_deletion_string(self.delete_arguments) if self.delete_arguments else None
        tagops.handle_update_string(self.update_arguments) if self.update_arguments else None

        tagops.update_tags()

    def env_name(self):
        if self.app.pargs.environment_name:
            env_name = self.app.pargs.environment_name
        else:
            env_name = commonops.get_current_branch_environment()

        if not env_name:
            message = strings['branch.noenv'].replace('{cmd}', self.Meta.label)
            io.log_error(message)

            raise NoEnvironmentForBranchError()

        return env_name

    def __assert_list_argument_xor_modifier_arguments_specified(self):
        if self.list_argument:
            if self.__modifier_arguments_specified():
                raise InvalidOptionsError(strings['tags.list_with_other_arguments'])

        else:
            if not self.__modifier_arguments_specified():
                raise InvalidOptionsError('usage: {0}'.format(self._usage_text))

    def __modifier_arguments_specified(self):
        return self.add_arguments or self.delete_arguments or self.update_arguments
