param([string]$Label = 'v0300')
$ErrorActionPreference = 'Stop'
if ($Label -notmatch '^[a-zA-Z0-9-]+$') { throw 'Invalid harness label' }
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$workspaceRoot = (Resolve-Path (Join-Path $projectRoot '../..')).Path
$harnessRoot = Join-Path $workspaceRoot 'work/sprite-rows-harness'
New-Item -ItemType Directory -Force -Path (Join-Path $harnessRoot 'src') | Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'sprite_rows_harness.c') -Destination (Join-Path $harnessRoot 'src/main.c')
Copy-Item -LiteralPath (Join-Path $projectRoot "validation/sprite-rows-$Label/helper.inc") -Destination (Join-Path $harnessRoot 'src/helper.inc')
$sdkPath = (Resolve-Path (Join-Path $workspaceRoot 'work/sgdk')).Path.Replace('\','/')
$sdkUnix = '/' + $sdkPath.Substring(0,1).ToLower() + $sdkPath.Substring(2)
$previousPath = $env:Path
Push-Location $harnessRoot
try {
    $env:Path = "$sdkPath/bin;$previousPath"
    & "$sdkPath/bin/sh.exe" -c 'export PATH="$3/bin:$PATH"; make -f "$1/makefile.gen" "GDK=$1" "JAVA=$2" -j2' build $sdkPath 'D:/jdk-25.0.1/bin/java.exe' $sdkUnix
    if ($LASTEXITCODE -ne 0) { throw 'Sprite row harness build failed' }
} finally { $env:Path = $previousPath; Pop-Location }
