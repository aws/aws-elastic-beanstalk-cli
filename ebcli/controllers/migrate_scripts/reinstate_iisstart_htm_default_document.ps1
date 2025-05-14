# This script ensures that iisstart.htm is reinstated as a DefaultDocument

. "$PSScriptRoot\\ebdeploy_utils.ps1"

if (-not [Environment]::Is64BitProcess) {
    Write-HostWithTimestamp "Restarting in 64-bit PowerShell"
    $scriptPath = $MyInvocation.MyCommand.Path
    $args = "-ExecutionPolicy unrestricted -NonInteractive -NoProfile -File `"$scriptPath`""
    Start-Process "$env:windir\\sysnative\\WindowsPowerShell\\v1.0\\powershell.exe" -ArgumentList $args -Wait -NoNewWindow
    exit
}

# Check if iisstart.htm is already in the default document list
$existingEntry = Get-WebConfigurationProperty -Filter "system.webServer/defaultDocument/files/add[@value='iisstart.htm']" -Name "." -ErrorAction SilentlyContinue

# Only add if it doesn't already exist
if ($existingEntry -eq $null) {
    Add-WebConfigurationProperty -Filter "system.webServer/defaultDocument/files" -Name "." -Value @{value='iisstart.htm'}
    Write-HostWithTimestamp "Added iisstart.htm to default documents"
} else {
    Write-HostWithTimestamp "iisstart.htm is already in default documents, skipping"
}