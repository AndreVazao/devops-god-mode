$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $root
$backendScript = Join-Path $PSScriptRoot 'start-god-mode-local.ps1'
$shellScript = Join-Path $PSScriptRoot 'start-mobile-shell-local.ps1'

if (-not (Test-Path $backendScript)) {
    Write-Host 'Script do backend não encontrado.' -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $shellScript)) {
    Write-Host 'Script da shell não encontrado.' -ForegroundColor Red
    exit 1
}

Write-Host 'A abrir backend local do God Mode...' -ForegroundColor Cyan
Start-Process powershell -ArgumentList '-NoExit','-ExecutionPolicy','Bypass','-File',"`"$backendScript`""

Start-Sleep -Seconds 2

Write-Host 'A abrir mobile shell local...' -ForegroundColor Cyan
Start-Process powershell -ArgumentList '-NoExit','-ExecutionPolicy','Bypass','-File',"`"$shellScript`""

Start-Sleep -Seconds 2

Write-Host 'URLs locais previstas:' -ForegroundColor Green
Write-Host 'Backend: http://127.0.0.1:8787'
Write-Host 'Shell:   http://127.0.0.1:4173'
Write-Host 'Quando quiseres expor ao telemóvel fora da LAN, liga um túnel privado/free por cima destas URLs.' -ForegroundColor Yellow
