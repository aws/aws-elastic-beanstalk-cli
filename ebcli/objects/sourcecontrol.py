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

from __future__ import print_function
import datetime
import fileinput
import os
import sys

from cement.utils.misc import minimal_logger
from cement.utils.shell import exec_cmd

from ebcli.lib import codecommit, utils
from ebcli.core import fileoperations, io
from ebcli.objects.exceptions import NoSourceControlError, CommandError, \
    NotInitializedError
from ebcli.resources.strings import git_ignore, strings

LOG = minimal_logger(__name__)


class SourceControl():
    name = 'base'

    def __init__(self):
        self.name = ''

    def get_name(self):
        return None

    def get_current_branch(self):
        pass

    def do_zip(self, location, staged=False):
        pass

    def set_up_ignore_file(self):
        pass

    def get_version_label(self):
        pass

    def untracked_changes_exist(self):
        pass

    @staticmethod
    def get_source_control():
        # First check for setting in config file
        try:
            git_installed = fileoperations.get_config_setting('global', 'sc')
        except NotInitializedError:
            git_installed = False

        if not git_installed:
            if Git().is_setup():
                return Git()
            else:
                return NoSC()

        return Git()


class NoSC(SourceControl):
    """
        No source control installed
    """
    DEFAULT_MESSAGE = 'EB-CLI deploy'

    def get_name(self):
        return None

    def get_version_label(self):
        # use timestamp as version
        suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        return 'app-' + suffix

    def get_current_branch(self):
        return 'default'

    def do_zip(self, location, staged=False):
        io.log_info('Creating zip using systems zip')
        fileoperations.zip_up_project(location)

    def get_message(self):
        return NoSC.DEFAULT_MESSAGE

    def is_setup(self):
        pass

    def set_up_ignore_file(self):
        Git().set_up_ignore_file()

    def clean_up_ignore_file(self):
        pass

    def untracked_changes_exist(self):
        return False


class Git(SourceControl):
    """
    The user has git installed
    """
    codecommit_remote_name = 'codecommit-origin'

    def get_name(self):
        return 'git'

    def _handle_exitcode(self, exitcode, stderr):
        if exitcode == 0:
            return
        if exitcode == 127:
            # 127 = git not installed
            raise NoSourceControlError
        if exitcode == 128:
            # 128 = No HEAD
            if "HEAD" in stderr:
                LOG.debug('An error occurred while handling git command.'
                                   '\nError code: ' + str(exitcode) + ' Error: ' +
                                   stderr)
                raise CommandError('git could not find the HEAD; most likely because there are no commits present')
            
        # Something else happened
        raise CommandError('An error occurred while handling git command.'
                           '\nError code: ' + str(exitcode) + ' Error: ' +
                           stderr)

    def get_version_label(self):
        io.log_info('Getting version label from git with git-describe')
        stdout, stderr, exitcode = \
            self._run_cmd(['git', 'describe', '--always', '--abbrev=4'])

        version_label = 'app-{}-{:%y%m%d_%H%M%S}'.format(stdout, datetime.datetime.now())
        #Replace dots with underscores
        return version_label.replace('.', '_')

    def untracked_changes_exist(self):
        stdout, stderr, exitcode = self._run_cmd(['git', 'diff', '--numstat'])
        LOG.debug('git diff --numstat result: ' + stdout +
                  ' with errors: ' + stderr)
        if stdout:
            return True
        return False

    def get_current_repository(self):
        # it's possible 'origin' isn't the name of their remote so attempt to get their current remote
        current_branch = self.get_current_branch()
        stdout, stderr, exitcode = self._run_cmd(
            ['git', 'config', '--get', 'branch.{0}.remote'.format(current_branch)], handle_exitcode=False)

        current_remote = stdout
        if exitcode != 0:
            LOG.debug("No remote found for the current working directory.")
            current_remote = "origin"
        else:
            LOG.debug("Found remote branch {0} that is currently being tracked".format(current_remote))
            try:
                if current_remote.split('/') > 1:
                    # TODO: To confirm a url like this is really hacky I should change it.
                    # This assumes the remote they have is a raw address and get the repository name from that. It works
                    # for the way that I use it but it might fail if it is used to get repos that were not created by
                    # the eb cli
                    LOG.debug("Assuming remote branch is a raw url, returning this as the repository")
                    return stdout.split('/')[-1]
            except TypeError:
                LOG.debug("stdout from git config branch remote was not a string: {0}".format(stdout))
                current_remote = "origin"

        # We want the name of the repository not the remote it is saved as locally
        stdout, stderr, exitcode = self._run_cmd(
            ['git', 'config', '--get', 'remote.{0}.url'.format(current_remote)], handle_exitcode=False)
        if exitcode != 0:
            LOG.debug('No remote repository found')
            return
        else:
            self._handle_exitcode(exitcode, stderr)

        LOG.debug('git config --get remote.origin.url: ' + stdout)
        # Need to parse branch from ref manually because "--short" is
        # not supported on git < 1.8
        return stdout.split('/')[-1]

    def get_current_branch(self):
        try:
            stdout, stderr, exitcode = self._run_cmd(['git', '--version'])
            LOG.debug('Git Version: ' + stdout)
        except:
            raise CommandError('Error getting "git --version".')

        stdout, stderr, exitcode = self._run_cmd(
            ['git', 'symbolic-ref', 'HEAD'], handle_exitcode=False)
        if exitcode != 0:
            io.log_warning('Git is in a detached head state. Using branch "default".')
            return 'default'
        else:
            self._handle_exitcode(exitcode, stderr)

        LOG.debug('git symbolic-ref result: ' + stdout)
        # Need to parse branch from ref manually because "--short" is
        # not supported on git < 1.8
        return stdout.split('/')[-1]

    def get_current_commit(self):
        stdout, stderr, exitcode = self._run_cmd(
            ['git', 'rev-parse', '--verify', 'HEAD'], handle_exitcode=False)
        if exitcode != 0:
            LOG.debug('No current commit found')
            return
        else:
            self._handle_exitcode(exitcode, stderr)

        LOG.debug('git rev-parse --verify HEAD result: ' + stdout)
        return stdout

    def do_zip_submodule(self, main_location, sub_location, staged=False, submodule_dir=None):
        if staged:
            commit_id, stderr, exitcode = self._run_cmd(['git', 'write-tree'])

        else:
            commit_id = 'HEAD'

        io.log_info('creating zip using git submodule archive {0}'.format(commit_id))

        # individually zip submodules if there are any
        stdout, stderr, exitcode = self._run_cmd(['git', 'archive', '-v', '--format=zip',
                                                  '--prefix', os.path.join(submodule_dir, ''),
                                                  '-o', sub_location, commit_id])
        io.log_info('git archive output: {0}'.format(stderr))

        # append and remove the submodule archive
        fileoperations.zip_append_archive(main_location, sub_location)
        fileoperations.delete_file(sub_location)

    def do_zip(self, location, staged=False):
        cwd = os.getcwd()
        try:
            # must be in project root for git archive to work.
            fileoperations._traverse_to_project_root()

            if staged:
                commit_id, stderr, exitcode = self._run_cmd(['git', 'write-tree'])
            else:
                commit_id = 'HEAD'

            io.log_info('creating zip using git archive {0}'.format(commit_id))
            stdout, stderr, exitcode = self._run_cmd(
                ['git', 'archive', '-v', '--format=zip',
                 '-o', location, commit_id])
            io.log_info('git archive output: {0}'.format(stderr))

            project_root = os.getcwd()

            must_zip_submodules = fileoperations.get_config_setting('global', 'include_git_submodules')

            if must_zip_submodules:
                # individually zip submodules if there are any
                stdout, stderr, exitcode = self._run_cmd(['git', 'submodule', 'foreach', '--recursive'])

                for index, line in enumerate(stdout.splitlines()):
                    submodule_dir = line.split(' ')[1].strip('\'')
                    os.chdir(os.path.join(project_root, submodule_dir))
                    self.do_zip_submodule(location, "{0}_{1}".format(location, str(index)), staged=staged, submodule_dir=submodule_dir)

        finally:
            os.chdir(cwd)

    def get_message(self):
        stdout, stderr, exitcode = self._run_cmd(
            ['git', 'log', '--oneline', '-1'])
        return stdout.split(' ', 1)[1]

    def is_setup(self):
        if fileoperations.is_git_directory_present():
            # We know that the directory has git, but
            # is git on the path?
            if not fileoperations.program_is_installed('git'):
                raise CommandError(strings['sc.gitnotinstalled'])
            else:
                return True
        return False

    def set_up_ignore_file(self):
        if not os.path.exists('.gitignore'):
            open('.gitignore', 'w')
        else:
            with open('.gitignore', 'r') as f:
                for line in f:
                    if line.strip() == git_ignore[0]:
                        return

        with open('.gitignore', 'a') as f:
            f.write(os.linesep)
            for line in git_ignore:
                f.write(line + os.linesep)

    def clean_up_ignore_file(self):
        cwd = os.getcwd()
        try:
            fileoperations._traverse_to_project_root()

            in_section = False
            for line in fileinput.input('.gitignore', inplace=True):
                if line.startswith(git_ignore[0]):
                    in_section = True
                if not line.strip():
                    in_section = False

                if not in_section:
                    print(line, end='')

        finally:
            os.chdir(cwd)

    def push_codecommit_code(self):
        io.log_info('Pushing local code to codecommit with git-push')
        stdout, stderr, exitcode = self._run_cmd(['git', 'push', self.get_codecommit_presigned_remote_url()])

        if exitcode != 0:
            io.log_warning('Git is not able to push code: {0}'.format(exitcode))
            io.log_warning(stderr)
        else:
            LOG.debug('git push result: {0}'.format(stdout))
            self._handle_exitcode(exitcode, stderr)

    def setup_codecommit_remote_repo(self, remote_url):
        stdout, stderr, exitcode = self._run_cmd(['git', 'remote', 'add', self.codecommit_remote_name, remote_url], handle_exitcode=False)

        # Setup the remote repository with code commit
        if exitcode != 0:
            if exitcode == 128:
                LOG.debug("git remote already exists modifying to new url: {0}".format(remote_url))
                self._run_cmd(['git', 'remote', 'set-url', self.codecommit_remote_name, remote_url])
                self._run_cmd(['git', 'remote', 'set-url', '--push', self.codecommit_remote_name, remote_url])
            else:
                LOG.debug("Error setting up git config for code commit: {0}".format(stderr))
                return
        else:
            self._run_cmd(['git', 'remote', 'set-url', '--add', '--push', self.codecommit_remote_name, remote_url])
            self._handle_exitcode(exitcode, stderr)

        LOG.debug('git remote result: ' + stdout)

    def setup_new_codecommit_branch(self, branch_name):
        # Get fetch to ensure the remote repository is up to date
        self.fetch_remote_branches(self.codecommit_remote_name)

        # Attempt to check out the desired branch, if it doesn't exist create it from the current HEAD
        self.checkout_branch(branch_name, create_branch=True)

        # Push the current code and set the remote as the current working remote
        stdout, stderr, exitcode = self._run_cmd(['git', 'push', '-u', self.get_codecommit_presigned_remote_url(), branch_name], handle_exitcode=False)

        if exitcode != 0:
            LOG.debug('git push error: ' + stderr)
            if exitcode == 1:
                io.log_warning('Git is not able to push code: {0}'.format(exitcode))
                io.log_warning(stderr)

        LOG.debug('git push result: ' + stdout)

        # Get fetch to ensure the remote repository is up to date because we just pushed a new branch
        self.fetch_remote_branches(self.codecommit_remote_name)

        # Set the remote branch up so it's not using the presigned remote OR if the push failed.
        stdout, stderr, exitcode = self._run_cmd(
            ['git', 'branch', '--set-upstream-to', "{0}/{1}".format(self.codecommit_remote_name, branch_name)],
            handle_exitcode=False)

        if exitcode != 0:
            LOG.debug('git branch --set-upstream-to error: ' + stderr)
            return False

        LOG.debug('git branch result: ' + stdout)

        return True

    def setup_existing_codecommit_branch(self, branch_name):
        # Get fetch to ensure the remote repository is up to date
        self.fetch_remote_branches(self.codecommit_remote_name)

        # Attempt to check out the desired branch, if it doesn't exist create it from the current HEAD
        self.checkout_branch(branch_name, create_branch=True)

        # Setup the remote branch with the local git directory
        stdout, stderr, exitcode = self._run_cmd(
            ['git', 'branch', '--set-upstream-to', "{0}/{1}".format(self.codecommit_remote_name, branch_name)],
            handle_exitcode=False)

        if exitcode != 0:
            LOG.debug('git branch --set-upstream-to error: ' + stderr)
            return False

        LOG.debug('git branch result: ' + stdout)

        return True

    def checkout_branch(self, branch_name, create_branch=False):
        # Attempt to checkout an existing branch and if it doesn't exist create a new one.
        stdout, stderr, exitcode = self._run_cmd(['git', 'checkout', branch_name], handle_exitcode=False)

        if exitcode != 0:
            LOG.debug('Git is not able to checkout code: {0}'.format(exitcode))
            LOG.debug(stderr)
            if exitcode == 1:
                if create_branch:
                    LOG.debug("Could not checkout branch '{0}', creating the branch locally with current HEAD".format(branch_name))
                    stdout, stderr, exitcode = self._run_cmd(['git', 'checkout', '-b', branch_name])
                else:
                    return False
        return True

    def get_list_of_staged_files(self):
        stdout, stderr, exitcode = self._run_cmd(['git', 'diff', '--name-only', '--cached'])
        LOG.debug('git diff result: {0}'.format(stdout))
        return stdout

    def create_initial_commit(self):
        self._run_cmd(['touch', 'README'])
        self._run_cmd(['git', 'add', 'README'])
        stdout, stderr, exitcode = self._run_cmd(['git', 'commit', '--allow-empty', '-m', 'EB CLI initial commit'], handle_exitcode=False)

        if exitcode !=0:
            LOG.debug('git was not able to initialize an empty commit: {0}'.format(stderr))

        LOG.debug('git commit result: {0}'.format(stdout))
        return stdout

    def fetch_remote_branches(self, remote):
        stdout, stderr, exitcode = self._run_cmd(['git', 'fetch', self.get_codecommit_presigned_remote_url(),
                                                  '+refs/heads/*:refs/remotes/{0}/*'.format(remote)],
                                                    handle_exitcode=False)
        if exitcode != 0:
            if exitcode == 1:
                LOG.debug('git fetch error: ' + stderr)

        LOG.debug('git fetch result: {0}'.format(stdout))

    def setup_codecommit_cred_config(self):
        self._run_cmd(
            ['git', 'config', '--local', '--replace-all', 'credential.UseHttpPath', 'true'])
        self._run_cmd(
            ['git', 'config', '--local', '--replace-all', 'credential.helper', '!aws codecommit credential-helper $@'])

    def _run_cmd(self, cmd, handle_exitcode=True):
        stdout, stderr, exitcode = exec_cmd(cmd)

        stdout = utils.decode_bytes(stdout).strip()
        stderr = utils.decode_bytes(stderr).strip()

        if handle_exitcode:
            self._handle_exitcode(exitcode, stderr)
        return stdout, stderr, exitcode

    def get_url_from_remote_repo(self, remote):
        stdout, stderr, exitcode = self._run_cmd(['git', 'config', '--get', "remote.{0}.url".format(remote)], handle_exitcode=False)
        if exitcode != 0:
            LOG.debug('git remote error: ' + stderr)
            return

        LOG.debug('git remote result: ' + stdout)
        return stdout

    def get_codecommit_presigned_remote_url(self):
        remote_url = self.get_url_from_remote_repo(self.codecommit_remote_name)
        signed_url = codecommit.create_signed_url(remote_url)
        return signed_url