import os
from datetime import datetime

from . import dockerrun
from ..core import fileoperations, io
from ..lib import utils
from ..resources.strings import strings


HOST_LOGS_DIRNAME = 'local'
LATEST_LOGS_DIRNAME = 'latest'
HOST_LOG_FILENAME_PATTERN = "%y%m%d_%H%M%S%f"


def get_log_volume_map(root_log_dir, dockerrun_dict):
    """
    Return host log path to container log path mapping if Logging is provided
    in the dockerrun, and otherwise return empty dict.
    :param root_log_dir: str: the root local logs directory
    :param dockerrun_dict: dict: Dockerrun.aws.json as dict
    :return: dict
    """

    if not dockerrun_dict:
        return {}
    host_log = get_host_log_path(root_log_dir)
    container_log = dockerrun.get_logdir(dockerrun_dict)
    return {host_log: container_log} if container_log else {}


def get_host_log_path(root_log_dir):
    """
    Return the host log path that will be used to make the new local logs dir.
    Format is like .elasticbeanstalk/logs/local/150318_132014410947/
    :param root_log_dir: str: the root local logs directory
    :return: str
    """

    return os.path.join(root_log_dir,
                        datetime.now().strftime(HOST_LOG_FILENAME_PATTERN))


def make_logdirs(root_log_dir, log_volume_map):
    """
    Create the new local directory and symlink that new directory inside
    root_log_dir.
    :param root_log_dir: str: the root local logs directory
    :param log_volume_map: dict: host log (new local dir) to container log map
    :return: None
    """

    return _make_logdirs(root_log_dir, utils.anykey(log_volume_map))


def print_logs():
    """
    Print the location of the root local logs directory we expect as well as
    the most recent local logs directory. Then tail -f all the log files
    and ignore if tail not installed.
    :return: None
    """

    root_log = fileoperations.get_logs_location(HOST_LOGS_DIRNAME)
    last_local_logs = _get_last_local_logs(root_log)
    timestamp = os.path.getmtime(last_local_logs) if last_local_logs else None

    _print_logs(root_log, last_local_logs, timestamp)


def _print_logs(root_log, last_local_logs=None, timestamp=None):
    if os.path.isdir(root_log):
        io.echo(strings['local.logs.location'].format(root_log))

    if last_local_logs and not fileoperations.directory_empty(last_local_logs):
        prettydate = utils.prettydate(timestamp)
        msg = strings['local.logs.lastlocation'].format(prettydate,
                                                        last_local_logs)
        io.echo(msg)
    else:
        io.echo(strings['local.logs.nologs'])


def _get_last_local_logs(root_log):
    if os.path.isdir(root_log):
        all_log_paths = [os.path.join(root_log, n) for n in os.listdir(root_log)]
        non_sym_paths = [p for p in all_log_paths if not os.path.islink(p)]
        if non_sym_paths:
            return utils.last_modified_file(non_sym_paths)
    return None


def _make_logdirs(root_log_dir, new_local_dir):
    os.makedirs(new_local_dir)
    fileoperations.set_all_unrestricted_permissions(new_local_dir)
    # Symlink latest
    latest_symlink_path = os.path.join(root_log_dir,
                                       LATEST_LOGS_DIRNAME)

    try:
        os.unlink(latest_symlink_path)
    except OSError:
        pass  # Windows or latest_symlink_path is not a symlink
    try:
        os.symlink(new_local_dir, latest_symlink_path)
    except OSError:
        pass
