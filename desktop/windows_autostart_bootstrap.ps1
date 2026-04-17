param(
    [string]$AppDataRoot = $env:APPDATA
)

$ErrorActionPreference = 'Stop'

$payloadPath = Join-Path $AppDataRoot 'GodModeDesktop\desktop_autostart_payload.json'
if (-not (Test-Path $payloadPath)) {
    throw "Autostart payload not found at $payloadPath"
}

$payload = Get-Content -Raw -Path $payloadPath | ConvertFrom-Json
$startupFolder = [Environment]::GetFolderPath('Startup')
$launcherPath = Join-Path $startupFolder 'GodModeDesktop-Autostart.cmd'
$targetUrl = if ($payload.target_shell_url) { $payload.target_shell_url } else { 'http://127.0.0.1:4173' }

if (-not $payload.autostart) {
    if (Test-Path $launcherPath) {
        Remove-Item -Path $launcherPath -Force
        Write-Host "Autostart launcher removed from $launcherPath"
    } else {
        Write-Host 'Autostart disabled and no launcher existed.'
    }
    exit 0
}

$cmdContent = @(
    '@echo off',
    'start "" "' + $targetUrl + '"'
) -join "`r`n"

Set-Content -Path $launcherPath -Value $cmdContent -Encoding ASCII
Write-Host "Autostart launcher created at $launcherPath"
