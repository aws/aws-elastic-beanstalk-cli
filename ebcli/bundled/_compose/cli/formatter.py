from __future__ import unicode_literals
from __future__ import absolute_import
import os
from tabulate import tabulate


def get_tty_width():
    tty_size = os.popen('stty size', 'r').read().split()
    if len(tty_size) != 2:
        return 80
    _, width = tty_size
    return int(width)


class Formatter(object):
    def table(self, headers, rows):
        return tabulate(headers, rows)
