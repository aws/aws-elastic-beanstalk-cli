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

from cement.ext.ext_logging import LoggingLogHandler

from ebcli import __version__
from ..lib import aws
from ..core import fileoperations, io


def pre_run_hook(app):
    if app.pargs.debug:
        io.echo('-- EBCLI Version:', __version__)
        io.echo('-- Python Version:', sys.version)

    if app.pargs.verbose:
        LoggingLogHandler.set_level(app.log, 'INFO')
    set_profile(app.pargs.profile)
    set_ssl(app.pargs.no_verify_ssl)


def set_profile(profile):
    if profile:
        aws.set_profile_override(profile)
    else:
        profile = fileoperations.get_default_profile()
        if profile:
            aws.set_profile(profile)


def set_ssl(noverify):
    if not noverify:
        noverify = fileoperations.get_config_setting(
            'global', 'no-verify-ssl', default=False)
    if noverify:
        aws.no_verify_ssl()