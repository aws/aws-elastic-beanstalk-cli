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



class EnvList():
    envlist = None
    """ Stores info for saved environments    """
    def __init__(self):
        self.envs = {} # key is environment name, value is last update date

    def add_env(self, env_name, date):
        self.envs[env_name] = date

    def get_env_names(self):
        return self.envs.keys()

    def get_env_date(self, env_name):
        return self.envs[env_name]

    def remove_env(self, env_name):
        del self.envs[env_name]