$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $root
$backendPath = Join-Path $repoRoot 'backend'

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host 'Python não encontrado no PATH.' -ForegroundColor Red
    exit 1
}

$env:GOD_MODE_PROFILE = 'hybrid_local'
$env:GOD_MODE_BACKEND_HOST = '127.0.0.1'
$env:GOD_MODE_BACKEND_PORT = '8787'
$env:GOD_MODE_SHELL_PORT = '4173'
$env:GOD_MODE_DRIVING_MODE_DEFAULT = 'true'
$env:GOD_MODE_ASSISTED_MODE_AVAILABLE = 'true'
$env:GOD_MODE_TUNNEL_ENABLED = 'false'

Push-Location $backendPath
try {
    Write-Host 'A arrancar backend local do God Mode...' -ForegroundColor Cyan
    python -m uvicorn main_candidate:app --host 127.0.0.1 --port 8787
}
finally {
    Pop-Location
}
