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
import collections
import urllib.parse, urllib.request, urllib.error
import socket

from cement.utils.misc import minimal_logger

from ebcli.lib import aws
from ebcli.objects.exceptions import ServiceError, AlreadyExistsError, \
    NotFoundError, NotAnEC2Instance
from ebcli.resources.strings import responses
from ebcli.core import fileoperations, io

LOG = minimal_logger(__name__)


def _make_api_call(operation_name, **operation_options):
    return aws.make_api_call('ec2', operation_name, **operation_options)


def get_key_pairs():
    result = _make_api_call('describe_key_pairs')
    return result['KeyPairs']


def import_key_pair(keyname, key_material):
    try:
        result = _make_api_call(
            'import_key_pair',
            KeyName=keyname,
            PublicKeyMaterial=key_material
        )
    except ServiceError as e:
        if e.message.endswith('already exists.'):
            raise AlreadyExistsError(e.message)
        else:
            raise

    return result


def describe_instances(instance_ids):
    result = _make_api_call('describe_instances',
                            InstanceIds=instance_ids)

    instances = []
    for r in result.get('Reservations', {}):
        for i in r.get('Instances', {}):
            instances.append(i)
    return instances


def describe_instance(instance_id):
    result = describe_instances([instance_id])

    try:
        return result[0]
    except (IndexError, NotFoundError):
        raise NotFoundError('Instance {0} not found.'.format(instance_id))


def has_default_vpc():
    result = _make_api_call('describe_account_attributes',
                            AttributeNames=['default-vpc'])
    default_vpc = None
    for attribute in result['AccountAttributes']:
        if attribute['AttributeName'] == 'default-vpc':
            try:
                default_vpc = attribute['AttributeValues'][0]['AttributeValue']
            except (KeyError, IndexError):
                default_vpc = None

    if default_vpc and default_vpc.lower() != 'none':
        return True
    else:
        return False


def revoke_ssh(security_group_id):
    try:
        _make_api_call(
            'revoke_security_group_ingress',
            GroupId=security_group_id,
            IpProtocol='tcp',
            ToPort=22,
            FromPort=22,
            CidrIp='0.0.0.0/0'
        )
    except ServiceError as e:
        if e.message.startswith(responses['ec2.sshalreadyopen']):
            pass
        else:
            raise


def authorize_ssh(security_group_id):
    try:
        _make_api_call(
            'authorize_security_group_ingress',
            GroupId=security_group_id,
            IpProtocol='tcp',
            ToPort=22,
            FromPort=22,
            CidrIp='0.0.0.0/0'
        )
    except ServiceError as e:
        if e.code == 'InvalidPermission.Duplicate':
            pass
        else:
            raise


def describe_security_group(security_group_id):
    result = _make_api_call('describe_security_groups',
                            GroupIds=[security_group_id])
    if result and len(result['SecurityGroups']) < 1:
        raise NotFoundError('Security Group {} not found.'
                            .format(security_group_id))
    return result['SecurityGroups'][0]


def terminate_instance(instance_id):
    return _make_api_call('terminate_instances',
                          InstanceIds=[instance_id])


def reboot_instance(instance_id):
    return _make_api_call('reboot_instances',
                          InstanceIds=[instance_id])


def ensure_vpc_exists(vpc_id):
    return _make_api_call('describe_vpcs',
                          VpcIds=[vpc_id])


# Function to get metadata
def get_instance_metadata(path):
    metadata_url = f"http://169.254.169.254/latest/meta-data/{path}"
    token_url = "http://169.254.169.254/latest/api/token"

    token_request = urllib.request.Request(token_url, method="PUT")
    token_request.add_header("X-aws-ec2-metadata-token-ttl-seconds", "21600")
    try:
        with urllib.request.urlopen(token_request) as token_response:
            token = token_response.read().decode('utf-8')

        metadata_request = urllib.request.Request(metadata_url)
        metadata_request.add_header("X-aws-ec2-metadata-token", token)
        with urllib.request.urlopen(metadata_request, timeout=5) as response:
            return response.read().decode('utf-8')
    except (urllib.error.URLError, socket.timeout, ConnectionError) as e:
        if _is_timeout_exception(e):
            LOG.debug("Communication with IMDSv2 timed out. This is likely not an EC2 instance.")
            raise NotAnEC2Instance(e)
        raise e


def _is_timeout_exception(exception: urllib.error.URLError) -> bool:
    return (
        isinstance(exception.__dict__.get('reason', False), TimeoutError)
            or 'timed out' in str(exception)
    )


def get_current_instance_details():
    instance_id = get_instance_metadata('instance-id')
    availability_zone = get_instance_metadata('placement/availability-zone')
    region = availability_zone[:-1]
    aws.set_region(region)
    fileoperations.write_config_setting('global', 'default_region', region)
    mac_address = get_instance_metadata('mac')
    vpc_id = get_instance_metadata(f'network/interfaces/macs/{mac_address}/vpc-id')
    subnet_id = get_instance_metadata(f'network/interfaces/macs/{mac_address}/subnet-id')
    try:
        ensure_vpc_exists(vpc_id)
        instance = describe_instance(instance_id=instance_id)
    except Exception as e:
        if 'InvalidVpcID.NotFound' in str(e) or f"The vpc ID '{vpc_id}' does not exist" in str(e):
            io.log_warning(f'Unable to retrieve details of VPC, {vpc_id}')
            vpc_id, subnet_id, instance_id, security_group_ids, tags = None, None, None, [], []
        elif 'InvalidInstanceID.NotFound' in str(e):
            vpc_id, subnet_id, instance_id, security_group_ids, tags = None, None, None, [], []
            io.log_warning(f'Unable to retrieve details of instance, {instance_id}')
        instance = None
    if instance:
        security_group_ids = [sg['GroupId'] for sg in instance['SecurityGroups']]
    else:
        security_group_ids = []

    try:
        tags = instance_tags(instance_id)
    except Exception:
        # Probably client-error, ignore
        tags = []

    return {
        'InstanceId': instance_id,
        'VpcId': vpc_id,
        'SubnetId': subnet_id,
        'SecurityGroupIds': security_group_ids,
        'Region': region,
        'Tags': tags,
    }


def list_subnets(vpc_id):
    result = _make_api_call(
        'describe_subnets',
        Filters=[
            {
                'Name': 'vpc-id',
                'Values': [vpc_id]
            },
        ]
    )
    return [subnet['SubnetId'] for subnet in result['Subnets']]


def list_subnets_azs_interleaved(vpc_id):
    result = _make_api_call(
        'describe_subnets',
        Filters=[
            {
                'Name': 'vpc-id',
                'Values': [vpc_id]
            },
        ]
    )

    subnet_map = collections.defaultdict(list)
    subnet_ids = []
    for subnet in result['Subnets']:
        subnet_map[subnet['AvailabilityZone']].append(subnet['SubnetId'])
    keys = subnet_map.keys()
    while any([v for v in subnet_map.values()]):
        for key in keys:
            subnet_ids.append(subnet_map[key].pop())
    return [subnet['SubnetId'] for subnet in result['Subnets']]


def get_instance_volumes(instance_id):
    response = _make_api_call(
        'describe_volumes',
        Filters=[
            {
                'Name': 'attachment.instance-id',
                'Values': [instance_id]
            }
        ]
    )
    return response['Volumes']


def enable_ebs_volume_encryption():
    _make_api_call('enable_ebs_encryption_by_default')


def instance_tags(instance_id):
    response = _make_api_call(
        'describe_tags',
        Filters=[
            {
                'Name': 'resource-id',
                'Values': [instance_id]
            }
        ]
    )
    return [
        {
            "Key": tag['Key'],
            "Value": tag['Value']
        }
        for tag in response['Tags']
    ]


def establish_security_group(ports, env_name, vpc_id):
    ec2_security_group = get_security_group(f'{env_name}-EC2')
    if ec2_security_group:
        ec2_security_group_id = ec2_security_group['GroupId']
        revoke_security_group_ingress(ec2_security_group_id, ec2_security_group['IpPermissions'])
    else:
        ec2_security_group_id = _create_security_group(f'{env_name}-EC2', vpc_id, f'EC2 Security group for {env_name}-EC2')

    alb_security_group = get_security_group(f'{env_name}-ALB')
    if alb_security_group:
        alb_security_group_id = ec2_security_group['GroupId']
        revoke_security_group_egress(alb_security_group_id, alb_security_group['IpPermissionsEgress'])
    else:
        alb_security_group_id = _create_security_group(f'{env_name}-ALB', vpc_id, f'ALB Security group for {env_name}-EC2')

    ingress_permissions, egress_permissions = create_peer_security_group_permissions(
        ports,
        ec2_security_group_id,
        alb_security_group_id,
        vpc_id
    )
    authorize_security_group_egress(alb_security_group_id, egress_permissions)
    authorize_security_group_ingress(ec2_security_group_id, ingress_permissions)

    return [
        {
            'Namespace': 'aws:elbv2:loadbalancer',
            'OptionName': 'SecurityGroups',
            'Value': alb_security_group_id
        },
        {
            'Namespace': 'aws:autoscaling:launchconfiguration',
            'OptionName': 'SecurityGroups',
            'Value': ec2_security_group_id
        },
    ]


def create_peer_security_group_permissions(
        ports,
        from_security_group,
        to_security_group,
        vpc_id
):
    egress_permissions, ingress_permissions = [], []
    for port in ports:
        egress_permission = define_group_pair_permission(
            port,
            from_security_group,
            f"Rule to allow {from_security_group} to access {to_security_group} at port {port} over tcp"
        )

        ingress_permission = define_group_pair_permission(
            port,
            to_security_group,
            f"Rule to allow {to_security_group} to receive traffic from {from_security_group} at {port} over tcp"
        )

        if vpc_id:
            ingress_permission["UserIdGroupPairs"][0]["VpcId"] = vpc_id
            egress_permission["UserIdGroupPairs"][0]["VpcId"] = vpc_id

        egress_permissions.append(egress_permission)
        ingress_permissions.append(ingress_permission)

    return ingress_permissions, egress_permissions


def define_group_pair_permission(port, security_group_id, description):
    return {
        'IpProtocol': 'tcp',
        'FromPort': port,
        'ToPort': port,
        "UserIdGroupPairs": [
            {
                "Description": description,
                "GroupId": security_group_id,
            }
        ],
    }


def revoke_security_group_ingress(security_group_ip, ip_permissions):
    kwargs = {
        'GroupId': security_group_ip,
        'IpPermissions': ip_permissions,
    }
    try:
        _make_api_call(
            'revoke_security_group_ingress',
            **kwargs
        )
    except Exception as e:
        if 'MissingParameter' in str(e) or "Either 'ipPermissions' or 'securityGroupRuleIds' should be provided." in str(e):
            return
        raise e


def revoke_security_group_egress(security_group_id, ip_permissions_egress):
    kwargs = {
        'GroupId': security_group_id,
        'IpPermissions': ip_permissions_egress,
    }
    try:
        _make_api_call(
            'revoke_security_group_egress',
            **kwargs
        )
    except Exception as e:
        if 'MissingParameter' in str(e) or "Either 'ipPermissions' or 'securityGroupRuleIds' should be provided." in str(e):
            return
        raise e


def authorize_security_group_ingress(security_group_id, ingress_permissions):
    kwargs = {
        'GroupId': security_group_id,
        'IpPermissions': ingress_permissions,
    }
    try:
        _make_api_call(
            'authorize_security_group_ingress',
            **kwargs
        )
    except Exception as e:
        if 'MissingParameter' in str(e):
            return
        raise e


def authorize_security_group_egress(security_group_id, egress_permissions):
    kwargs = {
        'GroupId': security_group_id,
        'IpPermissions': egress_permissions,
    }
    try:
        _make_api_call(
            'authorize_security_group_egress',
            **kwargs
        )
    except Exception as e:
        if 'MissingParameter' in str(e):
            return
        if 'already exists' in str(e):
            LOG.debug(f"Received non-fatal exception {str(e)} during invocation of ec2::authorize_security_group_egress.")
            return
        raise e


def get_security_group(group_name):
    try:
        response = _make_api_call(
            'describe_security_groups',
            GroupNames=[group_name]
        )
        return response['SecurityGroups'][0]
    except Exception as e:
        if 'InvalidGroup.NotFound' in str(e) or 'does not exist' in str(e):
            return None
        raise e


def _create_security_group(group_name, vpc_id, description):
    kwargs = {
        'GroupName': group_name,
        'Description': description,
    }
    if vpc_id:
        kwargs['VpcId'] = vpc_id

    response = _make_api_call(
        'create_security_group',
        **kwargs
    )

    return response['GroupId']
