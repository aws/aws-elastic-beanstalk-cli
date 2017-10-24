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
from datetime import datetime, timedelta
import time

from cement.utils.misc import minimal_logger

from ebcli.lib import aws
from ebcli.objects.exceptions import EBCLIException

LOG = minimal_logger(__name__)


def _make_api_call(operation_name, **operation_options):
    return aws.make_api_call('cloudformation', operation_name, **operation_options)


def get_template(stack_name):
    result = _make_api_call('get_template',
                            StackName=stack_name)
    return result


def wait_until_stack_exists(stack_name, timeout=120):
    """
    Given a template name, wait until stack is successfully created
    or 'timeout' seconds have elapsed.
    :param stack_name: name of the CloudFormation stack whose creation is pending
    :param timeout: number of seconds after which to stop polling 'DescribeStacks'
    :return:
    """
    LOG.debug('Inside describe_stacks api wrapper')

    stack_exists = False
    start_time = datetime.now()

    while not stack_exists:
        if (datetime.now() - start_time) > timedelta(timeout):
            raise CFNTemplateNotFound("Could not find CFN stack, '{stack_name}'.".format(stack_name=stack_name))

        response = _make_api_call('describe_stacks')

        if [stack for stack in response['Stacks'] if stack['StackName'] == stack_name]:
            stack_exists = True
        else:
            time.sleep(5)


class CFNTemplateNotFound(EBCLIException):
    """
    Exception class to raise when a CFN stack is not found
    """
