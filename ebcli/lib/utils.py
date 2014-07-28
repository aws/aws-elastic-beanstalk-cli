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

from ebcli.core import io

def prompt_for_item_in_list(list):
    for x in range(0, len(list)):
        io.echo(str(x + 1) + ') ', list[x])


    choice = int(io.prompt('number'))
    while not (0 < choice <= len(list)):
        io.echo('Sorry, that is not a valid choice, '
                                'please choose again')
        choice = int(io.prompt('number'))
    return list[choice - 1]


