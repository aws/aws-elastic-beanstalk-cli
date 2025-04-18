# This script hosts functions for convenience and utility.
# It is meant to be imported by the rest of the EB-defined
# scripts during deployment.

function utcNow {
    return $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
}

function Write-HostWithTimestamp {
    <#
        .SYNOPSIS
            Write standard output message with UTC timestamp.

        .DESCRIPTION
            Writes a message to the host (standard output) prefixed with UTC timestamp.
            Supports pipeline input for the message parameter.

        .PARAMETER Message
            The message to write to the host.

        .EXAMPLE
            Write-HostWithTimestamp "Deployment started"
            # Output: [2024-02-20 15:30:45] Deployment started

        .EXAMPLE
            "Process completed" | Write-HostWithTimestamp
            # Output: [2024-02-20 15:30:45] Process completed
    #>
    param(
        [Parameter(ValueFromPipeline=$true)]
        [string]$Message
    )

    Write-Host "[$(utcNow)] $Message"
}

function Write-ErrorWithTimestamp {
    <#
        .SYNOPSIS
            Write error message with UTC timestamp.

        .DESCRIPTION
            Writes a message to the error stream prefixed with UTC timestamp.
            Supports pipeline input for the message parameter.

        .PARAMETER Message
            The message to write to the error stream.

        .EXAMPLE
            Write-ErrorWithTimestamp "Failed to create website"
            # Output: [2024-02-20 15:30:45] Failed to create website
    #>
    param(
        [Parameter(ValueFromPipeline=$true)]
        [string]$Message
    )

    Write-Error "[$(utcNow)] $Message"
}

function Write-WarningWithTimestamp {
    <#
        .SYNOPSIS
            Write warning message with UTC timestamp.

        .DESCRIPTION
            Writes a message to the warning stream prefixed with UTC timestamp.
            Supports pipeline input for the message parameter.

        .PARAMETER Message
            The message to write to the warning stream.

        .EXAMPLE
            Write-WarningWithTimestamp "Configuration file not found"
            # Output: [2024-02-20 15:30:45] Configuration file not found
    #>
    param(
        [Parameter(ValueFromPipeline=$true)]
        [string]$Message
    )

    Write-Warning "[$(utcNow)] $Message"
}

function Get-GenericWebPathACLRules {
    <#
        .SYNOPSIS
            Get standard IIS web application ACL rules.

        .DESCRIPTION
            Returns an array of FileSystemAccessRule objects that define standard
            read and execute permissions for IIS web applications. These rules
            grant necessary access to IIS service accounts and authenticated users.

        .OUTPUTS
            System.Security.AccessControl.FileSystemAccessRule[]
            Array of three access rules:
            1. IIS_IUSRS: ReadAndExecute with inheritance
            2. IUSR: ReadAndExecute with inheritance
            3. Authenticated Users: ReadAndExecute with inheritance

        .NOTES
            All rules are configured with:
            - ContainerInherit and ObjectInherit flags
            - Allow type access
            - ReadAndExecute permissions
    #>
    $rules = @(
        [System.Security.AccessControl.FileSystemAccessRule]::new(
            "IIS_IUSRS", 
            "ReadAndExecute", 
            "ContainerInherit,ObjectInherit", 
            "None", 
            "Allow"
        ),
        
        [System.Security.AccessControl.FileSystemAccessRule]::new(
            "IUSR", 
            "ReadAndExecute", 
            "ContainerInherit,ObjectInherit", 
            "None",
            "Allow"
        ),
    
        [System.Security.AccessControl.FileSystemAccessRule]::new(
            "Authenticated Users", 
            "ReadAndExecute", 
            "ContainerInherit,ObjectInherit", 
            "None", 
            "Allow"
        )
    )

    return $rules
}
