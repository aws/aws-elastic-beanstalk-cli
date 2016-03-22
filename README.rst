======
EB-CLI
======

EB Command Line Interface (CLI) is a tool that helps you deploy and manage
your AWS Elastic Beanstalk applications and environments. It also
provides integration with Git. This file provides a sample walkthrough of EB CLI. To view a list of commands, type:

    eb --help

For more information about a specific command, type:

    eb {cmd} --help


For detailed information about EB CLI, see `EB Command Line Reference. <http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/command-reference-eb.html>`__

------------
Installation
------------

You will need administrator/sudo privileges unless you install into a virtual environment.
To install you will first need to install Python and Pip.
The most recent version of Python now includes pip.

`To install Python, go here. <https://www.python.org/downloads/>`__

If you already have Python, but need to install Pip, `go here. <http://pip.readthedocs.org/en/latest/installing.html>`__

After you have installed Pip, run the following command:

pip install awsebcli

---------------
Getting Started
---------------

EB CLI requires you to have AWS security credentials.
For procedures to get security credentials, `see the documentation. <http://docs.aws.amazon.com/general/latest/gr/managing-aws-access-keys.html>`__

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. Create a new directory for your project.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In Linux/UNIX, type the following:
    mkdir my-hello-app

In Windows, type the following:
	md my-hello-app

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2. Create an index.html file for EB CLI to use as your sample application.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    echo "Hello World" > index.html

NOTE: In Windows, do not include quotes in the command.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
3. Set up your directory with EB CLI and then answer the questions to configure AWS Elastic Beanstalk.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    eb init

When prompted for your AWS security credentials, type your access key ID and secret access key. To answer a question with the default value, press Enter.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
4. Create your running environment and deploy the Hello World application.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    eb create

Wait for AWS Elastic Beanstalk to finish creating the environment.
When it is done, your application is live in a load-balancing environment.

^^^^^^^^^^^^^^^^^^^^^^^^^
5. View your application.
^^^^^^^^^^^^^^^^^^^^^^^^^

    eb open

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
6. Update the sample application to create a new application version to deploy.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Make a change to your code by typing the following:

   echo " to you." >> index.html

NOTE: In Windows, do not include quotes in the command.

When you are ready to launch your new application version, type the following:

   eb deploy

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
7. View the health of your environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    eb health

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
8. View the updated environment.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    eb open

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
9. Shut down your running environment.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    eb terminate

Confirm that this is the environment that you want to terminate by typing the environment name.

^^^^^^^^^^^^^
10. Clean up.
^^^^^^^^^^^^^

To completely remove your application and clean up the local project directory, type the following:

    eb terminate --all

Confirm that this is the application that you want to remove by typing the application name.

---------------
EB CLI Commands
---------------

This section describes some EB CLI 3 commands and why you would use them.

^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. View environment status.
^^^^^^^^^^^^^^^^^^^^^^^^^^^

    eb status -v

The status command will show you the current state of your application. This includes things such as:
  * Environment Name
  * Application Version
  * Solution Stack
  * Health
  * Number of running instances

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2. List your running environments.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   eb list

The list command will show you a list of running environments.
The environment with an asterisk next to it is the default environment.
To see more detailed information about your environments, type the following to use verbose mode:

   eb list -v

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
3. Change your current environment.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can run most commands with any environment by using the following syntax:

    eb {cmd} <environment>

To change your default environment, type the following:

    eb use [environment_name]

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
4. Open the AWS Elastic Beanstalk management console.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To view your environment in the AWS Management Console, type the following:

    eb console

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
5. Change environment variables.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can set environment variables for your running environment at any time by typing the following:

    eb setenv foo=bar

You can view your environment variables by typing the following:

    eb printenv

---------------------
Using EB CLI with Git
---------------------

EB CLI 3 provides integration with Git. After running "git clone" or "git init", run the following command:

    eb init

EB CLI 3 will now recognize that your application is set up with Git.

To use Git with EB CLI 3:

1. Make any change to your code.

2. After you make a change to your code, type the following:

	git commit

3. Deploy your updated code.

Now when you run the "eb deploy" command, EB CLI will only deploy the code that was under source control.
Make sure to always commit what you want to deploy.
EB CLI uses your commit ID and message as the version label and description, respectively.

4. Deploy to production.

When you are ready to deploy an updated version of your code, use Git tags.

    git tag -a v1.0 -m "My version 1.0"

The tag will be used for the version label so you always know which version your environment is running on.
If you have already deployed this version, EB CLI will deploy that version to your environment instead of uploading a new application version.

5. Use branches.

EB CLI enables you to associate different environments with different branches of your code.
For example:

    git checkout master

    eb use prod

    git checkout develop

    eb use dev

Now whenever you switch to a new branch, your default environment will also switch.


