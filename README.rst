======
EB CLI
======

Introduction
============

The AWS Elastic Beanstalk Command Line Interface (EB CLI) is a tool that helps you deploy and manage
your Elastic Beanstalk applications and environments. It also
provides integration with Git.

For detailed information about the EB CLI, see `Using the Elastic Beanstalk Command Line Interface (EB CLI) <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html>`__
in the *AWS Elastic Beanstalk Developer Guide*.

The EB CLI is now an open source project, hosted in this repository.
You're welcome to participate by reporting issues, making suggestions, and submitting pull requests.
We value your contributions!

Installation
============

-------------------------------
If you'd like to use the EB CLI
-------------------------------

The easiest and recommended way to install the EB CLI is to use the EB CLI setup scripts available on a separate GitHub repository.
Use the scripts to install the EB CLI on Linux, macOS, or Windows. The scripts install the EB CLI and its dependencies, including Python and pip.
The scripts also create a virtual environment for the EB CLI.
For installation instructions, see the `aws/aws-elastic-beanstalk-cli-setup <https://github.com/aws/aws-elastic-beanstalk-cli-setup>`__ repository. 

-----------------------------------------
If you'd like to contribute to the EB CLI
-----------------------------------------

Dependencies
~~~~~~~~~~~~
Install Python and Pip. The most recent version of Python now includes pip.

To install Python, go `here <https://www.python.org/downloads/>`__.

If you already have Python, but need to install Pip, go `here <https://pip.readthedocs.org/en/latest/installing.html>`__.

Install the EB CLI from this repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need administrator/sudo privileges unless you install into a virtual environment.

To install the EB CLI

1. Clone or download this repository to your local environment.

2. Navigate to the the root of the repository.

3. Run the following command.
   
   `pip install .`:code:

Getting Started
===============

The EB CLI requires you to have AWS security credentials.
To learn how to get security credentials, see `Managing Access Keys for Your AWS Account Root User <https://docs.aws.amazon.com/general/latest/gr/managing-aws-access-keys.html>`__
in the *AWS General Reference*.

To view a list of EB CLI commands, type:

    eb --help

For more information about a specific command, type:

    eb {cmd} --help

For a detailed command reference for all EB CLI commands, see `EB CLI Command Reference <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb3-cmd-commands.html>`__
in the *AWS Elastic Beanstalk Developer Guide*.


