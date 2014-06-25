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

import six

from cement.core import output
from enum import Enum


class OutputHandler(output.CementOutputHandler):
    class Meta:
        label = 'customDictOutput'

    def render(data, template=None):
        for key in data:
            print("%s => %s" % (key, data[key]))

    def print_to_console(self, *args):
        for data in args:
            if isinstance(data, six.string_types) \
                    or isinstance(data, six.integer_types):
                print(data),
            elif isinstance(data, Enum):
                print(data.value),
            else:
                self.app.log.error("print_to_console called with an unsupported data type")
        print('')
