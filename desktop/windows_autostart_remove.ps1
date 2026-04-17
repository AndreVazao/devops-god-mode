param()

$ErrorActionPreference = 'Stop'
$startupFolder = [Environment]::GetFolderPath('Startup')
$launcherPath = Join-Path $startupFolder 'GodModeDesktop-Autostart.cmd'

if (Test-Path $launcherPath) {
    Remove-Item -Path $launcherPath -Force
    Write-Host "Autostart launcher removed from $launcherPath"
} else {
    Write-Host 'No autostart launcher found.'
}
