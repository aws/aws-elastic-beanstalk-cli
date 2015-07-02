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

"""
Dynamic IO / Interactive terminal
"""

import signal
import sys

from blessed import Terminal

from ..core import io, ebglobals

terminal = None
counter = 0
total = 1

# Special characters
UP_ARROW = u'\u25b2'
DOWN_ARROW = u'\u25bc'
LEFT_ARROW = u'\u25c0'
RIGHT_ARROW = u'\u25b6'


def get_terminal():
    if terminal is None:
        init_terminal()
    return terminal


def init_terminal():
    global terminal
    if terminal:
        return
    else:
        terminal = Terminal()
        io.echo(terminal.clear())

        def on_resize(sig, action):
            pass
        signal.signal(signal.SIGWINCH, on_resize)


def reset_terminal():
    global counter, total
    total = counter
    counter = 0


def height():
    init_terminal()
    return terminal.height


def width():
    init_terminal()
    return terminal.width


def underlined(string):
    init_terminal()
    return terminal.underline(string)


def reverse_colors(string):
    init_terminal()
    return terminal.reverse(string)


def echo_line(*strings):
    global counter
    init_terminal()
    # if total and counter < total:
    echo_on_line(counter, *strings)
    counter += 1


def clear_eos():
    init_terminal()
    if term_is_live():
        return terminal.clear_eos()
    else:
        return ''


def hide_cursor():
    init_terminal()
    io.echo(terminal.hide_cursor(), end='')


def return_cursor_to_normal():
    init_terminal()
    if term_is_live():
        move_cursor(total-1, 1)
    io.echo(terminal.normal_cursor())


def term_is_live():
    if not sys.stdout.isatty():  # pipe
        return False
    if ebglobals.app.pargs.debug:  # Debug mode. Don't overwrite anything
        return False
    return True


def echo_on_line(line_num, *strings):
    init_terminal()
    if term_is_live():
        # if line_num == 0:
        #     io.echo(terminal.clear_eos())
        with terminal.location(x=0, y=line_num):
            io.echo(terminal.clear_eol())
        with terminal.location(x=0, y=line_num):
            io.echo(*strings)
        # move_cursor(counter, 1)
    else:
        io.echo(*strings)


def move_cursor(line_num, column_num):
    io.echo(terminal.move(line_num, column_num), end='')