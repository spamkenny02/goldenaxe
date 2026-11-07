param(
    [string]$Sgdk = "$PSScriptRoot\..\..\work\sgdk",
    [string]$Java = 'D:/jdk-25.0.1/bin/java.exe',
    [ValidateRange(0, 255)][int]$PaddingByte = 255,
    [string]$ExpectedSha256 = ''
)
$ErrorActionPreference = 'Stop'
& python "$PSScriptRoot/tools/generate_axe_terrain.py"
if ($LASTEXITCODE -ne 0) { throw 'Axe terrain resource generation failed' }
& python "$PSScriptRoot/tools/generate_hero_walk_tables.py"
if ($LASTEXITCODE -ne 0) { throw 'Hero walk table generation failed' }
& python "$PSScriptRoot/tools/generate_screen_spell.py"
if ($LASTEXITCODE -ne 0) { throw 'Screen spell resource generation failed' }
& python "$PSScriptRoot/tools/extract_spell_teacher.py"
if ($LASTEXITCODE -ne 0) { throw 'Spell teacher resource generation failed' }
& python "$PSScriptRoot/tools/generate_ice_bell.py"
if ($LASTEXITCODE -ne 0) { throw 'Ice bell resource generation failed' }
& python "$PSScriptRoot/tools/generate_world_overview.py"
if ($LASTEXITCODE -ne 0) { throw 'World overview resource generation failed' }
& python "$PSScriptRoot/tools/generate_actor_descriptor_words.py"
if ($LASTEXITCODE -ne 0) { throw 'Actor descriptor word generation failed' }
& python "$PSScriptRoot/tools/generate_dialogue_glyph_lookup.py"
if ($LASTEXITCODE -ne 0) { throw 'Dialogue glyph lookup generation failed' }
& python "$PSScriptRoot/tools/generate_pattern_pairs.py"
if ($LASTEXITCODE -ne 0) { throw 'Pattern pair table generation failed' }
& python "$PSScriptRoot/tools/generate_pattern_plan.py"
if ($LASTEXITCODE -ne 0) { throw 'Pattern asset plan generation failed' }
& python "$PSScriptRoot/tools/generate_class0_video.py"
if ($LASTEXITCODE -ne 0) { throw 'Class0 video asset generation failed' }
$sdkPath = (Resolve-Path -LiteralPath $Sgdk).Path.Replace('\','/')
$sdkUnix = '/' + $sdkPath.Substring(0,1).ToLower() + $sdkPath.Substring(2)
Push-Location "$PSScriptRoot\megadrive"
$previousPath = $env:Path
try {
    $env:Path = "$sdkPath/bin;$previousPath"
    # Launch by name inside MSYS so old GNU make can restart after updating deps.
    & "$sdkPath/bin/sh.exe" -c 'export PATH="$3/bin:$PATH"; make -f "$1/makefile.gen" "GDK=$1" "JAVA=$2" -j2' build $sdkPath $Java $sdkUnix
    if ($LASTEXITCODE -ne 0) { throw 'SGDK build failed' }
    # Recreate SGDK's aligned program image even when make kept an already
    # padded rom.bin from the preceding build.
    & "$sdkPath/bin/objcopy.exe" '-O' 'binary' 'out/release/rom.out' 'out/release/rom.bin'
    if ($LASTEXITCODE -ne 0) { throw 'ROM extraction from ELF failed' }
    & $Java -jar "$sdkPath/bin/sizebnd.jar" 'out/release/rom.bin' '-sizealign' '131072' '-checksum'
    if ($LASTEXITCODE -ne 0) { throw 'SGDK program alignment failed' }
    $productionRomPath = Join-Path $PSScriptRoot 'megadrive/out/release/rom.bin'
    $productionCompiledLength = (Get-Item -LiteralPath $productionRomPath).Length
    if ($productionCompiledLength -gt 2097152) { throw 'ROM exceeds the 2 MiB cartridge' }
    # Match c0047: retain SGDK's program span and fill the external tail with FF.
    & $Java -jar "$sdkPath/bin/sizebnd.jar" 'out/release/rom.bin' '-sizealign' '2097152'
    if ($LASTEXITCODE -ne 0) { throw 'ROM padding/checksum failed' }
    if ($PaddingByte -ne 0) {
        $productionRomBytes = [IO.File]::ReadAllBytes($productionRomPath)
        for ($productionPaddingIndex = [int]$productionCompiledLength; $productionPaddingIndex -lt $productionRomBytes.Length; $productionPaddingIndex++) {
            $productionRomBytes[$productionPaddingIndex] = [byte]$PaddingByte
        }
        [IO.File]::WriteAllBytes($productionRomPath, $productionRomBytes)
    }
    # Mega Drive checksum: additive big-endian words from 0x200 to ROM end.
    & python "$PSScriptRoot/tools/finalize_md_rom.py" 'out/release/rom.bin'
    if ($LASTEXITCODE -ne 0) { throw 'Mega Drive checksum failed' }
    if ($ExpectedSha256 -and (Get-FileHash -LiteralPath $productionRomPath -Algorithm SHA256).Hash -ine $ExpectedSha256) {
        throw 'Compiled ROM differs from the expected artifact; aliases and numbered ROMs were preserved'
    }
    Copy-Item -LiteralPath 'out/release/rom.bin' -Destination "$PSScriptRoot\gaw-title-megadrive.bin"
    Copy-Item -LiteralPath 'out/release/rom.bin' -Destination "$PSScriptRoot\gaw-megadrive.bin"
    & python "$PSScriptRoot/tools/version_rom.py"
    if ($LASTEXITCODE -ne 0) { throw 'ROM version archive failed' }
} finally { $env:Path = $previousPath; Pop-Location }
