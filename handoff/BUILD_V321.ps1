param()
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
& (Join-Path $root 'BUILD_V320.ps1')
$sdk = Join-Path $root 'toolchain/sgdk/bin'
$build = Join-Path $root 'build'
$obj = Join-Path $build 'title-publication.o'
$elf = Join-Path $build 'title-publication.out'
$bin = Join-Path $build 'title-publication.bin'
& "$sdk/as.exe" '-m68000' '-o' $obj (Join-Path $root 'megadrive/overlays/title_publication.s')
if ($LASTEXITCODE -ne 0) { throw 'Title assembler failed' }
& "$sdk/ld.exe" '-Ttext=0x1f0100' '-e' 'title_publish_row' '-o' $elf $obj
if ($LASTEXITCODE -ne 0) { throw 'Title linker failed' }
& "$sdk/objcopy.exe" '-O' 'binary' $elf $bin
if ($LASTEXITCODE -ne 0) { throw 'Title extraction failed' }
$data = [IO.File]::ReadAllBytes((Join-Path $root 'dist/gaw-megadrive-v0320.bin'))
if ([GawV320Build]::Hash($data) -ne '9e5b0abed80678ce864a0bb796c17e97047d1d34e5227a5275bf9336129ceaff') { throw 'Wrong V320 base' }
$code = [IO.File]::ReadAllBytes($bin)
if ($code.Length -ne 60) { throw 'Unexpected title overlay size' }
for ($n=0; $n -lt $code.Length; $n++) {
    if ($data[0x1f0100+$n] -ne 255) { throw 'Title overlay area occupied' }
}
foreach ($site in @(0x4ad3c,0x4ad5e,0x4addc,0x4ae12,0x4ae36,0x4b11e,0x4b140,0x4b40e,0x4b42e,0x4b49e,0x4b4c0,0x4b4e6,0x4aef6)) {
    $expected = [byte[]]@(0x4e,0xb9,0,2,0x67,0x54)
    if ($site -eq 0x4aef6) { $expected[0]=0x49; $expected[1]=0xf9 }
    for ($n=0; $n -lt 6; $n++) { if ($data[$site+$n] -ne $expected[$n]) { throw 'Unexpected title instruction' } }
    [Array]::Copy([byte[]]@(0,0x1f,1,0),0,$data,$site+2,4)
}
$expected = [byte[]]@(0x48,0x78,0,2)
for ($n=0; $n -lt 4; $n++) { if ($data[0x4aae8+$n] -ne $expected[$n]) { throw 'Unexpected warrior restoration instruction' } }
[Array]::Copy([byte[]]@(0x42,0xa7,0x4e,0x71),0,$data,0x4aae8,4)
[Array]::Copy($code,0,$data,0x1f0100,$code.Length)
[GawV320Build]::Checksum($data)
$hash = [GawV320Build]::Hash($data)
if ($hash -ne '89c5833351312ffaa591efb1939161910a298af06437080e2cf84fb3fb8ac86e') { throw 'Final ROM differs from published V321' }
[IO.File]::WriteAllBytes((Join-Path $root 'dist/gaw-megadrive-v0321.bin'),$data)
@{ passed=$true; rom_sha256=$hash; checksum='CB3C'; bytes=$data.Length; build='Native source build, credits overlay and title publication overlay' } | ConvertTo-Json | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $root 'dist/build-verification-v321.json')
Write-Host "OK : dist/gaw-megadrive-v0321.bin ($hash)"
