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


from argparse import ArgumentParser
import argparse
from cement.core import backend, arg, handler
from cement.utils.misc import minimal_logger

LOG = minimal_logger(__name__)


class ArgParseHandler(arg.CementArgumentHandler, ArgumentParser):

    """
This class implements the :ref:`IArgument <cement.core.arg>`
interface, and sub-classes from `argparse.ArgumentParser
<http://docs.python.org/dev/library/argparse.html>`_.
Please reference the argparse documentation for full usage of the
class.

Arguments and Keyword arguments are passed directly to ArgumentParser
on initialization.
"""

    class Meta:

        """Handler meta-data."""

        interface = arg.IArgument
        """The interface that this class implements."""

        label = 'argparse'
        """The string identifier of the handler."""

    def __init__(self, *args, **kw):
        super(ArgParseHandler, self).__init__(*args, **kw)
        self.config = None

    def parse(self, arg_list):
        """
Parse a list of arguments, and return them as an object. Meaning an
argument name of 'foo' will be stored as parsed_args.foo.

:param arg_list: A list of arguments (generally sys.argv) to be
parsed.
:returns: object whose members are the arguments parsed.

"""
        return self.parse_args(arg_list)

    def add_argument(self, *args, **kw):
        """
Add an argument to the parser. Arguments and keyword arguments are
passed directly to ArgumentParser.add_argument().

"""
        # return self.parser.add_argument(*args, **kw)
        return super(ArgumentParser, self).add_argument(*args, **kw)


def load(app):
    """Called by the framework when the extension is 'loaded'."""
    handler.register(ArgParseHandler)