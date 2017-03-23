import os, sys

import logging
import traceback

from argparse import SUPPRESS, ArgumentTypeError

from botocore.compat import six

from ebcli.lib.aws import TooManyPlatformsError

iteritems = six.iteritems

from cement.core.exc import CaughtSignal

from . import io
from ebcli.objects.exceptions import *
from ebcli.resources.strings import strings, flag_text


def fix_path():
    parent_folder = os.path.dirname(__file__)
    parent_dir = os.path.abspath(parent_folder)
    while not parent_folder.endswith('ebcli'):
        # Keep going up until we get to the right folder
        parent_folder = os.path.dirname(parent_folder)
        parent_dir = os.path.abspath(parent_folder)

    vendor_dir = os.path.join(parent_dir, 'bundled')

    sys.path.insert(0, vendor_dir)

fix_path()

def run_app(app):
    # Squash cement logging
    ######
    for d, k in iteritems(logging.Logger.manager.loggerDict):
        if d.startswith('cement') and isinstance(k, logging.Logger):
            k.setLevel('ERROR')
    #######

    try:
        app.setup()
        app.run()

    # Handle General Exceptions
    except CaughtSignal:
        io.echo()
        app.close(code=5)
    except NoEnvironmentForBranchError:
        pass
    except InvalidStateError:
        io.log_error(strings['exit.invalidstate'])
        app.close(code=3)
    except NotInitializedError:
        io.log_error(strings['exit.notsetup'])
        app.close(code=126)
    except NoSourceControlError:
        io.log_error(strings['sc.notfound'])
        app.close(code=3)
    except NoRegionError:
        io.log_error(strings['exit.noregion'])
        app.close(code=3)
    except ConnectionError:
        io.log_error(strings['connection.error'])
        app.close(code=2)
    except ArgumentTypeError:
        io.log_error(strings['exit.argerror'])
        app.close(code=4)
    except TooManyPlatformsError:
        io.log_error(strings['toomanyplatforms.error'])
        app.close(code=4)
    except EBCLIException as e:
        io.log_info(traceback.format_exc())
        if app.pargs and app.pargs.debug:
            raise

        message = next(io._convert_to_strings([e]))

        if app.pargs and app.pargs.verbose:
            io.log_error(e.__class__.__name__ + " - " + message)
        else:
            io.log_error(message)
        app.close(code=4)
    except Exception as e:
        # Generic catch all
        io.log_info(traceback.format_exc())
        if app.pargs and app.pargs.debug:
            raise

        message = next(io._convert_to_strings([e]))
        io.log_error(e.__class__.__name__ + " :: " + message)
        app.close(code=10)
    finally:
        app.close()
