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
from ebcli.resources.strings import strings

def are_instance_types_valid(instance_types):
    if instance_types is not None:
        instance_types_list = [instance_type.strip() for instance_type in instance_types.split(',')]
    if instance_types is None or '' in instance_types_list or len(instance_types_list) < 2:
        return False
    else:
        return True

def get_spot_instance_types_from_customer(interactive, enable_spot):
    """
    Prompt customer to specify their desired instances types if they
    selected enabled spot requests from the interactive flow.

    :return: list of comma separated instance types
    """
    if not interactive:
        return False
    io.echo('Please enter your desired instance types for your spot request in a comma separated list.')
    instance_types = prompt_for_instance_types()

    return instance_types

def get_spot_request_from_customer(interactive):
    """
    Prompt customer to select if they would like to enable spot requests if
    operating in the interactive mode.

    Selection defaults to 'No' when provided with blank input.
    :param interactive: True/False depending on whether operating in the interactive mode or not
    :param single: False/True depending on whether environment is load balanced or not
    :return: selected value for if to enable spot requests or not: True/False
    """
    if not interactive:
        return
    io.echo()
    io.echo('Would you like to enable Spot requests for this environment?')
    user_input = prompt_for_enable_spot_request()
    while user_input not in ['y', 'n', 'Y', 'N']:
        io.echo(strings['create.download_sample_app_choice_error'].format(choice=user_input))
        user_input = prompt_for_enable_spot_request()

    return True if user_input in ['y', 'Y'] else False

def prompt_for_enable_spot_request():
    """
    Method accepts the user's choice of whether spot requests should be enabled.
    Defaults to 'Y' when none is provided.

    :return: user's choice of whether the spot request should be enabled
    """
    return io.get_input('(y/N)', default='n')

def prompt_for_instance_types():
    """
    Method accepts the user's choice of whether spot requests should be enabled.
    Defaults to 'Y' when none is provided.

    :return: user's choice of whether the spot request should be enabled
    """
    while True:
        instance_types = io.prompt('For example: t2.micro, t3.micro')
        if are_instance_types_valid(instance_types):
            return instance_types
        else:
            io.echo('Spot instance types must contain at least two valid instance types')
            io.echo('')