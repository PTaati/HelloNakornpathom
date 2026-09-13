param(
    [string]$Url = 'https://go2jd.taati.dev/',
    [string]$BuildPath = 'builds/web',
    [string]$ReportPath = 'reports/qa/HNP-RELEASE-20260913-deployment.json'
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$outputPath = if ([IO.Path]::IsPathRooted($BuildPath)) { $BuildPath } else { Join-Path $projectRoot $BuildPath }
$localManifest = Get-Content -LiteralPath (Join-Path $outputPath 'release.json') -Raw | ConvertFrom-Json
$remoteManifest = Invoke-RestMethod -Uri ($Url.TrimEnd('/') + '/release.json?v=' + $localManifest.buildId) -TimeoutSec 60
if ($remoteManifest.buildId -ne $localManifest.buildId) { throw 'Deployed release is not the tested build yet.' }
$checks = @()
$client = [Net.Http.HttpClient]::new()
$client.Timeout = [TimeSpan]::FromSeconds(120)
try {
    foreach ($entry in $localManifest.files.PSObject.Properties) {
        $relative = $entry.Name
        # Check the ordinary HTML entry point; binaries use the same version key as the loader.
        $suffix = if ($relative -eq 'index.html') { '' } else { '?v=' + $entry.Value.sha256.Substring(0,16) }
        $response = $client.GetAsync($Url.TrimEnd('/') + '/' + $relative + $suffix).GetAwaiter().GetResult()
        try {
            $response.EnsureSuccessStatusCode() | Out-Null
            $bytes = $response.Content.ReadAsByteArrayAsync().GetAwaiter().GetResult()
            $sha = [Security.Cryptography.SHA256]::Create()
            try { $hash = [Convert]::ToHexString($sha.ComputeHash($bytes)).ToLowerInvariant() } finally { $sha.Dispose() }
            if ($hash -ne $entry.Value.sha256) { throw "Deployed file differs from tested build: $relative" }
            $mime = [string]$response.Content.Headers.ContentType
            if ($relative.EndsWith('.wasm') -and $mime -notlike 'application/wasm*') { throw "Incorrect Wasm MIME type: $mime" }
            $checks += [ordered]@{file=$relative; status='PASS'; bytes=$bytes.Length; sha256=$hash; contentType=$mime}
        } finally { $response.Dispose() }
    }
} finally { $client.Dispose() }
$report = [ordered]@{status='PASS'; url=$Url; buildId=$localManifest.buildId; checkedUtc=[DateTime]::UtcNow.ToString('o'); checks=$checks; browserGameplay='separate QA report'; physicalMobile='NOT RUN'}
$target = Join-Path $projectRoot $ReportPath
[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($target)) | Out-Null
$json = $report | ConvertTo-Json -Depth 5
[IO.File]::WriteAllText($target, $json, [Text.UTF8Encoding]::new($false))
Write-Output $json
