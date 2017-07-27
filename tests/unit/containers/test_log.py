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

from datetime import datetime
from mock import patch, MagicMock
import unittest
from unittest import TestCase
import os
import shutil
import sys
import time

from ebcli.containers import log, dockerrun
from ebcli.core import fileoperations
from ebcli.resources.strings import strings


ROOT_LOG_DIR = '.elasticbeanstalk/logs/local/'
LATEST_SYMLINK = '.elasticbeanstalk/logs/local/latest'
HOST_LOG = '.elasticbeanstalk/logs/local/1234567'
CONTAINER_LOG = '/var/log'
LOG_VOLUME_MAP = {HOST_LOG: CONTAINER_LOG}
DOCKERRUN = {dockerrun.LOGGING_KEY: CONTAINER_LOG}
MOCK_DATETIME = datetime(2015, 3, 18, 13, 33, 30, 254552)
EXPECTED_DATETIME_STR = '150318_133330254552'
EXPECTED_HOST_LOG_PATH = os.path.join(ROOT_LOG_DIR, EXPECTED_DATETIME_STR)
EXPECTED_LOGDIR_PATH = os.path.join('/')
MOCK_LOCAL_DIRS = ['a', 'b', 'c']
MOCK_LOCAL_LOGFILES = ['0', '1', '2']
EXPECTED_LOCAL_LOGPATHS = ['/a/0', '/a/1', '/a/2']
LAST_MODIFIED_FILE_PATH = '/a'


class TestLog(TestCase):
    def test_get_log_volume_map_dockerrun_none(self):
        self.assertDictEqual({}, log.get_log_volume_map(ROOT_LOG_DIR, None))

    @patch('ebcli.containers.log.new_host_log_path')
    def test_get_log_volume_map_dockerrun_logging_exists(self,
                                                         new_host_log_path):
        new_host_log_path.return_value = HOST_LOG
        self.assertDictEqual(LOG_VOLUME_MAP,
                             log.get_log_volume_map(ROOT_LOG_DIR, DOCKERRUN))

    @patch('ebcli.containers.log.new_host_log_path')
    def test_get_log_volume_map_dockerrun_logging_not_exists(self,
                                                             new_host_log_path):
        new_host_log_path.return_value = HOST_LOG
        self.assertDictEqual({}, log.get_log_volume_map(ROOT_LOG_DIR, {}))

    @patch('ebcli.containers.log.datetime')
    def test_new_host_log_path(self, datetime):
        datetime.now.return_value = MOCK_DATETIME
        datetime.strftime.return_value = EXPECTED_DATETIME_STR

        self.assertEquals(EXPECTED_HOST_LOG_PATH, log.new_host_log_path(ROOT_LOG_DIR))
        datetime.now.assert_called_once_with()


    @patch('ebcli.containers.log.fileoperations.set_all_unrestricted_permissions')
    @patch('ebcli.containers.log.os')
    def test_make_logdirs(self, os, set_all_unrestricted_permissions):
        os.path.join.return_value = LATEST_SYMLINK
        fileoperations.remove_execute_access_from_group_and_other_users = MagicMock()

        log.make_logdirs(ROOT_LOG_DIR, HOST_LOG)

        os.path.join.assert_called_once_with(ROOT_LOG_DIR,
                                             log.LATEST_LOGS_DIRNAME)
        os.makedirs.assert_called_once_with(HOST_LOG)
        set_all_unrestricted_permissions.assert_called_once_with(HOST_LOG)
        os.unlink.assert_called_with(LATEST_SYMLINK)
        os.symlink.assert_called_with(HOST_LOG, LATEST_SYMLINK)

    @unittest.skipIf(sys.platform.startswith('win'), 'Test is not designed for Windows')
    def test_make_logdirs__root_log_dir_and_host_log_dir_allow_full_write_access(self):
        try:
            enclosign_dir = '.elasticbeanstalk/logs'
            root_log_dir = '.elasticbeanstalk/logs/local'
            new_local_dir = '.elasticbeanstalk/logs/local/1234456'

            log.make_logdirs(root_log_dir, new_local_dir)

            if sys.version_info < (3, 0):
                local_dir_permissions = '040777'
                enclosing_dir_permissions = '040744'
            else:
                local_dir_permissions = '0o40777'
                enclosing_dir_permissions = '0o40744'

            self.assertEquals(enclosing_dir_permissions, oct(os.stat(enclosign_dir).st_mode))
            self.assertEquals(local_dir_permissions, oct(os.stat(root_log_dir).st_mode))
            self.assertEquals(local_dir_permissions, oct(os.stat(new_local_dir).st_mode))

        finally:
            shutil.rmtree(ROOT_LOG_DIR)


    @patch('ebcli.containers.log.os')
    @patch('ebcli.containers.log.io.echo')
    @patch('ebcli.containers.log.fileoperations.get_logs_location')
    def test_print_log_location_no_root_logs(self, get_logs_location, echo,
                                             os):
        get_logs_location.return_value = EXPECTED_LOGDIR_PATH
        os.path.isdir.return_value = False

        log.print_logs()

        echo.assert_called_once_with(strings['local.logs.nologs'])

    @patch('ebcli.containers.log.os')
    @patch('ebcli.containers.log.io.echo')
    @patch('ebcli.containers.log.fileoperations.get_logs_location')
    @patch('ebcli.containers.log.fileoperations.directory_empty')
    def test_print_log_location_no_sub_logs(self, directory_empty,
                                            get_logs_location, echo, os):
        get_logs_location.return_value = EXPECTED_LOGDIR_PATH
        os.path.isdir.return_value = False
        directory_empty.return_value = True

        log.print_logs()

        echo.assert_called_once_with(strings['local.logs.nologs'])

    @patch('ebcli.containers.log.os')
    @patch('ebcli.containers.log.io.echo')
    @patch('ebcli.containers.log.fileoperations.directory_empty')
    def test_print_log_location_some_log_exists(self, directory_empty, echo,
                                                os):
        timestamp = time.time()
        os.path.isdir.return_value = True
        directory_empty.return_value = False

        log._print_logs(EXPECTED_LOGDIR_PATH, LAST_MODIFIED_FILE_PATH,
                        timestamp)

        fst_msg = strings['local.logs.location'].format(location=EXPECTED_LOGDIR_PATH)
        snd_msg = strings['local.logs.lastlocation'].format(prettydate='just now',
                                                            location=LAST_MODIFIED_FILE_PATH)
        echo.assert_any_call(fst_msg)
        echo.assert_any_call(snd_msg)
