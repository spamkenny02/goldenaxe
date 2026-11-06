"""Preserve all attract-loop experiments, then clean only verified closed outputs."""
import difflib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from archive_lossless_evidence import freeze,sha
from run_core import ROOT

def main():
    base=ROOT/'validation/menu-raster-v0316';project=base/'candidate37';integration=base/'integration-v0317';backup=integration/'previous-production'
    proof=ROOT/'analysis/attract_v0317_report.json';r=json.loads(proof.read_bytes());digest=r['md_sha256'];assert r['development']and r['candidate_promoted']and r['production_build_matches_tested_candidate']
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==sha((project/'out/release/rom.bin').read_bytes())==digest
    assert (base/'candidate37-clean/out/release/rom.bin').read_bytes()==(ROOT/'gaw-megadrive.bin').read_bytes()
    old=json.loads((backup/'index.json').read_bytes());assert len(old)==316
    current=json.loads((ROOT/'versions/index.json').read_bytes());assert len(current)==317
    for entry in old:assert sha((ROOT/'versions'/entry['rom']).read_bytes())==entry['sha256']
    entry=current[-1];assert entry['version']==317 and entry['sha256']==digest and entry['validation']=='development_targeted_checks'
    release=ROOT/'versions'/entry['rom'];assert release.read_bytes()==(ROOT/'gaw-megadrive.bin').read_bytes()
    shutil.copyfile(ROOT/'megadrive/out/release/symbol.txt',release.parent/'symbol.txt')
    patch=ROOT/'analysis/attract_candidate37_v0317_crlf.patch';assert not patch.exists();text=''
    for name in('main.c','intro.inc'):
        before=(backup/name).read_bytes();after=(ROOT/'megadrive/src'/name).read_bytes();assert after==(project/'src'/name).read_bytes()
        text+=''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/megadrive/src/'+name,tofile='b/megadrive/src/'+name))
    patch.write_bytes(text.encode())
    with tempfile.TemporaryDirectory(prefix='gaw-v317-source-')as name:
        dest=Path(name)/'megadrive/src';dest.mkdir(parents=True)
        for f in('main.c','intro.inc'):(dest/f).write_bytes((backup/f).read_bytes())
        subprocess.run(['git','apply',str(patch)],cwd=name,check=True,capture_output=True)
        assert all((dest/f).read_bytes()==(project/'src'/f).read_bytes()for f in('main.c','intro.inc'))
    candidates=[]
    for n in range(30,38):
        folder=base/f'candidate{n}';b=folder/'out/release/rom.bin';candidates.append(dict(candidate=n,sha256=sha(b.read_bytes()),bytes=b.stat().st_size,source_sha256={p.relative_to(folder).as_posix():sha(p.read_bytes())for p in(folder/'src').rglob('*')if p.is_file()}))
    artifacts=ROOT/'analysis/attract_v0317_artifacts_report.json';assert not artifacts.exists()
    artifacts.write_text(json.dumps(dict(version=317,development=True,md_sha256=digest,root_aliases_match=True,default_sources_match_tested_candidate=True,production_symbol_sha256=sha((release.parent/'symbol.txt').read_bytes()),patch_sha256=sha(patch.read_bytes()),patch_reconstructs_exact_sources=True,baseline_commit=r['baseline_commit'],candidates=candidates,public_numbered_roms_preserved=317,previous_preview_c0029_sha256=sha((ROOT/'versions/candidates/c0029-c3fca1d6/gaw-megadrive-c0029.bin').read_bytes()),driver_sha256=sha(Path(__file__).read_bytes())),indent=2)+'\n')
    selected=[p for p in base.iterdir()if p.is_dir()and(p.name=='candidate29'or any(p.name.startswith('candidate'+str(n))for n in range(30,38))or p.name in('reentry29','reentry30','reentry31','reentry32','reentry33','reentry34','reentry35','reentry36','reentry37','source-attract01','source-attract02','reentry-observer01','reentry-observer02','integration-v0317'))]
    paths=[p for folder in selected for p in folder.rglob('*')if p.is_file()]+[proof,artifacts,patch,release,release.parent/'symbol.txt',ROOT/'versions/index.json',ROOT/'megadrive/src/main.c',ROOT/'megadrive/src/intro.inc']
    names=['finalize_attract_v0317.py','integrate_attract_candidate37_v0317.py','profile_intro_reentry.py','profile_source_attract.py','validate_source_attract_audio.py','build_intro_irq_raster_observer.py','compare_boot_to_sms.py','validate_name_map_candidate.py','validate_inventory_restore.py','validate_start_menu_sfx.py','probe_start_menu_reveal.py','natural_dungeon_route.py','version_rom.py','update_readme.py','run_core.py','build_private_candidate.ps1']
    paths += [ROOT/'tools'/name for name in names]
    archive=ROOT/'analysis/attract-v0317';manifest=freeze(ROOT,archive,paths,dict(version=317,development=True,md_sha256=digest,scope='Attract-loop candidates30..37, full source measurements, receiving-build checks and integration. Candidate37 remains live; public numbered ROMs never cleaned.'),[p for p in selected if p.name!='candidate37'],cleanup=True)
    for entry in current:assert sha((ROOT/'versions'/entry['rom']).read_bytes())==entry['sha256']
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest
    size=sum(p.stat().st_size for p in archive.rglob('*')if p.is_file());removed=sum(p['bytes']for p in manifest['removed_verified_generated'])
    (ROOT/'analysis/attract_v0317_cleanup_report.json').write_text(json.dumps(dict(passed=True,version=317,md_sha256=digest,removed_files=len(manifest['removed_verified_generated']),removed_bytes=removed,archive_bytes=size,net_bytes_freed=removed-size,numbered_roms_preserved=317,manifest_sha256=sha((archive/'manifest.json').read_bytes()),latest_candidate_retained=True),indent=2)+'\n')
    print('v317 source/evidence preserved; all317 numbered ROMs verified after cleanup.',flush=True)

if __name__=='__main__':main()
