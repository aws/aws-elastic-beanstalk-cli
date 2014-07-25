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

import mock

from cement.utils import test
from core.ebcore import EB

from lib import aws


class TestInit(test.CementTestCase):
    app_class = EB

    def setUp(self):
        super(TestInit, self).setUp()
        self.reset_backend()


    def test_myapp(self):
        self.app = EB(argv=['update'])
        self.app.setup()
        self.app.run()
        self.app.close()

    @mock.patch('lib.elasticbeanstalk.aws')
    def myTest(self, mock_aws):
        aws.make_api_call('elasticbeanstalk', 'describe-applications')
        mock_aws._get_session.assert_called_with('elasticbeanstalk')


