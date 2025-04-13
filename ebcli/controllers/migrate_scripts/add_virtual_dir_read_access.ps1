. "$PSScriptRoot\\ebdeploy_utils.ps1"

$paths = @(
    # This will be populated dynamically with physical paths
)
foreach ($path in $paths) {
    if (-not (Test-Path $path)) {
        Write-HostWithTimestamp "'$path' for virtual directory does not exist. Creating."
        New-Item -Path $path -ItemType Directory -Force | Out-Null
    }   

    $acl = Get-Acl $path
    foreach ($rule in $(Get-GenericWebpathACLRules)) {
        $acl.AddAccessRule($rule)
    }
    Set-Acl $path $acl

    Write-HostWithTimestamp "Read permission granted for $path"
}
