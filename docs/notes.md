# Elastic Beanstalk CLI, v2

## What is the Elastic Beanstalk CLI?
The Elastic Beanstalk CLI (referred to by its binary name `eb` going forward) is a command line client written in Python that allows a customer to associate an application stored in a git repository with Elastic Beanstalk and deploy that application to an EB environment. `eb` can also associate branches with environments. In addition to deploying an application to an environment, `eb` may be used to operate a running application, including retrieving logs or events and changing the configuration of an environment (e.g., adjust Auto Scaling capacity configuration, security groups, etc.)

## Challenges and Opportunities with Current `eb` Implementation
### Distribution
`eb` does not have an installer and is not available in a package repository (i.e., PyPI). The package is buried at http://aws.amazon.com/code/6752709412171743 and must be installed manually. A community-managed Homebrew (http://brew.sh) installer package is maintained and may be used to install on OS X. This provides the best customer experience; installation is as simple as `brew install aws-elasticbeanstalk`

### Updates
This stems from the distribution challenge. When `eb` is updated, there is no workflow to easily update the tool (or even notify users that an udpate exists). A customer must download the package and reinstall again.

### Extensibility
`eb` was not written to be extended. If a customer or internal developer wants to add her own sub-command she must modify the code base in a non-pluggable way with no clear path to share back her contributions to the community.

### Inconsistent Interface
Some actions (i.e., initializing a new environment with `eb init`) can only be performed interactively. `eb init` results in a `.elasticbeanstalk` directory being created and added to the project's `.gitignore`, meaning the config can't be shared with anyone else on a team.

Further, commands don't have a _help_ interface. For example, `eb branch` is a powerful option, but there are no docs and `eb branch --help` does nothing.

## Goals for V2
### Deprecate standalone `eb` and port as plugin to `aws` CLI
The official and universal `aws` CLI has over 19k active users and is extensible via a customizations interface (see https://github.com/aws/aws-cli/tree/develop/awscli/customizations). Services like CloudTrail and CloudSearch have chosen to build their CLIs as an `aws` customization. Porting `eb` to `aws eb` means the tool gets the broad distribution and simple installation (i.e., `pip install aws-cli`) of `aws`, and allows contributions from both within and outside AWS to be contributed.

#### Backwards Compatibility
`aws eb` does not need to maintain strict backwards compatibility with `eb`. That is, if a customer who has used `eb` were to alias `aws eb` to  `eb`, there is no guarantee that all commands will work. `aws eb` is considered a major release, similar to the migration between the old CLIs (e.g., `ec2-*`) and the unified CLI.

Although backwards compatibility isn't required, the command and argument structure of `eb` is well established and all existing commands should be supported. Those commands are documented in the [Commands](#commands) section below.

### Consistent Interface
All commands should assume sane defaults wherever possible. Defaults should be overrideable by arguments or configuration files. As a last resort, the tool will prompt the user for interactive input for values that can't have default values and aren't provided as args or in a config file.

### Version Control Environment Configuration
Today, an application in a git repo is associated with an Elastic Beanstalk environment using `eb init` and interactively completing a wizard to characterize the application's requirements. The new `aws eb init` command should be easily automated (without using `expect`) to provide required config information via arguments or configuration file.

Today, when a repo has been initialized and associated with an EB environment, a `.elasticbeanstalk` directory is created at the top level of the repo and added to `.gitignore`. This prevents developers from the EB binding information across a project. Two developers may want to deploy against the same environment (i.e., the entire `.elasticbeanstalk` directory would be shared), or they may want to deploy against separate but identically-configured Beanstalk environments. In this latter case, files in the `.elasticbeanstalk` that define shared configuration would be committed, while developer or environment-specific (i.e., EC2 Key Name, Env URL, etc) configuration information would not be committed.




**Initializaing a new environment**: The current version of `eb` requires an user to interactively choose options from a text wizard in the terminal to initialize an application in a git repository and associate it with an Elastic Beanstalk environment.

## Existing Commands
* **`init`**
* **`branch`**
* **`start`**
* **`status`**
* **`update`**
* **`stop`**
* **`delete`**
* **`logs`**
* **`events`**
* **`push`**

## New Commands
* **`aws eb import`** Import an existing Elastic Beanstalk environment and map it to the current repository
* **`aws eb open`** Open the environment's URL in the default web browser
* **`aws eb envvar`** List environment variables for the current environment
* **`aws eb envvar`** set KEY=VAL** Add a new env var to the correct location in the `.elasticbeanstalk` directory. Requires `aws eb update` to enact.
* **`aws eb envvar unset KEY`** Remove an env var from the correct location in the `.elasticbeanstalk` directory. Requires `aws eb update` to enact.
* **`aws eb envvar export-local`** Export EB environment variables into local env
* **`aws eb scale min=x max=y`** Modify the scaling attributes. Requires `aws eb update` to enact.
* **`aws eb keypair new-keypair`** Set or update the EC2 keypair. Requires `aws eb update` to enact.
* **`aws eb update --dry-run`** Show changes that will result in new launch configuration (and instance replacement)
* **`aws eb ssh`** SSH to a host in the environment. Interactive prompt with available instances (by instance ID) of desired capacity > 1.
* **`aws eb local`** Deploy a repo with a Dockerrun.aws.json or Dockerfile to a local Docker environment.

