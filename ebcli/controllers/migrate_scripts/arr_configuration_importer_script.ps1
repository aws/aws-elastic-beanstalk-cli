<#
    .SYNOPSIS
        Imports Application Request Routing (ARR) configuration from XML files.

    .DESCRIPTION
        Handles the import of ARR configuration settings, including backup of current
        configuration and type-safe import of new settings.

    .NOTES
        Requires:
        - WebAdministration module
        - Administrative privileges
        - Configuration files named arr_config_[section].xml
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

function Export-ARRConfig {
    param (
        [Parameter(Mandatory=$false)]
        [string]$configPath
    )
    <#
        .SYNOPSIS
            Exports current ARR configuration to XML files.

        .DESCRIPTION
            Exports modified (non-default) settings for proxy, rewrite, and caching
            configurations to separate XML files.

        .PARAMETER configPath
            Optional base path for output files. Files will be named {configPath}-{section}.xml

        .NOTES
            - Only exports modified settings (different from defaults)
            - Creates separate files for each configuration section
    #>

    # Get the proxy configuration
    $configSections = @(
        "system.webServer/proxy",
        "system.webServer/rewrite",
        "system.webServer/caching"
    )

	$outputPath = ""
    try {
        foreach ($section in $configSections) {
            $sectionName = $section.Split('/')[-1]
            if ([string]::IsNullOrEmpty($configPath)) {
                $outputPath = ".\\arr_config_$sectionName.xml"
            }
            else {
                $outputPath = "$configPath-$sectionName.xml"
            }
            $proxyConfig = Get-WebConfiguration -Filter $section

            # Filter attributes that have been modified from defaults
            $modifiedAttributes = $proxyConfig.Attributes | 
                    Where-Object { -not $_.IsInheritedFromDefaultValue }

            # Build XML string
            $xmlContent = "<proxy"
            foreach ($attr in $modifiedAttributes) {
                    $xmlContent += " $($attr.Name)=`"$($attr.Value)`""
            }
            $xmlContent += " />"

            # Save to file
            $xmlContent | Out-File -FilePath $outputPath -Force

            Write-HostWithTimestamp "Backed up '$section' to $outputPath"
        }
    }
    catch {
        Write-ErrorWithTimestamp "Failed to export ARR configuration: $_"
        throw
    }
    Write-HostWithTimestamp "Current Automatic Request Routing (ARR) configuration exported to $($configPath)*"
}


function Get-SectionAttributeTypeMappings {
    <#
        .SYNOPSIS
            Retrieves type information for IIS configuration section attributes.

        .DESCRIPTION
            Maps each attribute in a specified IIS configuration section to its corresponding
            .NET type. Used to ensure type-safe configuration imports by determining the
            correct type for each property value.

        .PARAMETER SectionPrefix
            The IIS configuration section path (e.g., "system.webServer/proxy")

        .OUTPUTS
            System.Collections.Hashtable
            A hashtable where:
                - Keys are attribute names from the configuration section
                - Values are .NET type names (e.g., "Boolean", "Int32", "String")

        .EXAMPLE
            $typeMappings = Get-SectionAttributeTypeMappings "system.webServer/proxy"
            # Returns hashtable like:
            # @{
            #     "enabled" = "Boolean"
            #     "timeout" = "TimeSpan"
            #     "httpVersion" = "String"
            # }

        .NOTES
            - Uses MACHINE/WEBROOT/APPHOST configuration path
            - Defaults to "String" type for null values
            - Supports standard IIS configuration types:
                * Boolean
                * Int32
                * Int64
                * Double
                * TimeSpan
                * String
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$SectionPrefix
    )
    # Get the proxy section properties
    $sectionConfig = Get-WebConfiguration "$SectionPrefix" -pspath 'MACHINE/WEBROOT/APPHOST'

    # Loop through each attribute and determine its type
    $propertyMappings = @{}

    foreach ($attr in $sectionConfig.Attributes) {
        $propName = $attr.Name
        $propValue = $sectionConfig.$propName  
        $propType = if ($propValue -ne $null) { $propValue.GetType().Name } else { "String" }
        # Store in hashtable
        $propertyMappings[$propName] = $propType
    }
    return $propertyMappings
}


function Import-ARRConfig {
    <#
        .SYNOPSIS
            Imports ARR configuration from XML files.

        .DESCRIPTION
            Reads configuration from XML files and applies settings to IIS, handling
            proper type conversion and validation.

        .NOTES
            - Creates backup before import
            - Handles type conversion for various configuration values
            - Logs all changes with detailed output
            - Provides backup restoration information on failure
    #>
    $configSections = @(
        "system.webServer/proxy",
        "system.webServer/rewrite",
        "system.webServer/caching"
    )

    $configurationExists = $false
    foreach ($section in $configSections) {
        $sectionName = $section.Split('/')[-1]
        $outputPath = "C:\\staging\\ebmigrateScripts\\arr_config_$sectionName.xml"

        if (Test-Path $outputPath) {
        	$configurationExists = $true
        	break
        }
    }
    if (! $configurationExists) {
       Write-HostWithTimestamp "No Automatic Request Routing configuration found."
    	return
    }
    try {
	    # Create backup of current state
        $backupPath = "arr-backup"
        Export-ARRConfig -configPath $backupPath

        Write-HostWithTimestamp "Applying new ARR configuration"
	    $i = 1
        foreach ($section in $configSections) {
            $sectionName = $section.Split('/')[-1]
            $outputPath = "C:\\staging\\ebmigrateScripts\\arr_config_$sectionName.xml"

            Write-HostWithTimestamp "Handling $sectionName at $outputPath"

            if (! $(Test-Path $outputPath)) {
            	Write-HostWithTimestamp "  $($i; $i++). $outputPath doesn't exist. No relevant configuration for $sectionName present."
            	continue
            }
            [xml]$config = Get-Content $outputPath
            $proxyNode = $config.proxy

            $attributes = $proxyNode.Attributes

    		if ([string]::IsNullOrEmpty($attributes)) {
				Write-HostWithTimestamp "  $($i; $i++). $section -> {}"
				continue
    		}

            $propertyTypeMappings = Get-SectionAttributeTypeMappings $section
            foreach ($attr in $proxyNode.Attributes) {
                $propName = $attr.Name
                $propValue = $attr.Value
                if ($propertyTypeMappings.ContainsKey($propName)) {
                    $expectedType = $propertyTypeMappings[$propName]

                    # Convert based on expected type
                    switch ($expectedType) {
                        "Boolean" { $propValue = [System.Boolean]::Parse($propValue) }
                        "Int32"   { $propValue = [int]$propValue }
                        "Int64"   { $propValue = [long]$propValue }
                        "Double"  { $propValue = [double]$propValue }
                        "TimeSpan" { $propValue = [System.TimeSpan]::Parse($propValue) }
                        "String"  { $propValue = [string]$propValue }
                        default   { Write-Host "Warning: Unknown type $expectedType for $propName. Using string."; $propValue = [string]$propValue }
                    }

                    Set-WebConfigurationProperty -pspath 'MACHINE/WEBROOT/APPHOST' `
                        -filter $section `
                        -name $propName `
                        -value $propValue
                } else {
                    Write-WarningWithTimestamp "Ignoring unknown type for $propName from section $section"
                }
            }

            $output = @"
  $($i; $i++). $section -> 
    {
$($proxyNode.Attributes | ForEach-Object { "      $($_.Name): $($_.Value)" } | Out-String)    }
"@

            Write-HostWithTimestamp $output
        }
    }
    catch {
        Write-ErrorWithTimestamp "Failed to import ARR configuration: $_"
        if (![string]::IsNullOrEmpty($backupPath)) {
	        if (Test-Path $backupPath) {
	            Write-HostWithTimestamp "Backup is available at: $backupPath*"
	        }
	    }
        throw
    }
}

Import-ARRConfig
