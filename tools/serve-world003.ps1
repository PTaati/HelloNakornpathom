$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$webRoot = Join-Path $projectRoot 'builds/web'
if (-not (Test-Path -LiteralPath (Join-Path $webRoot 'index.html'))) {
    throw "Web build missing: $webRoot"
}
Write-Host 'Hello Nakornpathom: http://localhost:8081 (Ctrl+C to stop)'
python -m http.server 8081 --bind 127.0.0.1 --directory $webRoot
