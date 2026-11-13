param(
    [Parameter(Mandatory = $true)][string]$Sgdk,
    [Parameter(Mandatory = $true)][string]$Java,
    [string]$Python = 'python'
)
$ErrorActionPreference = 'Stop'
$trial = 'validation/final-build-' + [Guid]::NewGuid().ToString('N')
Push-Location -LiteralPath $PSScriptRoot
try {
    & $Python tools/build_final_rom.py --out $trial --sgdk $Sgdk --java $Java
    if ($LASTEXITCODE -ne 0) { throw "Build failed: $trial" }
    New-Item -ItemType Directory -Force -Path dist | Out-Null
    Copy-Item -LiteralPath "$trial/gaw-megadrive-v0328.bin" -Destination dist/gaw-megadrive-v0328.bin
    Copy-Item -LiteralPath "$trial/source-build-report.json" -Destination dist/source-build-report.json
    Copy-Item -LiteralPath "$trial/base/project/out/release/symbol.txt" -Destination dist/symbol.txt
    Copy-Item -LiteralPath "$trial/base/project/out/release/rom.out" -Destination dist/base-rom.out
    Write-Host 'OK: dist/gaw-megadrive-v0328.bin (SHA-256 checked against accepted V328)'
} finally { Pop-Location }
