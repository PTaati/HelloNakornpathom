$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$unityProject = Join-Path $projectRoot 'hnp-game'
$versionLine = Get-Content (Join-Path $unityProject 'ProjectSettings/ProjectVersion.txt') | Where-Object { $_ -match '^m_EditorVersion: ' }
$unityVersion = ($versionLine -replace '^m_EditorVersion: ', '').Trim()
$unityEditor = Join-Path $env:ProgramFiles "Unity/Hub/Editor/$unityVersion/Editor/Unity.exe"
if (-not (Test-Path -LiteralPath $unityEditor)) { throw "Unity Editor not found: $unityEditor" }
if (Get-Process Unity -ErrorAction SilentlyContinue) { throw 'Save your work and close Unity before running this build.' }
$buildLog = Join-Path $projectRoot 'reports/world/canonical-web-build.log'
# Existing project build method writes directly to builds/web, the committed Pages input.
$unityArgs = @('-projectPath', ('"' + $unityProject + '"'), '-executeMethod', 'HNP.Editor.HnpWorldBuilder.Build', '-quit', '-logFile', ('"' + $buildLog + '"'))
$buildProcess = Start-Process -FilePath $unityEditor -ArgumentList $unityArgs -WindowStyle Hidden -Wait -PassThru
if ($buildProcess.ExitCode -ne 0 -or -not (Select-String -LiteralPath $buildLog -SimpleMatch 'Build Finished, Result: Success.' -Quiet)) { throw "Build failed. Inspect $buildLog" }
foreach ($file in @('index.html','Build/web.loader.js','Build/web.framework.js','Build/web.data','Build/web.wasm')) {
    $outputFile = Join-Path $projectRoot "builds/web/$file"
    if (-not (Test-Path -LiteralPath $outputFile) -or (Get-Item -LiteralPath $outputFile).Length -eq 0) { throw "Build output missing: $outputFile" }
}
Write-Host 'Build ready: builds/web. Commit builds/web and push main to run the existing Pages workflow.'
