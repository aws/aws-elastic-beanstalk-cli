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

from ebcli.containers.fshandler import ContainerFSHandler
from ebcli.containers import containerops
from ebcli.containers.preconfigured_container import PreconfiguredContainer
from ebcli.objects.exceptions import ValidationError
from mock import patch, Mock
from unittest import TestCase


HOST_LOG_PATH = '/.elasticbeanstalk/logs/local/12345/'
DEFAULT_LOG_PATH = '/bar'
DOCKERRUN_LOG_PATH = '/bar'
VOLUME_MAP = {HOST_LOG_PATH: DOCKERRUN_LOG_PATH}
MOCK_IMG = 'foo'
MOCK_DOCKERFILE_SRC = '/glassfish-runtime-4.1-jdk8'
MOCK_DOCKERFILE_DEST = '/bar/Dockerfile.local'
PRECONFIG_HOST_LOG_PATH = '/.elasticbeanstalk/logs/local'
PRECONFIG_CONTAINER_LOG_PATH = '/foo'
SOLN_STK = Mock()
SOLN_STK.version = 'Multi-container Docker 1.3.3 (Generic)'


class TestPreconfiguredContainer(TestCase):
    def setUp(self):
        self.pathconfig = Mock()
        self.fs_handler = Mock(pathconfig=self.pathconfig)
        self.fs_handler.copy_dockerfile = Mock()
        self.fs_handler.dockerrun = None
        self.container = PreconfiguredContainer(self.fs_handler, SOLN_STK, None)

    @patch('ebcli.containers.preconfigured_container._validate_preconfig_dockerfile')
    def test_no_preconfig_dockerfile_check(self, _validate_preconfig_dockerfile):
        _bypass_preconfig_dockerfile_validation(self.pathconfig)

        try:
            self.container.validate()
        except:
            self.fail('No validation is necessary if no Dockerfile exists')

        self.assertFalse(_validate_preconfig_dockerfile.called)

    @patch('ebcli.containers.preconfigured_container.containerops._get_preconfig_info')
    @patch('ebcli.containers.preconfigured_container.commands._get_base_img')
    def test_validation_pass(self, _get_base_img, _get_preconfig_info):
        _expect_preconfig_dockerfile_validation(self.pathconfig)
        _get_preconfig_info.return_value = {containerops.RUNTIME_IMG_KEY:
                                            MOCK_IMG}
        _get_base_img.return_value = MOCK_IMG

        msg = ('If user provides Dockerfile, then that Dockerfile img must '
               'match runtime img appropriate for the solution stack')

        try:
            self.container.validate()
        except:
            self.fail(msg)

    @patch('ebcli.containers.preconfigured_container.containerops._get_preconfig_info')
    @patch('ebcli.containers.preconfigured_container.commands._get_base_img')
    def test_validation_fail(self, _get_base_img, _get_preconfig_info):
        _expect_preconfig_dockerfile_validation(self.pathconfig)
        _get_preconfig_info.return_value = {containerops.RUNTIME_IMG_KEY:
                                            MOCK_IMG}
        _get_base_img.return_value = None

        self.assertRaises(ValidationError, self.container.validate)

    @patch('ebcli.containers.preconfigured_container.dockerrun')
    def test_validate_dockerrun_v1(self, dockerrun):
        _bypass_preconfig_dockerfile_validation(self.pathconfig)
        self.container.validate()
        dockerrun.validate_dockerrun_v1.assert_called_once_with(self.fs_handler.dockerrun,
                                                                False)

    def test_containerize(self):
        _bypass_preconfig_dockerfile_validation(self.pathconfig)

        self.container._containerize()
        self.fs_handler.copy_dockerfile.assert_called_once_with(self.container.soln_stk,
                                                                self.container.container_cfg)

    @patch('ebcli.containers.preconfigured_container.AbstractContainer._get_log_volume_map')
    def test_get_log_volume_map_exists_from_dockerrun(self,
                                                      _get_container_log_path):
        _bypass_preconfig_dockerfile_validation(self.pathconfig)
        _get_container_log_path.return_value = VOLUME_MAP

        self.assertDictEqual(self.container._get_log_volume_map(), VOLUME_MAP)

    @patch('ebcli.containers.preconfigured_container.log')
    @patch('ebcli.containers.preconfigured_container.containerops')
    @patch('ebcli.containers.preconfigured_container.AbstractContainer._get_log_volume_map')
    def test_get_log_volume_map_exists_by_default_log_path(self,
                                                           _get_container_log_path,
                                                           containerops, log):
        _bypass_preconfig_dockerfile_validation(self.pathconfig)
        _get_container_log_path.return_value = {}
        log.new_host_log_path.return_value = HOST_LOG_PATH
        containerops.get_runtime_default_log_path.return_value = DEFAULT_LOG_PATH

        expected_volume_map = {HOST_LOG_PATH: DEFAULT_LOG_PATH}

        self.assertDictEqual(expected_volume_map, self.container._get_log_volume_map())


def _bypass_preconfig_dockerfile_validation(pathconfig):
    pathconfig.dockerfile_exists = lambda: False


def _expect_preconfig_dockerfile_validation(pathconfig):
    pathconfig.dockerfile_exists = lambda: True
