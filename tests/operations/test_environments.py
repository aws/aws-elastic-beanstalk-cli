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

from baseoperationstest import BaseOperationsTest
from ebcli.core import operations
from ebcli.lib.aws import InvalidParameterValueError


class TestCreateEnvironment(BaseOperationsTest):

    def test_create_new_environment_envname_taken(self):
        self.mock_elasticbeanstalk.create_environment.side_effect = [
            InvalidParameterValueError('Environment env-name already exists.'),
            None,
        ]

        self.mock_input.return_value = 'new-env-name'

        operations.create_env(
            'app-name', 'env-name', 'region', 'cname',
            'solution-stack', 'tier', 'itype', 'label',
            'single', 'key_name', 'profile', 'tags', 'size',
            'database', 'vpc', interactive=True
        )
        self.assertEqual(self.mock_elasticbeanstalk.create_environment.call_count, 2)

    def test_create_new_environment_envname_taken_script(self):
        self.mock_elasticbeanstalk.create_environment.side_effect = [
            InvalidParameterValueError('Environment env-name already exists.'),
        ]

        try:
            operations.create_env(
                'app-name', 'env-name', 'region', 'cname',
                'solution-stack', 'tier', 'itype', 'label',
                'single', 'key_name', 'profile', 'tags', 'size',
                'database', 'vpc', interactive=False
            )
            self.fail('Should have thrown InvalidParameterValueError')
        except InvalidParameterValueError:
            # Expected
            pass

    def test_create_new_environment_cname_taken(self):
        self.mock_elasticbeanstalk.create_environment.side_effect = [
            InvalidParameterValueError('DNS name (cname) is not available.'),
            None,
        ]

        self.mock_input.return_value = 'new-cname'

        operations.create_env(
            'app-name', 'env-name', 'region', 'cname',
            'solution-stack', 'tier', 'itype', 'label',
            'single', 'key_name', 'profile', 'tags', 'size',
            'database', 'vpc', interactive=True
        )

        self.assertEqual(self.mock_elasticbeanstalk.create_environment.call_count, 2)

    def test_create_new_environment_cname_taken_script(self):
        self.mock_elasticbeanstalk.create_environment.side_effect = [
            InvalidParameterValueError('DNS name (cname) is not available.'),
        ]

        try:
            operations.create_env(
                'app-name', 'env-name', 'region', 'cname',
                'solution-stack', 'tier', 'itype', 'label',
                'single', 'key_name', 'profile', 'tags', 'size',
                'database', 'vpc', interactive=False
            )
            self.fail('Should have thrown InvalidParameterValueError')
        except InvalidParameterValueError:
            # Expected
            pass

    def test_create_new_environment_app_notexists(self):
        self.mock_elasticbeanstalk.create_environment.side_effect = [
            InvalidParameterValueError('Application \'app-name\' already exists.'),
        ]

        try:
            operations.create_env(
                'app-name', 'env-name', 'region', 'cname',
                'solution-stack', 'tier', 'itype', 'label',
                'single', 'key_name', 'profile', 'tags', 'size',
                'database', 'vpc', interactive=True
            )
            self.fail('Should have thrown InvalidParameterValueError')
        except InvalidParameterValueError:
            # Expected
            pass

    def test_create_new_environment_app_notexists_script(self):
        self.mock_elasticbeanstalk.create_environment.side_effect = [
            InvalidParameterValueError('Application \'app-name\' already exists.'),
        ]

        try:
            operations.create_env(
                'app-name', 'env-name', 'region', 'cname',
                'solution-stack', 'tier', 'itype', 'label',
                'single', 'key_name', 'profile', 'tags', 'size',
                'database', 'vpc', interactive=False
            )
            self.fail('Should have thrown InvalidParameterValueError')
        except InvalidParameterValueError:
            #Expected
            pass