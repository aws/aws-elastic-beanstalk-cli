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

import time
import sys

from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.resources.strings import strings
from ebcli.lib import elasticbeanstalk, iam
from ebcli.objects.exceptions import NotFoundException, NotInitializedError
from ebcli.core import io, fileoperations, operations
from ebcli.objects.tier import Tier


class CreateController(AbstractBaseController):
    class Meta:
        label = 'create'
        description = strings['create.info']
        arguments = [
            (['-e', '--env_name'], dict(dest='env', help='Environment name')),
            (['-r', '--region'], dict(help='Region which environment '
                                           'will be created in')),
            (['-c', '--cname'], dict(help='Cname prefix')),
            (['-t', '--tier'], dict(help='Environment tier type')),
            (['-s', '--solution'], dict(help='Solution stack')),
            (['--single'], dict(action='store_true',
                                help='Environment will use a Single '
                                     'Instance with no Load Balancer')),
            (['--sample'], dict(action='store_true',
                                help='Use Sample Application')),
            (['-d', '--branch_default'], dict(action='store_true',
                                              help='Set as branches default '
                                                   'environment')),
            (['-p', '--profile'], dict(help='Instance profile')),
            (['-vl', '--versionlabel'], dict(help='Version label to deploy')),
            (['-k', '--keyname'], dict(help='EC2 SSH KeyPair name')),
            (['-nh', '--nohang'], dict(action='store_true',
                                       help='Do not hang and wait for create '
                                            'to be CompleterController')),
        ]
        usage = 'eb create [options ...]'


    def do_command(self):
        env_name = self.app.pargs.env
        region = self.app.pargs.region
        cname = self.app.pargs.cname
        tier = self.app.pargs.tier
        solution_string = self.app.pargs.solution
        single = self.app.pargs.single
        profile = self.app.pargs.profile
        label = self.app.pargs.versionlabel
        branch_default = self.app.pargs.branch_default
        key_name = self.app.pargs.keyname
        sample = self.app.pargs.sample
        nohang = self.app.pargs.nohang


        # get application name
        app_name = fileoperations.get_application_name()

        #load default region
        if not region:
            region = fileoperations.get_default_region()

        #load solution stack
        if not solution_string:
            solution_string = fileoperations.get_default_solution_stack()

        # Test out solution stack before we ask any questions (Fast Fail)
        if solution_string:
            try:
                solution = elasticbeanstalk.get_solution_stack(solution_string,
                                                               region)
            except NotFoundException:
                io.log_error('Could not find specified solution stack')
                sys.exit(127)

        if tier:
            try:
                tier = Tier.parse_tier(tier)
            except NotFoundException:
                io.log_error('Provided tier does not appear to be valid')
                sys.exit(127)

        if not env_name:
            # default is app-name plus '-dev'
            default_name = app_name + '-dev'
            env_name = io.prompt_for_environment_name(default_name)

        if not cname:
            cname = io.prompt_for_cname()
            while cname and \
                    (not elasticbeanstalk.is_cname_available(cname, region)):
                io.echo('That cname is not available. '
                        'Please choose another')
                cname = io.prompt_for_cname()

        if not solution_string:
            solution = operations.prompt_for_solution_stack(region)

        if not tier:
            tier = elasticbeanstalk.select_tier()

        if not label:
            # Default to service, will launch sample app
            pass

        if not profile:
            # Default to service
            pass

        operations.make_new_env(app_name, env_name, region, cname, solution,
                                tier, label, profile, single, key_name,
                                branch_default, sample, nohang)