<#
.DESCRIPTION
Script runs the unit tests of the current Git commit in an exclusive virtualenv created
from the the PYTHON_INSTALLATION path passed. If the current branch is a `master` branch
(irrespective of the `remote`), the script generates an EBCLI artifact tar file available
for consumers such as an end-to-end tests runner, and for the purposes of uploading to
PyPi.

.EXAMPLE
Usage:

    bash runner.py <PYTHON_EXECUTABLE>

e.g., to test this project against Python 2.7 and Python 3.6, you would:

    python runner.py C:\Python27\python.exe

        and

    python runner.py C:\Python36\python.exe

.SYNOPSIS
EBCLI test runner + artifact generation tool
#>
Param(
    [Parameter(Mandatory=$True,Position=1)]
    [string]$PYTHON_INSTALLATION
)

$ARTIFACTS_DIRECTORY = "$env:JENKINS_HOME\awsebcli_artifacts"
$PYTHON_VERSION = & "${PYTHON_INSTALLATION}" -c 'import sys; print(\".\".join(map(str, sys.version_info[:3])))'
$GIT_COMMIT = Invoke-Expression "git rev-parse HEAD"
$VENV_ENV_NAME="$PYTHON_VERSION-$GIT_COMMIT"
$PYTHON_NOT_FOUND="${PYTHON_INSTALLATION} --version' did not work. Is '$PYTHON_INSTALLATION' really a Python binary?"

function Exit-UponFailure() {
    if ($LASTEXITCODE -ne 0) {
        Write-Output -InputObject "Delete Python $PYTHON_VERSION virtualenv before premature exit"
        Remove-Item -Path $VENV_ENV_NAME -Recurse
        Exit 1
    }
}

function Validate-PythonVersionName()
{
    if ($PYTHON_VERSION -eq '') {
        Write-Output $PYTHON_NOT_FOUND -Recurse
        Exit 1
    }
}

Write-Output "******************************************************"
Write-Output "1. Verifying Python binary path is valid"
Write-Output "******************************************************"
Validate-PythonVersionName

Write-Output ""
Write-Output "******************************************************"
Write-Output "2. Create new Python $PYTHON_VERSION virtualenv"
Write-Output "******************************************************"
Invoke-Expression "virtualenv.exe -p '$PYTHON_INSTALLATION' '$VENV_ENV_NAME'"
Exit-UponFailure

Write-Output "******************************************************"
Write-Output "3. Loading Python $PYTHON_VERSION virtualenv"
Write-Output "******************************************************"
Invoke-Expression ".\$VENV_ENV_NAME\Scripts\activate"
Exit-UponFailure

Write-Output "******************************************************"
Write-Output "4. (Re)Installing AWSEBCLI and dependencies using commit $env:GIT_BRANCH/$GIT_COMMIT"
Write-Output "******************************************************"
Invoke-Expression "python .\scripts\jenkins\install_dependencies"
Exit-UponFailure

Write-Output "******************************************************"
Write-Output "5. Check of missing dependencies and dependency mismatches in the package set"
Write-Output "******************************************************"
Invoke-Expression "python .\tests\test_dependencies_mismatch.py"
Exit-UponFailure

Write-Output "******************************************************"
Write-Output "6. Executing unit tests"
Write-Output "******************************************************"
Invoke-Expression "python .\scripts\jenkins\run_unit_tests"
Exit-UponFailure

Write-Output "******************************************************"
Write-Output "7. Checking whether to generate `awsebcli` artifact for $env:GIT_BRANCH"
Write-Output "******************************************************"
if ( $env:GIT_BRANCH -like '*master' ) {
    Write-Output "    6.1. Ensuring $ARTIFACTS_DIRECTORY exists"
    if (!(Test-Path -Path $ARTIFACTS_DIRECTORY -PathType Container))
    {
        New-Item $ARTIFACTS_DIRECTORY -ItemType directory
    }

    Write-Output "    6.2. Recreating $ARTIFACTS_DIRECTORY\$PYTHON_VERSION"
    if (Test-Path -Path $ARTIFACTS_DIRECTORY\$PYTHON_VERSION -PathType Container)
    {
        Remove-Item $ARTIFACTS_DIRECTORY\$PYTHON_VERSION -Recurse -Force
    }
    New-Item "$ARTIFACTS_DIRECTORY\$PYTHON_VERSION" -ItemType directory

    Write-Output "    6.4. Packaging awsebcli to store in $ARTIFACTS_DIRECTORY\$PYTHON_VERSION"
    Write-Output "******************************************************"
    Invoke-Expression "python setup.py sdist --dist-dir '$ARTIFACTS_DIRECTORY\$PYTHON_VERSION'"
} else {
    Write-Output "    6.1. Branch is not a 'master' branch; skipping artifact generation"
}
Exit-UponFailure

Write-Output "******************************************************"
Write-Output "8. Deleting Python $PYTHON_VERSION virtualenv"
Write-Output "******************************************************"
Remove-Item -Path $VENV_ENV_NAME -Recurse
Exit-UponFailure
