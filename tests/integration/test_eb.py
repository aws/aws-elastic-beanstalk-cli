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
import sys

from tests.utilities.testutils import unittest, eb

class TestBaseCommandFunctionality(unittest.TestCase):
    """
    These are a set of tests that assert high level features of
    the CLI.  They don't anything exhaustive and is meant as a smoke
    test to verify basic CLI functionality isn't entirely broken.
    """
    def test_help_usage_top_level(self):
        p = eb('')
        self.assertEqual(p.rc, 0)

        expected_output = ''
        if sys.platform.startswith('win'):
            expected_output = ''.join(['usage: eb \(sub-commands ...\) \[options ...\] {arguments ...}\r\n\r\n',
                                       'Welcome\s+to\s+the\s+Elastic\s+Beanstalk\s+Command\s+Line\s+Interface\s+\(EB\s+CLI\).*'])
        else:
            expected_output = ''.join(['usage: eb \(sub-commands ...\) \[options ...\] {arguments ...}\n\n',
                                       'Welcome\s+to\s+the\s+Elastic\s+Beanstalk\s+Command\s+Line\s+Interface\s+\(EB\s+CLI\).*'])

        self.assertRegexpMatches(
            p.stdout, expected_output)

    def test_top_level_options_debug(self):
        p = eb('--debug')
        self.assertEqual(p.rc, 0)
        self.assertIn('DEBUG', p.stderr)

    def test_unknown_command(self):
        p = eb('bad-command')
        self.assertEqual(p.rc, 0)
        self.assertIn('eb: error: unrecognized arguments: bad-command', p.stderr)

    def test_unknown_argument(self):
        p = eb('--bad-flag')
        self.assertEqual(p.rc, 0)
        self.assertIn('eb: error: unrecognized arguments: --bad-flag', p.stderr)

    def test_version(self):
        p = eb('--version')
        self.assertEqual(p.rc, 0)
        # The version is wrote to standard out for Python 3.4 and
        # standard error for other Python versions.
        version_output = p.stderr.startswith('EB CLI') or \
            p.stdout.startswith('EB CLI')
        self.assertTrue(version_output, p.stderr)
        self.assertRegexpMatches(p.stdout, 'EB\s+CLI\s+[0-9]+.[0-9]+.[0-9]+\s+\(Python\s+.*\)')


if __name__ == '__main__':
    unittest.main()
