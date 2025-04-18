<#
    .SYNOPSIS
        Restarts a specified IIS website during Elastic Beanstalk deployment.

    .DESCRIPTION
        PowerShell script that safely stops and starts a specified IIS website.
        Includes checks for site existence and detailed logging of the restart process.

    .NOTES
        Requires:
        - WebAdministration module
        - Administrative privileges
        - ebdeploy_utils.ps1 in same directory

    .OUTPUTS
        Logs the restart process with timestamps, including:
        - Site existence verification
        - Stop operation
        - Start operation
        - Cases where site doesn't exist
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

if (Get-Website -Name $websiteName) {
    Write-HostWithTimestamp "Restarting IIS site, $websiteName."
    Write-HostWithTimestamp "Stopping ..."
    Stop-Website -Name $websiteName
    Write-HostWithTimestamp "Starting ..."
    Start-Website -Name $websiteName
}
else {
    Write-HostWithTimestamp "Website IIS site, $websiteName, doesn't exist. Nothing to restart."
}
