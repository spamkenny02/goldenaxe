param()
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath $PSScriptRoot).Path
if ($root -match '\s') { throw 'Extract this package into a path without spaces, for example C:\gaw-v320' }
$sdk = (Join-Path $root 'toolchain/sgdk').Replace('\','/')
$java = (Join-Path $root 'toolchain/java/bin/java.exe').Replace('\','/')
if (!(Test-Path -LiteralPath "$sdk/bin/gcc.exe") -or !(Test-Path -LiteralPath $java)) { throw 'Bundled SGDK or Java runtime missing' }
$build = [IO.Path]::GetFullPath((Join-Path $root 'build'))
if (!$build.StartsWith($root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or (Split-Path $build -Leaf) -ne 'build') { throw 'Invalid build directory' }
if (Test-Path -LiteralPath $build) {
    $item = Get-Item -Force -LiteralPath $build
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Build directory cannot be a junction or symbolic link' }
    Remove-Item -LiteralPath $build -Recurse -Force
}
$project = Join-Path $build 'project'
New-Item -ItemType Directory -Path $project -Force | Out-Null
foreach ($dir in @('src','research','z80')) { Copy-Item -LiteralPath (Join-Path $root "megadrive/$dir") -Destination $project -Recurse }
Add-Type -TypeDefinition @"
using System;
using System.Security.Cryptography;
public static class GawV320Build {
    public static void Checksum(byte[] data) {
        uint sum=0;
        for(int n=0x200;n<data.Length;n+=2) sum+=(uint)((data[n]<<8)|data[n+1]);
        data[0x18e]=(byte)(sum>>8); data[0x18f]=(byte)sum;
    }
    public static byte[] Pad(byte[] raw) {
        if(raw.Length>0x200000) throw new Exception("Program exceeds 2 MiB");
        byte[] data=new byte[0x200000];
        for(int n=0;n<data.Length;n++) data[n]=255;
        Buffer.BlockCopy(raw,0,data,0,raw.Length); Checksum(data); return data;
    }
    public static string Hash(byte[] data) {
        using(var sha=SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(data)).Replace("-", "").ToLowerInvariant();
    }
    public static void Hook(byte[] data,int at,byte[] expected,uint target) {
        for(int n=0;n<6;n++) if(data[at+n]!=expected[n]) throw new Exception("Original instruction mismatch");
        data[at]=0x4e;data[at+1]=0xb9;
        data[at+2]=(byte)(target>>24);data[at+3]=(byte)(target>>16);data[at+4]=(byte)(target>>8);data[at+5]=(byte)target;
    }
    public static void Overlay(byte[] data,byte[] code) {
        if(code.Length>=512) throw new Exception("Unexpected overlay size");
        for(int n=0;n<code.Length;n++) if(data[0x1f0000+n]!=255) throw new Exception("Overlay area is not empty");
        Buffer.BlockCopy(code,0,data,0x1f0000,code.Length); Checksum(data);
    }
}
"@
$oldPath=$env:Path; $oldTmp=$env:TMP; $oldTemp=$env:TEMP; $oldTmpdir=$env:TMPDIR
Push-Location -LiteralPath $project
try {
    $env:Path="$sdk/bin;$oldPath"; $env:TMP='.'; $env:TEMP='.'; $env:TMPDIR='.'
    $unix='/' + $sdk.Substring(0,1).ToLower() + $sdk.Substring(2)
    Write-Host 'Compiling native 68000 sources with bundled SGDK...'
    $ErrorActionPreference='Continue'
    & "$sdk/bin/sh.exe" -c 'export PATH="$3/bin:$PATH"; make -f "$1/makefile.gen" "GDK=$1" "JAVA=$2" -j2' build $sdk $java $unix *> (Join-Path $build 'compile.log')
    $status=$LASTEXITCODE; $ErrorActionPreference='Stop'
    if ($status -ne 0) { throw 'Compilation failed; see build/compile.log' }
    $basePath=Join-Path $project 'out/release/rom.bin'
    $data=[GawV320Build]::Pad([IO.File]::ReadAllBytes($basePath))
    $baseHash=[GawV320Build]::Hash($data)
    if ($baseHash -ne 'd3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e') { throw 'Base differs from audited V319. Do not apply fixed-address hooks to modified code.' }
    $source=Join-Path $root 'megadrive/overlays/credits_border.s'
    $obj=Join-Path $build 'credits-border.o'; $elf=Join-Path $build 'credits-border.out'; $bin=Join-Path $build 'credits-border.bin'
    & "$sdk/bin/as.exe" '-m68000' '-o' $obj $source
    if ($LASTEXITCODE -ne 0) { throw 'Overlay assembler failed' }
    & "$sdk/bin/ld.exe" '-Ttext=0x1f0000' '-e' 'credits_border_enter' '-o' $elf $obj
    if ($LASTEXITCODE -ne 0) { throw 'Overlay linker failed' }
    & "$sdk/bin/objcopy.exe" '-O' 'binary' $elf $bin
    if ($LASTEXITCODE -ne 0) { throw 'Overlay extraction failed' }
    $symbols=@{}
    & "$sdk/bin/nm.exe" $elf | ForEach-Object {
        if ($_ -match '^\s*([0-9a-fA-F]+)\s+\w\s+(\S+)') { $symbols[$matches[2]]=[Convert]::ToUInt32($matches[1],16) }
    }
    [GawV320Build]::Hook($data,0x2144e,[byte[]]@(0x47,0xf9,0,3,0x7b,0xd6),$symbols['credits_border_enter'])
    [GawV320Build]::Hook($data,0x226f6,[byte[]]@(0x47,0xf9,0,3,0x7b,0xd6),$symbols['credits_border_enter'])
    [GawV320Build]::Hook($data,0x221e2,[byte[]]@(0x42,0x39,0xe0,0xff,0x2b,0x78),$symbols['credits_border_exit'])
    [GawV320Build]::Overlay($data,[IO.File]::ReadAllBytes($bin))
    $hash=[GawV320Build]::Hash($data)
    if ($hash -ne '9e5b0abed80678ce864a0bb796c17e97047d1d34e5227a5275bf9336129ceaff') { throw 'Final ROM differs from published V320' }
    $dist=Join-Path $root 'dist'; New-Item -ItemType Directory -Force -Path $dist | Out-Null
    [IO.File]::WriteAllBytes((Join-Path $dist 'gaw-megadrive-v0320.bin'),$data)
    @{ passed=$true; base_sha256=$baseHash; rom_sha256=$hash; bytes=$data.Length; checksum='B0A2'; build='Bundled Windows SGDK and OpenJDK runtime; native 68000 source build plus assembled credits overlay' } | ConvertTo-Json | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $dist 'build-verification.json')
    Write-Host "OK : dist/gaw-megadrive-v0320.bin ($hash)"
} finally {
    Pop-Location
    $env:Path=$oldPath; $env:TMP=$oldTmp; $env:TEMP=$oldTemp; $env:TMPDIR=$oldTmpdir
}
