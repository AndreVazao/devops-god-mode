param(
    [string]$AppDataRoot = $env:APPDATA,
    [string]$DesktopRoot = [Environment]::GetFolderPath('Desktop')
)

$ErrorActionPreference = 'Stop'

$payloadPath = Join-Path $AppDataRoot 'GodModeDesktop\desktop_shortcut_payload.json'
if (-not (Test-Path $payloadPath)) {
    throw "Shortcut payload not found at $payloadPath"
}

$payload = Get-Content -Raw -Path $payloadPath | ConvertFrom-Json
if (-not $payload.desktop_shortcut) {
    Write-Host 'Desktop shortcut disabled in payload.'
    exit 0
}

$shortcutName = if ($payload.suggested_shortcut_name) { $payload.suggested_shortcut_name } else { 'GodModeDesktop' }
$targetUrl = if ($payload.target_shell_url) { $payload.target_shell_url } else { 'http://127.0.0.1:4173' }
$shortcutPath = Join-Path $DesktopRoot ($shortcutName + '.url')

$shortcutContent = @(
    '[InternetShortcut]'
    "URL=$targetUrl"
    'IconIndex=0'
) -join "`r`n"

Set-Content -Path $shortcutPath -Value $shortcutContent -Encoding ASCII
Write-Host "Desktop shortcut created at $shortcutPath"
