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
    # When an update is available on PyPi
    'base.update_available': 'An update to the EB CLI is available. '
                             'Run "pip install --upgrade awsebcli" to get the latest version.',
    # Initial text that you see on a 'eb --help'
    'base.info': 'Welcome to the Elastic Beanstalk Command Line Interface (EB CLI). \n'
                 'For more information on a specific command, type "eb {cmd} --help".',
    # Initial epilog (last line) that you see on 'eb --help'
    'base.epilog': 'To get started type "eb init". Then type "eb create" and "eb open"',

    # All .infos are for --help text. All .epilogs are the epilogs shown on the given command
    'init.info': 'Initializes your directory with the EB CLI. Creates the application.',
    'init.epilog': 'This command is safe when run in a previously initialized'
                   ' directory. To re-initialize with different options, '
                   'use the -i option.',
    'init.dir.notexists': 'The specified directory {dir} does not exist. Please ensure that you are specifying the proper directory.',
    'init.usingenvyamlplatform': 'Using platform specified in env.yaml: {platform}',
    'create.info': 'Creates a new environment.',
    'create.epilog': 'Type "--vpc." or "--database." for more VPC and database options.',
    'create.missinggroup': 'A group name is required when creating multiple environments. Please use the --group option.',
    'events.info': 'Gets recent events.',
    'open.info': 'Opens the application URL in a browser.',
    'console.info': 'Opens the environment in the AWS Elastic Beanstalk Management Console.',
    'clone.info': 'Clones an environment.',
    'clone.epilog': 'This command clones your environment and attempts to upgrade the platform to the latest version.\n'
                    'To create a clone with the same platform version, use the "--exact" option.',
    'abort.info': 'Cancels an environment update or deployment.',
    'logs.info': 'Gets recent logs.',
    'use.info': 'Sets default environment.',
    'health.info': 'Shows detailed environment health.',
    'logs.epilog': 'This command displays the last 100 lines of logs. To retrieve all logs, use the "--all" option.',
    'deploy.info': 'Deploys your source code to the environment.',
    'platform.info': 'Manages platforms.',
    'platformshow.info': 'Shows information about current platform.',
    'platformlist.info': 'Lists available platforms.',
    'platformselect.info': 'Selects a default platform.',
    'platformselect.epilog': 'This command is an alternative to "eb init -i" and "eb init -p". It does not change the platform on any existing environments.\n'
                             'To upgrade an environment\'s platform, type:\n'
                             '    eb upgrade',
    'platformlist.epilog': 'Shows a list of platforms for use with "eb init -p". Type "--verbose" to get the full platform name.',
    'upgrade.info': 'Updates the environment to the most recent platform version.',
    'scale.info': 'Changes the number of running instances.',
    'status.info': 'Gets environment information and status.',
    'setenv.info': 'Sets environment variables.',
    'setenv.epilog': 'Use this command to set environment variables by typing a space-separated list of key=value pairs.\n'
                     'For example, to set HeapSize to 256m and Site_Url to mysite.elasticbeanstalk.com, type:\n'
                     '  eb setenv HeapSize=256m Site_Url=mysite.elasticbeanstalk.com\n'
                     'You can also remove environment variables by specifying no value. For example:\n'
                     '  eb setenv HeapSize= Site_Url=\n'
                     'This removes the environment variables.',
    'swap.info': 'Swaps two environment CNAMEs with each other.',
    'config.epilog': 'Use this command to work with environment configuration settings. \n'
                     'To update your environment directly in an interactive editor, type:\n'
                     '  eb config\n',
    'config.notfound': 'Elastic Beanstalk could not find any saved configuration with the name "{config-name}".',
    'config.envyamlexists': 'It appears your environment is using an env.yaml file. Be aware that a saved configuration will take precedence over the contents of your env.yaml file when both are present.',
    'list.info': 'Lists all environments.',
    'terminate.info': 'Terminates the environment.',
    'terminate.epilog': 'This command terminates the environment. To terminate the application and everything in it, use the "--all" option.',
    'config.info': "Modify an environment's configuration. Use subcommands to manage saved configurations.",
    'ssh.info': 'Opens the SSH client to connect to an instance.',
    'printenv.info': 'Shows the environment variables.',
    'local.info': 'Runs commands on your local machine.',
    'local.printenv.info': 'Shows local environment variables.',
    'local.run.info': 'Runs the Docker container on your local machine.',
    'local.setenv.info': 'Sets local environment variables.',
    'local.logs.info': 'Prints where logs are locally saved.',
    'local.open.info': 'Opens the application URL in a browser.',
    'local.status.info': 'Gets container information and status.',
    'local.setenv.epilog': 'Use this command to set environment variables by typing a space-separated list of key=value pairs.',
    # Error when --sample and --label flag are both used on create
    'create.sampleandlabel': 'You cannot use the "--sample" and "--version" options together.',
    'create.singleandsize': 'You cannot use the "--single" and "--scale" options together.',
    'create.appdoesntexist': 'The specified app {app_name} does not exist. Skipping.',
    'create.missinggroupsuffix': 'The environment name specified in env.yaml ends with a \'+\', but no group suffix was provided. Please pass the --env-group-suffix argument.',
    'appversion.create': 'Creating application version archive "{version}".',
    'logs.allandzip': 'You cannot use the "--all" and "--all_zip" options together.',
    'logs.allandinstance': 'You cannot use the "--all" and "--instance" options together.',
    'ssh.instanceandnumber': 'You cannot use the "--instance" and "--number" options together.',
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
    # Default template description
    'template.description': 'Configuration created from the EB CLI using "eb config save".',
    'env.exists': 'An environment with that name already exists.',
    # When create is called, if we cant find any files, we say this
    'appversion.none': 'The current directory does not contain any source code. Elastic Beanstalk is launching the sample application instead.',
    # Error, no solution stacks returned. Almost always due to permissions
    'sstacks.notfound': 'Elastic Beanstalk could not find any platforms. Ensure you have the necessary permissions to access Elastic Beanstalk.',
    'sstacks.notaversion': 'Elastic Beanstalk could not find any supported platforms for the given version {version}.',
    'timeout.error': 'The operation timed out. The state of the environment is unknown. The timeout can be set using the --timeout option.',
    'sc.notfound': 'Git is not set up for this project. EB CLI will deploy a .zip file of the entire directory.',
    'exit.notsetup': 'This directory has not been set up with the EB CLI\n'
                     'You must first run "eb init".',
    'exit.noregion': 'The EB CLI cannot find a default region. Run "eb init" or use a specific region by including the "--region" option with the command.',
    # Typical response when an environment is in pending state
    'exit.invalidstate': 'The operation cannot be completed at this time due to a pending operation. Try again later.',
    'exit.argerror': 'There was an argument error in the given command',
    'branch.noenv': 'This branch does not have a default environment. You must either specify an environment by typing '
                    '"eb {cmd} my-env-name" or set a default environment by typing "eb use my-env-name".',
    'ssh.notpresent': 'SSH is not installed. You must install SSH before continuing.',
    'ssh.filenotfound': 'The EB CLI cannot find your SSH key file for keyname "{key-name}".'
                        ' Your SSH key file must be located in the .ssh folder in your home directory.',
    'logs.location': 'Logs were saved to {location}',
    'local.logs.location': 'Elastic Beanstalk will write logs locally to {location}',
    'local.logs.lastlocation': 'Logs were most recently created {prettydate} and written to {location}',
    'local.logs.symlink': 'Updated symlink at {symlink}',
    'local.logs.nologs': 'There are currently no local logs.',
    'setenv.invalidformat': 'You must use the format KEY=VALUE to set an environment variable. '
                            'Variables must start with a letter.',
    'tags.invalidformat': 'You must provide a comma-separated list using the format name=value to set tags. '
                          'Tags may only contain letters, numbers, and the following symbols: / _ . : + = - @',
    'tags.max': 'Elastic Beanstalk supports a maximum of 7 tags.',
    'deploy.invalidoptions': 'You cannot use the "--version" option with either the "--message" or "--label" option.',
    'init.getvarsfromoldeb': 'You previous used an earlier version of eb. Getting options from .elasticbeanstalk/config.\n'
                             'Credentials will now be stored in ~/.aws/config',
    'ssh.noip': 'This instance does not have a Public IP address. This is possibly because the instance is terminating.',
    # Error thrown when someone provides a cname with a worker tier
    'worker.cname': 'Worker tiers do not support a CNAME.',
    # Error thrown when available cname is not available
    'cname.unavailable': 'The CNAME prefix {cname} is already in use.',
    'ssh.openingport': 'INFO: Attempting to open port 22.',
    'ssh.portopen': 'INFO: SSH port 22 open.',
    'ssh.notopening': 'Found source restriction on ssh port; not attempting to open. Use the --force flag to force opening of the port.',
    'ssh.closeport': 'INFO: Closed port 22 on ec2 instance security group.',
    'ssh.uploaded': 'Uploaded SSH public key for "{keyname}" into EC2 for region {region}.',
    'swap.unsupported': 'You must have at least 2 running environments to swap CNAMEs.',
    'connection.error': 'Having trouble communicating with AWS. Please ensure the provided region is correct and you have a working internet connection.',
    'sc.unstagedchanges': 'You have uncommitted changes.',
    'sc.gitnotinstalled': 'Your project is using git, but git doesn\'t appear to be installed.\n'
                          'Have you added git to your PATH?',
    'events.streamprompt': ' -- Events -- (safe to Ctrl+C)',
    'events.abortmessage': ' Use "eb abort" to cancel the command.',
    'abort.noabortableenvs': 'There are no environments currently being updated.',
    'local.unsupported': 'You can use "eb local" only with preconfigured, generic and multicontainer Docker platforms.',
    'local.dockernotpresent': 'You must install Docker version {docker-version} to continue. If you are using Mac OS X, ensure you have boot2docker version {boot2docker-version}. Currently, "eb local" does not support Windows.',
    'local.filenotfound': 'The EB CLI cannot find Dockerfile or the Dockerrun.aws.json file in the application root directory.',
    'local.missingdockerrun': 'This environment requires a Dockerrun.aws.json file to run.',
    'local.invaliddockerrunversion': 'The AWSEBDockerrunVersion key in the Dockerrun.aws.json file is not valid or is not included.',
    'local.missingdockerrunimage': 'The Dockerrun.aws.json file requires the Image key.',
    'local.missingdockerrunports': 'The Dockerrun.aws.json file requires the Ports key.',
    'local.missingdockerruncontainerport': 'The Dockerrun.aws.json file requires the ContainerPort field.',
    'local.invalidjson': 'The Dockerrun.aws.json file is not in valid JSON format.',
    'local.run.noportexposed': 'The Dockerfile must list ports to expose on the Docker container. Specify at least one port, and then try again.',
    'local.run.nobaseimg': 'The Dockerfile or Dockerrun.aws.json file does not specify a base image. Specify a base image, and then try again.',
    'local.run.socketperms': 'If you are on Ubuntu, ensure that you have added yourself into the Unix docker group by running "sudo usermod -aG docker $USER" '
                             'and then log out and log back in.',
    'local.open.nocontainer': 'Elastic Beanstalk did not detect a running Docker container. Ensure that a container is running before you use "eb local open".',
    'local.open.noexposedport': 'This container has no exposed host ports.',
    'labs.info': 'Extra experimental commands.',
    'quicklink.info': 'Generate a quick-launch link for your project.',
    'quicklink.epilog': 'Applications and environments created from the quick link are accessible to your account only. \n'
                        'To share the link with other accounts, you must explicitly grant those accounts read access to your S3 application version .zip file.',
    'download.info': 'Download Application Version.',
    'convert-dockkerrun.info': 'Converts Dockerrun.aws.json from version 1 to version 2.',
    'cleanup-versions.info': 'Cleans up old application versions.',
    'cloudwatch-setup.info': 'Create .ebextensions files necessary for setting up CloudWatch used in logging instance deployment.',
    'cloudwatch-setup.alreadysetup': 'CloudWatch file {filename} is already set up.',
    'cloudwatch-stream.notsetup': 'eb-activity.log not setup with AWS Cloudwatch for this environment.\n'
                                  'Try running "eb labs cloudwatch-setup".',
    'cloudwatch-setup.text': '.ebextensions created. In order to complete setup you will need\n'
                             'to check in any changes, (if applicable) and run "eb deploy".\n'
                             'You will also need the cloudwatch log permissions for this IAM User\n'
                             'as well as for the environments instance profile.\n'
                             'For more information see: http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/AWSHowTo.cloudwatchlogs.html',
    'cloudwatch-setup.removetext': 'Removed .ebextensions. In order to complete removal you\n'
                                   'will need to check in any changes, (if applicable) an run\n'
                                   '"eb deploy".',
    'setup-ssl.info': 'Sets up ssl on your environment.',
    'region.china.credentials': 'To use the China (Beijing) region, account credentials unique to the China (Beijing) region must be used.',
    'deploy.notadirectory': 'The directory {module} does not exist.',
    'deploy.modulemissingenvyaml': 'All specified modules require an env.yaml file.\n'
                                   'The following modules are missing this file: {modules}',
    'deploy.noenvname': 'No environment name was specified in env.yaml for module {module}. Unable to deploy.',
    'compose.noenvyaml': 'The module {module} does not contain an env.yaml file. This module will be skipped.',
    'compose.novalidmodules': 'No valid modules were found. No environments will be created.',
    'appversion.processfailed': 'Pre-processing of application version {app_version} has failed.',
    'appversion.cannotdeploy': 'Some application versions failed to process. Unable to continue deployment.',
    'appversion.processtimeout': 'All application versions have not reached a "Processed" state. Unable to continue with deployment.',
    'instance.processes.health': '{healthy}/{total} processes healthy.',
    'codesource.info': 'Configures the code source for the EB CLI to use by default.',
}

prompts = {
    'events.hanging': 'Streaming new events. Use CTRL+C to exit.',
    'platform.validate': 'It appears you are using {platform}. Is this correct?',
    'platform.prompt': 'Select a platform.',
    'platform.prompt.withmodule': 'Select a platform for module: {module_name}.',
    'sstack.version': 'Select a platform version.',
    'init.selectdefaultenv': 'Select the default environment. \n'
                             'You can change this later by typing "eb use [environment_name]".',
    'scale.switchtoloadbalance': 'The environment is currently a single-instance. Do you want'
                                 ' to change to a load-balancing environment?',
    'scale.switchtoloadbalancewarn': 'If you choose yes, the environment and your application will be temporarily unavailable.',
    'cname.unavailable': 'The CNAME you provided is already in use.\n',
    'terminate.confirm': 'The environment "{env-name}" and all associated instances will be terminated.',
    'terminate.validate': 'To confirm, type the environment name',
    'upgrade.validate': 'To continue, type the environment name',
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
    'rds.username': 'Enter an RDS DB username (default is "ebroot")',
    'rds.password': 'Enter an RDS DB master password',
    'vpc.id': 'Enter the VPC ID',
    'vpc.publicip': 'Do you want to associate a public IP address?',
    'vpc.ec2subnets': 'Enter a comma-separated list of Amazon EC2 subnets',
    'vpc.elbsubnets': 'Enter a comma-separated list of Amazon ELB subnets',
    'vpc.securitygroups': 'Enter a comma-separated list of Amazon VPC security groups',
    'vpc.elbpublic': 'Do you want the load balencer to be public? (Select no for internal)',
    'vpc.dbsubnets': 'Enter a comma-separated list of database subnets',
    'logs.retrieving': 'Retrieving logs...',
    'swap.envprompt': 'Select the environment with which you want to swap CNAMEs.',
    'abort.envprompt': 'Select the environment you want to stop updating.',
    'clone.latest': 'There is a newer version of the platform used by the environment you are cloning.\n'
                    'Select the version of the platform that you want to use for the clone.',
    'clone.latestwarn': 'Launching environment clone on most recent platform version. Override this behavior by using the "--exact" option.',
    'upgrade.altmessage': 'You can also change your platform version by typing "eb clone" and then "eb swap".',
    'upgrade.singleinstance': 'This operation causes application downtime while Elastic Beanstalk replaces the instance.',
    'upgrade.norollingapply': 'Elastic Beanstalk will enable {0}-based rolling updates to avoid application downtime while it replaces your instances. You may cancel the upgrade after it has started by typing "eb abort". To upgrade without rolling updates, type "eb upgrade --noroll".',
    'upgrade.norollingforce': 'This operation causes application downtime while Elastic Beanstalk replaces your instances.',
    'upgrade.rollingupdate': 'This operation replaces your instances with minimal or zero downtime. You may cancel the upgrade after it has started by typing "eb abort".',
    'upgrade.infodialog': 'The environment "{0}" will be updated to use the most recent platform version.',
    'upgrade.alreadylatest': 'Environment already on most recent platform version.',
    'upgrade.applyrolling': 'Enabling {0}-based rolling updates to environment.',
    'create.dockerrunupgrade': 'Multicontainer Docker environments do not support the version number of the Dockerrun.aws.json file that you provided. Type "eb labs convert-dockerrun" to convert it to a newer format.',
    'ecs.permissions': 'The Multi-container Docker platform requires additional ECS permissions. Add the permissions to the aws-elasticbeanstalk-ec2-role or use your own instance profile by typing "-ip {profile-name}".\n'
                       'For more information see: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create_deploy_docker_ecstutorial.html#create_deploy_docker_ecstutorial_role',
    'create.servicerole.info': '2.0+ Platforms require a service role. We will attempt to create one for you. You can specify your own role using the --service-role option.',
    'create.servicerole.view': 'Type "view" to see the policy, or just press ENTER to continue',
    'create.servicerole.required': '2.0+ Platforms require a service role. You can provide one with --service-role option',
    'create.servicerole.nopermissions': 'No permissions to create a role. '
                                        'Create an IAM role called "{}" with appropriate permissions to continue, or specify a role with --service-role.\n'
                                        'See http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/concepts-roles.html for more info. \nActual error: {}',
    'general.pressenter': 'Press enter to continue',
    'compose.groupname': 'Please enter the group name to be used'
}

alerts = {
    'platform.old': 'There is a newer version of the platform used by your environment. You can upgrade your environment to the most recent platform version by typing "eb upgrade".'
}

flag_text = {
    # General
    'general.env': 'environment name',
    'base.version': 'show application/version info',
    'base.verbose': 'toggle verbose output',
    'base.profile': 'use a specific profile from your credential file',
    'base.region': 'use a specific region',
    'general.timeout': 'timeout period in minutes',
    'base.noverify': 'do not verify AWS SSL certificates',

    # Clone
    'clone.env': 'name of environment to clone',
    'clone.name': 'desired name for environment clone',
    'clone.cname': 'cname prefix',
    'clone.scale': 'number of desired instances',
    'clone.tags': 'a comma separated list of tags as key=value pairs',
    'clone.nohang': 'return immediately, do not wait for clone to be completed',
    'clone.exact': 'match the platform version of the original environment',

    # Config
    'config.nohang': 'return immediately, do not wait for config to be completed',
    'config.codesource': 'configure the settings for which source the CLI will use for your code.'
                         ' Availables sources: {codecommit}. Available actions: {enable, disable}',

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
    'create.servicerole': 'Service Role',
    'create.version': 'version label to deploy',
    'create.keyname': 'EC2 SSH KeyPair name',
    'create.scale': 'number of desired instances',
    'create.nohang': 'return immediately, do not wait for create to be completed',
    'create.tags': 'a comma separated list of tags as key=value pairs',
    'create.envvars': 'a comma-separated list of environment variables as key=value pairs',
    'create.database': 'create a database',
    'create.vpc': 'create environment inside a VPC',
    'create.config': 'saved configuration name',
    'create.group': 'group suffix',
    'create.modules': 'a list of modules',
    'create.elb_type': 'load balancer type',

    # Deploy
    'deploy.env': 'environment name',
    'deploy.modules': 'modules to deploy',
    'deploy.version': 'existing version label to deploy',
    'deploy.label': 'label name which version will be given',
    'deploy.message': 'description for version',
    'deploy.nohang': 'return immediately, do not wait for deploy to be completed',
    'deploy.staged': 'deploy files staged in git rather than the HEAD commit',
    'deploy.group_suffix': 'group suffix',
    'deploy.source': 'source of code to deploy directly; example repo/branch',

    # Events
    'events.follow': 'wait and continue to print events as they come',

    # Init
    'init.name': 'application name',
    'init.platform': 'default Platform',
    'init.keyname': 'default EC2 key name',
    'init.interactive': 'force interactive mode',
    'init.module': 'module directory',
    'init.source': 'source of code to set as default; example repo/branch',

    # labs
    'labs.cwl.remove': 'remove .ebextensions',

    # List
    'list.all': 'show environments for all applications',

    # Local
    'local.run.envvars': 'a comma-separated list of environment variables as key=value pairs',
    'local.run.hostport': 'the host port that is exposed and mapped to the container port',
    'local.run.insecuressl': 'Allow insecure connections to the docker registry',
    'local.setenv.vars': 'space-separated list in format: VAR_NAME=KEY',

    # Logs
    'logs.all': 'retrieve all logs',
    'logs.zip': 'retrieve all logs as .zip',
    'logs.instance': 'instance id',
    'logs.stream': 'stream deployment logs that were set up with cloudwatch',

    # Scale
    'scale.number': 'number of desired instances',
    'scale.force': 'skip confirmation prompt',

    # Setenv
    'setenv.vars': 'space-separated list in format: VAR_NAME=KEY',
    'setenv.env': 'environment name',

    # SSH
    'ssh.number': 'index of instance in list',
    'ssh.instance': 'instance id',
    'ssh.keepopen': 'keep port 22 open',
    'ssh.command': 'Execute a shell command on the specified instance instead of starting an SSH session.',
    'ssh.custom': "Specify an SSH command to use instead of 'ssh -i keyfile'. Do not include the remote user and hostname.",
    'ssh.force': 'force port 22 open to 0.0.0.0',
    'ssh.setup': 'setup SSH for the environment',

    # terminate
    'terminate.force': 'skip confirmation prompt',
    'terminate.all': 'terminate everything',
    'terminate.nohang': 'return immediately, do not wait for terminate to be completed',
    'terminate.ignorelinks': 'terminate even if environment is linked',

    # Upgrade
    'upgrade.noroll': 'do not enable rolling updates before upgrade',

    # use
    'use.env': 'environment name',
    'use.source': 'source of code to set as default; example repo/branch',
    'use.repo': 'default code commit repository',
    'use.branch': 'default code commit branch will use default repository if none is specified',

    # swap
    'swap.env': 'name of source environment',
    'swap.name': 'name of destination environment',

    # codesource
    'codesource.sourcename': 'name of the code source to set as default'
}


### The below are programmatic and are not intended to be edited unless the service response changes
responses = {
    'event.redmessage': 'Environment health has been set to RED',
    'event.redtoyellowmessage': 'Environment health has transitioned '
                               'from YELLOW to RED',
    'event.yellowmessage': 'Environment health has been set to YELLOW',
    'event.greenmessage': 'Environment health has been set to GREEN',
    'event.launchsuccess': 'Successfully launched environment:',
    'event.launchbad': 'Create environment operation is CompleterController, '
                       'but with errors',
    'event.failedlaunch': 'Failed to launch environment.',
    'event.faileddeploy': 'Failed to deploy application.',
    'event.failedupdate': 'Failed to deploy configuration.',
    'event.updatebad': 'Update environment operation is complete, but with errors.',
    'event.updatefailed': 'Failed to deploy configuration.',
    'git.norepository': 'Error: Not a git repository '
                        '(or any of the parent directories): .git',
    'health.nodescribehealth': 'DescribeEnvironmentHealth is not supported.',
    'env.updatesuccess': 'Environment update completed successfully.',
    'env.configsuccess': 'Successfully deployed new configuration to environment.',
    'env.cnamenotavailable': 'DNS name \([^ ]+\) is not available.',
    'env.nameexists': 'Environment [^ ]+ already exists.',
    'app.deletesuccess': 'The application has been deleted successfully.',
    'app.exists': 'Application {app-name} already exists.',
    'app.notexists': 'No Application named {app-name} found.',
    'logs.pulled': 'Pulled logs for environment instances.',
    'logs.successtail': 'Successfully finished tailing',
    'logs.successbundle': 'Successfully finished bundling',
    'logs.fail': 'Failed to pull logs for environment instances.',
    'env.terminated': 'terminateEnvironment completed successfully.',
    'env.invalidstate': 'Environment named {env-name} is in an invalid state for this operation. Must be Ready.',
    'loadbalancer.notfound': 'There is no ACTIVE Load Balancer named',
    'loadbalancer.targetgroup.notfound': 'Target group \'{tgarn}\' not found',
    'ec2.sshalreadyopen': 'the specified rule "peer: 0.0.0.0/0, TCP, from port: 22, to port: 22,',
    'swap.success': 'Completed swapping CNAMEs for environments',
    'cfg.nameexists': 'Configuration Template {name} already exists.',
    'create.noplatform': 'Unable to determine base for template pack (no solution stack)',
    'create.ecsdockerrun1': 'ECS Application sourcebundle validation error: Unsupported AWSEBDockerrunVersion:',
}
git_ignore = [
    '# Elastic Beanstalk Files',        # comment line
    '.elasticbeanstalk/*',              # ignore eb files
    '!.elasticbeanstalk/*.cfg.yml',       # don't ignore configuration templates
    '!.elasticbeanstalk/*.global.yml',    # don't ignore global configurations
]

docker_ignore = git_ignore[:2] + ['.git', '.gitignore']
