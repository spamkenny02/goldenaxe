"""Losslessly archive explicitly inventoried inactive validation build outputs."""
import argparse,json,shutil,subprocess
from pathlib import Path
from run_core import ROOT
from archive_lossless_evidence import freeze,sha


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True)
    a=parser.parse_args();base=(ROOT/'validation').resolve()
    plan=a.plan.resolve();out=a.out.resolve();report=a.report.resolve()
    assert plan.is_relative_to(base) and out.is_relative_to(ROOT/'analysis')
    assert report.is_relative_to(ROOT/'analysis') and not out.exists() and not report.exists()
    # Never clear outputs while a compiler/linker is running on this machine.
    active=subprocess.check_output(['powershell','-NoProfile','-Command',
        "Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(make|gcc|cc1|ld|as|m68k-elf-gcc)\\.exe$' } | Select-Object -ExpandProperty ProcessId"],cwd=ROOT).strip()
    assert not active,'A compiler or linker is active; leave its outputs alone'
    tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
    inventory=json.loads(plan.read_bytes());paths=[];skipped=[]
    for item in inventory['files']:
        p=(ROOT/item['path']).resolve();assert p.is_relative_to(base)
        relative=p.relative_to(base)
        assert 'out' in relative.parts and p.suffix.lower() in ('.o','.out','.d')
        assert not any(part.startswith(('intro-audio-v0313','v0314')) for part in relative.parts)
        if p.relative_to(ROOT).as_posix() in tracked:
            skipped.append(item['path']);continue
        stat=p.stat();assert stat.st_size==item['bytes'] and stat.st_mtime_ns==item['mtime_ns'],p
        with p.open('rb') as stream:header=stream.read(4096)
        valid=(header.startswith(b'\x7fELF') if p.suffix.lower()!='.d' else
               b'\0' not in header and b'.o:' in header)
        if not valid:
            skipped.append(item['path']);continue
        paths.append(p)
    assert paths
    before=shutil.disk_usage(ROOT).free
    manifest=freeze(ROOT,out,[*paths,plan,Path(__file__)],dict(
        scope='Only inventoried inactive ELF objects/executables and make dependencies inside validation/**/out.',
        current_projects_excluded=['intro-audio-v0313','v0314*'],
        skipped_tracked_or_unrecognized_files=skipped,
        binaries_symbols_sources_and_game_captures_preserved=True),[base],cleanup=True)
    after=shutil.disk_usage(ROOT).free
    removed=sum(item['bytes']for item in manifest['removed_verified_generated'])
    stored=sum(p.stat().st_size for p in out.rglob('*')if p.is_file())
    result=dict(passed=True,md_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),
        manifest=out.relative_to(ROOT).as_posix()+'/manifest.json',
        manifest_sha256=sha((out/'manifest.json').read_bytes()),
        removed_verified_files=len(manifest['removed_verified_generated']),
        removed_generated_bytes=removed,archive_bytes=stored,net_artifact_bytes_freed=removed-stored,
        observed_disk_free_delta_bytes=after-before,skipped_files=len(skipped),
        numbered_roms_preserved=len(json.loads((ROOT/'versions/index.json').read_bytes())),
        current_rom_sources_symbols_and_game_captures_preserved=True,
        archive_objects_retained_locally=True,full_game_validated=False,
        limits=['Each source object is read, compressed, decompressed and hash-checked before per-file deletion inside the verified validation output root.',
                'Only the manifest/report need Git tracking; this local archive contains reproducible historical compiler outputs. Current intro-audio/v0314 projects and all game captures are excluded.'])
    report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Inactive generated outputs removed:',result['removed_verified_files'],
          'net artifact bytes freed:',result['net_artifact_bytes_freed'],flush=True)


if __name__=='__main__':main()
