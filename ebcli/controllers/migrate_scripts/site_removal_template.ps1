<#
    .SYNOPSIS
        Removes a specified IIS website during Elastic Beanstalk uninstallation.

    .DESCRIPTION
        PowerShell script that safely stops and removes a specified IIS website.
        Includes error handling and detailed logging of the removal process.

    .NOTES
        Requires:
        - WebAdministration module
        - Administrative privileges
        - ebdeploy_utils.ps1 in same directory

    .OUTPUTS
        Logs the removal process with timestamps:
        - Site stop operation
        - Site removal operation
        - Any errors encountered during the process
#>

. "$PSScriptRoot\\ebdeploy_utils.ps1"

if (-not [Environment]::Is64BitProcess) {
    Write-HostWithTimestamp "Restarting in 64-bit PowerShell"
    $scriptPath = $MyInvocation.MyCommand.Path
    $args = "-ExecutionPolicy unrestricted -NonInteractive -NoProfile -File `"$scriptPath`""
    Start-Process "$env:windir\\sysnative\\WindowsPowerShell\\v1.0\\powershell.exe" -ArgumentList $args -Wait -NoNewWindow
    exit
}

Import-Module WebAdministration

$websiteName = "{site_name}"

try {
    Write-HostWithTimestamp "Stopping IIS site, $websiteName."
    Stop-Website -Name $websiteName
    Write-HostWithTimestamp "Successfully stopped IIS site, $websiteName."
    Write-HostWithTimestamp "Removing IIS site $websiteName from IIS server."
    Remove-Website -Name $websiteName
    Write-HostWithTimestamp "Successfully removed site $websiteName from IIS server."
} catch {
    Write-ErrorWithTimestamp "Could not remove IIS site ${websiteName}: $_"
    throw $_
}
