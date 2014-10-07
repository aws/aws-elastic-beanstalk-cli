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
from ebcli.lib import elasticbeanstalk, utils
from ebcli.objects.exceptions import NotFoundError
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
            (['-i', '--instance_profile'], dict(help='Instance profile')),
            (['-vl', '--versionlabel'], dict(help='Version label to deploy')),
            (['-k', '--keyname'], dict(help='EC2 SSH KeyPair name')),
            (['-nh', '--nohang'], dict(action='store_true',
                                       help='Do not hang and wait for create '
                                            'to be completed')),
        ]
        usage = 'eb create [options ...]'

    def do_command(self):
        # save command line args
        env_name = self.app.pargs.env
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
        provided_env_name = env_name is not None

        if sample and label:
            io.log_error(strings['create.sampleandlabel'])
            return

        app_name = self.get_app_name()
        region = self.get_region()

        #load solution stack
        if not solution_string:
            solution_string = fileoperations.get_default_solution_stack()

        # Test out sstack and tier before we ask any questions (Fast Fail)
        if solution_string:
            try:
                solution = operations.get_solution_stack(solution_string,
                                                               region)
            except NotFoundError:
                raise NotFoundError('Solution stack ' + solution_string +
                                    ' does not appear to be valid')

        if tier:
            try:
                tier = Tier.parse_tier(tier)
            except NotFoundError:
                raise NotFoundError('Provided tier ' + tier + ' does not '
                                    'appear to be valid')

        # If we still dont have what we need, ask for it
        if not env_name:
            # default is app-name plus '-dev'
            default_name = app_name + '-dev'
            current_environments = operations.get_env_names(app_name, region)
            unique_name = utils.get_unique_name(default_name,
                                                current_environments)
            env_name = io.prompt_for_environment_name(unique_name)

        if not cname and not provided_env_name:
            cname = get_cname(region)

        if not solution:
            solution = operations.prompt_for_solution_stack(region)

        if not tier:
            tier = operations.select_tier()

        if not key_name:
            key_name = fileoperations.get_default_keyname()

        operations.make_new_env(app_name, env_name, region, cname, solution,
                                tier, label, profile, single, key_name,
                                branch_default, sample, nohang)

    def complete_command(self, commands):
        region = fileoperations.get_default_region()
        app_name = fileoperations.get_application_name()

        self.complete_region(commands)

        # We only care about top command, because there are no positional
        ## args for this command
        cmd = commands[-1]
        if cmd in ['-t', '--tier']:
            io.echo(*Tier.get_all_tiers())
        if cmd in ['-s', '--solution']:
            io.echo(*elasticbeanstalk.get_available_solution_stacks(region))
        if cmd in ['-vl', '--versionlabel']:
            io.echo(*operations.get_app_version_labels(app_name, region))


def get_cname(region):
    while True:
        cname = io.prompt_for_cname()
        if not cname:
            # Reverting to default
            break
        if not operations.is_cname_available(cname, region):
            io.echo('That cname is not available. '
                    'Please choose another')
        else:
            break
    return cname