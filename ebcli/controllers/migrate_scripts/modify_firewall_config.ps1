# This script executes PowerShell commands on a remote machine to 
# configure the firewall based on configuration of a source machine

. "$PSScriptRoot\\ebdeploy_utils.ps1"
 
if (-not [Environment]::Is64BitProcess) {
    $utcNow = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-HostWithTimestamp "[$($utcNow)] Restarting in 64-bit PowerShell"
    $scriptPath = $MyInvocation.MyCommand.Path
    $args = "-ExecutionPolicy unrestricted -NonInteractive -NoProfile -File `"$scriptPath`""
    Start-Process "$env:windir\\sysnative\\WindowsPowerShell\\v1.0\\powershell.exe" -ArgumentList $args -Wait -NoNewWindow
    exit
}

{firewall_rules}
