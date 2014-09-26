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
    'base.info': "Welcome to EB. Please "
                 "use 'eb {cmd} --help' for more info",
    'base.epilog': "To get started please use 'eb init' followed by 'eb create' and 'eb open'",
    'init.info': 'Initializes your directory with eb. '
                 'Sets up the app',
    'create.info': 'Create a new environment',
    'delete.info': 'Completely remove application and all environments in it',
    'events.info': 'Get recent events',
    'open.info': 'Opens the environment app in a browser',
    'console.info': 'Opens the Environments AWS console in a browser',
    'logs.info': 'Get recent logs',
    'deploy.info': 'Deploys your current branch to the environment',
    'scale.info': 'Change number of running instances',
    'status.info': 'Get Environment info and status',
    'setenv.info': 'Set environment variables',
    'list.info': 'List all environments',
    'terminate.info': 'Terminate environment',
    'update.info': 'Update environment',
    'sync.info': 'Pull down environment configurations',
    'config.info': 'Config stuff',
    'error.nocreds': 'A credentials file can not be found. \n'
                     'Please place a credential file at ~/.aws/config',
    'cred.prompt':  'It looks like your credentials are not yet set up '
                    'or are incorrect \n'
                    'Please enter your credentials now',
    'prompt.invalid': 'Sorry, that choice is invalid.',
    'prompt.yes-or-no': 'Please enter either Y or N',
    'app.description': 'Application created from eb-cli tool using eb init',
    'env.description': 'Environment created from eb-cli tool using eb create',
    'env.exists': 'An environment with that name already exists, '
                  'please try another.',
    'sstacks.notfound': 'No Solution Stacks found. It is possible this could '
                        'be due to a lack of permissions',
    'timeout.error': 'Unknown state of environment. Operation timed out.',
    'sc.notfound': 'No source control found. '
                     'Will use system\'s zip for deploys.',
    'exit.notsetup': 'This directory does not appear to be setup with EB-CLI\n'
                     'Have you ran eb init?',
    'exit.noregion': 'A default region can not be found. Please run eb init or'
                     ' add the region using --region',
    'branch.noenv': 'No environment is registered with this branch. You must'
                    ' specify an environment, i.e. eb {cmd} envName',
    'init.epilog': 'This command is safe when ran in a previously initialized'
                   ' directory. To re-initialize with different options, '
                   'use the -i flag.',
    'env.updatesuccess': '-- The environment has been updated successfully! --',
    'env.createsuccess': '-- The environment has been created successfully! --',
    'env.createstarted': '-- The environment is being created. --',
    'env.updatestarted': '-- The environment is being updated. --',
}
prompts = {
    'events.hanging': 'Hanging and waiting for events. Use CTRL + C to exit.',
    'platform.validate': 'It appears you are using {platform}. Is this correct?',
    'platform.prompt': 'Please choose a platform type',
    'sstack.version': 'Please choose a version',
    'scale.switchtoloadbalance': 'The environment is currently a Single Instance, would you'
                                 ' like to switch to a Load Balanced environment?',
    'cname.unavailable': 'The CNAME you provided is currently not available.\n'
                         'Please try another',
    'delete.confirm': 'This application has currently running environments, '
                      'if you delete it, all environments will be terminated. '
                      'Are you sure you want to delete the application?',
    'fileopen.error1': 'Unable to open file with editor {editor}\nPlease check your settings and try again.',
    'fileopen.error2': 'Unable to open environment file. Try setting the editor environment variable',
    'update.invalidstate': 'Cannot update environment at this time. Wait for environment to finish its current operation.',
    'sstack.invalid': 'Solution Stack provided is not valid. Please choose another.',
}

responses = {
    'event.redmessage': 'Environment health has been set to RED',
    'event.redtoyellowmessage': 'Environment health has transitioned '
                               'from YELLOW to RED',
    'event.yellowmessage': 'Environment health has been set to YELLOW',
    'event.greenmessage': 'Environment health has been set to GREEN',
    'event.launchsuccess': 'Successfully launched environment:',
    'event.launchbad': 'Create environment operation is CompleterController, '
                       'but with errors',
    'git.norepository': 'Error: Not a git repository ' \
                        '(or any of the parent directories): .git',
    'env.updatesuccess': 'Environment update completed successfully.',
    'env.cnamenotavailable': 'DNS name \([^ ]+\) is not available.',
    'env.nameexists': 'Environment [^ ]+ already exists.',
    'app.deletesuccess': 'The application has been deleted successfully.',
    'logs.pulled': 'Pulled logs for environment instances.',
    'env.terminated': 'terminateEnvironment completed successfully.',
    'env.invalidstate': 'Environment named {env-name} is in an invalid state for this operation. Must be Ready.'
}
git_ignore = [
    '# Elastic Beanstalk Files',        # comment line
    '.elasticbeanstalk/*',              # ignore eb files
    '!.elasticbeanstalk/*.ebe.*',       # don't ignore shareable environments
    '!.elasticbeanstalk/*.global.*',    # don't ignore global configurations
]
