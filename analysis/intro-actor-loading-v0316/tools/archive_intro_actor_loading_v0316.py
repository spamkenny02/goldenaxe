"""Preserve native intro loader/bitmap fixes and their remaining release gate."""
import difflib
import json
import subprocess
import tempfile
from pathlib import Path
from run_core import ROOT
from archive_lossless_evidence import freeze,sha

def main():
    base=ROOT/'validation/menu-raster-v0316';latest=base/'candidate26';archive=ROOT/'analysis/intro-actor-loading-v0316'
    public=sha((ROOT/'gaw-megadrive.bin').read_bytes());assert public=='8b94f2e022d1027b5bc3cefd18ffd9f79a8895fba7622defc400c10d6fdfff7b'
    numbered={p.relative_to(ROOT).as_posix():sha(p.read_bytes())for p in (ROOT/'versions').glob('v*/*.bin')};assert len(numbered)==316
    for name in ('main.c','intro.inc'):
        assert (ROOT/'megadrive/src'/name).read_bytes()==subprocess.check_output(['git','show','HEAD:megadrive/src/'+name],cwd=ROOT)
    candidates=[]
    for number in range(19,27):
        folder=base/f'candidate{number}';rom=folder/'out/release/rom.bin';comparisons=[]
        for region in ('ntsc','pal'):
            path=base/f'candidate{number}-source-{region}/report.json';r=json.loads(path.read_bytes());assert r['md_sha256']==sha(rom.read_bytes())and r['frames']==6500
            comparisons.append(dict(region=region,report=path.relative_to(ROOT).as_posix(),report_sha256=sha(path.read_bytes()),totals=r['totals'],improved_pixels=r['improved_pixels'],degraded_pixels=r['degraded_pixels']))
        candidates.append(dict(candidate=number,rom_sha256=sha(rom.read_bytes()),checksum=rom.read_bytes()[0x18e:0x190].hex().upper(),comparisons=comparisons,
            sources={p.relative_to(folder).as_posix():sha(p.read_bytes())for p in(folder/'src').rglob('*')if p.is_file()}))
    def read(name):return json.loads((base/name).read_bytes())
    planes=read('candidate26-third-planes/report.json');audio=read('candidate26-audio/report.json');assert planes['passed']and audio['passed']and planes['md_sha256']==audio['md_sha256']==candidates[-1]['rom_sha256']
    source=read('source-loads03/report.json');assert all(r['loads'][2]['asset_foreground_tstates']==1195746 for r in source['cases'])
    patch=ROOT/'analysis/intro_actor_candidate26_v0316_crlf.patch';assert not patch.exists();text=''
    for name in ('main.c','intro.inc'):
        text+=''.join(difflib.unified_diff((ROOT/'megadrive/src'/name).read_bytes().decode().splitlines(True),(latest/'src'/name).read_bytes().decode().splitlines(True),fromfile='a/megadrive/src/'+name,tofile='b/megadrive/src/'+name))
    patch.write_bytes(text.encode())
    with tempfile.TemporaryDirectory(prefix='gaw-actor-patch-')as name:
        dest=Path(name)/'megadrive/src';dest.mkdir(parents=True)
        for file in ('main.c','intro.inc'):(dest/file).write_bytes((ROOT/'megadrive/src'/file).read_bytes())
        subprocess.run(['git','apply',str(patch)],cwd=name,check=True,capture_output=True)
        assert all((dest/file).read_bytes()==(latest/'src'/file).read_bytes()for file in('main.c','intro.inc'))
    report=ROOT/'analysis/intro_actor_loading_v0316_report.json';assert not report.exists()
    report.write_text(json.dumps(dict(passed=False,promoted=False,public_md_sha256=public,candidates=candidates,source_load_measurements=source,
        latest_clock_comparison=read('candidate26-clock-summary.json'),bitmap_validation=planes,boot_audio_equivalence=audio,
        patch_sha256=sha(patch.read_bytes()),patch_reconstructs_exact_source=True,
        original_callback_bytes=(ROOT/'input/original.sms').read_bytes()[0x104a:0x108b].hex(),
        fixes=['Scene2/3 loader pacing uses source foreground T states with current source audio work debited from each IRQ budget.',
            'Scene2 actors initialize before the first blank-map wait, and four full waits are restored.',
            'Source palette/SAT prepared after0F09 are published on the following full IRQ, not the audio-only transfer IRQ.',
            'Third-scene blank-map transfer touches only12 picture rows, preserving text.',
            'Source0DA5 writes both planes2/3, with two packed bytes per row and a two-bit rotation each row; native formerly wrote only plane2 and used the wrong stride.',
            'Only callback104A invokes bank5:BE25 lightning colors. Callback1055 preserves the scene2 picture palette.',
            'Third-animation mask work is derived as1536*178-5+31=273434 foreground T states; later passes begin at V112.'],
        limits=['Source-visible pixel regressions remain; no full release gate is declared passed.',
            'PAL scene2 and3 clock/counter matches apply only to the recorded paired no-input frames.',
            'NTSC source full-IRQ losses and first-mask timing remain unresolved. Source clock is not forced to a recorded trace.',
            'First-boot clock seed22 remains provisional; attract-loop reentry is not certified.',
            'Menus on this exact binary, complete campaign, RNG refresh and physical hardware remain unvalidated.'],
        numbered_roms_preserved=316,ram_writes=0,sram_imports=0,driver_sha256=sha(Path(__file__).read_bytes())),indent=2)+'\n')
    selected=[p for p in base.iterdir()if p.is_dir()and (any(p.name.startswith(f'candidate{n}')or p.name==f'logical-clock{n}'for n in range(19,27))or p.name in('candidate18','source-loads02','source-loads03'))]
    paths=[p for folder in selected for p in folder.rglob('*')if p.is_file()]+[base/'candidate26-clock-summary.json',patch,report]
    paths += [ROOT/'tools'/name for name in('archive_intro_actor_loading_v0316.py','profile_source_intro_loads.py','profile_intro_logical_clock.py','validate_intro_third_planes.py','compare_boot_to_sms.py','compare_boot_audio_state.py','run_core.py','build_private_candidate.ps1')]
    manifest=freeze(ROOT,archive,paths,dict(public_md_sha256=public,latest_candidate_md_sha256=candidates[-1]['rom_sha256'],scope='Unreleased intro actors/loaders/graphics19..26; candidate26 build remains live. Earlier candidate18 cache archived before cleanup.'),[p for p in selected if p.name!='candidate26'],cleanup=True)
    assert all(sha((ROOT/name).read_bytes())==digest for name,digest in numbered.items())
    removed=sum(p['bytes']for p in manifest['removed_verified_generated']);size=sum(p.stat().st_size for p in archive.rglob('*')if p.is_file())
    (ROOT/'analysis/intro_actor_loading_cleanup_v0316_report.json').write_text(json.dumps(dict(passed=True,removed_files=len(manifest['removed_verified_generated']),removed_bytes=removed,archive_bytes=size,net_bytes_freed=removed-size,manifest_sha256=sha((archive/'manifest.json').read_bytes()),numbered_roms_preserved=316,latest_candidate_sha256=sha((latest/'out/release/rom.bin').read_bytes())),indent=2)+'\n')
    print('Intro actors/loaders archived; all316 public ROMs preserved; candidate26 remains live.')

if __name__=='__main__':main()
