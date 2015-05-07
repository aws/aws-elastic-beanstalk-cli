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

from ebcli.containers.envvarcollector import EnvvarCollector
from mock import patch
from unittest import TestCase


class TestEnvvarCollector(TestCase):
    def test_empty_environment(self):
        self.assertDictEqual({}, EnvvarCollector().map)
        self.assertSetEqual(set(), EnvvarCollector().to_remove)

    def test_merge_non_overlapping_envs(self):
        env0 = EnvvarCollector({'a': '0', 'b': '1'})
        env1 = EnvvarCollector({'c': '3', 'd': '4'})

        expected_envvars = {'a': '0', 'b': '1', 'c': '3', 'd': '4'}

        self.assertDictEqual(expected_envvars, env0.merge(env1).filtered().map)
        self.assertDictEqual(expected_envvars, env1.merge(env0).filtered().map)

        self.assertSetEqual(set(), env0.merge(env1).to_remove)
        self.assertSetEqual(set(), env1.merge(env0).to_remove)

    def test_merge_overlapping_and_vars_to_remove(self):
        env0 = EnvvarCollector({'a': '0', 'd': '1'})
        env1 = EnvvarCollector({'a': '5', 'd': '5'}, {'d', 'c'})

        self.assertEqual({'a': '5'}, env0.merge(env1).filtered().map)
        self.assertEqual({'a': '0'}, env1.merge(env0).filtered().map)

        self.assertSetEqual({'d', 'c'}, env0.merge(env1).to_remove)
        self.assertSetEqual({'d', 'c'}, env1.merge(env0).to_remove)

    def test_fitered_removed_all_envvars(self):
        env = EnvvarCollector({'a': '5', 'd': '5'}, {'a', 'd'})
        result = env.filtered()
        self.assertDictEqual({}, result.map)
        self.assertSetEqual(set(), result.to_remove)

    def test_fitered_removed_some_envvars(self):
        env = EnvvarCollector({'a': '5', 'd': '5'}, {'a'})
        result = env.filtered()
        self.assertDictEqual({'d': '5'}, result.map)
        self.assertSetEqual(set(), result.to_remove)

    def test_fitered_removed_no_envvars(self):
        envvars = {'a': '5', 'd': '5'}
        env = EnvvarCollector(envvars)
        result = env.filtered()
        self.assertDictEqual(envvars, result.map)
        self.assertSetEqual(set(), result.to_remove)
