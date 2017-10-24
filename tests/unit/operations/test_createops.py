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
import mock
import unittest

from ebcli.core import io
from ebcli.lib import cloudformation, elasticbeanstalk
from ebcli.objects.environment import Environment
from ebcli.objects.exceptions import NotFoundError
from ebcli.operations import createops
from ebcli.operations.tagops.taglist import TagList


class TestCreateOps(unittest.TestCase):

    def test_get_and_validate_tags__tags_is_empty(self):
        tags = ''

        self.assertEqual([], createops.get_and_validate_tags(tags))

    def test_get_and_validate_tags__tags_is_empty__add_multiple_new_tags(self):
        taglist = TagList([])

        addition_string = ','.join(
            [
                'key1=value1',
                'key2=value2',
                'key3=value3'
            ]
        )

        expected_additions_list = [
            {'Key': 'key1', 'Value': 'value1'},
            {'Key': 'key2', 'Value': 'value2'},
            {'Key': 'key3', 'Value': 'value3'}
        ]

        self.assertEqual(
            expected_additions_list,
            createops.get_and_validate_tags(addition_string)
        )

    def test_retrieve_application_version_url__successfully_returns_sample_app_url(self):
        get_template_response = {
            "TemplateBody": {
                "Parameters": {
                    "AppSource": {
                        "NoEcho": "true",
                        "Type": "String",
                        "Description": "The url of the application source.",
                        "Default": "http://sample-app-location/python-sample.zip"
                    },
                },
                "Description": "AWS Elastic Beanstalk environment (Name: 'my_env_name'  Id: 'my_env_id')",
            }
        }
        elasticbeanstalk.get_environment = mock.MagicMock(return_value=Environment(name='my_env_name', id='my_env_id'))
        cloudformation.wait_until_stack_exists = mock.MagicMock()
        cloudformation.get_template = mock.MagicMock(return_value=get_template_response)

        self.assertEqual(
            "http://sample-app-location/python-sample.zip",
            createops.retrieve_application_version_url('my_env_name')
        )

    def test_retrieve_application_version_url__empty_response__raises_not_found_error(self):
        # save original definition of io.log_warning
        io._log_warning = io.log_warning
        io.log_warning = mock.MagicMock()

        self.__assert_app_source_not_found_warning_log(template_response={})

    def test_retrieve_application_version_url__app_version_url_not_found_in_app_source__raises_not_found_error(self):
        # save original definition of io.log_warning
        io._log_warning = io.log_warning
        io.log_warning = mock.MagicMock()

        get_template_response = {
            "TemplateBody": {
                "Parameters": {
                    "AppSource": {
                        "NoEcho": "true",
                        "Type": "String",
                        "Description": "The url of the application source."
                    }
                },
                "Description": "AWS Elastic Beanstalk environment (Name: 'my_env_name'  Id: 'my_env_id')",
            }
        }

        self.__assert_app_source_not_found_warning_log(template_response=get_template_response)

    def __assert_app_source_not_found_warning_log(self, template_response):
        elasticbeanstalk.get_environment = mock.MagicMock(return_value=Environment(name='my_env_name', id='my_env_id'))
        cloudformation.wait_until_stack_exists = mock.MagicMock()
        cloudformation.get_template = mock.MagicMock(return_value=template_response)

        createops.retrieve_application_version_url('my_env_name')

        io.log_warning.assert_called_with('Cannot find app source for environment. ')

        io.log_warning = io._log_warning
