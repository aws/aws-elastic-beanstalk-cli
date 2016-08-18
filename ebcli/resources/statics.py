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


class namespaces(object):
    AUTOSCALING = 'aws:autoscaling:asg'
    COMMAND = 'aws:elasticbeanstalk:command'
    RDS = 'aws:rds:dbinstance'
    ENVIRONMENT = 'aws:elasticbeanstalk:environment'
    HEALTH_CHECK = 'aws:elb:healthcheck'
    HEALTH_SYSTEM = 'aws:elasticbeanstalk:healthreporting:system'
    LAUNCH_CONFIGURATION = 'aws:autoscaling:launchconfiguration'
    LOAD_BALANCER = 'aws:elb:loadbalancer'
    ELB_POLICIES = 'aws:elb:policies'
    ROLLING_UPDATES = 'aws:autoscaling:updatepolicy:rollingupdate'
    VPC = 'aws:ec2:vpc'


class option_names(object):
    BATCH_SIZE = 'BatchSize'
    BATCH_SIZE_TYPE = 'BatchSizeType'
    CONNECTION_DRAINING = 'ConnectionDrainingEnabled'
    CROSS_ZONE = 'CrossZone'
    DB_DELETION_POLICY = 'DBDeletionPolicy'
    DB_ENGINE = 'DBEngine'
    DB_ENGINE_VERSION = 'DBEngineVersion'
    DB_INSTANCE = 'DBInstanceClass'
    DB_PASSWORD = 'DBPassword'
    DB_STORAGE_SIZE = 'DBAllocatedStorage'
    DB_SUBNETS = 'DBSubnets'
    DB_USER = 'DBUser'
    EC2_KEY_NAME = 'EC2KeyName'
    ELB_SCHEME = 'ELBScheme'
    ELB_SUBNETS = 'ELBSubnets'
    ENVIRONMENT_TYPE = 'EnvironmentType'
    IAM_INSTANCE_PROFILE = 'IamInstanceProfile'
    INSTANCE_TYPE = 'InstanceType'
    INTERVAL = 'Interval'
    LOAD_BALANCER_HTTP_PORT = 'LoadBalancerHTTPPort'
    LOAD_BALANCER_HTTPS_PORT = 'LoadBalancerHTTPSPort'
    LOAD_BALANCER_TYPE = 'LoadBalancerType'
    MAX_SIZE = 'MaxSize'
    MIN_SIZE = 'MinSize'
    PUBLIC_IP = 'AssociatePublicIpAddress'
    ROLLING_UPDATE_ENABLED = 'RollingUpdateEnabled'
    ROLLING_UPDATE_TYPE = 'RollingUpdateType'
    SECURITY_GROUPS = 'SecurityGroups'
    SERVICE_ROLE = 'ServiceRole'
    SUBNETS = 'Subnets'
    SSL_CERT_ID = 'SSLCertificateId'
    SYSTEM_TYPE = 'SystemType'
    VPC_ID = 'VPCId'


class elb_names(object):
    HEALTHY_STATE = 'healthy'
    UNHEALTHY_STATE = 'unhealthy'
    V2_RESOURCE_TYPE = 'AWS::ElasticLoadBalancingV2::TargetGroup'
    DEFAULT_PROCESS_LOGICAL_ID = 'AWSEBV2LoadBalancerTargetGroup'
    CLASSIC_VERSION = 'classic'
    APPLICATION_VERSION = 'application'
