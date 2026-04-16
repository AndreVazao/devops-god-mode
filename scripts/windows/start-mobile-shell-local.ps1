$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $root
$shellPath = Join-Path $repoRoot 'frontend/mobile-shell'

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host 'Python não encontrado no PATH.' -ForegroundColor Red
    exit 1
}

Push-Location $shellPath
try {
    Write-Host 'A arrancar mobile shell local em http://127.0.0.1:4173' -ForegroundColor Cyan
    python -m http.server 4173 --bind 127.0.0.1
}
finally {
    Pop-Location
}
