# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import time
import logging

from ebcli.lib import elasticbeanstalk

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger('ebcli.beanstalkutils')


class BeanstalkUtilities():
    def __init__(self, region, app_name=None, env_name=None):
        self.env_name = env_name
        self.app_name = app_name
        self.region = region

    def check_env_status(self, status, env_name=None, timeout=900, poll_rate=2):
        if env_name is None and self.env_name is None:
            LOG.error("No environment specified cannot poll")
            return False
        if env_name is None:
            env_name = self.env_name

        LOG.info("Polling Env '{0}' for status: {1} for {2} seconds".format(env_name, status, timeout))
        elasticbeanstalk.aws._region_name = self.region
        env = elasticbeanstalk.get_environment(app_name=self.app_name, env_name=env_name)

        if env is None:
            LOG.error("Env {0} does not exist, cannot poll for status".format(env_name))
            return False

        start_time = time.time()
        while env.status != status:
            LOG.debug("{0}: {1}; expected: {2}".format(env_name, env.status, status))
            if time.time() - start_time > timeout:
                LOG.error("Poll timeout exceed for Env {0} polling for status: {1}".format(env_name, status))
                return False
            time.sleep(poll_rate)
            env = elasticbeanstalk.get_environment(app_name=self.app_name, env_name=env_name)
        LOG.info("Successfully matched Env {0} for status {1}".format(env_name, status))
        return True


class EnvStatus(object):
    Launching = 'Launching'
    Updating = 'Updating'
    Ready = 'Ready'
    Terminating = 'Terminating'
    Terminated = ' Terminated'
