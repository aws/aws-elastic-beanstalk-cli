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

import textwrap

from cement.core import foundation, controller, handler

import ebcli
from ebcli.resources.strings import strings
from ebcli.core import io

class EbBaseController(controller.CementBaseController):
    """
    This is the application base controller.
    It handles eb when no sub-commands are given
    """
    class Meta:
        label = 'base'
        description = strings['base.info']
        arguments = [
            (['-v', '--version'], dict(action='store_true',
                                       help='show application/version info')),
            ]

    @controller.expose(hide=True)
    def default(self):
        self.app.log.debug('my awesome debug test')
        if self.app.pargs.version:
            io.echo(strings['app.version_message'],
                                      ebcli.__version__)
        else:
            self.app.args.print_help()

    @property
    def _help_text(self):
        """Returns the help text displayed when '--help' is passed."""
        longest = 0
        def pad(label):
            padlength = longest - len(label)
            padding = '   '
            for x in range(0, padlength):
                padding+= ' '
            return padding

        cmd_txt = ''
        for label in self._visible_commands:
            # get longest command
            if len(label) > longest:
                longest = len(label)

        for label in self._visible_commands:
            cmd = self._dispatch_map[label]
            if len(cmd['aliases']) > 0 and cmd['aliases_only']:
                if len(cmd['aliases']) > 1:
                    first = cmd['aliases'].pop(0)
                    cmd_txt = cmd_txt + " %s (aliases: %s)\n" % \
                                        (first, ', '.join(cmd['aliases']))
                else:
                    cmd_txt = cmd_txt + " %s\n" % cmd['aliases'][0]
            elif len(cmd['aliases']) > 0:
                cmd_txt = cmd_txt + " %s (aliases: %s)\n" % \
                                    (label, ', '.join(cmd['aliases']))
            else:
                cmd_txt = cmd_txt + "   %s" % label

            if cmd['help']:
                cmd_txt = cmd_txt + pad(label) + "%s\n" % cmd['help']
            else:
                cmd_txt = cmd_txt + "\n"

        if len(cmd_txt) > 0:
            txt = '''%s

commands:
%s


''' % (self._meta.description, cmd_txt)
        else:
            txt = self._meta.description

        return textwrap.dedent(txt)