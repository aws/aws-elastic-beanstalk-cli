# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License'). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the 'license' file accompanying this file. This file is
# distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from ebcli.containers import containerops as cops
from mock import patch, Mock
from unittest import TestCase


PRECONFIG_SOLN_STK = Mock(version='GlassFish 4.1 Java 8 (Preconfigured - Docker)')
GENERIC_SOLN_STK = Mock(platform='Docker')
MULTI_SOLN_STK = Mock(platform='Multi-container Docker')
NON_DOCKER_SOLN_STK = Mock(version='Ruby 2.0 (Puma)', platform='Ruby')
EXPECTED_PRECONFIG_LOG_PATH = '/usr/local/glassfish4/glassfish/domains/domain1/logs'


class TestContainerOps(TestCase):
    def setUp(self):
        self.config = cops.get_configuration()

    def test_is_container(self):
        self.assertTrue(cops.is_container(GENERIC_SOLN_STK, self.config))
        self.assertTrue(cops.is_container(PRECONFIG_SOLN_STK, self.config))
        self.assertFalse(cops.is_container(NON_DOCKER_SOLN_STK, self.config))

    def test_is_preconfigured(self):
        self.assertTrue(cops.is_preconfigured(PRECONFIG_SOLN_STK, self.config))
        self.assertFalse(cops.is_preconfigured(GENERIC_SOLN_STK, self.config))
        self.assertFalse(cops.is_preconfigured(NON_DOCKER_SOLN_STK,
                         self.config))

    def test_is_generic(self):
        self.assertTrue(cops.is_generic(GENERIC_SOLN_STK, self.config))
        self.assertFalse(cops.is_generic(PRECONFIG_SOLN_STK, self.config))
        self.assertFalse(cops.is_generic(NON_DOCKER_SOLN_STK, self.config))

    def test_is_multi(self):
        self.assertTrue(cops.is_multi(MULTI_SOLN_STK, self.config))
        self.assertFalse(cops.is_multi(GENERIC_SOLN_STK, self.config))
        self.assertFalse(cops.is_multi(NON_DOCKER_SOLN_STK, self.config))

    @patch('ebcli.containers.containerops.fileoperations.get_json_dict')
    def test_get_configuration(self, get_json_dict):
        get_json_dict.return_value = {}
        self.assertEquals({}, cops.get_configuration())
        get_json_dict.assert_called_once_with(cops.CONTAINER_CONFIG_PATH)

    def test_get_runtime_default_log_path(self):
        actual_log = cops.get_runtime_default_log_path(PRECONFIG_SOLN_STK,
                                                       self.config)
        self.assertEqual(EXPECTED_PRECONFIG_LOG_PATH, actual_log)
