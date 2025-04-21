<#
.SYNOPSIS
    Installs and configures an IIS website with specified bindings and application pool.

.DESCRIPTION
    Deploys a website from a ZIP package, configuring IIS bindings, application pool,
    and file system permissions. Handles ARR configuration if enabled.

.NOTES
    Requires:
    - WebAdministration module
    - Web Deploy V3 (msdeploy.exe)
    - Administrative privileges
    - Source ZIP at C:\\staging\\{site_name}.zip
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

$destination = "{physical_path}"
$sourceZip = "C:\staging\{site_name}.zip"
if (-not (Test-Path $sourceZip)) {
    Write-HostWithTimestamp "$sourceZip not found. Nothing to do."
    exit 0
}
Write-HostWithTimestamp "Found or expecting source ZIP at $sourceZip"
$websiteName = "{site_name}"
$appPoolName = "{site_name}"

function Ensure-AppPool {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name
    )
    <#
        .SYNOPSIS
            Creates and configures an IIS application pool with standard settings.

        .DESCRIPTION
            Creates a new application pool if it doesn't exist, configures it with
            .NET 4.0 runtime, integrated pipeline mode, and ApplicationPoolIdentity.

        .PARAMETER Name
            Name of the application pool to create/configure

        .NOTES
            - Silently handles creation if pool already exists
            - Sets managed runtime to v4.0
            - Uses integrated pipeline mode
            - Uses ApplicationPoolIdentity
    #>
    try {
        Write-HostWithTimestamp "Attempting to create application pool, $Name"
        New-WebAppPool -Name $Name -ErrorAction SilentlyContinue
    } catch {}

    Write-HostWithTimestamp "Setting AppPool properties of application pool, $Name"
    Set-ItemProperty IIS:\\AppPools\\$Name -Name "managedRuntimeVersion" -Value "v4.0"
    Set-ItemProperty IIS:\\AppPools\\$Name -Name "managedPipelineMode" -Value "Integrated"
    Set-ItemProperty IIS:\\AppPools\\$Name -Name "processModel.identityType" -Value "ApplicationPoolIdentity"

    try {
        Write-HostWithTimestamp "Setting AppPool properties of application pool, $Name"
        Start-WebAppPool -Name $Name
    }
    catch {}
    Write-HostWithTimestamp "Application pool '$Name' configured and started."
}

function Ensure-Website {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name,

        [Parameter(Mandatory=$true)]
        [string]$Path,

        [Parameter(Mandatory=$true)]
        [string]$AppPoolName
    )
    <#
        .SYNOPSIS
            Creates and configures an IIS website with specified settings.

        .DESCRIPTION
            Creates a new IIS website if it doesn't exist, configures its application
            pool and bindings. Skips creation if website already exists.

        .PARAMETER Name
            Name of the website to create

        .PARAMETER Path
            Physical path for the website content

        .PARAMETER AppPoolName
            Name of the application pool to use

        .NOTES
            - Checks for existing website before creation
            - Configures bindings from pre-defined array
            - Associates with specified application pool
    #>
    if (Get-Website -Name $Name) {
        Write-HostWithTimestamp "Site, $Name, already exists. Returning."
        return
    }

    Write-HostWithTimestamp "Creating new Site, $Name, to run on application pool, $AppPoolName."
    New-Website -Name $Name -PhysicalPath $Path -ApplicationPool $AppPoolName | Out-Null
    Set-ItemProperty IIS:\\Sites\\$Name -Name applicationPool -Value $AppPoolName
    
    $bindings = @{
        {binding_protocol_powershell_array}
    }
    
    # Create an array of binding objects
    $bindingsArray = $bindings.GetEnumerator() | ForEach-Object {
        @{
            protocol = $_.Value
            bindingInformation = $_.Key
        }
    }

    Write-HostWithTimestamp "Associating the following bindings with Site, $Name"
    $bindingsArray
    Set-ItemProperty IIS:\\Sites\\$Name -Name bindings -Value $bindingsArray
    Write-HostWithTimestamp "Website, $Name, created or updated."
}

function Install-Website {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name
    )
    <#
        .SYNOPSIS
            Deploys website content using Web Deploy and configures permissions.

        .DESCRIPTION
            Uses msdeploy.exe to sync website content from a ZIP package, sets
            application pool association, and configures file system permissions.

        .PARAMETER Name
            Name of the website to install

        .NOTES
            - Uses Web Deploy V3
            - Skips app pool and ACL settings during sync
            - Applies standard IIS file permissions
            - Requires Get-GenericWebPathACLRules from ebdeploy_utils.ps1
    #>

    $msDeploy = "C:\\Program Files\\IIS\\Microsoft Web Deploy V3\\msdeploy.exe"
    Write-HostWithTimestamp "Using msdeploy.exe at $msDeploy to sync $sourceZip with its destination"

    & $msDeploy `
        -verb:sync `
        -source:package="$sourceZip" `
        -dest:auto `
        -skip:objectName=appPool `
        -skip:objectName=setAcl `

    Set-ItemProperty "IIS:\\Sites\\$Name" -Name "applicationPool" -Value $Name

    $acl = Get-Acl '{physical_path}'

    Write-HostWithTimestamp "Granting ReadAndExecute permissions ot IIS_IUSRS, IUSR, and Authenticated Users"
    foreach ($rule in $(Get-GenericWebpathACLRules)) {
        $acl.AddAccessRule($rule)
    }
    Set-Acl '{physical_path}' $acl
}

function Invoke-ARRImportScript {
    <#
        .SYNOPSIS
            Installs Application Request Routing components.

        .DESCRIPTION
            Executes the ARR MSI installer script to set up Application Request
            Routing features.

        .NOTES
            - Script must be at C:\\staging\\ebmigrateScripts\\arr_msi_installer.ps1
            - Silently handles execution errors
    #>
    try {
        & 'C:\\staging\\ebmigrateScripts\\arr_msi_installer.ps1'
        Write-HostWithTimestamp "Successfully executed 'C:\\staging\\ebmigrateScripts\\arr_msi_installer.ps1'"
    }
    catch {}
}

Ensure-AppPool -Name $appPoolName
New-Item -ItemType Directory -Force -Path $destination | Out-Null
Ensure-Website -Name $websiteName -Path $destination -AppPoolName $appPoolName
Install-Website -Name $websiteName
Write-HostWithTimestamp "Stopping site, $websiteName"
Stop-Website -Name $websiteName -ErrorAction SilentlyContinue
{invoke_arr_import_script_call}
Start-Website -Name $websiteName
Write-HostWithTimestamp "Started site, $websiteName"
