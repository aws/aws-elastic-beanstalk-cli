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
    # Version message got 'eb --version'
    'app.version_message': 'EBCLI - AWS Elastic Beanstalk CLI - Version:',
    # Initial text that you see on a 'eb --help'
    'base.info': "Welcome to EB. Please "
                 "use 'eb {cmd} --help' for more info",
    # Initial epilog (last line) that you see on 'eb --help'
    'base.epilog': "To get started please use 'eb init' followed by 'eb create' and 'eb open'",

    # All .infos are for --help text. All .epilogs are the epilogs shown on the given command
    'init.info': 'Initializes your directory with eb. Sets up the app',
    'init.epilog': 'This command is safe when ran in a previously initialized'
                   ' directory. To re-initialize with different options, '
                   'use the -i flag.',
    'create.info': 'Create a new environment',
    'delete.info': 'Completely remove application and all environments in it',
    'events.info': 'Get recent events',
    'open.info': 'Opens the environment app in a browser',
    'console.info': 'Opens the Environments AWS console in a browser',
    'clone.info': 'Clone an environment',
    'logs.info': 'Get recent logs',
    'use.info': 'Set default environment',
    'logs.epilog': 'Defaults to the recent logs. If you would instead like to retrieve all the logs, please use the "--all" flag.',
    'deploy.info': 'Deploys your current branch to the environment',
    'scale.info': 'Change number of running instances',
    'status.info': 'Get Environment info and status',
    'setenv.info': 'Set environment variables',
    'list.info': 'List all environments',
    'terminate.info': 'Terminate environment',
    'terminate.epilog': 'In order to terminate the application and everything in it, use the --all flag',
    'config.info': 'Update environment configuration',
    'sync.info': 'Pull down environment configurations',
    'ssh.info': 'SSH into environment instance',

    # Error when --sample and --label falg are both used on create
    'create.sampleandlabel': 'Both sample and versionlabel cannot be used together',
    # Text shown if 'eb terminate' is called while no environment is selected as default
    'terminate.noenv': 'To delete the application and all application versions, use "eb terminate --all"',

    'cred.prompt':  'It looks like your credentials are not yet set up '
                    'or are incorrect \n'
                    'Please enter your credentials now',
    'prompt.invalid': 'Sorry, that choice is invalid.',
    'prompt.yes-or-no': 'Please enter either Y or N',
    # Default description for apps created with cli
    'app.description': 'Application created from eb-cli tool using eb init',
    # Default description for environment created with cli
    'env.description': 'Environment created from eb-cli tool using eb create',
    # Same as above but for cloned environments
    'env.clonedescription': 'Environment clone of {env-name}. Created by the eb-cli tool using eb clone',
    'env.exists': 'An environment with that name already exists, '
                  'please try another.',
    # When create is called, if we cant find any files, we say this
    'appversion.none': 'Cannot find any code. Launching Sample application.',
    # Error, no solution stacks returned. Almost always due to permissions
    'sstacks.notfound': 'No Solution Stacks found. It is possible this could '
                        'be due to a lack of permissions',
    'timeout.error': 'Unknown state of environment. Operation timed out.',
    'sc.notfound': 'No source control found. Will use system\'s zip for deploys.',
    'exit.notsetup': 'This directory does not appear to be setup with EB-CLI\n'
                     'Have you ran eb init?',
    'exit.noregion': 'A default region can not be found. Please run eb init or'
                     ' add the region using --region',
    # Typical response when an environment is in pending state
    'exit.invalidstate': 'The operation can not be completed at this time due to a pending operation. Please try again later.',
    'branch.noenv': 'No environment is registered with this branch. You must'
                    ' specify an environment, i.e. eb {cmd} my-env-name\n'
                    'Alternatively you can register an environment with "eb use my-env-name"',
    'ssh.notpresent': 'You do not seem to have ssh installed. Please install before continuing.',
    'ssh.filenotfound': 'Can not find your ssh key file for keyname "{key-name}".'
                        ' Please make sure it is located in your .ssh folder in your home directory.',
    'logs.location': 'Logs saved at {location}',
    'setenv.invalidformat': 'Must use format VAR_NAME=KEY. Variable and keys '
                            'cannot contain any spaces or =. They must start'
                            ' with a letter, number or one of \\_.:/+-@',
}
prompts = {
    'events.hanging': 'Hanging and waiting for events. Use CTRL + C to exit.',
    'platform.validate': 'It appears you are using {platform}. Is this correct?',
    'platform.prompt': 'Please choose a platform type',
    'sstack.version': 'Please choose a version',
    'init.selectdefaultenv': 'Select an environment to set as branch default. \n'
                             'Note, you can change this in the future by using "eb use [environment_name]"',
    'scale.switchtoloadbalance': 'The environment is currently a Single Instance, would you'
                                 ' like to switch to a Load Balanced environment?',
    'scale.switchtoloadbalancewarn': 'By choosing yes, the environment will terminate and your application will be temporarily unavailable.',
    'cname.unavailable': 'The CNAME you provided is currently not available.\n'
                         'Please try another',
    'delete.confirm': 'You are about to delete the application "{app-name}" and all its resources.\n'
                      'This app currently has the following,\n'
                      'Running environments: {env-num}\n'
                      'Configuration Templates: {config-num}\n'
                      'Application Versions: {version-num}\n',
    'fileopen.error1': 'Unable to open file with editor {editor}\nPlease check your settings and try again.',
    'fileopen.error2': 'Unable to open environment file. Try setting the editor environment variable',
    'update.invalidstate': 'Cannot update environment at this time. Wait for environment to finish its current operation.',
    'update.invalidsyntax': 'The updated settings contained an error. Environment will not be updated.',
    'ssh.setup': 'Would you like to set up ssh for your instances?',
    'sstack.invalid': 'Solution Stack provided is not valid. Please choose another.',
    'sstack.invalidkey': 'Solution stack not found for given key "{string}"',
    'keypair.prompt': 'Choose a keypair',
    'keypair.nameprompt': 'Enter keypair name',
    'tier.prompt': 'Please choose a tier',
    # Error given on terminate when the user input does not match name
    'terminate.nomatch': 'Names do not match. Exiting',
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
    'event.updatebad': 'Update environment operation is complete, but with errors.',
    'git.norepository': 'Error: Not a git repository '
                        '(or any of the parent directories): .git',
    'env.updatesuccess': 'Environment update completed successfully.',
    'env.cnamenotavailable': 'DNS name \([^ ]+\) is not available.',
    'env.nameexists': 'Environment [^ ]+ already exists.',
    'app.deletesuccess': 'The application has been deleted successfully.',
    'app.exists': 'Application {app-name} already exists.',
    'logs.pulled': 'Pulled logs for environment instances.',
    'logs.successtail': 'Successfully finished tailing',
    'logs.successbundle': 'Successfully finished bundling',
    'env.terminated': 'terminateEnvironment completed successfully.',
    'env.invalidstate': 'Environment named {env-name} is in an invalid state for this operation. Must be Ready.',
    'loadbalancer.notfound': 'There is no ACTIVE Load Balancer named',
}
git_ignore = [
    '# Elastic Beanstalk Files',        # comment line
    '.elasticbeanstalk/*',              # ignore eb files
    '!.elasticbeanstalk/*.env.yml',       # don't ignore shareable environments
    '!.elasticbeanstalk/*.global.yml',    # don't ignore global configurations
]
