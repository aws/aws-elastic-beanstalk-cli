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

from ebcli.objects.exceptions import ValidationError
from mock import patch
from unittest import TestCase
import ebcli.containers.dockerrun as dr


INVALID_VERSION = '3.5'
MOCK_IMG_NAME = 'janedoe/image'
MOCK_DOCKERRUN_PATH = '/home/local/ANT/user/hello/Dockerrun.aws.json'
MOCK_DOCKERRUN_CONTENTS = '{}'
MOCK_DOCKERRUN = {}
MOCK_PORT = '5000'
JSON_TRUE = "true"
MOCK_AUTH_KEY = '.dockerfg'
MOCK_AUTH_BUCKET = 'bucket'
MOCK_LOGDIR = '.elasticbeanstalk/logs/local'


class TestDockerrun(TestCase):
    def test_validate_dockerrun_v1_missing_version(self):
        drun = _make_mock_dockerrun()
        self.assertRaises(ValidationError, dr.validate_dockerrun_v1, drun, False)
        self.assertRaises(ValidationError, dr.validate_dockerrun_v1, drun, True)

    def test_validate_dockerrun_v1_invalid_version(self):
        drun = _make_mock_dockerrun(INVALID_VERSION)
        self.assertRaises(ValidationError, dr.validate_dockerrun_v1, drun, False)
        self.assertRaises(ValidationError, dr.validate_dockerrun_v1, drun, True)

    def test_validate_dockerrun_v1_valid_version(self):
        dockerrun = _make_mock_dockerrun(dr.VERSION_ONE)
        try:
            dr.validate_dockerrun_v1(dockerrun, False)
        except Exception:
            assertFail('Expected no exceptions raised.')

    def test_validate_dockerrun_v1_no_img(self):
        drun = _make_mock_dockerrun(dr.VERSION_ONE)
        self.assertRaises(ValidationError, dr.validate_dockerrun_v1, drun, True)

    def test_validate_dockerrun_v1_no_img_name(self):
        drun = _make_mock_dockerrun(dr.VERSION_ONE, img_update=JSON_TRUE)
        self.assertRaises(ValidationError, dr.validate_dockerrun_v1, drun, True)

    def test_validate_dockerrun_v1_no_port(self):
        drun = _make_mock_dockerrun(dr.VERSION_ONE, MOCK_IMG_NAME, JSON_TRUE)
        self.assertRaises(ValidationError, dr.validate_dockerrun_v1, drun, True)

    def test_validate_dockerrun_v1_has_port(self):
        drun = _make_mock_dockerrun(dr.VERSION_ONE, MOCK_IMG_NAME,
                                    JSON_TRUE, MOCK_PORT)
        try:
            dr.validate_dockerrun_v1(drun, True)
        except Exception:
            self.assertFail('Expected no exceptions raised.')

    def test_validate_dockerrun_v2_no_dockerrun(self):
        self.assertRaises(ValidationError, dr.validate_dockerrun_v2, None)

    def test_validate_dockerrun_v2_invalid_version(self):
        drun = _make_mock_dockerrun(dr.VERSION_ONE)
        self.assertRaises(ValidationError, dr.validate_dockerrun_v2, drun)

    def test_validate_dockerrun_v2_valid_version(self):
        drun = _make_mock_dockerrun(dr.VERSION_TWO)
        try:
            dr.validate_dockerrun_v2(drun)
        except Exception:
            self.assertFail('Expected no exceptions raised.')

    def test_require_docker_pull_with_no_dockerrun(self):
        self.assertTrue(dr.require_docker_pull(None),
                        'Expected pull True when no dockerrun is provided')

    def test_require_docker_pull_with_missing_img(self):
        dockerrun = _make_mock_dockerrun()
        self.assertTrue(dr.require_docker_pull(dockerrun),
                        'Expected pull True when no Image is provided')

    def test_require_docker_pull_with_img_true(self):
        dockerrun = _make_mock_dockerrun(img_update=JSON_TRUE)
        self.assertTrue(dr.require_docker_pull(dockerrun),
                        'Expected pull True when Image.Update=' + JSON_TRUE)

    def test_require_docker_pull_with_img_false(self):
        dockerrun = _make_mock_dockerrun(img_update=dr.JSON_FALSE)
        msg = 'Expected False on when Image.Update=' + dr.JSON_FALSE
        self.assertFalse(dr.require_docker_pull(dockerrun), msg)

    @patch('ebcli.containers.dockerrun.fileoperations.get_json_dict')
    def test_get_dockerrun_happy_case(self, get_json_dict):
        get_json_dict.return_value = {}
        self.assertEquals({}, dr.get_dockerrun(MOCK_DOCKERRUN_PATH))

    @patch('ebcli.containers.dockerrun.fileoperations.get_json_dict')
    def test_get_dockerrun_ioerror_case(self, get_json_dict):
        get_json_dict.side_effect = IOError
        self.assertIsNone(dr.get_dockerrun(MOCK_DOCKERRUN_PATH))

    @patch('ebcli.containers.dockerrun.fileoperations.get_json_dict')
    def test_get_dockerrun_valueerror_case(self, get_json_dict):
        get_json_dict.side_effect = ValueError
        self.assertRaises(ValidationError, dr.get_dockerrun,
                          MOCK_DOCKERRUN_PATH)

    def test_require_auth_download_when_dockerrun_none(self):
        self.assertFalse(dr.require_auth_download(None))

    def test_require_auth_download_key_and_bucket_exists(self):
        dockerrun = _make_mock_dockerrun(auth_key=MOCK_AUTH_KEY,
                                         auth_bucket=MOCK_AUTH_BUCKET,
                                         version=dr.VERSION_ONE)
        self.assertTrue(dr.require_auth_download(dockerrun))

    def test_require_auth_download_key_and_bucket_not_exists(self):
        self.assertFalse(dr.require_auth_download({}))

    def test_get_auth_key(self):
        dockerrun = _make_mock_dockerrun(auth_key=MOCK_AUTH_KEY, version=dr.VERSION_ONE)
        self.assertEquals(MOCK_AUTH_KEY, dr.get_auth_key(dockerrun))

    def test_get_auth_key_keyerror(self):
        self.assertRaises(KeyError, dr.get_auth_key, {})

    def test_get_auth_bucket_name(self):
        dockerrun = _make_mock_dockerrun(auth_bucket=MOCK_AUTH_BUCKET,
                                         version=dr.VERSION_ONE)
        self.assertEquals(MOCK_AUTH_BUCKET, dr.get_auth_bucket_name(dockerrun))

    def test_get_auth_bucket_name_keyerror(self):
        self.assertRaises(KeyError, dr.get_auth_bucket_name, {})

    def test_get_logdir(self):
        dockerrun = _make_mock_dockerrun(logdir=MOCK_LOGDIR)
        self.assertEquals(MOCK_LOGDIR, dr.get_logdir(dockerrun))

    def test_get_logdir_none_dockerrun(self):
        self.assertIsNone(dr.get_logdir(None))

    def test_get_logdir_key_missing_dockerrun(self):
        self.assertIsNone(dr.get_logdir({}))


def _make_mock_dockerrun(version=None, img_name=None, img_update=None,
                         port=None, auth_key=None, auth_bucket=None,
                         logdir=None):
    dockerrun = {}

    if version:
        dockerrun[dr.VERSION_KEY] = version

    if img_name or img_update:
        dockerrun[dr.IMG_KEY] = {}

    if img_name:
        dockerrun[dr.IMG_KEY][dr.IMG_NAME_KEY] = img_name

    if img_update:
        dockerrun[dr.IMG_KEY][dr.IMG_UPDATE_KEY] = img_update

    if port:
        dockerrun[dr.PORTS_KEY] = [{dr.CONTAINER_PORT_KEY: port}]

    if auth_key or auth_bucket:
        dockerrun[dr.AUTH_KEY] = {}

    if auth_key:
        dockerrun[dr.AUTH_KEY][dr.AUTHKEY_KEY] = auth_key

    if auth_bucket:
        dockerrun[dr.AUTH_KEY][dr.AUTH_BUCKET_KEY] = auth_bucket

    if logdir:
        dockerrun[dr.LOGGING_KEY] = logdir

    return dockerrun
