<#
    .SYNOPSIS
        Downloads and installs IIS Application Request Routing component.

    .DESCRIPTION
        Handles the download and installation of ARR module,
        including verification of existing installation and error handling.

    .NOTES
        Requires:
        - Administrative privileges
        - Internet access for downloads
        - Windows MSI installer
#>

. "$PSScriptRoot\\ebdeploy_utils.ps1"

if (-not [Environment]::Is64BitProcess) {
    Write-HostWithTimestamp "Restarting in 64-bit PowerShell"
    $scriptPath = $MyInvocation.MyCommand.Path
    $args = "-ExecutionPolicy unrestricted -NonInteractive -NoProfile -File `"$scriptPath`""
    Start-Process "$env:windir\\sysnative\\WindowsPowerShell\\v1.0\\powershell.exe" -ArgumentList $args -Wait -NoNewWindow
    exit
}

function Test-ARRInstalled {
    <#
        .SYNOPSIS
            Checks if ARR is already installed.

        .DESCRIPTION
            Verifies ARR installation by checking for system.webServer/proxy configuration section.

        .OUTPUTS
            Boolean indicating whether ARR is installed
    #>
    Write-HostWithTimestamp "Checking for ARR configuration based on 'system.webServer/proxy'"
    $arrFeature = Get-WebConfiguration -Filter "system.webServer/proxy"
    return ($null -ne $arrFeature)
}


function Download-ARR {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ArrInstallPath
    )
    <#
        .SYNOPSIS
            Downloads ARR MSI installer from Microsoft.

        .PARAMETER ArrInstallPath
            Directory where the MSI will be downloaded

        .NOTES
            - Downloads from Microsoft's official URL
            - Handles 404 and 403 errors with user guidance
            - Provides GitHub issue reporting information
    #>
    $arrMSIPath = "https://download.microsoft.com/download/E/9/8/E9849D6A-020E-47E4-9FD0-A023E99B54EB/requestRouter_amd64.msi"
    $ebcliGithub = "https://github.com/aws/aws-elastic-beanstalk-cli"

    try {
        Write-HostWithTimestamp "Downloading $arrMSIPath into $ArrInstallPath"
        Invoke-WebRequest $arrMSIPath -OutFile "$ArrInstallPath\\requestRouter_amd64.msi"
    } catch [System.Net.WebException] {
        if ($_.Exception.Response.StatusCode.Value__ -eq 404) {
            Write-WarningWithTimestamp @"
The Automatic Request Routing (ARR) module MSI *does not exist* at the following path anymore:

    $arrMSIPath

Install the latest version of ARR manually and report this issue at $ebcliGithub.
"@
        } elseif ($_.Exception.Response.StatusCode.Value__ -eq 403) {
            Write-WarningWithTimestamp @"
Failed to download and install the Automatic Request Routing (ARR) module MSI from the following path:

    $arrMSIPath

Install the latest version of ARR manually and report this issue on $ebcliGithub.
"@
        }
    } catch {
        Write-Host "Some exception"
    }
}


function Install-ARRFromMSI {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ArrInstallPath
    )
    <#
        .SYNOPSIS
            Installs ARR module from downloaded MSI.
    
        .PARAMETER ArrInstallPath
            Directory containing the downloaded MSI file
    
        .NOTES
            - Runs installer in quiet mode
            - Waits for installation completion
            - Provides detailed error reporting
    #>
    $ebcliGithub = "https://github.com/aws/aws-elastic-beanstalk-cli"

    try {
        Write-HostWithTimestamp "Installing ARR and Rewrite modules"
        Start-Process msiexec.exe -ArgumentList "/i $ArrInstallPath\\requestRouter_amd64.msi /quiet" -Wait
        Write-HostWithTimestamp "Successfully installed the ARR module"
    }
    catch {
        Write-WarningWithTimestamp @"
    Failed to install ARR module:
    
    $($_.Exception.Message)
    
    Install the latest versions of these modules manually and report this issue on $ebcliGithub.
"@
        }
}


function Install-ARR {
    <#
        .SYNOPSIS
            Orchestrates the complete ARR installation process.
    
        .DESCRIPTION
            Creates installation directory, downloads required MSI,
            and executes the installation process.
    
        .NOTES
            - Creates directory at C:\\installers\\arr-install
            - Coordinates download and installation functions
            - Provides overall process logging
    #>
    $arrInstallPath = "C:\\installers\\arr-install"
    Write-HostWithTimestamp "Create temp dir, $arrInstallPath, to store installers"
    New-Item -ItemType Directory -Path $arrInstallPath -Force | Out-Null

    Download-ARR -ArrInstallPath $arrInstallPath
    Install-ARRFromMSI -ArrInstallPath $arrInstallPath
}


$arrInstalled = $false
if (Test-ARRInstalled) {
    Write-HostWithTimestamp "Application Request Routing is already installed."
    $arrInstalled = $true
}
try {   
    if (! $arrInstalled) {
        Install-ARR
        if (Test-ARRInstalled) {
            Write-HostWithTimestamp "Application Request Routing was installed successfully."
        }
        else {
            throw "ARR installation could not be verified."
        }
    }
}
catch {
    Write-ErrorWithTimestamp "ARR Installation failed: $_"
    exit 1
}
