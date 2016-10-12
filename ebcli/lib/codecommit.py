# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import datetime
import sys

if sys.version_info >= (3, 0):
    from urllib.parse import urlsplit
if sys.version_info < (3, 0) and sys.version_info >= (2, 5):
    from urlparse import urlsplit

from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from cement.utils.misc import minimal_logger

from . import aws
from ..core import io
from ..lib import utils
from ..objects.exceptions import ServiceError

LOG = minimal_logger(__name__)


def _make_api_call(operation_name, **operation_options):
    try:
        result = aws.make_api_call('codecommit', operation_name, **operation_options)
    except ServiceError as ex:
        if ex.code == 'AccessDeniedException':
            io.echo("EB CLI does not have the right permissions to access CodeCommit."
                    " List of IAM policies needed by EB CLI, please configure and try again.\n "
                    "codecommit:CreateRepository\n codecommit:CreateBranch\n codecommit:GetRepository\n "
                    "codecommit:ListRepositories\n codecommit:ListBranches\n"
                    "To learn more, see Docs: http://docs.aws.amazon.com/codecommit/latest/userguide/access-permissions.html")
        raise ex
    return result


def create_repository(repo_name, repo_description=None):
    params = dict(repositoryName=repo_name)

    if repo_description is not None:
        params['repositoryDescription'] = repo_description

    result = _make_api_call('create_repository', **params)
    return result


def create_branch(repo_name, branch_name, commit_id):
    params = dict(repositoryName=repo_name, branchName=branch_name, commitId=commit_id)

    _make_api_call('create_branch', **params)


def get_repository(repo_name):
    params = dict(repositoryName=repo_name)

    result = _make_api_call('get_repository', **params)
    return result


def get_branch(repo_name, branch_name):
    params = dict(repositoryName=repo_name, branchName=branch_name)

    result = _make_api_call('get_branch', **params)
    return result


def list_repositories(next_token=None, sort_by='lastModifiedDate', order='descending'):
    params = dict()

    if next_token is not None:
        params['nextToken'] = next_token

    if sort_by is not None:
        params['sortBy'] = sort_by

    if order is not None:
        params['order'] = order

    result = _make_api_call('list_repositories', **params)
    return result


def list_branches(repo_name, next_token=None):
    params = dict(repositoryName=repo_name)

    if next_token is not None:
        params['nextToken'] = next_token

    result = _make_api_call('list_branches', **params)
    return result


def region_supported(region):
    supported_regions = ["us-east-1"]
    if region is not None and region in supported_regions:
        return True

    return False


def _sign_codecommit_url(region, url_to_sign):
    credentials = aws.get_credentials()
    signer = SigV4Auth(credentials, 'codecommit', region)
    request = AWSRequest()
    request.url = url_to_sign
    request.method = 'GIT'
    now = datetime.datetime.utcnow()
    request.context['timestamp'] = now.strftime('%Y%m%dT%H%M%S')
    split = urlsplit(request.url)
    # we don't want to include the port number in the signature
    hostname = split.netloc.split(':')[0]
    canonical_request = '{0}\n{1}\n\nhost:{2}\n\nhost\n'.format(
        request.method,
        split.path,
        hostname)
    LOG.debug("Calculating signature using v4 auth.")
    LOG.debug('CanonicalRequest: %s', canonical_request)
    string_to_sign = signer.string_to_sign(request, canonical_request)
    LOG.debug('StringToSign: %s', utils.retract_string(string_to_sign))
    signature = signer.signature(string_to_sign, request)
    LOG.debug('Signature: %s', utils.retract_string(signature))
    return '{0}Z{1}'.format(request.context['timestamp'], signature)


def create_signed_url(remote_url):
    split_url = remote_url.split("//")
    credentials = aws.get_credentials()
    password = _sign_codecommit_url(aws.get_region_name(), remote_url)
    username = credentials.access_key

    if credentials.token is not None:
        username += "%" + credentials.token

    signed_url = "https://{0}:{1}@{2}".format(username, password, split_url[1])
    retracted_signed_url = "https://{0}:{1}@{2}".format(utils.retract_string(username), utils.retract_string(password), split_url[1])
    LOG.debug("Created Signed URL for CodeCommit: " + retracted_signed_url)
    return signed_url