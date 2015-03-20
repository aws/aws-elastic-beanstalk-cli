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

from cement.utils.misc import minimal_logger

from ..lib import aws

LOG = minimal_logger(__name__)


def _make_api_call(operation_name, **operation_options):
    return aws.make_api_call('cloudformation', operation_name, **operation_options)


def get_template(stack_name):
    result = _make_api_call('get_template',
                            StackName=stack_name)
    return result