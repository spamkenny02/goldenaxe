param([Parameter(Mandatory=$true)][string]$Lab,[Parameter(Mandatory=$true)][string]$Root)
$ErrorActionPreference='Stop'
$rootPath=(Resolve-Path -LiteralPath $Root).Path
$labPath=(Resolve-Path -LiteralPath $Lab).Path
$workPath=(Resolve-Path -LiteralPath (Join-Path $rootPath '../../work')).Path
$projectPath=Join-Path $labPath 'isolated/project'
if (-not $labPath.StartsWith((Join-Path $rootPath 'validation')+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Lab must stay in validation' }
$links=@(
    @((Join-Path $projectPath 'input'),(Join-Path $rootPath 'input')),
    @((Join-Path $projectPath 'analysis'),(Join-Path $rootPath 'analysis')),
    @((Join-Path $labPath 'work/libretro'),(Join-Path $workPath 'libretro')),
    @((Join-Path $labPath 'work/genesis-plus-gx'),(Join-Path $workPath 'genesis-plus-gx')),
    @((Join-Path $labPath 'work/z80dis'),(Join-Path $workPath 'z80dis'))
)
foreach ($pair in $links) {
    $target=(Resolve-Path -LiteralPath $pair[1]).Path
    if (Test-Path -LiteralPath $pair[0]) {
        $existing=Get-Item -LiteralPath $pair[0]
        if ($existing.LinkType -ne 'Junction' -or -not [string]::Equals([string]$existing.Target,$target,[StringComparison]::OrdinalIgnoreCase)) { throw "Unexpected existing link: $($pair[0])" }
    } else {
        New-Item -ItemType Junction -Path $pair[0] -Target $target | Out-Null
    }
}
