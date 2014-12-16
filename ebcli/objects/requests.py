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

from ..resources.strings import strings


class CreateEnvironmentRequest(object):

    def __init__(self, app_name=None, env_name=None, cname=None, platform=None,
                 tier=None, instance_type=None, version_label=None,
                 instance_profile=None, single_instance=False, key_name=None,
                 sample_application=False, tags=None, scale=None,
                 database=None, vpc=None):
        self.app_name = app_name
        self.env_name = env_name
        self.cname = cname
        self.platform = platform
        self.tier = tier
        self.instance_type = instance_type
        self.version_label = version_label
        self.instance_profile = instance_profile
        self.single_instance = single_instance
        self.key_name = key_name
        self.sample_application = sample_application
        if self.tags is None:
            self.tags = []
        else:
            self.tags = list(tags)
        if self.database is None:
            self.database = {}
        else:
            self.database = dict(database)
        if self.vpc is None:
            self.vpc = {}
        else:
            self.vpc = dict(vpc)
        self.description = strings['env.description']
        self.scale = None
        self.option_settings = []

        if not self.app_name:
            raise TypeError(self.__class__.__name__ + ' requires key-word argument app_name')
        if not self.env_name:
            raise TypeError(self.__class__.__name__ + ' requires key-word argument env_name')

        if scale:
            if not isinstance(scale, int):
                raise TypeError('key-word argument scale must be of type int')
            else:
                self.scale = str(scale)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return self.__dict__ != other.__dict__

    def add_option_setting(self, namespace, option_name, value, resource=None):
        setting = {'Namespace': namespace,
                   'OptionName': option_name,
                   'Value': value}
        if resource:
            setting['ResourceName'] = resource

        self.option_settings.append(setting)

    def convert_to_kwargs(self):
        self.add_client_defaults()
        self.compile_database_options()
        self.compile_vpc_options()
        self.compile_common_options()
        return self.get_standard_kwargs()

    def get_standard_kwargs(self):
        kwargs = {
            'application_name': self.app_name,
            'environment_name': self.env_name,
            'option_settings': self.option_settings,
            }
        if self.platform:
            kwargs['solution_stack_name'] = self.platform.name
        if self.description:
            kwargs['description'] = self.description
        if self.cname:
            kwargs['cname_prefix'] = self.cname
        if self.version_label:
            kwargs['version_label'] = self.version_label
        if self.tags:
            kwargs['tags'] = self.tags
        if self.tier:
            kwargs['tier'] = self.tier.to_struct()

        if self.scale:
            self.add_option_setting(
                'aws:autoscaling:asg',
                'MaxSize',
                self.scale)
            self.add_option_setting(
                'aws:autoscaling:asg',
                'MinSize',
                self.scale)

        return kwargs

    def compile_common_options(self):
        if self.instance_profile:
            self.add_option_setting(
                'aws:autoscaling:launchconfiguration',
                'IamInstanceProfile',
                self.instance_profile)
        if self.instance_type:
            self.add_option_setting(
                'aws:autoscaling:launchconfiguration',
                'InstanceType',
                self.instance_type)
        if self.single_instance:
            self.add_option_setting(
                'aws:elasticbeanstalk:environment',
                'EnvironmentType',
                'SingleInstance')
        if self.key_name:
            self.add_option_setting(
                'aws:autoscaling:launchconfiguration',
                'EC2KeyName',
                self.key_name)

    def add_client_defaults(self):
        self.add_option_setting(
            'aws:elasticbeanstalk:command',
            'BatchSize',
            '30')
        self.add_option_setting(
            'aws:elasticbeanstalk:command',
            'BatchSizeType',
            'Percentage')
        if not self.tier or self.tier.name.lower() != 'worker':
            self.add_option_setting(
                'aws:elb:policies',
                'ConnectionDrainingEnabled',
                'true')
            self.add_option_setting(
                'aws:elb:healthcheck',
                'Interval',
                '30')
            self.add_option_setting(
                'aws:elb:loadbalancer',
                'CrossZone',
                'true')

    def compile_database_options(self):
        if not self.database:
            return

        namespace = 'aws:rds:dbinstance'
        self.add_option_setting(namespace, 'DBPassword',
                                self.database['password'])
        self.add_option_setting(namespace, 'DBUser', self.database['username'])
        if self.database['instance']:
            self.add_option_setting(namespace, 'DBInstanceClass',
                                    self.database['instance'])
        if self.database['size']:
            self.add_option_setting(namespace, 'DBAllocatedStorage',
                                    self.database['size'])
        if self.database['engine']:
            self.add_option_setting(namespace, 'DBEngine',
                                    self.database['engine'])
        self.add_option_setting(namespace, 'DBDeletionPolicy', 'Snapshot')

    def compile_vpc_options(self):
        if not self.vpc:
            return

        namespace = 'aws:ec2:vpc'
        self.add_option_setting(namespace, 'VPCId', self.vpc['id'])
        self.add_option_setting(namespace, 'AssociatePublicIpAddress',
                                self.vpc['publicip'])
        self.add_option_setting(namespace, 'ELBScheme', self.vpc['elbscheme'])
        if self.vpc['elbsubnets']:
            self.add_option_setting(namespace, 'ELBSubnets',
                                    self.vpc['elbsubnets'])
        if self.vpc['ec2subnets']:
            self.add_option_setting(namespace, 'Subnets',
                                    self.vpc['ec2subnets'])
        if self.vpc['securitygroups']:
            self.add_option_setting('aws:autoscaling:launchconfiguration',
                                    'SecurityGroups',
                                    self.vpc['securitygroups'])
        if self.vpc['dbsubnets']:
            self.add_option_setting(namespace, 'DBSubnets',
                                    self.vpc['dbsubnets'])


class CloneEnvironmentRequest(CreateEnvironmentRequest):
    def __init__(self, app_name=None, env_name=None, original_name=None,
                 cname=None, platform=None, scale=None, tags=None):
        if not original_name:
            raise TypeError(self.__class__.__name__ + ' requires key-word argument clone_name')
        self.original_name = original_name
        super(CloneEnvironmentRequest, self).__init__(
            app_name=app_name, env_name=env_name, cname=cname,
            platform=platform, scale=scale, tags=tags
        )
        self.description = strings['env.clonedescription']. \
            replace('{env-name}', self.env_name)

    def convert_to_kwargs(self):
        return self.get_standard_kwargs()