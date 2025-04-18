<#
    .SYNOPSIS
        Reassigns the Default Web Site's port 80 binding to a specified configuration.

    .DESCRIPTION
        PowerShell script that modifies the Default Web Site's port binding from
        port 80 to a specified port configuration. Includes site restart and
        logging functionality.

    .NOTES
        Requires:
        - WebAdministration module
        - Administrative privileges
        - ebdeploy_utils.ps1 in same directory
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

function Reassign-DefaultWebSitePort {
    <#
        .SYNOPSIS
            Updates Default Web Site bindings and restarts the site.

        .DESCRIPTION
            Locates the port 80 binding of Default Web Site and updates it to
            the specified binding configuration. Restarts the website to apply changes.

        .OUTPUTS
            Logs binding configuration before and after changes.

        .NOTES
            - Exits silently if no port 80 binding exists
            - Restarts website as current user
            - Requires WebAdministration module
    #>
    $site = Get-Item "IIS:\\Sites\\Default Web Site"
    $bindings = $site.Bindings.Collection
    
    $bindingToUpdate = $bindings | Where-Object {
        $_.protocol -eq "http" -and
        $_.bindingInformation -eq "*:80:"
    }
    if (-not $bindingToUpdate) {
        Write-HostWithTimestamp "Site, 'Default Web Site', is already running on a non-80 port:"
        Get-WebBinding -Name 'Default Web Site'
        return
    }
    $bindingToUpdate.bindingInformation = "{host}:{port}:{domain}"

    Set-ItemProperty 'IIS:\\Sites\\Default Web Site' -Name bindings -Value $bindings

    $username = [Environment]::UserName
    Write-HostWithTimestamp "Restarting Site, 'Default Web Site', as $username for new bindings to take effect."
    Stop-Website -Name 'Default Web Site'
    Start-Website -Name 'Default Web Site'
    Write-HostWithTimestamp "Site, 'Default Web Site', has been reassigned to run with the following bindings:"
    Get-WebBinding -Name 'Default Web Site'
}

Reassign-DefaultWebSitePort
