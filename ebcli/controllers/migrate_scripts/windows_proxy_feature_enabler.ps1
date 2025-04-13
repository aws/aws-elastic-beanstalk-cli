# This script imports Automatic Request Routing (ARR) config from arr_*.xml
# files, if found, exported by some source machine. This script will also
# ensure that the ARR and Rewrite modules are installed from well-known
# locations.  

. "$PSScriptRoot\\ebdeploy_utils.ps1"

if (-not [Environment]::Is64BitProcess) {
    Write-HostWithTimestamp "Restarting in 64-bit PowerShell"
    $scriptPath = $MyInvocation.MyCommand.Path
    $args = "-ExecutionPolicy unrestricted -NonInteractive -NoProfile -File `"$scriptPath`""
    Start-Process "$env:windir\\sysnative\\WindowsPowerShell\\v1.0\\powershell.exe" -ArgumentList $args -Wait -NoNewWindow
    exit
}

Import-Module WebAdministration

Write-HostWithTimestamp "Installing Web-Application-Proxy Windows feature. This may take a few minutes."
Install-WindowsFeature Web-Application-Proxy
Write-HostWithTimestamp "Successfully installed Web-Application-Proxy"
