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

import re
import argparse

from ..core.abstractcontroller import AbstractBaseController
from ..resources.strings import strings, prompts
from ..lib import elasticbeanstalk, utils
from ..objects.exceptions import NotFoundError, AlreadyExistsError, \
    InvalidOptionsError
from ..core import io, fileoperations, operations
from ..objects.tier import Tier


class CreateController(AbstractBaseController):
    class Meta:
        label = 'create'
        description = strings['create.info']
        arguments = [
            (['environment_name'], dict(action='store', nargs='?',
                                        default=None,
                                        help='Desired Environment name')),
            (['-r', '--region'], dict(help='Region which environment '
                                           'will be created in')),
            (['-c', '--cname'], dict(help='Cname prefix')),
            (['-t', '--tier'], dict(help='Environment tier type')),
            (['-i', '--instance_type'], dict(help='Instance Type '
                                                  'i.e. t1.micro')),
            (['-s', '--solution'], dict(help='Solution stack')),
            (['--single'], dict(action='store_true',
                                help='Environment will use a Single '
                                     'Instance with no Load Balancer')),
            (['--sample'], dict(action='store_true',
                                help='Use Sample Application')),
            (['-d', '--branch_default'], dict(action='store_true',
                                              help='Set as branches default '
                                                   'environment')),
            (['-ip', '--instance_profile'], dict(help='EC2 Instance profile')),
            (['--version'], dict(help='Version label to deploy')),
            (['-k', '--keyname'], dict(help='EC2 SSH KeyPair name')),
            (['--size'], dict(type=int, help='Number of desired instances')),
            (['-nh', '--nohang'], dict(action='store_true',
                                       help='Do not hang and wait for create '
                                            'to be completed')),
            (['--tags'], dict(help='A semi-colon separated list of tags '
                                   'as key=value pairs')),
            (['-db', '--database'], dict(action="store_true",
                                         help='Create a Database')),
            ## Add addition hidden db commands
            (['-db.user', '--database.username'], dict(dest='db_user',
                                                   help=argparse.SUPPRESS)),
            (['-db.pass', '--database.password'],
                dict(dest='db_pass', help=argparse.SUPPRESS)),
            (['-db.i', '--database.instance'],
                dict(dest='db_instance', help=argparse.SUPPRESS)),
            (['-db.size', '--database.size'],
                dict(dest='db_size', help=argparse.SUPPRESS)),
            (['-db.engine', '--database.engine'],
                dict(dest='db_engine', help=argparse.SUPPRESS)),
        ]

    def do_command(self):
        # save command line args
        env_name = self.app.pargs.environment_name
        cname = self.app.pargs.cname
        tier = self.app.pargs.tier
        itype = self.app.pargs.instance_type
        solution_string = self.app.pargs.solution
        single = self.app.pargs.single
        iprofile = self.app.pargs.instance_profile
        label = self.app.pargs.version
        branch_default = self.app.pargs.branch_default
        key_name = self.app.pargs.keyname
        sample = self.app.pargs.sample
        nohang = self.app.pargs.nohang
        tags = self.app.pargs.tags
        size = self.app.pargs.size


        provided_env_name = env_name is not None

        if sample and label:
            raise InvalidOptionsError(strings['create.sampleandlabel'])

        app_name = self.get_app_name()
        region = self.get_region()

        # get tags
        tags = self.get_and_validate_tags(tags)

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
            if 'worker' in tier.lower() and cname:
                raise InvalidOptionsError(strings['worker.cname'])
            try:
                tier = Tier.parse_tier(tier)
            except NotFoundError:
                raise NotFoundError('Provided tier ' + tier + ' does not '
                                    'appear to be valid')

        if cname:
            if not operations.is_cname_available(cname, region):
                raise AlreadyExistsError(strings['cname.unavailable'].
                                         replace('{cname}', cname))

        # If we still dont have what we need, ask for it
        if not env_name:
            # default is app-name plus '-dev'
            default_name = app_name + '-dev'
            current_environments = operations.get_env_names(app_name, region)
            unique_name = utils.get_unique_name(default_name,
                                                current_environments)
            env_name = io.prompt_for_environment_name(unique_name)

        if not tier or tier.name.lower() == 'webserver':
            if not cname and not provided_env_name:
                cname = get_cname(env_name, region)
            elif not cname:
                cname = env_name
                if not operations.is_cname_available(cname, region):
                    raise AlreadyExistsError(strings['cname.unavailable'].
                                             replace('{cname}', cname))

        if not solution:
            solution = operations.prompt_for_solution_stack(region)

        # if not tier:
        #     tier = operations.select_tier()

        if not key_name:
            key_name = fileoperations.get_default_keyname()


        database = self.form_database_object()


        operations.make_new_env(app_name, env_name, region, cname, solution,
                                tier, itype, label, iprofile, single, key_name,
                                branch_default, sample, tags, size,
                                database, nohang)

    def get_and_validate_tags(self, tags):
        if not tags:
            return []

        tags = tags.strip().strip('"').strip('\'')
        tags = tags.split(';')
        tag_list = []
        if len(tags) > 7:
            raise InvalidOptionsError(strings['tags.max'])
        for t in tags:
            # validate
            if not re.match('^[\w.:/+@-]+=[\w.:/+@-]+$', t):
                raise InvalidOptionsError(strings['tags.invalidformat'])
            else:
                # build tag
                key, value = t.split('=')
                tag_list.append(
                    {'Key': key,
                     'Value': value}
                )
        return tag_list

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

    def form_database_object(self):
        create_db = self.app.pargs.database
        username = self.app.pargs.db_user
        password = self.app.pargs.db_pass
        engine = self.app.pargs.db_engine
        size = self.app.pargs.db_size
        instance = self.app.pargs.db_instance

        # Do we want a database?
        if create_db or username or password or engine or size or instance:
            db_object = dict()
            if not username:
                io.echo()
                username = io.get_input(prompts['rds.username'],
                                        default='admin')
            if not password:
                password = io.get_pass(prompts['rds.password'])
            db_object['username'] = username
            db_object['password'] = password
            db_object['engine'] = engine
            db_object['size'] = size
            db_object['instance'] = instance
            return db_object
        else:
            return False






def get_cname(env_name, region):
    while True:
        cname = io.prompt_for_cname(default=env_name)
        if not cname:
            # Reverting to default
            break
        if not operations.is_cname_available(cname, region):
            io.echo('That cname is not available. '
                    'Please choose another')
        else:
            break
    return cname