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

import argparse

from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.core import io


'''  Flag types
  When you specify arguments, there are three types of 'actions'
    store: the argument will parsed the next item on the command line
        and store it.
        Example:  eb example --foo bar
            self.app.pargs.foo will then contain 'bar'

    store_true: the argument will be saved as True if the flag is given, and
        false otherwise
        Example: eb example -V
            self.app.pargs.vendetta will then be True

    store_const: the argument will be saved as a predefined constant.
        Example: eb example -A
            self.app.pargs.a will then be 12345


   Note: If arguments is omitted, all default arguments will be given

'''


class ExampleController(AbstractBaseController):
    class Meta:
        label = 'example'  # command name
        description = 'Does cool stuff'  # Help text description
        arguments = [  # All arguments specific to this command
            (['-f', '--foo'], dict(action='store', dest='foo',
                                   help='the notorious foo option')),
            (['-V'], dict(action='store_true', dest='vendetta',
                                              help='V for Vendetta')),
            (['-A'], dict(action='store_const', const=12345,
                                              help='the A option')),
            # The position_arg is a flagless argument
            ##  nargs specifies the number of arguments expected
            (['positional_arg'], dict(action='store', nargs='*', default=[])),
            # The below is a hidden option flag, it is set as hidden by the
            ## help text being set to SUPRESS
            (['--hidden'], dict(action='store_true', help=argparse.SUPPRESS))
        ]

    def do_command(self):
        """
        This method actually does the command
        """
        io.echo('Hello World!')

        for arg in self.app.pargs.positional_arg:
            io.echo(arg)

        if self.app.pargs.foo:
            io.echo(self.app.pargs.foo)

        if self.app.pargs.vendetta:
            io.echo('Vendetta Flag was set')

        if self.app.pargs.hidden:
            io.echo('The hidden flag was set')

    def complete_command(self, commands):
        """
        Implement this method for autocompletion to work
        You do not have to worry about the --flags, only positional arguments

        :param commands: A list of commands on the command line so fat
        """
        # Print out all possible options. The completer function is smart
        ## enough to filter out the ones that dont match
        io.echo('option1')
        io.echo('option2')