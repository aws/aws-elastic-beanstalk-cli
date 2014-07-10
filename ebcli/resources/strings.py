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
    'status.info': 'Status stuff',
    'terminate.info': 'Stop stuff',
    'update.info': 'Update environment',
    'config.info' : 'Configure your environment',
    'error.nocreds': 'A credentials file can not be found. \n'
                     'Please place a credential file at ~/.awskeys'
}

responses = {
    'event.greenmessage': 'Environment health has been set to GREEN'
}