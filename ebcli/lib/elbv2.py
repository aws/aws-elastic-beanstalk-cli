# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
from ..objects.exceptions import ServiceError, NotFoundError
from ..resources.strings import responses

LOG = minimal_logger(__name__)


def _make_api_call(operation_name, **operation_options):
    return aws.make_api_call('elbv2', operation_name, **operation_options)


def get_instance_healths_from_target_groups(target_group_arns):
    results = []
    instance_healths = {}
    for arn in target_group_arns:
        try:
            results.append( {
                'TargetGroupArn': arn,
                'Result': _make_api_call('describe_target_health', TargetGroupArn=arn)
            } )
        except ServiceError as e:
            if e.message == responses['loadbalancer.targetgroup.notfound'].replace('{tgarn}', arn):
                raise NotFoundError(e)

    for result in results:
        for description in result['Result']['TargetHealthDescriptions']:
            instance_id = description['Target']['Id']
            if instance_id not in instance_healths:
                instance_healths[instance_id] = []
            instance_healths[instance_id].append({
                'TargetGroupArn': result['TargetGroupArn'],
                'State': description['TargetHealth'].get('State', ''),
                'Description': description['TargetHealth'].get('Description', ''),
                'Reason': description['TargetHealth'].get('Reason', '')
            })

    return instance_healths #map of instance_id => [target group health descrpitions]

def get_target_group_healths(target_group_arns):
    results = {}
    for arn in target_group_arns:
        try:
            results[arn] = _make_api_call('describe_target_health', TargetGroupArn=arn)
        except ServiceError as e:
            if e.code == 'TargetGroupNotFound':
                raise NotFoundError(e)
            else:
                raise e

    return results #map of target_group_arn => [target group health descrpitions]
