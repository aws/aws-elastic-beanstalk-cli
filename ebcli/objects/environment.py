# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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


class Environment(object):
    def __init__(self, version_label=None, status=None, app_name=None,
                 health=None, id=None, date_updated=None,
                 platform=None, description=None,
                 name=None, date_created=None, tier=None,
                 cname=None, option_settings=None, is_abortable=False,
                 environment_links=None, environment_arn=None):

        self.version_label = version_label
        self.status = status
        self.app_name = app_name
        self.health = health
        self.id = id
        self.date_updated = date_updated
        self.platform = platform
        self.description = description
        self.name = name
        self.date_created = date_created
        self.tier = tier
        self.cname = cname
        self.option_settings = option_settings
        self.is_abortable = is_abortable
        self.environment_links = environment_links
        self.environment_arn = environment_arn

    def __str__(self):
        return self.name