"""Freeze source-derived intro clock work and preserve the unreleased ROMs."""
import difflib
import json
import subprocess
from pathlib import Path
from archive_lossless_evidence import freeze,sha
from run_core import ROOT


def main():
    base=ROOT/'validation/menu-raster-v0316';latest=base/'candidate18';archive=ROOT/'analysis/intro-clock-progress-v0316'
    public='8b94f2e022d1027b5bc3cefd18ffd9f79a8895fba7622defc400c10d6fdfff7b'
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==public
    assert sha((ROOT/'input/original.sms').read_bytes())=='852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9'
    numbered={p.relative_to(ROOT).as_posix():sha(p.read_bytes())for p in (ROOT/'versions').glob('v*/*.bin')}
    assert len(numbered)==316
    for name in ['main.c','intro.inc']:
        path='megadrive/src/'+name
        assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT)
    candidates=[]
    for number in range(10,19):
        folder=base/f'candidate{number:02d}';rom=folder/'out/release/rom.bin'
        comparisons=[]
        for region in ('ntsc','pal'):
            name=f'candidate{number:02d}-source'+('02-'if number==10 else'-')+region+'/report.json'
            path=base/name;r=json.loads(path.read_bytes());assert r['md_sha256']==sha(rom.read_bytes()) and r['frames']==6500
            comparisons.append(dict(region=region,report=path.relative_to(ROOT).as_posix(),report_sha256=sha(path.read_bytes()),
                totals=r['totals'],improved_pixels=r['improved_pixels'],degraded_pixels=r['degraded_pixels'],no_source_pixel_regression=r['no_source_pixel_regression']))
        proposal=dict(candidate=number,rom_sha256=sha(rom.read_bytes()),rom_bytes=rom.stat().st_size,
            checksum=rom.read_bytes()[0x18e:0x190].hex().upper(),public_baseline_sha256=public,
            source_sha256={p.relative_to(folder).as_posix():sha(p.read_bytes())for p in sorted((folder/'src').rglob('*'))if p.is_file()},
            comparisons=comparisons,promoted=False)
        target=folder/'clock-audit-binding.json';assert not target.exists();target.write_text(json.dumps(proposal,indent=2)+'\n');candidates.append(proposal)
    source=json.loads((base/'source-loads01/report.json').read_bytes())
    assert all(r['official_clock_trace_exact_frames']==3800 and r['initial_logic_clock']==20 for r in source['cases'])
    observer=json.loads((base/'source-loader-observer/report.json').read_bytes());assert observer['original_source_restored']
    audio=json.loads((base/'candidate18-audio/report.json').read_bytes());assert audio['passed']and audio['md_sha256']==candidates[-1]['rom_sha256']
    assert json.loads((base/'observer-exception01/report.json').read_bytes())['passed']
    patches=[]
    for number in (13,16,18):
        text=''
        for name in ('main.c','intro.inc'):
            before=(ROOT/'megadrive/src'/name).read_bytes().decode();after=(base/f'candidate{number:02d}'/'src'/name).read_bytes().decode()
            text+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/megadrive/src/'+name,tofile='b/megadrive/src/'+name))
        path=ROOT/f'analysis/intro_clock_candidate{number:02d}_v0316_crlf.patch';assert not path.exists();path.write_bytes(text.encode());patches.append(path)
        subprocess.run(['git','apply','--check',str(path)],cwd=ROOT,check=True,capture_output=True)
    report=ROOT/'analysis/intro_clock_progress_v0316_report.json';assert not report.exists()
    result=dict(passed=False,promoted=False,public_md_sha256=public,latest_candidate=18,latest_candidate_md_sha256=candidates[-1]['rom_sha256'],
        source_loader_measurements=source,source_observer_build=observer,candidates=candidates,boot_audio_equivalence=audio,
        patches={p.relative_to(ROOT).as_posix():sha(p.read_bytes())for p in patches},
        source_files_unchanged=True,numbered_roms_preserved=len(numbered),ram_writes=0,sram_imports=0,
        findings=['Intro fire used physical vtimer instead of the full-IRQ C02F clock.',
            'Source0F09 publishes the previous fire palette only on full IRQs; foreground preparation and audio-only IRQs are distinct.',
            'Source0D59 transfers768 text bytes, not the entire1536-byte map; full native conversion could visibly tear text.',
            'Candidate11 applies an isolated clock to every actor before fixing loaders; source comparison rejects this as worse.',
            'Candidate14 queues text after the second wait, candidate17 queues before it; both retain regressions and are not promoted.',
            'Candidate15/16 preserve the public menu code while isolating the fire correction; menu candidates remain preserved separately.'],
        limits=['Candidate18 retains source-visible raster regressions; no release gate is declared passed.',
            'Clock seed22 accounts for the first loader two omitted fall-through waits, based on measured source CE0=20. Attract-loop reentry remains unverified.',
            'Second/third intro actors still use vtimer; loader timing, SAT/palette publication and absolute source clock remain incomplete.',
            'Candidate08 menu proofs do not automatically certify candidate18.',
            'No new complete campaign or physical hardware validation was run. Global RNG/refresh fidelity remains open.'],
        driver_sha256=sha(Path(__file__).read_bytes()))
    report.write_text(json.dumps(result,indent=2)+'\n')
    selected=[p for p in base.iterdir()if p.is_dir()and (p.name.startswith(('candidate','logical-clock','source-load','observer-exception','text-raster-inspect')))]
    paths=[p for folder in selected for p in folder.rglob('*')if p.is_file()]
    tools=['archive_intro_clock_progress_v0316.py','compare_boot_to_sms.py','compare_boot_audio_state.py','profile_intro_logical_clock.py',
        'profile_source_intro_loads.py','build_intro_loader_observer.py','build_timing_core.py','run_core.py','build_private_candidate.ps1']
    paths += [ROOT/'tools'/name for name in tools]+[report]+patches
    roots=[p for p in selected if p.name!='candidate18']
    manifest=freeze(ROOT,archive,paths,dict(public_md_sha256=public,latest_candidate_md_sha256=candidates[-1]['rom_sha256'],
        scope='Unreleased intro clock/loader/text publication experiments10..18. Sources, symbols, screenshots preserved. Candidate18 build retained live.'),roots,cleanup=True)
    assert all(sha((ROOT/name).read_bytes())==digest for name,digest in numbered.items())
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==public
    assert sha((latest/'out/release/rom.bin').read_bytes())==candidates[-1]['rom_sha256']
    removed=manifest['removed_verified_generated'];size=sum(p.stat().st_size for p in archive.rglob('*')if p.is_file())
    cleanup=dict(passed=True,removed_files=len(removed),removed_bytes=sum(p['bytes']for p in removed),archive_bytes=size,
        net_bytes_freed=sum(p['bytes']for p in removed)-size,manifest_sha256=sha((archive/'manifest.json').read_bytes()),
        numbered_rom_sha256=numbered,latest_candidate_retained=True,public_md_sha256=public)
    (ROOT/'analysis/intro_clock_progress_cleanup_v0316_report.json').write_text(json.dumps(cleanup,indent=2)+'\n')
    print('Intro clock candidates preserved; production v316 unchanged; release gate remains open.')


if __name__=='__main__':main()
