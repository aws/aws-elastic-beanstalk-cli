===========
EB-CLI
===========

EB is the command line interface for Amazon Web Services Elastic
Beanstalk product. This command line interface tool will help you
manage your Elastic Beanstalk environments. It also integrates
with Git. To see commands use:

    eb --help

To get more info on a specific command use:

    eb {cmd} --help


please see `Official Documentation <http://my.example.com>`__


Installation
====
You will need administrator/sudo privileges (unless you install into a virtualenv).
To install you will first need to install python and pip.
The latest version of python (3.4) now includes pip.

`Go here to install python <https://www.python.org/downloads/>`__

If you already have python, but need pip, `go here to install pip <http://pip.readthedocs.org/en/latest/installing.html>`__

Once you have pip installed run the following command:

pip install aws-eb-cli


Getting Started
====
You will need a set of AWS Access Keys to use the eb-cli.
You can get these by following the `directions here <http://docs.aws.amazon.com/general/latest/gr/managing-aws-access-keys.html>`__

1. Make a new directory for your project.
----

    mkdir my-hello-app

(on windows you can use "md my-hello-app")

2. Write the code for your application
----

    echo "Hello World!" > index.html

(on windows use the same command but without the quotes.)

3. Setup your directory with the eb-cli and create an application:
----

    eb init

Answer the questions at the default value by hitting enter. Make sure to put in your AWS credentials correctly when prompted.

4. Create your running environment
----

    eb create

Answer the questions at the default value by hitting enter.

Wait for the environment to finish being created.
Your Application is now live in a load balanced environment!

5. View your application
----

    eb open

6. Make a change
----

Make a change to your code

   echo " - Sincerely Elastic Beanstalk" >> index.html

(on windows use the same command but without the quotes.)

Once you are ready to launch your new version, simply use the command

   eb deploy

7. View updated environment
----

    eb open


8. Shut down your running environment
----

    eb terminate

You will need to type in the environment name to confirm.

9. Clean up
----

To completely remove your application and clean up the local project directory use:

    eb terminate --all

You will need to type in the application name to confirm.


Moving Around
====

The following set of commands can be used to use the eb-cli more effectively

1. View environment status
----

    eb status -v

The status command will show you the current state of your application. This includes things such as:
  * Environment Name
  * Application Version
  * Solution Stack
  * Health
  * Number of running instances

2. List your running environments
----

   eb list

The list command will show you a list of running environments.
The environment with a star next to it is your selected default environment.
If you would like to see more detailed information, you can use verbose mode:

   eb list -v

3. Switch your current environment
----

You can run most commands with any environment by using the following syntax:

    eb {cmd} <environment>

However if you would like to switch your default environment you can select it using

    eb use [environment_name]

4. Open up the AWS Elastic Beanstalk console
----

If you would like to view your Environment in the AWS Console you can use:

    eb console

5. Changing environment variables
----

You can set environment variables for your running environment at anytime by using:

    eb setenv foo=bar

If you would just like to view your environment variables, you can do so by using:

    eb printenv


EB-CLI works better with git
====
The eb-cli works even better when you are using git! After running "git clone" or "git init" simply run

    eb init

The eb-cli will now recognize that your application is set up with git. Here is our recommended steps for using git.

1. Make a change to your code.
----

After you make a change to your code, run "git commit".

2. Deploy a change
----

Now when you call deploy, the eb-cli will only deploy the code that was under source control.
Make sure to always commit what you want deployed!
The version label and description are based on your commit id and message.

3. Push to production
----
Once you are ready to deploy a more stable version of your code, make sure to use git tags.

    git tag -a v1.0 -m "My version 1.0"

The tag will be used for the version label so you always know which version your environment is running on.
If you have already deployed this version somewhere else, the eb-cli will tell your environment to use that version instead of uploading a new one.

4. Use branches.
----

The eb-cli allows you to associate different branches with different branches of your code.
For example

    git checkout master
    eb use prod
    git checkout develop
    eb use dev

Now whenever you switch branches, your default environment will also switch!
