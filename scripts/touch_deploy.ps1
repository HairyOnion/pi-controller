param(
    [string]$PiDrive = "Y:",
    [string]$ProjectPath = "pi_controller",
    [string]$ServiceName = "pi-touch-controller.service",
    [string]$SourceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$StateFile = (Join-Path $PSScriptRoot ".touch_deploy_state.json"),
    [string]$SshHost = "pi-touch-controller",
    [string]$SshUser = "hairyonion",
    [switch]$ForceAll,
    [switch]$SkipPipInstall,
    [switch]$NoServiceRestart,
    [switch]$AllowReboot
)

$ErrorActionPreference = "Stop"

function Normalize-RelativePath {
    param(
        [Parameter(Mandatory = $true)][string]$PathValue
    )
    return ($PathValue -replace "\\", "/").TrimStart("/")
}

function Should-IncludeFile {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath
    )

    $p = Normalize-RelativePath -PathValue $RelativePath
    $excludedPrefixes = @(
        ".git/",
        ".venv/",
        "venv/",
        "__pycache__/",
        "app/__pycache__/",
        "scripts/__pycache__/"
    )
    foreach ($prefix in $excludedPrefixes) {
        if ($p.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $false
        }
    }

    $excludedNames = @(
        "scripts/.touch_deploy_state.json"
    )
    foreach ($name in $excludedNames) {
        if ($p.Equals($name, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $false
        }
    }

    $excludedExt = @(".pyc", ".pyo", ".db", ".sqlite", ".sqlite3", ".log")
    $ext = [System.IO.Path]::GetExtension($p)
    if ($excludedExt -contains $ext.ToLowerInvariant()) {
        return $false
    }

    return $true
}

function Get-DeployState {
    param(
        [Parameter(Mandatory = $true)][string]$PathValue
    )

    if (-not (Test-Path -LiteralPath $PathValue)) {
        return [pscustomobject]@{
            LastDeployUtc = $null
            LastDeployLocal = $null
            LastCopiedCount = 0
        }
    }

    try {
        return Get-Content -LiteralPath $PathValue -Raw | ConvertFrom-Json
    }
    catch {
        Write-Warning "State file is unreadable. Starting with a full deploy."
        return [pscustomobject]@{
            LastDeployUtc = $null
            LastDeployLocal = $null
            LastCopiedCount = 0
        }
    }
}

function Save-DeployState {
    param(
        [Parameter(Mandatory = $true)][string]$PathValue,
        [Parameter(Mandatory = $true)][datetime]$DeployUtc,
        [Parameter(Mandatory = $true)][int]$CopiedCount
    )

    $dir = Split-Path -Parent $PathValue
    if ($dir -and -not (Test-Path -LiteralPath $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    $payload = [ordered]@{
        LastDeployUtc = $DeployUtc.ToString("o")
        LastDeployLocal = $DeployUtc.ToLocalTime().ToString("yyyy-MM-dd HH:mm:ss zzz")
        LastCopiedCount = $CopiedCount
    }
    ($payload | ConvertTo-Json) | Set-Content -LiteralPath $PathValue -Encoding UTF8
}

function Get-CandidateFiles {
    param(
        [Parameter(Mandatory = $true)][string]$Root
    )

    $all = Get-ChildItem -LiteralPath $Root -Recurse -File
    $result = New-Object System.Collections.Generic.List[object]
    foreach ($item in $all) {
        $relativeRaw = $item.FullName.Substring($Root.Length)
        $relative = Normalize-RelativePath -PathValue $relativeRaw.TrimStart([char[]]@('\', '/'))
        if (Should-IncludeFile -RelativePath $relative) {
            $result.Add([pscustomobject]@{
                RelativePath = $relative
                FullPath = $item.FullName
                LastWriteTimeUtc = $item.LastWriteTimeUtc
            })
        }
    }
    return $result
}

function Get-GitChangedPaths {
    param(
        [Parameter(Mandatory = $true)][string]$Root
    )

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        return @()
    }

    $inside = ""
    try {
        $inside = (git -C $Root rev-parse --is-inside-work-tree 2>$null).Trim()
    }
    catch {
        return @()
    }
    if ($inside -ne "true") {
        return @()
    }

    $lines = @()
    try {
        $lines = git -C $Root status --porcelain=v1 --untracked-files=all
    }
    catch {
        return @()
    }

    $changed = New-Object System.Collections.Generic.HashSet[string]([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($line in $lines) {
        if (-not $line -or $line.Length -lt 4) {
            continue
        }
        $status = $line.Substring(0, 2)
        if ($status.Contains("D")) {
            continue
        }
        $rawPath = $line.Substring(3).Trim()
        if (-not $rawPath) {
            continue
        }
        if ($rawPath.Contains(" -> ")) {
            $rawPath = $rawPath.Split(" -> ", 2)[1]
        }
        $norm = Normalize-RelativePath -PathValue $rawPath
        if (Should-IncludeFile -RelativePath $norm) {
            [void]$changed.Add($norm)
        }
    }
    return @($changed)
}

function Copy-ProjectFile {
    param(
        [Parameter(Mandatory = $true)][string]$SourceRootValue,
        [Parameter(Mandatory = $true)][string]$DestRootValue,
        [Parameter(Mandatory = $true)][string]$RelativePath
    )

    $src = Join-Path $SourceRootValue $RelativePath
    $dst = Join-Path $DestRootValue $RelativePath
    $dstDir = Split-Path -Parent $dst

    if (-not (Test-Path -LiteralPath $src)) {
        throw "Missing source file: $src"
    }
    if (-not (Test-Path -LiteralPath $dstDir)) {
        New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
    }

    Copy-Item -LiteralPath $src -Destination $dst -Force
    Write-Host "Copied $RelativePath"
}

function Invoke-RemotePostDeploy {
    param(
        [Parameter(Mandatory = $true)][string[]]$CopiedFiles,
        [Parameter(Mandatory = $true)][string]$UserName,
        [Parameter(Mandatory = $true)][string]$HostName,
        [Parameter(Mandatory = $true)][string]$RemoteProjectPath,
        [Parameter(Mandatory = $true)][string]$ServiceUnitName,
        [Parameter(Mandatory = $true)][bool]$InstallPythonDeps,
        [Parameter(Mandatory = $true)][bool]$RestartService,
        [Parameter(Mandatory = $true)][bool]$AllowRebootWhenNeeded
    )

    if (-not $RestartService -and $CopiedFiles.Count -eq 0) {
        return
    }

    $copiedSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($path in $CopiedFiles) {
        [void]$copiedSet.Add((Normalize-RelativePath -PathValue $path))
    }

    $needsSystemdReload = $copiedSet.Contains("systemd/pi-touch-controller.service")
    $needsBacklightRuleApply = $copiedSet.Contains("systemd/90-backlight.rules")
    $needsReboot = $false
    foreach ($path in $CopiedSet) {
        if (
            $path.Equals("boot/config.txt", [System.StringComparison]::OrdinalIgnoreCase) -or
            $path.Equals("boot/cmdline.txt", [System.StringComparison]::OrdinalIgnoreCase)
        ) {
            $needsReboot = $true
            break
        }
    }

    $parts = New-Object System.Collections.Generic.List[string]
    $parts.Add("set -e")
    $parts.Add("cd ~/$RemoteProjectPath")
    if ($needsSystemdReload) {
        $parts.Add("sudo cp systemd/pi-touch-controller.service /etc/systemd/system/pi-touch-controller.service")
        $parts.Add("sudo systemctl daemon-reload")
    }
    if ($needsBacklightRuleApply) {
        $parts.Add("sudo cp systemd/90-backlight.rules /etc/udev/rules.d/90-backlight.rules")
        $parts.Add("sudo udevadm control --reload-rules")
        $parts.Add("sudo udevadm trigger")
    }
    if ($InstallPythonDeps) {
        $parts.Add("python3 -m pip install -e .")
    }
    if ($RestartService) {
        $parts.Add("sudo systemctl restart $ServiceUnitName")
    }
    if ($needsReboot -and $AllowRebootWhenNeeded) {
        $parts.Add("sudo reboot")
    }

    if ($parts.Count -gt 0) {
        $cmd = ($parts -join " && ")
        Write-Host "Running remote post-deploy actions on $UserName@$HostName ..."
        ssh "$UserName@$HostName" $cmd
    }

    if ($needsReboot -and -not $AllowRebootWhenNeeded) {
        Write-Warning "A reboot is recommended for some changes. Re-run with -AllowReboot to reboot automatically."
    }
}

$source = (Resolve-Path -LiteralPath $SourceRoot).Path
$destRoot = Join-Path $PiDrive $ProjectPath

if (-not (Test-Path -LiteralPath $destRoot)) {
    throw "Destination root not found: $destRoot"
}

$state = Get-DeployState -PathValue $StateFile
$lastDeployUtc = $null
if ($state.LastDeployUtc) {
    try {
        $lastDeployUtc = [datetime]::Parse($state.LastDeployUtc).ToUniversalTime()
    }
    catch {
        $lastDeployUtc = $null
    }
}

$candidates = Get-CandidateFiles -Root $source

$gitChangedPaths = Get-GitChangedPaths -Root $source

$toCopy = @()
if ($ForceAll) {
    $toCopy = $candidates | Sort-Object RelativePath
}
elseif ($lastDeployUtc) {
    $toCopy = $candidates |
        Where-Object { $_.LastWriteTimeUtc -gt $lastDeployUtc } |
        Sort-Object RelativePath
}
elseif ($gitChangedPaths.Count -gt 0) {
    $gitSet = New-Object System.Collections.Generic.HashSet[string]([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($path in $gitChangedPaths) {
        [void]$gitSet.Add((Normalize-RelativePath -PathValue $path))
    }
    $toCopy = $candidates |
        Where-Object { $gitSet.Contains($_.RelativePath) } |
        Sort-Object RelativePath
}
else {
    Write-Warning "No prior deploy timestamp and no git working-tree changes detected."
    Write-Warning "Use -ForceAll to run a full bootstrap deploy."
    exit 0
}

Write-Host "Source root: $source"
Write-Host "Destination: $destRoot"
if ($lastDeployUtc) {
    Write-Host "Last deploy (UTC): $($lastDeployUtc.ToString("yyyy-MM-dd HH:mm:ss"))"
}
else {
    Write-Host "Last deploy: none"
}

if ($toCopy.Count -eq 0) {
    Write-Host "No changed files detected since last deploy."
    exit 0
}

foreach ($entry in $toCopy) {
    Copy-ProjectFile -SourceRootValue $source -DestRootValue $destRoot -RelativePath $entry.RelativePath
}

Invoke-RemotePostDeploy `
    -CopiedFiles ($toCopy.RelativePath) `
    -UserName $SshUser `
    -HostName $SshHost `
    -RemoteProjectPath $ProjectPath `
    -ServiceUnitName $ServiceName `
    -InstallPythonDeps (-not $SkipPipInstall) `
    -RestartService (-not $NoServiceRestart) `
    -AllowRebootWhenNeeded $AllowReboot.IsPresent

$nowUtc = [datetime]::UtcNow
Save-DeployState -PathValue $StateFile -DeployUtc $nowUtc -CopiedCount $toCopy.Count

Write-Host ""
Write-Host "Deploy complete."
Write-Host "Copied files: $($toCopy.Count)"
Write-Host "Saved last deploy timestamp: $($nowUtc.ToString("yyyy-MM-dd HH:mm:ss")) UTC"
