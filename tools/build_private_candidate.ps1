param(
    [Parameter(Mandatory = $true)][string]$Project,
    [string]$Sgdk = "$PSScriptRoot/../../../work/sgdk",
    [string]$Java = 'D:/jdk-25.0.1/bin/java.exe'
)
$ErrorActionPreference = 'Stop'
$candidateRoot = (Resolve-Path -LiteralPath $Project).Path
$validationRoot = (Resolve-Path -LiteralPath "$PSScriptRoot/../validation").Path
if (-not $candidateRoot.StartsWith($validationRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Private candidates must stay inside validation'
}
if (Test-Path -LiteralPath "$candidateRoot/out/release/rom.bin") { throw 'Preserve the existing candidate ROM' }
$sdkPath = (Resolve-Path -LiteralPath $Sgdk).Path.Replace('\','/')
$sdkUnix = '/' + $sdkPath.Substring(0,1).ToLower() + $sdkPath.Substring(2)
$previousPath = $env:Path
Push-Location -LiteralPath $candidateRoot
try {
    $env:Path = "$sdkPath/bin;$previousPath"
    # Windows PowerShell represents native stderr warnings as ErrorRecords.
    # The compiler exit code determines success; warnings stay in the log.
    $ErrorActionPreference = 'Continue'
    & "$sdkPath/bin/sh.exe" -c 'export PATH="$3/bin:$PATH"; make -f "$1/makefile.gen" "GDK=$1" "JAVA=$2" -j2' build $sdkPath $Java $sdkUnix *> build.log
    $buildExit = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    if ($buildExit -ne 0) { throw 'Private SGDK build failed; inspect build.log' }
    & $Java -jar "$sdkPath/bin/sizebnd.jar" out/release/rom.bin -sizealign 2097152
    if ($LASTEXITCODE -ne 0) { throw 'Private ROM padding failed' }
    & python "$PSScriptRoot/finalize_md_rom.py" out/release/rom.bin
    if ($LASTEXITCODE -ne 0) { throw 'Private ROM checksum failed' }
} finally { $env:Path = $previousPath; Pop-Location }
