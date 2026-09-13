param([string]$Source = 'builds/web-release-final/web')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$sourcePath = (Resolve-Path -LiteralPath (Join-Path $projectRoot $Source)).Path
$targetPath = [IO.Path]::GetFullPath((Join-Path $projectRoot 'builds/web'))
foreach ($required in @('index.html','Build/web.loader.js','Build/web.framework.js','Build/web.data','Build/web.wasm')) {
    if (-not (Test-Path -LiteralPath (Join-Path $sourcePath $required))) { throw "Missing source artifact: $required" }
}
# Identical bytes need no overwrite. This also avoids replacing a loader mapped
# by a browser while promoting a separately successful, clean Unity build.
foreach ($file in Get-ChildItem -LiteralPath $sourcePath -Recurse -File) {
    $relative = [IO.Path]::GetRelativePath($sourcePath, $file.FullName)
    $destination = [IO.Path]::GetFullPath((Join-Path $targetPath $relative))
    if (-not $destination.StartsWith($targetPath + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Artifact escapes canonical build directory: $relative"
    }
    $sourceHash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
    $same = (Test-Path -LiteralPath $destination) -and ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash -eq $sourceHash)
    if (-not $same) {
        [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($destination)) | Out-Null
        Copy-Item -LiteralPath $file.FullName -Destination $destination -Force
    }
    if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash -ne $sourceHash) { throw "Promotion mismatch: $relative" }
    Write-Output "Verified $relative"
}
& (Join-Path $PSScriptRoot 'prepare-web-release.ps1')
