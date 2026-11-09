"""Freeze current sources, compact evidence and the audited Windows toolchain."""
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'handoff/gaw-v321-projet-complet-llm-2026-11-09.zip'


def main():
    assert not TARGET.exists(), 'Keep delivered snapshots immutable'
    files = {}

    def add(path, name=None):
        assert path.is_file(), path
        files[name or path.relative_to(ROOT).as_posix()] = path

    for directory in ('megadrive/src', 'megadrive/research', 'megadrive/z80', 'megadrive/overlays', 'tools', 'testkit', 'input'):
        for p in (ROOT / directory).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and 'logs' not in p.parts:
                add(p)
    # Compact top-level reports, not the 3+ GiB of historical binary evidence/cache.
    for p in (ROOT / 'analysis').iterdir():
        if p.is_file():
            add(p)
    for name in ('README.md', 'build.ps1', 'HISTORIQUE_PORTAGE.md', 'JALONS_C0046_C0047.md', 'REPRISE_CODEX.md', '.gitignore', '.gitattributes'):
        add(ROOT / name)
    for name in ('BUILD_V320.ps1', 'BUILD_V321.ps1', 'PASSATION_V321_LLM.md'):
        add(ROOT / 'handoff' / name, name)
    add(ROOT / 'megadrive/out/release/symbol.txt')
    add(ROOT / 'megadrive/out/release/rom.out')
    add(ROOT / 'versions/v0321-89c58333/gaw-megadrive-v0321.bin', 'reference/gaw-megadrive-v0321.bin')
    add(ROOT / 'gaw-megadrive.bin')
    core = ROOT.parents[1] / 'work/genesis-plus-gx/genesis_plus_gx_libretro.dll'
    add(core, 'testkit/runtime/genesis_plus_gx_libretro.dll')
    core_license = core.parent / 'LICENSE.txt'
    if core_license.exists():
        add(core_license, 'testkit/runtime/GENESIS_PLUS_GX_LICENSE.txt')
    # Only selected continuous campaign stages and their canonical fixed replays.
    stages = {
        'natural-service-route': ['sms-npc-village94-house00-01', 'sms-npc-village94-house02-01', 'sms-npc-villagec7-house01-01', 'sms-npc-villagec7-house1f-01'],
        'natural-dungeon-route': ['sms-sms-npc-village94-house00-01', 'sms-sms-npc-village94-house02-01', 'sms-sms-reference-d1-entry-guard01', 'sms-sms-npc-villagec7-house01-01', 'sms-sms-npc-villagec7-house1f-01'],
        'natural-dungeon-combat': ['sms-auto-sms-reference-d1-keys02', 'sms-auto-sms-reference-d1-boss01', 'sms-auto-sms-reference-d1-exit02'],
    }
    for category, names in stages.items():
        base = ROOT / 'validation' / category
        for name in names:
            folder = base / name
            assert folder.is_dir(), folder
            related = [folder] + list(base.glob(name + '-assisted-fixed-replay-*')) + list(base.glob(name + '-fixed-replay'))
            for item in related:
                for p in item.rglob('*'):
                    if p.is_file() and p.suffix.lower() not in ('.wav', '.mp4'):
                        add(p)
    snapshot = dict(
        date='2026-11-09', version='v0321',
        git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        working_tree_status=subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True),
        archive_scope='Current source tree, tools, top-level analysis, selected SMS route evidence, test kit, input/reference ROMs, bundled Windows SGDK/Java toolchain. No Git history, historical binary caches, videos or old ROM collection.',
        first_read='PASSATION_V321_LLM.md', build='BUILD_V321.ps1',
        expected_rom_sha256='89c5833351312ffaa591efb1939161910a298af06437080e2cf84fb3fb8ac86e',
        complete_game_or_all_npcs_certified=False,
    )
    hashes = {}
    prefix = 'gaw-v321/'
    with zipfile.ZipFile(TARGET, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as out:
        def write(name, data):
            assert name not in hashes, name
            hashes[name] = hashlib.sha256(data).hexdigest()
            out.writestr(prefix + name, data)
        old = ROOT / 'handoff/gaw-v320-ready-to-build-windows.zip'
        with zipfile.ZipFile(old) as original:
            for item in original.infolist():
                name = item.filename.removeprefix('gaw-v320/')
                if name.startswith('toolchain/') or name == 'LICENCES.txt':
                    write(name, original.read(item))
        for name, path in sorted(files.items()):
            write(name, path.read_bytes())
        write('SNAPSHOT.json', (json.dumps(snapshot, indent=2, ensure_ascii=False) + '\n').encode())
        out.writestr(prefix + 'CONTENTS_SHA256.json', json.dumps(hashes, indent=2) + '\n')
    with zipfile.ZipFile(TARGET) as archive:
        assert archive.testzip() is None
        for name, expected in hashes.items():
            assert hashlib.sha256(archive.read(prefix + name)).hexdigest() == expected, name
    digest = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    TARGET.with_suffix('.zip.sha256').write_text(digest + '  ' + TARGET.name + '\n')
    result = dict(archive=str(TARGET), bytes=TARGET.stat().st_size, sha256=digest,
                  files=len(hashes) + 1, every_member_readback_sha256_verified=True)
    (ROOT / 'handoff/v321-package-verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
