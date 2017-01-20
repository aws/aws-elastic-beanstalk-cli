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

from unittest import TestCase

from mock import patch

from ebcli.containers import factory
from ebcli.containers.generic_container import GenericContainer
from ebcli.containers.multicontainer import MultiContainer
from ebcli.containers.preconfigured_container import PreconfiguredContainer
from ebcli.objects.exceptions import NotSupportedError
from tests.unit.containers import dummy


class TestFactory(TestCase):
    @patch('ebcli.containers.factory.dockerrun')
    def test_make_container_fs_handler(self, dockerrun):
        dockerrun.get_dockerrun.return_value = dummy.get_dockerrun_dict()
        fs_handler = factory.make_container_fs_handler(dummy.PATH_CONFIG)

        self.assertEqual(dummy.PATH_CONFIG, fs_handler.pathconfig)
        self.assertDictEqual(dummy.DOCKERRUN_DICT, fs_handler.dockerrun)

    @patch('ebcli.containers.factory.dockerrun')
    def test_make_multicontainer_fs_handler(self, dockerrun):
        dockerrun.get_dockerrun.return_value = dummy.DOCKERRUN_DICT
        fs_handler = factory.make_multicontainer_fs_handler(dummy.PATH_CONFIG)

        self.assertEqual(dummy.PATH_CONFIG, fs_handler.pathconfig)
        self.assertEqual(dummy.DOCKERRUN_DICT, fs_handler.dockerrun)

    @patch('ebcli.containers.factory._get_solution_stack')
    @patch('ebcli.containers.factory.containerops')
    def test_make_container_not_supported(self, containerops, _get_solution_stack):
        containerops.is_multi.return_value = False
        containerops.is_generic.return_value = False
        containerops.is_preconfigured.return_value = False
        self.assertRaises(NotSupportedError, factory.make_container, pathconfig=dummy.PATH_CONFIG)

    @patch('ebcli.containers.factory.make_multicontainer_fs_handler')
    @patch('ebcli.containers.factory._get_solution_stack')
    @patch('ebcli.containers.factory.containerops')
    def test_make_container_multi(self, containerops, _get_solution_stack,
                                  make_multicontainer_fs_handler):
        containerops.is_multi.return_value = True
        containerops.is_generic.return_value = False
        containerops.is_preconfigured.return_value = False
        make_multicontainer_fs_handler.return_value = dummy.MULTICONTAINER_FS_HANDLER
        _get_solution_stack.return_value = dummy.SOLN_STK

        multicontainer = factory.make_container(envvars_str='a=b,c=d',
                                                pathconfig=dummy.PATH_CONFIG)

        self.assertIsInstance(multicontainer, MultiContainer)
        self.assertEqual(dummy.MULTICONTAINER_FS_HANDLER, multicontainer.fs_handler)
        self.assertEqual(dummy.SOLN_STK, multicontainer.soln_stk)
        self.assertDictEqual({'a': 'b', 'c': 'd'}, multicontainer.opt_env.filtered().map)

    @patch('ebcli.containers.factory.make_container_fs_handler')
    @patch('ebcli.containers.factory._get_solution_stack')
    @patch('ebcli.containers.factory.containerops')
    def test_container_generic(self, containerops, _get_solution_stack,
                               make_container_fs_handler):
        containerops.is_multi.return_value = False
        containerops.is_generic.return_value = True
        containerops.is_preconfigured.return_value = False
        make_container_fs_handler.return_value = dummy.CONTAINER_FS_HANDLER
        _get_solution_stack.return_value = dummy.SOLN_STK

        generic_container = factory.make_container(envvars_str='a=b,c=d',
                                                   pathconfig=dummy.PATH_CONFIG,
                                                   host_port=dummy.HOST_PORT)

        self.assertIsInstance(generic_container, GenericContainer)
        self.assertEqual(dummy.CONTAINER_FS_HANDLER, generic_container.fs_handler)
        self.assertEqual(dummy.SOLN_STK, generic_container.soln_stk)
        self.assertEqual(dummy.HOST_PORT, generic_container.host_port)
        self.assertDictEqual({'a': 'b', 'c': 'd'}, generic_container.opt_env.filtered().map)

    @patch('ebcli.containers.factory.make_container_fs_handler')
    @patch('ebcli.containers.factory._get_solution_stack')
    @patch('ebcli.containers.factory.containerops')
    def test_container_preconfigured(self, containerops, _get_solution_stack,
                                     make_container_fs_handler):
        containerops.is_multi.return_value = False
        containerops.is_generic.return_value = False
        containerops.is_preconfigured.return_value = True
        make_container_fs_handler.return_value = dummy.CONTAINER_FS_HANDLER
        _get_solution_stack.return_value = dummy.SOLN_STK

        generic_container = factory.make_container(envvars_str='a=b,c=d',
                                                   pathconfig=dummy.PATH_CONFIG,
                                                   host_port=dummy.HOST_PORT)

        self.assertIsInstance(generic_container, PreconfiguredContainer)
        self.assertEqual(dummy.CONTAINER_FS_HANDLER, generic_container.fs_handler)
        self.assertEqual(dummy.SOLN_STK, generic_container.soln_stk)
        self.assertEqual(dummy.HOST_PORT, generic_container.host_port)
        self.assertDictEqual({'a': 'b', 'c': 'd'}, generic_container.opt_env.filtered().map)
