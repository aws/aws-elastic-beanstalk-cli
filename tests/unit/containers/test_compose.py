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
import sys

import unittest
from mock import patch
from unittest import TestCase

from ebcli.containers import compose
from ebcli.containers.envvarcollector import EnvvarCollector


DOCKER_PROJ_PATH = '/a/b/c'
HOST_LOG = '/a/b/c/.elasticbeanstalk/logs/local/12345_6789'
ENV_COLLECTOR = EnvvarCollector({'a': 'b', 'c': 'd'})


class TestCompose(TestCase):
    def test_iter_services_simple(self):
        simple_compose = _get_expected_multicontainer_compose_dict_simple()
        actual_services = compose.iter_services(simple_compose)
        expected_services = ('nginxproxy', 'phpapp')
        self.assertListEqual(sorted(expected_services), sorted(actual_services))

    def test_iter_services_complex(self):
        complex_compose = _get_expected_multicontainer_compose_dict_complex()
        actual_services = compose.iter_services(complex_compose)
        expected_services = ('nginxproxy', 'nodeapp', 'tomcatapp')

        self.assertListEqual(sorted(expected_services), sorted(actual_services))

    def test_compose_simple(self):
        dockerrun = _get_mock_multicontainer_dockerrun_simple()
        expected_compose = _get_expected_multicontainer_compose_dict_simple()
        actual_compose = compose.compose_dict(dockerrun, DOCKER_PROJ_PATH,
                                              HOST_LOG, ENV_COLLECTOR)

        self.assertDictEqual(expected_compose, actual_compose)

    @unittest.skipIf(sys.platform.startswith('win'), 'Test is not designed for Windows presently')
    @patch('ebcli.containers.compose.os.makedirs')
    def test_compose_complex(self, makedirs):
        dockerrun = _get_mock_multicontainer_dockerrun_complex()
        expected_compose = _get_expected_multicontainer_compose_dict_complex()
        actual_compose = compose.compose_dict(dockerrun, DOCKER_PROJ_PATH,
                                              HOST_LOG, ENV_COLLECTOR)

        self.assertDictEqual(expected_compose, actual_compose)

    def test_compose_with_envvars(self):
        dockerrun = _get_mock_multicontainer_dockerrun_with_envvars()
        expected_compose = _get_expected_multicontainer_compose_dict_with_envvars()

        actual_compose = compose.compose_dict(dockerrun, DOCKER_PROJ_PATH,
                                              HOST_LOG, ENV_COLLECTOR)

        self.assertDictEqual(expected_compose, actual_compose)

    def test_compose_with_local_definitions(self):
        dockerrun = _get_mock_multicontainer_dockerrun_with_local_definitions()
        expected_compose = _get_expected_multicontainer_compose_dict_with_local_definitions()

        actual_compose = compose.compose_dict(dockerrun, DOCKER_PROJ_PATH,
                                              HOST_LOG, ENV_COLLECTOR)

        self.assertDictEqual(expected_compose, actual_compose)


def _get_mock_multicontainer_dockerrun_simple():
    return {
        "containerDefinitions": [
            {
                "image": "php:fpm",
                "name": "php-app"
            },
            {
                "image": "nginx",
                "links": [
                    "php-app"
                ],
                "name": "nginx-proxy",
                "portMappings": [
                    {
                        "containerPort": 80,
                        "hostPort": 80
                    }
                ]
            }
        ]
    }


def _get_expected_multicontainer_compose_dict_simple():
    return {
        "nginxproxy": {
            "image": "nginx",
            "links": [
                "phpapp:php-app"
            ],
            "ports": [
                "80:80"
            ],
            'environment': ENV_COLLECTOR.map
        },
        "phpapp": {
            "image": "php:fpm",
            'environment': ENV_COLLECTOR.map
        }
    }


def _get_mock_multicontainer_dockerrun_complex():
    return {
        "AWSEBDockerrunVersion": 2,
        "containerDefinitions": [
            {
                "command": [
                    "/bin/bash",
                    "/usr/src/app/run.sh"
                ],
                "essential": "true",
                "image": "node:0.12",
                "memory": 128,
                "name": "node-app"
            },
            {
                "essential": "true",
                "image": "tomcat:8.0",
                "memory": 256,
                "mountPoints": [
                    {
                        "containerPath": "/usr/local/tomcat/logs",
                        "sourceVolume": "awseb-logs-tomcat-app"
                    }
                ],
                "name": "tomcat-app"
            },
            {
                "essential": "true",
                "image": "nginx",
                "links": [
                    "node-app",
                    "tomcat-app"
                ],
                "memory": 128,
                "mountPoints": [
                    {
                        "containerPath": "/var/log/nginx",
                        "sourceVolume": "awseb-logs-nginx-proxy"
                    },
                    {
                        "containerPath": "/etc/nginx/conf.d",
                        "readOnly": "true",
                        "sourceVolume": "nginx-proxy-conf"
                    }
                ],
                "name": "nginx-proxy",
                "portMappings": [
                    {
                        "containerPort": 8000,
                        "hostPort": 9000
                    },
                    {
                        "containerPort": 1000,
                        "hostPort": 2000
                    }
                ]
            }
        ],
        "volumes": [
            {
                "host": {
                    "sourcePath": "/var/app/current/proxy/conf.d"
                },
                "name": "nginx-proxy-conf"
            }
        ]
    }


def _get_expected_multicontainer_compose_dict_complex():
    return {
        "nginxproxy": {
            "image": "nginx",
            "links": [
                "nodeapp:node-app",
                "tomcatapp:tomcat-app"
            ],
            "ports": [
                "9000:8000",
                "2000:1000"
            ],
            "volumes": [
                "{}/nginx-proxy:/var/log/nginx".format(HOST_LOG),
                "{}/proxy/conf.d:/etc/nginx/conf.d:ro".format(DOCKER_PROJ_PATH)
            ],
            'environment': ENV_COLLECTOR.map
        },
        "nodeapp": {
            "command": ["/bin/bash", "/usr/src/app/run.sh"],
            "image": "node:0.12",
            'environment': ENV_COLLECTOR.map
        },
        "tomcatapp": {
            "image": "tomcat:8.0",
            "volumes": [
                "{}/tomcat-app:/usr/local/tomcat/logs".format(HOST_LOG)
            ],
            'environment': ENV_COLLECTOR.map
        }
    }


def _get_mock_multicontainer_dockerrun_with_envvars():
    return {
        "containerDefinitions": [
            {
                "image": "php:fpm",
                "name": "php-app"
            },
            {
                "image": "nginx",
                "links": [
                    "php-app"
                ],
                "name": "nginx-proxy",
                "portMappings": [
                    {
                        "containerPort": 80,
                        "hostPort": 80
                    }
                ],
                "environment": [
                    {
                      "name": "a",
                      "value": 1000
                    },
                    {
                      "name": "c",
                      "value": 2000
                    },
                    {
                      "name": "e",
                      "value": "f"
                    },
                ]
            }
        ]
    }


def _get_expected_multicontainer_compose_dict_with_envvars():
    return {
        "nginxproxy": {
            "image": "nginx",
            "links": [
                "phpapp:php-app"
            ],
            "ports": [
                "80:80"
            ],
            'environment': {'a': 'b', 'c': 'd', 'e': 'f'}
        },
        "phpapp": {
            "image": "php:fpm",
            'environment': ENV_COLLECTOR.map
        }
    }


def _get_mock_multicontainer_dockerrun_with_local_definitions():
    return {
        "containerDefinitions": [
            {
                "image": "php:fpm",
                "name": "php-app"
            }
        ],
        'localContainerDefinitions': [
            {
                "image": "nginx",
                "links": [
                    "php-app"
                ],
                "name": "nginx-proxy",
                "portMappings": [
                    {
                        "containerPort": 80,
                        "hostPort": 80
                    }
                ],
                "environment": [
                    {
                      "name": "a",
                      "value": 1000
                    },
                    {
                      "name": "c",
                      "value": 2000
                    },
                    {
                      "name": "e",
                      "value": "f"
                    },
                ]
            }
        ]
    }

# They are the same since only difference is php-app was moved into localContainerDefinitions
_get_expected_multicontainer_compose_dict_with_local_definitions = _get_expected_multicontainer_compose_dict_with_envvars
