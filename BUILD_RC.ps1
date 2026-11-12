param(
    [string]$Sgdk = '',
    [string]$Java = '',
    [string]$Python = 'python'
)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
if (-not $Sgdk) { $Sgdk = Join-Path $root 'toolchain/sgdk' }
if (-not $Java) { $Java = Join-Path $root 'toolchain/java/bin/java.exe' }
if (!(Test-Path -LiteralPath "$Sgdk/bin/gcc.exe") -or !(Test-Path -LiteralPath $Java)) {
    throw 'Supply -Sgdk and -Java, or use the ready-to-build archive with its bundled toolchain.'
}
$trial = 'validation/rc-build-' + [Guid]::NewGuid().ToString('N')
Push-Location -LiteralPath $root
try {
    & $Python tools/build_rc_rom.py --out $trial --sgdk $Sgdk --java $Java
    if ($LASTEXITCODE -ne 0) { throw 'RC build failed; inspect validation/rc-build-*/ logs' }
    New-Item -ItemType Directory -Force -Path (Join-Path $root 'dist') | Out-Null
    Copy-Item -LiteralPath (Join-Path $root "$trial/gaw-megadrive-v0322-rc1.bin") -Destination (Join-Path $root 'dist/gaw-megadrive-v0322-rc1.bin')
    Copy-Item -LiteralPath (Join-Path $root "$trial/source-build-report.json") -Destination (Join-Path $root 'dist/source-build-report.json')
    Write-Host 'OK: dist/gaw-megadrive-v0322-rc1.bin'
} finally { Pop-Location }
