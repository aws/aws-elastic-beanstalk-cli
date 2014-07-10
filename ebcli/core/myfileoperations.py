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

import os

from six.moves import configparser

from ebcli.core.ebcore import app

def _try_read_credential_file():
    pass

def read_credential_file():
    location = '.elasticbeanstalk' + os.path.sep + 'config'

def get_directory_name():
    pass

def create_config_file():
    location = '.elasticbeanstalk' + os.path.sep + 'config'

    if not os.path.exists('.elasticbeanstalk'):
        os.makedirs('.elasticbeanstalk')


    try:
        #We want to try to open directory first, than file

        config = configparser.ConfigParser()
        config.read(location)
        sections = config.sections()
        app_name = config.get('global', 'ApplicationName')


        config.add_section('global')
        config.set('global', 'ApplicationName', 'test')

        with open(location, "wb") as configfile:
            config.write(configfile)

    except IOError:

        # File does not exist, we want to create it
        os.mkdir()
        f = file(location, "w")