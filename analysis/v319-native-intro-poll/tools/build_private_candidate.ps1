param(
    [Parameter(Mandatory = $true)][string]$Project,
    [string]$Sgdk = '',
    [string]$Java = 'D:/jdk-25.0.1/bin/java.exe',
    [ValidateRange(0, 255)][int]$PaddingByte = 0
)
$ErrorActionPreference = 'Stop'
if (-not $Sgdk) { $Sgdk = Join-Path $PSScriptRoot '../../../work/sgdk' }
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
    $candidateRomPath = Join-Path $candidateRoot 'out/release/rom.bin'
    $candidateCompiledLength = (Get-Item -LiteralPath $candidateRomPath).Length
    if ($candidateCompiledLength -gt 2097152) { throw 'Private ROM exceeds the 2 MiB cartridge' }
    & $Java -jar "$sdkPath/bin/sizebnd.jar" out/release/rom.bin -sizealign 2097152
    if ($LASTEXITCODE -ne 0) { throw 'Private ROM padding failed' }
    if ($PaddingByte -ne 0) {
        $candidateRomBytes = [IO.File]::ReadAllBytes($candidateRomPath)
        for ($candidatePaddingIndex = [int]$candidateCompiledLength; $candidatePaddingIndex -lt $candidateRomBytes.Length; $candidatePaddingIndex++) {
            $candidateRomBytes[$candidatePaddingIndex] = [byte]$PaddingByte
        }
        [IO.File]::WriteAllBytes($candidateRomPath, $candidateRomBytes)
    }
    & python "$PSScriptRoot/finalize_md_rom.py" out/release/rom.bin
    if ($LASTEXITCODE -ne 0) { throw 'Private ROM checksum failed' }
    @{
        compiledBytes = $candidateCompiledLength
        finalBytes = (Get-Item -LiteralPath $candidateRomPath).Length
        paddingByte = $PaddingByte
    } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $candidateRoot 'packaging-build.json') -Encoding UTF8
} finally { $env:Path = $previousPath; Pop-Location }
