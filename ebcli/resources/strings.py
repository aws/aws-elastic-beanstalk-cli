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

strings = {
    'app.version_message': 'EBCLI - AWS Elastic Beanstalk CLI - Version:',
    'base.info': 'Welcome to EB. Please '
                 'see below for a list of available commands.',
    'init.info': 'Initializes your directory with eb. '
                 'Sets up the environment',
    'create.info': 'Create a new environment',
    'delete.info': 'Delete your application and all environments in it',
    'events.info': 'Get recent events',
    'import.info': 'Import an old configuration of eb',
    'logs.info': 'Get recent logs',
    'deploy.info': 'Deploys your current branch to the environment',
    'status.info': 'Get Environment info and status',
    'terminate.info': 'Stop stuff',
    'update.info': 'Update environment',
    'config.info': 'Configure your environment',
    'error.nocreds': 'A credentials file can not be found. \n'
                     'Please place a credential file at ~/.aws/config',
    'cred.prompt':  'It looks like your credentials are not yet set up \n'
                    'Please enter your credentials now',
    'prompt.invalid': 'Sorry, that choice is invalid.',
    'prompt.yes-or-no': 'Please enter either Y or N',
    'app.description': 'Application created from eb-cli tool using eb init',
    'env.description': 'Environment created from eb-cli tool using eb create',
    'env.exists': 'An environment with that name already exists, '
                  'please try another.',
    'git.notfound': 'Git does not seem to be installed. '
                     'Have you ran git init?',
    'exit.notsetup': 'This directory does not appear to be setup with EB-CLI\n'
                     'Have you ran eb init?',
    'exit.noregion': 'A default region can not be found. Please run eb init or'
                     ' add the region using --region',

}

responses = {
    'event.redmessage': 'Environment health has been set to RED',
    'evnt.redtoyellowmessage': 'Environment health has transitioned '
                               'from YELLOW to RED',
    'event.yellowmessage': 'Environment health has been set to YELLOW',
    'event.greenmessage': 'Environment health has been set to GREEN',
    'event.launchsuccess': 'Successfully launched environment:',
    'git.norepository': 'Error: Not a git repository ' \
                        '(or any of the parent directories): .git',
    'env.cnamenotavailable': 'DNS name \([a-zA-Z-]+\) is not available.',
    'env.nameexists': 'Environment [^ ]+ already exists.',
}
git_ignore = [
    '# Elastic Beanstalk Files',        # comment line
    '.elasticbeanstalk/*',              # ignore eb files
    '!.elasticbeanstalk/*.ebe.*',       # don't ignore shareable environments
    '!.elasticbeanstalk/*.global.*',    # don't ignore global configurations
]
