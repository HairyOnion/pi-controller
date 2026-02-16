param(
    [string]$PiDrive = "Y:",
    [string]$ProjectPath = "pi_controller",
    [string]$SourceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [switch]$RestartService,
    [string]$SshHost = "pi-touch-controller",
    [string]$SshUser = "hairyonion"
)

$ErrorActionPreference = "Stop"

function Copy-ProjectFile {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath
    )

    $src = Join-Path $SourceRoot $RelativePath
    $dstRoot = Join-Path $PiDrive $ProjectPath
    $dst = Join-Path $dstRoot $RelativePath
    $dstDir = Split-Path -Parent $dst

    if (-not (Test-Path -LiteralPath $src)) {
        throw "Missing source file: $src"
    }

    if (-not (Test-Path -LiteralPath $dstRoot)) {
        throw "Destination root not found: $dstRoot"
    }

    if (-not (Test-Path -LiteralPath $dstDir)) {
        New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
    }

    Copy-Item -LiteralPath $src -Destination $dst -Force
    Write-Host "Copied $RelativePath"
}

$files = @(
    "app/ui/app_window.py",
    "app/ui/screen_renderer.py",
    "app/ui/svg_widgets.py",
    "app/actions/client.py",
    "app/actions/dispatcher.py",
    "app/main.py",
    "app/settings/manager.py",
    "app/data/schema.py",
    "app/data/repository.py",
    "systemd/pi-touch-controller.env.example",
    "scripts/configure_display_linuxfb.sh",
    "scripts/enable_virtual_keyboard.sh"
)

Write-Host "Source root: $SourceRoot"
Write-Host "Destination: $(Join-Path $PiDrive $ProjectPath)"

foreach ($file in $files) {
    Copy-ProjectFile -RelativePath $file
}

if ($RestartService) {
    Write-Host "Applying display env and restarting service over SSH..."
    $cmd = "cd ~/pi_controller && ./scripts/configure_display_linuxfb.sh && sudo systemctl restart pi-touch-controller.service"
    ssh "$SshUser@$SshHost" $cmd
}

Write-Host "Done."
