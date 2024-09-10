# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
from mock import patch, Mock
from unittest import TestCase

from ebcli.containers import compat
from ebcli.objects.exceptions import CommandError


DOCKER_HOST_KEY = 'DOCKER_HOST'
DOCKER_HOST_VAL = 'tcp://192.168.59.105:2376'
DOCKER_TLS_VERIFY_KEY = 'DOCKER_TLS_VERIFY'
DOCKER_TLS_VERIFY_VAL = '1'
DOCKER_CERT_PATH_KEY = 'DOCKER_CERT_PATH'
DOCKER_CERT_PATH_VAL = '/a/b/c'
MOCK_MAC_CONTAINER_IP = '123.456.789'
EXPECTED_SHELLINIT = os.linesep.join(['    export {}={}'.format(DOCKER_TLS_VERIFY_KEY, DOCKER_TLS_VERIFY_VAL),
                                      '    export {}={}'.format(DOCKER_HOST_KEY, DOCKER_HOST_VAL),
                                      '    export {}={}'.format(DOCKER_CERT_PATH_KEY, DOCKER_CERT_PATH_VAL)])

EXPECTED_ENVIRON_VARS_SET = {DOCKER_HOST_KEY: DOCKER_HOST_VAL,
                             DOCKER_TLS_VERIFY_KEY: DOCKER_TLS_VERIFY_VAL,
                             DOCKER_CERT_PATH_KEY: DOCKER_CERT_PATH_VAL}


class TestCompat(TestCase):
    def test_remove_leading_zeros_from_version(self):
        versions_tests = []
        versions_tests.append(('0001.000.000', '1.0.0'))
        versions_tests.append(('1.0001.0000-rc.1', '1.1.0-rc.1'))
        versions_tests.append(('1.3.0', '1.3.0'))
        versions_tests.append(('17.03.0-ce', '17.3.0-ce'))
        versions_tests.append(('107.3.30-ce', '107.3.30-ce'))
        versions_tests.append(('017.030.07-ce', '17.30.7-ce'))
        versions_tests.append(('17.03.08-ce', '17.3.8-ce'))
        for test in versions_tests:
            self.assertEqual(compat.remove_leading_zeros_from_version(test[0]), test[1])
