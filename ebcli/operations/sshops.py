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

import subprocess
import os

from cement.utils.misc import minimal_logger

from ..lib import ec2, utils
from ..objects.exceptions import NoKeypairError, NotFoundError, CommandError
from ..resources.strings import strings, prompts
from ..core import io, fileoperations
from . import commonops


LOG = minimal_logger(__name__)


def ssh_into_instance(instance_id, keep_open=False, force_open=False):
    instance = ec2.describe_instance(instance_id)
    try:
        keypair_name = instance['KeyName']
    except KeyError:
        raise NoKeypairError()
    try:
        ip = instance['PublicIpAddress']
    except KeyError:
        raise NotFoundError(strings['ssh.noip'])
    security_groups = instance['SecurityGroups']

    user = 'ec2-user'

    # Get security group to open
    ssh_group = None
    has_restriction = False
    group_id = None
    for group in security_groups:
        group_id = group['GroupId']
        # see if group has ssh rule
        group = ec2.describe_security_group(group_id)
        for permission in group.get('IpPermissions', []):
            if permission.get('ToPort', None) == 22:
                # SSH Port group
                ssh_group = group_id
                for rng in permission.get('IpRanges', []):
                    ip_restriction = rng.get('CidrIp', None)
                    if ip_restriction is not None \
                            and ip_restriction != '0.0.0.0/0':
                        has_restriction = True

    if has_restriction and not force_open:
        io.log_warning(strings['ssh.notopening'])
    elif group_id:
        # Open up port for ssh
        io.echo(strings['ssh.openingport'])
        ec2.authorize_ssh(ssh_group or group_id)
        io.echo(strings['ssh.portopen'])

    # do ssh
    try:
        ident_file = _get_ssh_file(keypair_name)
        returncode = subprocess.call(['ssh', '-i', ident_file,
                                      user + '@' + ip])
        if returncode != 0:
            LOG.debug('ssh returned exitcode: ' + str(returncode))
            raise CommandError('An error occurred while running ssh.')
    except OSError:
        CommandError(strings['ssh.notpresent'])
    finally:
        # Close port for ssh
        if keep_open:
            pass
        elif (not has_restriction or force_open) and group_id:
            ec2.revoke_ssh(ssh_group or group_id)
            io.echo(strings['ssh.closeport'])


def _get_ssh_file(keypair_name):
    key_file = fileoperations.get_ssh_folder() + keypair_name
    if not os.path.exists(key_file):
        if os.path.exists(key_file + '.pem'):
            key_file += '.pem'
        else:
            raise NotFoundError(strings['ssh.filenotfound'].replace(
                '{key-name}', keypair_name))

    return key_file


def prompt_for_ec2_keyname(env_name=None):
    if env_name:
        io.validate_action(prompts['terminate.validate'], env_name)
    else:
        io.echo(prompts['ssh.setup'])
        ssh = io.get_boolean_response()
        if not ssh:
            return None

    keys = [k['KeyName'] for k in ec2.get_key_pairs()]

    if len(keys) < 1:
        keyname = _generate_and_upload_keypair(keys)

    else:
        new_key_option = '[ Create new KeyPair ]'
        keys.append(new_key_option)
        io.echo()
        io.echo(prompts['keypair.prompt'])
        keyname = utils.prompt_for_item_in_list(keys, default=len(keys))

        if keyname == new_key_option:
            keyname = _generate_and_upload_keypair(keys)

    return keyname


def _generate_and_upload_keypair(keys):
    # Get filename
    io.echo()
    io.echo(prompts['keypair.nameprompt'])
    unique = utils.get_unique_name('aws-eb', keys)
    keyname = io.prompt('Default is ' + unique, default=unique)
    file_name = fileoperations.get_ssh_folder() + keyname

    try:
        exitcode = subprocess.call(
            ['ssh-keygen', '-f', file_name, '-C', keyname]
        )
    except OSError:
        raise CommandError(strings['ssh.notpresent'])

    if exitcode == 0 or exitcode == 1:
        # if exitcode is 1, they file most likely exists, and they are
        ## just uploading it
        commonops.upload_keypair_if_needed(keyname)
        return keyname
    else:
        LOG.debug('ssh-keygen returned exitcode: ' + str(exitcode) +
                  ' with filename: ' + file_name)
        raise CommandError('An error occurred while running ssh-keygen.')