param([string]$BuildPath = 'builds/web')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$outputPath = if ([IO.Path]::IsPathRooted($BuildPath)) { $BuildPath } else { Join-Path $projectRoot $BuildPath }
$required = @('Build/web.loader.js', 'Build/web.framework.js', 'Build/web.data', 'Build/web.wasm')
$files = [ordered]@{}
foreach ($relative in $required) {
    $path = Join-Path $outputPath $relative
    if (-not (Test-Path -LiteralPath $path) -or (Get-Item -LiteralPath $path).Length -eq 0) {
        throw "Missing Web build file: $relative"
    }
    $files[$relative] = [ordered]@{
        sha256 = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
        bytes = (Get-Item -LiteralPath $path).Length
    }
}
# Each generated binary gets its own stable cache key, including scene-only changes.
$indexPath = Join-Path $outputPath 'index.html'
$html = [IO.File]::ReadAllText($indexPath)
foreach ($relative in $required) {
    $pattern = [regex]::Escape($relative) + '(?:\?v=[a-f0-9]+)?'
    if ($html -notmatch $pattern) { throw "index.html does not reference $relative" }
    $html = [regex]::Replace($html, $pattern, ($relative + '?v=' + $files[$relative].sha256.Substring(0,16)))
}
[IO.File]::WriteAllText($indexPath, $html, [Text.UTF8Encoding]::new($false))
$files['index.html'] = [ordered]@{
    sha256 = (Get-FileHash -LiteralPath $indexPath -Algorithm SHA256).Hash.ToLowerInvariant()
    bytes = (Get-Item -LiteralPath $indexPath).Length
}
$manifest = [ordered]@{
    schema = 1
    buildId = $files['Build/web.data'].sha256.Substring(0,12) + '-' + $files['Build/web.wasm'].sha256.Substring(0,12)
    files = $files
}
$json = $manifest | ConvertTo-Json -Depth 5
[IO.File]::WriteAllText((Join-Path $outputPath 'release.json'), $json, [Text.UTF8Encoding]::new($false))
Write-Output $json
