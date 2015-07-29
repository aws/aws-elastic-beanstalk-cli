=========================
Elastic Beanstalk CLI, v3
=========================

This is the documentation for developers. This readme should help you understand the source.

---------------
Getting Started
---------------

To set up a development version of the EB CLI, cd into the project directory and run:

    [sudo] python setup.py develop


-------
Testing
-------

To install test dependencies:

    [sudo] pip install -r dev_requirements.txt

To run tests:

    py.test

To run end-to-end tests (warning: will spin up instances in your account and incur cost)

    py.test --end2end

As a policy, it is always best to test on python2 and python3.
I recommend you add the following alias to your bash profile.
This will clean up all compiled files, and run py.test for python3 and python2.
Make sure you have all dependencies installed for both versions of python.

    pytest() { rm -rf out/; find . -type f -name '*.pyc' -delete; python2.7 -m pytest; python3 -m pytest; }

Then you can just type

    pytest

To run tests for both versions.


-----------------------
Architecture/Code paths
-----------------------

The CLI is designed with the following package architecture.

    Controllers -> Operations -> Service

For example, controllers.create imports operations.createops, which will then import libs.elasticbeanstalk.
Keeping this structure segments commands and minimizes impact. Shared code should be in operations.commonops and should be modified with care.
The controller should act as the Interface, operations as the client side logic, which then calls a service.
Other packages are for bundling larger features, such as labs/health/local.

All customer facing text should be located in resources.strings

~~~~~~~~~~~~~
Drilling Down
~~~~~~~~~~~~~

- Controllers -
The Controllers are built on top of cement, which is a python framework for CLI's.
Cement is built on top of Argparse. Understanding how the flags/options work in a controller
is often as easy as understanding how argparse works.

- Operations -
Operations are typically just pure code. Nothing special here.

- libs/services
You will notice a file called aws.py. This file is a wrapper around botocore.
Other than tests, it should be the only file importing botocore. It does a lot of the common handling
for you so that service wrappers are fairly skeleton.
Other wrappers such as elasticbeanstalk are fairly skeleton, but allow you to separate the service model
from the internal model (a good example is create) if needed.

- health -
Health is a fairly complex command, because it has dynamic printing. The basic idea behind health
is that screen.py is doing all the printing. It grabs the data from the data_poller.py and send the data to
a table.py. The table then figures out how to print the items it is responsible for.
The data_poller is responsible for calling the API when appropriate, and updating the data. It also
converts the service model into a more flat model. The data_poller runs on a separate thread so
that is does not block screen inputs/printing.

- local -
The code for local is mostly in the containers package. It uses docker and docker_compose behind
the scenes.