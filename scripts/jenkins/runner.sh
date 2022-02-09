#!/usr/bin/env bash
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
ARTIFACTS_DIRECTORY="$HOME/awsebcli_artifacts"
GIT_COMMIT=`git rev-parse HEAD`

if [[ ! $GIT_BRANCH ]]; then
    GIT_BRANCH = `git rev-parse --abbrev-ref HEAD`
fi
PYTHON_INSTALLATION=$1
PYTHON_VERSION=`${PYTHON_INSTALLATION} -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'`
VENV_ENV_NAME="$PYTHON_VERSION-$GIT_COMMIT"
USAGE_TEXT=$(cat <<usage
This Bash script runs the unit tests of the current Git commit in an exclusive
virtualenv created from the Python installation described by the first argument
to it. If the current branch is a `master` branch (irrespective of the `remote`),
the script generates an EBCLI artifact tar file available for consumers such as an
end-to-end tests runner, and for the purposes of uploading to PyPi.

Usage:

    ./scripts/jenkins/runner.sh <PYTHON_EXECUTABLE>

e.g., to test this project against Python 2.7 and Python 3.6, you would:

    ./scripts/jenkins/runner.sh /usr/local/bin/python2.7

        and

    ./scripts/jenkins/runner.sh /usr/local/bin/python3.6

usage
)
PYTHON_NOT_FOUND="\"$PYTHON_INSTALLATION --version\" did not work. Is \"$PYTHON_INSTALLATION\" really a Python binary?"
STEP_NUMBER=1
SUBSTEP_NUMBER=1

error_if_required_number_of_arguments_have_not_been_passed()
{
    if [ "$#" -ne 1 ] ; then
        echo "$USAGE_TEXT"
        exit 1
    fi
}

exit_upon_failure()
{
    if [[ $? -ne 0 ]] ; then
        echo "Delete Python $PYTHON_VERSION virtualenv before premature exit"
        rm -rf $VENV_ENV_NAME

        exit 1
    fi
    increment_step_number
    echo ""
}

exit_upon_substep_failure()
{
    if [[ $? -ne 0 ]] ; then
        echo "Delete Python $PYTHON_VERSION virtualenv before premature exit"
        rm -rf $VENV_ENV_NAME

        exit 1
    fi
    increment_substep_number
    echo ""
}

print_help_message_if_requested_and_exit()
{
    for i in $*
    do
        if [ "$i" == "--help" ] ; then
            echo "$USAGE_TEXT"
            exit 0
        fi
    done
}

validate_python_version_name()
{
    if [ "$PYTHON_VERSION" == '' ] ; then
        echo "$PYTHON_NOT_FOUND"
        exit 1
    fi
}

step_title()
{
    echo ""
    echo "******************************************************"
    echo "$STEP_NUMBER. $1"
    echo "******************************************************"
}

substep_title()
{
    echo "    $STEP_NUMBER.$SUBSTEP_NUMBER $1"
}

increment_step_number()
{
    STEP_NUMBER=$(($STEP_NUMBER + 1))
}

increment_substep_number()
{
    SUBSTEP_NUMBER=$((SUBSTEP_NUMBER + 1))
}


print_help_message_if_requested_and_exit $*

step_title "Verifying required number of arguments have been passed"
error_if_required_number_of_arguments_have_not_been_passed $*
increment_step_number

step_title "Verifying Python binary path is valid"
validate_python_version_name
increment_step_number

create_and_load_new_virtualenv()
{
    substep_title "Creating new Python $PYTHON_VERSION virtualenv"
    virtualenv -p $PYTHON_INSTALLATION $VENV_ENV_NAME
    exit_upon_substep_failure

    substep_title "Loading Python $PYTHON_VERSION virtualenv"
    source $VENV_ENV_NAME/bin/activate
    exit_upon_substep_failure

    substep_title "Installing pip 21.1"
    pip install pip=="21.1"
    exit_upon_substep_failure
}

step_title "Checking for CVEs"
check_for_cves()
{
    create_and_load_new_virtualenv

    substep_title "Installing AWSEBCLI and dependencies"
    pip install . --no-cache-dir
    exit_upon_substep_failure

    substep_title "Installing package, 'safety'"
    pip install safety --no-cache-dir
    exit_upon_substep_failure

    substep_title "Checking for known security vulnerabilities"
    safety check
    exit_upon_substep_failure

    substep_title "Deleting Python $PYTHON_VERSION virtualenv"
    rm -rf $VENV_ENV_NAME
    exit_upon_substep_failure
    SUBSTEP_NUMBER=1
}
check_for_cves
increment_step_number


step_title "Ensuring AWSEBCLI installs correctly after AWSCLI"
ensure_awsebcli_installs_correctly_after_awscli()
{
    create_and_load_new_virtualenv

    substep_title "Installing AWSCLI and dependencies"
    pip install awscli --no-cache-dir
    exit_upon_substep_failure

    substep_title "Installing AWSEBCLI and dependencies"
    pip install . --no-cache-dir
    exit_upon_substep_failure

    substep_title "Checking for missing dependencies and dependency mismatches in the package set"
    python tests/test_dependencies_mismatch.py
    exit_upon_substep_failure

    substep_title "Deleting Python $PYTHON_VERSION virtualenv"
    rm -rf $VENV_ENV_NAME
    SUBSTEP_NUMBER=1
}
ensure_awsebcli_installs_correctly_after_awscli
increment_step_number

step_title "Ensuring AWSCLI installs correctly after AWSEBCLI"
ensure_awscli_installs_correctly_after_awsebcli()
{
    create_and_load_new_virtualenv

    substep_title "Installing AWSEBCLI and dependencies"
    pip install . --no-cache-dir
    exit_upon_substep_failure

    substep_title "Checking for missing dependencies and dependency mismatches in the package set"
    python tests/test_dependencies_mismatch.py
    exit_upon_substep_failure

    substep_title "Installing AWSEBCLI and dependencies"
    pip install awsebcli --no-cache-dir
    exit_upon_substep_failure

    substep_title "Checking for missing dependencies and dependency mismatches in the package set"
    python tests/test_dependencies_mismatch.py
    exit_upon_substep_failure

    substep_title "Deleting Python $PYTHON_VERSION virtualenv"
    rm -rf $VENV_ENV_NAME
    SUBSTEP_NUMBER=1
}
ensure_awscli_installs_correctly_after_awsebcli
increment_step_number

step_title "Creating new Python $PYTHON_VERSION virtualenv"
virtualenv -p $PYTHON_INSTALLATION $VENV_ENV_NAME
exit_upon_failure

step_title "Installing pip 21.1"
pip install pip=="21.1"
exit_upon_failure

step_title "Loading Python $PYTHON_VERSION virtualenv"
source $VENV_ENV_NAME/bin/activate
exit_upon_failure

step_title "(Re)Installing AWSEBCLI and dependencies using commit $GIT_BRANCH/$GIT_COMMIT"
python scripts/jenkins/install_dependencies
exit_upon_failure

step_title "Checking for missing dependencies and dependency mismatches in the package set"
python tests/test_dependencies_mismatch.py
exit_upon_failure

step_title "Executing unit tests"
python scripts/jenkins/run_unit_tests
exit_upon_failure

step_title "Checking whether branch is a 'master' branch"
if [[ $GIT_BRANCH =~ 'master' ]]; then
    substep_title "Ensuring $ARTIFACTS_DIRECTORY exists"
    if [ ! -d "$ARTIFACTS_DIRECTORY" ]; then
        mkdir "$ARTIFACTS_DIRECTORY"
    fi
    increment_substep_number

    substep_title "Recreating $ARTIFACTS_DIRECTORY/$PYTHON_VERSION"
    if [ -d $ARTIFACTS_DIRECTORY/$PYTHON_VERSION ]; then
        rm -rf $ARTIFACTS_DIRECTORY/$PYTHON_VERSION
    fi
    mkdir $ARTIFACTS_DIRECTORY/$PYTHON_VERSION
    increment_substep_number

    substep_title "Packaging awsebcli to store in $ARTIFACTS_DIRECTORY/$PYTHON_VERSION"
    python setup.py sdist
    mv dist/* $ARTIFACTS_DIRECTORY/$PYTHON_VERSION/
    increment_substep_number
else
    substep_title "Branch is not a 'master' branch; skipping artifact generation"
    increment_substep_number
fi

step_title "Deleting Python $PYTHON_VERSION virtualenv"
rm -rf $VENV_ENV_NAME
