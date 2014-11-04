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
    'app.version_message': 'EB CLI',
    # Initial text that you see on a 'eb --help'
    'base.info': "Welcome to the Elastic Beanstalk Command Line Interface (EB CLI). \n"
                 "For more information on a specific command, type 'eb {cmd} --help'.",
    # Initial epilog (last line) that you see on 'eb --help'
    'base.epilog': "To get started type 'eb init'. Then type 'eb create' and 'eb open'",

    # All .infos are for --help text. All .epilogs are the epilogs shown on the given command
    'init.info': 'Initializes your directory with the EB CLI. Creates the application.',
    'init.epilog': 'This command is safe when run in a previously initialized'
                   ' directory. To re-initialize with different options, '
                   'use the -i flag.',
    'create.info': 'Creates a new environment.',
    'events.info': 'Gets recent events.',
    'open.info': 'Opens the application URL in a browser.',
    'console.info': 'Opens the environment in the AWS Elastic Beanstalk Management Console.',
    'clone.info': 'Clones an environment.',
    'logs.info': 'Gets recent logs.',
    'use.info': 'Sets default environment.',
    'logs.epilog': 'This command displays the last 100 lines of logs. To retrieve all logs, use the "--all" flag.',
    'deploy.info': 'Deploys your source code to the environment.',
    'scale.info': 'Changes the number of running instances.',
    'status.info': 'Gets environment information and status.',
    'setenv.info': 'Sets environment variables.',
    'setenv.epilog': 'Use this command to set environment variables by typing a space-separated list of key=value pairs.\n'
                     'For example, to set HeapSize to 256m and Site_Url to mysite.elasticbeanstalk.com, type:\n'
                     '  eb setenv HeapSize=256m Site_Url=mysite.elasticbeanstalk.com\n'
                     'You can also remove environment variables by specifying no value. For example:\n'
                     '  eb setenv HeapSize= Site_Url=\n'
                     'This removes the environment variables.',
    'list.info': 'Lists all environments.',
    'terminate.info': 'Terminates the environment.',
    'terminate.epilog': 'This command terminates the environment. To terminate the application and everything in it, use the "--all" flag.',
    'config.info': 'Edits the environment configuration settings.',
    'ssh.info': 'Opens the SSH client to connect to an instance.',
    'printenv.info': 'Shows the environment variables.',

    # Error when --sample and --label falg are both used on create
    'create.sampleandlabel': 'You cannot use the "--sample" and "--version" flags together.',
    'create.singleandsize': 'You cannot use the "--single" and "--size" flags together.',
    'logs.allandzip': 'You cannot use the "--all" and "--all_zip" flags together.',
    'logs.allandinstance': 'You cannot use the "--all" and "--instance" flags together.',
    'ssh.instanceandnumber': 'You cannot use the "--instance" and "--number" flags together.',
    # Text shown if 'eb terminate' is called while no environment is selected as default
    'terminate.noenv': 'To delete the application and all application versions, type "eb terminate --all".',

    'cred.prompt':  'You have not yet set up your credentials or your credentials are incorrect \n'
                    'You must provide your credentials.',
    'prompt.invalid': 'You did not provide a valid value.',
    'prompt.yes-or-no': 'Type either "Y" or "N".',
    # Default description for apps created with cli
    'app.description': 'Application created from the EB CLI using "eb init"',
    # Default description for environment created with cli
    'env.description': 'Environment created from the EB CLI using "eb create"',
    # Same as above but for cloned environments
    'env.clonedescription': 'Environment cloned from {env-name} from the EB CLI using "eb clone"',
    'env.exists': 'An environment with that name already exists.',
    # When create is called, if we cant find any files, we say this
    'appversion.none': 'The current directory does not contain any source code. Elastic Beanstalk is launching the sample application instead.',
    # Error, no solution stacks returned. Almost always due to permissions
    'sstacks.notfound': 'Elastic Beanstalk could not find any platforms. Ensure you have the necessary permissions to access Elastic Beanstalk.',
    'timeout.error': 'The operation timed out. The state of the environment is unknown.',
    'sc.notfound': 'Git is not set up for this project. EB CLI will deploy a .zip file of the entire directory.',
    'exit.notsetup': 'This directory has not been set up with the EB CLI\n'
                     'You must first run "eb init".',
    'exit.noregion': 'The EB CLI cannot find a default region. Run "eb init" or add the region using the "--region" flag.',
    # Typical response when an environment is in pending state
    'exit.invalidstate': 'The operation cannot be completed at this time due to a pending operation. Try again later.',
    'branch.noenv': 'This branch does not have a default environment. You must either specify an environment by typing ' 
                    '"eb {cmd} my-env-name" or set a default environment by typing "eb use my-env-name".',
    'ssh.notpresent': 'SSH is not installed. You must install SSH before continuing.',
    'ssh.filenotfound': 'The EB CLI cannot find your SSH key file for keyname "{key-name}".'
                        ' Your SSH key file must be located in the .ssh folder in your home directory.',
    'logs.location': 'Logs saved to {location}',
    'setenv.invalidformat': 'You must use the format VAR_NAME=KEY to set an environment variable. Variables and keys '
                            'cannot contain any spaces or =. They must start'
                            ' with a letter, number or one of the following symbols: \\ _ . : / + - @',
    'tags.invalidformat': 'You must provide a comma-separated list using the format name=value to set tags. '
                          'Tags may only contain letters, numbers, and the following symbols: / _ . : + - @',
    'tags.max': 'Elastic Beanstalk supports a maximum of 7 tags.',
    'deploy.invalidoptions': 'You cannot use the "--version" flag with either the "--message" or "--label" flag.',
    'init.getvarsfromoldeb': 'You previous used an earlier version of eb. Getting options from .elasticbeanstalk/config.\n'
                             'Credentials will now be stored in ~/.aws/config',
    'ssh.noip': 'This instance does not have a Public IP address. This is possibly because the instance is terminating.',
    # Error thrown when someone provides a cname with a worker tier
    'worker.cname': 'Worker tiers do not support a CNAME.',
    # Error thrown when available cname is not available
    'cname.unavailable': 'The CNAME prefix {cname} is already in use.',
    'ssh.openingport': 'INFO: Attempting to open port 22.',
    'ssh.portopen': 'INFO: SSH port 22 open.',
    'ssh.closeport': 'INFO: Closed port 22 on ec2 instance security group.',
    'ssh.uploaded': 'Uploaded SSH public key for "{keyname}" into EC2 for region {region}.',
    'connection.error': 'Having trouble communicating with AWS. Please ensure the provided region is correct and you have a working internet connection.',
}

prompts = {
    'events.hanging': 'Streaming new events. Use CTRL+C to exit.',
    'platform.validate': 'It appears you are using {platform}. Is this correct?',
    'platform.prompt': 'Select a platform.',
    'sstack.version': 'Select a platform version.',
    'init.selectdefaultenv': 'Select the default environment. \n'
                             'You can change this later by typing "eb use [environment_name]".',
    'scale.switchtoloadbalance': 'The environment is currently a single-instance. Do you want'
                                 ' to change to a load-balancing environment?',
    'scale.switchtoloadbalancewarn': 'If you choose yes, the environment and your application will be temporarily unavailable.',
    'cname.unavailable': 'The CNAME you provided is already in use.\n',
    'terminate.confirm': 'The environment "{env-name}" and all associated instances will be terminated.',
    'terminate.validate': 'To confirm, type the environment name',
    'delete.confirm': 'The application "{app-name}" and all its resources will be deleted.\n'
                      'This application currently has the following:\n'
                      'Running environments: {env-num}\n'
                      'Configuration templates: {config-num}\n'
                      'Application versions: {version-num}\n',
    'delete.validate': 'To confirm, type the application name',
    'fileopen.error1': 'EB CLI cannot open the file using the editor {editor}.',
    'fileopen.error2': 'Unable to open environment file. Try setting the EDITOR environment variable.',
    'update.invalidstate': 'The environment update cannot be complete at this time. Try again later.',
    'update.invalidsyntax': 'The configuration settings you provided contain an error. The environment will not be updated.',
    'ssh.setup': 'Do you want to set up SSH for your instances?',
    'sstack.invalid': 'You specified a platform that is not valid.',
    'sstack.invalidkey': 'The EB CLI cannot find a platform for key "{string}".',
    'keypair.prompt': 'Select a keypair.',
    'keypair.nameprompt': 'Type a keypair name.',
    'tier.prompt': 'Select an environment tier.',
    # Error given on terminate when the user input does not match name
    'terminate.nomatch': 'Names do not match. Exiting.',
    'ssh.nokey': 'This environment is not set up for SSH. Use "eb ssh --setup" to set up SSH for the environment.',
    'ssh.setupwarn': 'You are about to setup SSH for environment "{env-name}". If you continue, your existing instances will have to be **terminated** and new instances will be created. The environment will be temporarily unavailable.',
    'rds.username': 'Enter an RDS DB username (default is "admin")',
    'rds.password': 'Enter an RDS DB master password',
}

flag_text = {
    # General
    'general.env': 'environment name',
    'base.version': 'show application/version info',
    'base.verbose': 'toggle verbose output',
    'base.profile': 'use a specific profile from your credential file',
    'base.region': 'use a specific region',

    # Clone
    'clone.env': 'name of environment to clone',
    'clone.name': 'desired name for environment clone',
    'clone.cname': 'cname prefix',
    'clone.scale': 'number of desired instances',
    'clone.tags': 'a comma separated list of tags as key=value pairs',
    'clone.nohang': 'return immediately, do not wait for clone to be completed',

    # Config
    'config.nohang': 'return immediately, do not wait for config to be completed',

    # Create
    'create.name': 'desired Environment name',
    'create.cname': 'cname prefix',
    'create.itype': 'instance type i.e. t1.micro',
    'create.tier': 'environment tier type',
    'create.platform': 'platform',
    'create.single': 'environment will use a single instance with no load balancer',
    'create.sample': 'use Sample Application',
    'create.default': 'set as branches default environment',
    'create.iprofile': 'EC2 Instance profile',
    'create.version': 'version label to deploy',
    'create.keyname': 'EC2 SSH KeyPair name',
    'create.scale': 'number of desired instances',
    'create.nohang': 'return immediately, do not wait for create to be completed',
    'create.tags': 'a comma separated list of tags as key=value pairs',
    'create.database': 'create a database',

    # Deploy
    'deploy.env': 'environment name',
    'deploy.version': 'existing version label to deploy',
    'deploy.label': 'label name which version will be given',
    'deploy.message': 'description for version',

    # Events
    'events.follow': 'wait and continue to print events as they come',

    # Init
    'init.name': 'application name',
    'init.platform': 'default Platform',
    'init.keyname': 'default EC2 key name',
    'init.interactive': 'force interactive mode',

    # List
    'list.all': 'show environments for all applications',

    # Logs
    'logs.all': 'retrieve all logs',
    'logs.zip': 'retrieve all logs as .zip',
    'logs.instance': 'instance id',

    # Scale
    'scale.number': 'number of desired instances',
    'scale.force': 'skip confirmation prompt',

    # Setenv
    'setenv.vars': 'space separated list in format: VAR_NAME=KEY',
    'setenv.env': 'environment name',

    # SSH
    'ssh.number': 'index of instance in list',
    'ssh.instance': 'instance id',
    'ssh.keepopen': 'keep port 22 open',
    'ssh.setup': 'setup SSH for the environment',

    # terminate
    'terminate.force': 'skip confirmation prompt',
    'terminate.all': 'terminate everything',
    'terminate.nohang': 'return immediately, do not wait for terminate to be completed',

    # use
    'use.env': 'environment name',
}


### The below are programatic and are not intended to be edited unless the service response changes
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
    'app.notexists': 'No Application named {app-name} found.',
    'logs.pulled': 'Pulled logs for environment instances.',
    'logs.successtail': 'Successfully finished tailing',
    'logs.successbundle': 'Successfully finished bundling',
    'env.terminated': 'terminateEnvironment completed successfully.',
    'env.invalidstate': 'Environment named {env-name} is in an invalid state for this operation. Must be Ready.',
    'loadbalancer.notfound': 'There is no ACTIVE Load Balancer named',
    'ec2.sshalreadyopen': 'the specified rule "peer: 0.0.0.0/0, TCP, from port: 22, to port: 22,',

}
git_ignore = [
    '# Elastic Beanstalk Files',        # comment line
    '.elasticbeanstalk/*',              # ignore eb files
    '!.elasticbeanstalk/*.cfg.yml',       # don't ignore configuration templates
    '!.elasticbeanstalk/*.global.yml',    # don't ignore global configurations
]
