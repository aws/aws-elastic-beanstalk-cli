<#
.DESCRIPTION
This PowerShell script runs the unit tests of the current Git commit in an exclusive
virtualenv created from the the PYTHON_INSTALLATION path passed. If the current branch
is a `master` branch (irrespective of the `remote`), the script generates an EBCLI
artifact tar file available for consumers such as an end-to-end tests runner, and for
the purposes of uploading to PyPi.

.EXAMPLE
Usage:

    .\scripts\jenkins\runner <PYTHON_EXECUTABLE>

e.g., to test this project against Python 2.7 and Python 3.6, you would:

    .\scripts\jenkins\runner C:\Python27\python.exe

        and

    .\scripts\jenkins\runner C:\Python36\python.exe

.SYNOPSIS
EBCLI test suite runner + artifact generation tool
#>
Param(
    [Parameter(Mandatory=$True,Position=1)]
    [string]$PYTHON_INSTALLATION
)
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
$ARTIFACTS_DIRECTORY = "$env:JENKINS_HOME\awsebcli_artifacts"
$PYTHON_VERSION = & "${PYTHON_INSTALLATION}" -c 'import sys; print(\".\".join(map(str, sys.version_info[:3])))'
$GIT_COMMIT = Invoke-Expression "git rev-parse HEAD"
if (-not (Test-Path env:GIT_BRANCH)) {
    $GIT_BRANCH = Invoke-Expression "git rev-parse --abbrev-ref HEAD"
}
$VENV_ENV_NAME="$PYTHON_VERSION-$GIT_COMMIT"
$PYTHON_NOT_FOUND="${PYTHON_INSTALLATION} --version' did not work. Is '$PYTHON_INSTALLATION' really a Python binary?"
$STEP_NUMBER = 1
$SUBSTEP_NUMBER = 1

function Increment-StepNumber() {
    $script:STEP_NUMBER++
}

function Increment-SubStepNumber() {
    $script:SUBSTEP_NUMBER++
}

function Exit-UponFailure() {
    if ($LASTEXITCODE -ne 0) {
        Write-Output -InputObject "Delete Python $PYTHON_VERSION virtualenv before premature exit"
        Remove-Item -Path $VENV_ENV_NAME -Recurse
        Exit 1
    }
    Increment-StepNumber
}

function Exit-UponSubStepFailure() {
    if ($LASTEXITCODE -ne 0) {
        Write-Output -InputObject "Delete Python $PYTHON_VERSION virtualenv before premature exit"
        Remove-Item -Path $VENV_ENV_NAME -Recurse
        Exit 1
    }
    Increment-SubStepNumber
}

function Validate-PythonVersionName()
{
    if ($PYTHON_VERSION -eq '') {
        Write-Output $PYTHON_NOT_FOUND -Recurse
        Exit 1
    }
}

function Print-StepTitle($title)
{
    Write-Output ""
    Write-Output "******************************************************"
    Write-Output "$STEP_NUMBER. $title"
    Write-Output "******************************************************"
}

function Print-SubStepTitle($title)
{
    Write-Output "    $STEP_NUMBER.$SUBSTEP_NUMBER $title"
}

function CreateAndLoad-Virtualenv()
{
    Print-SubStepTitle "Create new Python $PYTHON_VERSION virtualenv"
    Invoke-Expression "virtualenv.exe -p '$PYTHON_INSTALLATION' '$VENV_ENV_NAME'"
    Exit-UponSubStepFailure

    Print-SubStepTitle "Loading Python $PYTHON_VERSION virtualenv"
    Invoke-Expression ".\$VENV_ENV_NAME\Scripts\activate"
    Exit-UponSubStepFailure

    Print-SubStepTitle "Installing pip 21.1"
    Invoke-Expression "python -m pip install pip==21.1"
    Exit-UponSubStepFailure
}

Print-StepTitle "Verifying Python binary path is valid"
Validate-PythonVersionName
Exit-UponFailure

Print-StepTitle "Checking for CVEs"
function CheckFor-CVEs()
{
    CreateAndLoad-Virtualenv

    Print-SubStepTitle "Installing AWSCLI and dependencies"
    Invoke-Expression "pip install .  --no-cache-dir"
    Exit-UponSubStepFailure

    Print-SubStepTitle "Installing package, 'safety'"
    Invoke-Expression "pip install safety --no-cache-dir"
    Exit-UponSubStepFailure

    Print-SubStepTitle "Checking for known security vulnerabilities"
    Invoke-Expression "safety check"
    Exit-UponSubStepFailure

    Print-SubStepTitle "Deleting Python $PYTHON_VERSION virtualenv"
    Remove-Item -Path $VENV_ENV_NAME -Recurse
    Exit-UponSubStepFailure
    $SUBSTEP_NUMBER = 1
}
CheckFor-CVEs
Exit-UponFailure

Print-StepTitle "Ensuring AWSEBCLI installs correctly after AWSCLI"
function Ensure-AWSEBCLIInstallsCorrectlyAfterAWSCLI()
{
    CreateAndLoad-Virtualenv

    Print-SubStepTitle "Installing AWSCLI and dependencies"
    Invoke-Expression "pip install awscli --no-cache-dir"
    Exit-UponSubStepFailure

    Print-SubStepTitle "Installing AWSEBCLI and dependencies"
    Invoke-Expression "pip install . --no-cache-dir"
    Exit-UponSubStepFailure

    Print-SubStepTitle "Check of missing dependencies and dependency mismatches in the package set"
    Invoke-Expression "python .\tests\test_dependencies_mismatch.py"
    Exit-UponSubStepFailure

    Print-SubStepTitle "Deleting Python $PYTHON_VERSION virtualenv"
    Remove-Item -Path $VENV_ENV_NAME -Recurse
    Exit-UponSubStepFailure
    $SUBSTEP_NUMBER = 1
}
Ensure-AWSEBCLIInstallsCorrectlyAfterAWSCLI
Exit-UponFailure

Print-StepTitle "Ensuring AWSCLI installs correctly after AWSEBCLI"
function Ensure-AWSCLIInstallsCorrectlyAfterAWSEBCLI()
{
    CreateAndLoad-Virtualenv

    Print-SubStepTitle "Installing AWSEBCLI and dependencies"
    Invoke-Expression "pip install . --no-cache-dir"
    Exit-UponSubStepFailure

    Print-SubStepTitle "Installing AWSCLI and dependencies"
    Invoke-Expression "pip install awscli --no-cache-dir"
    Exit-UponSubStepFailure

    Print-SubStepTitle "Check of missing dependencies and dependency mismatches in the package set"
    Invoke-Expression "python .\tests\test_dependencies_mismatch.py"
    Exit-UponSubStepFailure

    Print-SubStepTitle "Deleting Python $PYTHON_VERSION virtualenv"
    Remove-Item -Path $VENV_ENV_NAME -Recurse
    Exit-UponSubStepFailure

    $SUBSTEP_NUMBER = 1
}
Ensure-AWSEBCLIInstallsCorrectlyAfterAWSCLI
Exit-UponFailure

Print-StepTitle "Create new Python $PYTHON_VERSION virtualenv"
Invoke-Expression "virtualenv.exe -p '$PYTHON_INSTALLATION' '$VENV_ENV_NAME'"
Exit-UponFailure

Print-StepTitle "Loading Python $PYTHON_VERSION virtualenv"
Invoke-Expression ".\$VENV_ENV_NAME\Scripts\activate"
Exit-UponFailure

Print-StepTitle "Installing pip 21.1"
Invoke-Expression "python -m pip install pip==21.1"
Exit-UponFailure

Print-StepTitle "(Re)Installing AWSEBCLI and dependencies using commit $env:GIT_BRANCH/$GIT_COMMIT"
Invoke-Expression "python .\scripts\jenkins\install_dependencies"
Exit-UponFailure

Print-StepTitle "Check of missing dependencies and dependency mismatches in the package set"
Invoke-Expression "python .\tests\test_dependencies_mismatch.py"
Exit-UponFailure

Print-StepTitle "Executing unit tests"
Invoke-Expression "python .\scripts\jenkins\run_unit_tests"
Exit-UponFailure

Print-StepTitle "Checking whether to generate `awsebcli` artifact for $env:GIT_BRANCH"
if ( $env:GIT_BRANCH -like '*master' ) {
    Print-SubStepTitle "Ensuring $ARTIFACTS_DIRECTORY exists"
    if (!(Test-Path -Path $ARTIFACTS_DIRECTORY -PathType Container))
    {
        New-Item $ARTIFACTS_DIRECTORY -ItemType directory
    }
    Increment-SubStepNumber

    Print-SubStepTitle "Recreating $ARTIFACTS_DIRECTORY\$PYTHON_VERSION"
    if (Test-Path -Path $ARTIFACTS_DIRECTORY\$PYTHON_VERSION -PathType Container)
    {
        Remove-Item $ARTIFACTS_DIRECTORY\$PYTHON_VERSION -Recurse -Force
    }
    New-Item "$ARTIFACTS_DIRECTORY\$PYTHON_VERSION" -ItemType directory
    Increment-SubStepNumber

    Print-SubStepTitle "Packaging awsebcli to store in $ARTIFACTS_DIRECTORY\$PYTHON_VERSION"
    Invoke-Expression "python setup.py sdist --dist-dir '$ARTIFACTS_DIRECTORY\$PYTHON_VERSION'"
    Increment-SubStepNumber
} else {
    Print-SubStepTitle "Branch is not a 'master' branch; skipping artifact generation"
    Increment-SubStepNumber
}
Exit-UponFailure

Print-StepTitle "Deleting Python $PYTHON_VERSION virtualenv"
Remove-Item -Path $VENV_ENV_NAME -Recurse
Exit-UponFailure
