#!/usr/bin/env bash

ARTIFACTS_DIRECTORY="$HOME/awsebcli_artifacts"
GIT_COMMIT=`git rev-parse HEAD`
PYTHON_INSTALLATION=$1
PYTHON_VERSION=`${PYTHON_INSTALLATION} -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'`
VENV_ENV_NAME="$PYTHON_VERSION-$GIT_COMMIT"
USAGE_TEXT=$(cat <<usage
Usage:

    bash runner.py <PYTHON_EXECUTABLE>

e.g., to test this project against Python 2.7 and Python 3.6, you would:

    python runner.py /usr/local/bin/python2.7

        and

    python runner.py /usr/local/bin/python3.6

usage
)
PYTHON_NOT_FOUND="\"$PYTHON_INSTALLATION --version\" did not work. Is \"$PYTHON_INSTALLATION\" really a Python binary?"

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

print_help_message_if_requested_and_exit $*

echo ""
echo "******************************************************"
echo "1. Verifying required number of arguments have been passed"
echo "******************************************************"
error_if_required_number_of_arguments_have_not_been_passed $*

echo ""
echo "******************************************************"
echo "2. Verifying Python binary path is valid"
echo "******************************************************"
validate_python_version_name

echo ""
echo "******************************************************"
echo "3. Create new Python $PYTHON_VERSION virtualenv"
echo "******************************************************"
virtualenv -p $PYTHON_INSTALLATION $VENV_ENV_NAME
exit_upon_failure

echo "******************************************************"
echo "4. Loading Python $PYTHON_VERSION virtualenv"
echo "******************************************************"
source $VENV_ENV_NAME/bin/activate
exit_upon_failure

echo "******************************************************"
echo "5. (Re)Installing AWSEBCLI and dependencies using commit $GIT_BRANCH/$GIT_COMMIT"
echo "******************************************************"
python scripts/jenkins/install_dependencies
exit_upon_failure

echo "******************************************************"
echo "6. Check of missing dependencies and dependency mismatches in the package set"
echo "******************************************************"
python tests/test_dependencies_mismatch.py
exit_upon_failure

echo "******************************************************"
echo "7. Executing unit tests"
echo "******************************************************"
python scripts/jenkins/run_unit_tests
exit_upon_failure

echo "******************************************************"
echo "8. Checking whether branch is a 'master' branch"
echo "******************************************************"
if [[ $GIT_BRANCH =~ 'master' ]]; then
    echo "    6.1. Ensuring $ARTIFACTS_DIRECTORY exists"
    if [ ! -d "$ARTIFACTS_DIRECTORY" ]; then
        mkdir "$ARTIFACTS_DIRECTORY"
    fi

    echo "    6.2. Recreating $ARTIFACTS_DIRECTORY/$PYTHON_VERSION"
    if [ -d $ARTIFACTS_DIRECTORY/$PYTHON_VERSION ]; then
        rm -rf $ARTIFACTS_DIRECTORY/$PYTHON_VERSION
    fi
    mkdir $ARTIFACTS_DIRECTORY/$PYTHON_VERSION

    echo "    6.4. Packaging awsebcli to store in $ARTIFACTS_DIRECTORY/$PYTHON_VERSION"
    echo "******************************************************"
    python setup.py sdist
    mv dist/* $ARTIFACTS_DIRECTORY/$PYTHON_VERSION/
else
    echo "    6.1. Branch is not a 'master' branch; skipping artifact generation"
fi
exit_upon_failure

echo "******************************************************"
echo "9. Delete Python $PYTHON_VERSION virtualenv"
echo "******************************************************"
rm -rf $VENV_ENV_NAME

echo "******************************************************"
echo "10. Deleting Python $PYTHON_VERSION virtualenv"
echo "******************************************************"
rm -rf $VENV_ENV_NAME
