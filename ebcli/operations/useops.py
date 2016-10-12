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
from ..objects.exceptions import ServiceError, NotFoundError

from ..lib import elasticbeanstalk, codecommit
from . import commonops, gitops


def switch_default_environment(app_name, env_name):
    # check that environment exists
    elasticbeanstalk.get_environment(app_name, env_name)
    commonops.set_environment_for_current_branch(env_name)


def switch_default_repo_and_branch(repo_name, branch_name):
    # check that branch and repo exist
    try:
        codecommit.get_branch(repo_name, branch_name)
    except ServiceError:
        raise NotFoundError("CodeCommit branch not found: {0}".format(branch_name))

    gitops.set_repo_default_for_current_environment(repo_name)
    gitops.set_branch_default_for_current_environment(branch_name)
