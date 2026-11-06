"""Publish a numbered development ROM without replacing stable v316."""
import difflib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from archive_lossless_evidence import freeze,sha
from run_core import ROOT

def main():
    base=ROOT/'validation/menu-raster-v0316';project=base/'candidate29';rom=project/'out/release/rom.bin';digest=sha(rom.read_bytes())
    stable=sha((ROOT/'gaw-megadrive.bin').read_bytes());assert stable=='8b94f2e022d1027b5bc3cefd18ffd9f79a8895fba7622defc400c10d6fdfff7b'
    assert (base/'candidate29-clean/out/release/rom.bin').read_bytes()==rom.read_bytes()
    numbered={p.relative_to(ROOT).as_posix():sha(p.read_bytes())for p in(ROOT/'versions').glob('v*/*.bin')};assert len(numbered)==316
    baseline_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name in('main.c','intro.inc'):assert (ROOT/'megadrive/src'/name).read_bytes()==subprocess.check_output(['git','show',baseline_commit+':megadrive/src/'+name],cwd=ROOT)
    changed=[p.relative_to(project/'src').as_posix()for p in(project/'src').rglob('*')if p.is_file()and p.read_bytes()!=(ROOT/'megadrive/src'/p.relative_to(project/'src')).read_bytes()];assert sorted(changed)==['intro.inc','main.c']
    refs={}
    def load(name):
        path=base/name;refs[path.relative_to(ROOT).as_posix()]=sha(path.read_bytes());return json.loads(path.read_bytes())
    matrix=load('candidate29-name-matrix/report.json');assert matrix['passed']and len(matrix['cases'])==210 and matrix['md_sha256']==digest
    audio=load('candidate29-audio/report.json');assert audio['passed']and audio['md_sha256']==digest
    tick=load('candidate29-tick-work/report.json');forecast=load('candidate29-text-forecast/report.json');planes=load('candidate29-third-planes/report.json')
    assert all(r['passed']and r['md_sha256']==digest for r in(tick,forecast,planes))
    sfx=load('candidate29-sfx/natural_start_menu_sfx_report.json');assert sfx['md_sha256']==digest and len(sfx['cases'])==4 and all(r['results']['sms']['events']==r['results']['md']['events']for r in sfx['cases'])
    inventory=load('candidate29-inventory/inventory_restore_report.json');assert inventory['md_sha256']==digest and len(inventory['cases'])==6 and all(not any(r['static_background_pattern_difference_indices'].values())for r in inventory['cases'])
    comparisons=[];menus=[];clocks=[];routes=[]
    for region in('ntsc','pal'):
        r=load('candidate29-source-'+region+'/report.json');assert r['md_sha256']==digest;comparisons.append(r)
        video=load('candidate29-video-'+region+'/report.json');assert video['md_sha256']==digest
        checked=[r for r in video['pixel_differences']if r['frame']>=938];assert len(checked)==135 and all(not r['pixels']for r in checked)
        menus.append(dict(region=region,selected_normalized_frames_exact=135,all_normalized_frames=len(video['pixel_differences']),all_normalized_frames_exact=sum(not r['pixels']for r in video['pixel_differences'])))
        source=load('logical-clock29/'+region+'-sms/observations.json');native=load('logical-clock29/'+region+'-md/observations.json')
        groups=[]
        for callback,scene in((0x1055,2),(0x104a,3)):
            pairs=[(s,m)for s,m in zip(source,native)if s['callback']==callback and m['scene']==scene]
            assert all(s['clock']==m['logic_clock']and s['counter']==m['counter']for s,m in pairs)
            groups.append(dict(scene=scene,paired_frames=len(pairs),clock_and_counter_exact=True))
        clocks.append(dict(region=region,groups=groups))
        folder='md-fresh-d1-ntsc02'if region=='ntsc'else'md-pal-fresh-d1-pal01'
        route=load('candidate29-routes/'+folder+'/route_report.json');assert route['rom_sha256']==digest and not route['failure']and route['reached_entrance']and route['directional_probe_succeeded']and not route['ram_injections']
        routes.append(route)
    # The first route trial selected the old production ROM with candidate symbols;
    # preserve it as a driver failure, never as an observed candidate game failure.
    invalid=load('candidate29-routes/md-fresh-d1-ntsc/route_report.json');assert invalid['rom_sha256']==stable and invalid['rom_sha256']!=digest
    preview=ROOT/'versions/candidates'/('c0029-'+digest[:8]);preview.mkdir(parents=True,exist_ok=False)
    target=preview/'gaw-megadrive-c0029.bin';shutil.copyfile(rom,target)
    text=''
    for name in('main.c','intro.inc'):
        before=(ROOT/'megadrive/src'/name).read_bytes();after=(project/'src'/name).read_bytes();dest=preview/'src'/name;dest.parent.mkdir(exist_ok=True);dest.write_bytes(after)
        text+=''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/megadrive/src/'+name,tofile='b/megadrive/src/'+name))
    patch=preview/'source.patch';patch.write_bytes(text.encode())
    with tempfile.TemporaryDirectory(prefix='gaw-preview-source-')as name:
        dest=Path(name)/'megadrive/src';dest.mkdir(parents=True)
        for f in('main.c','intro.inc'):(dest/f).write_bytes((ROOT/'megadrive/src'/f).read_bytes())
        subprocess.run(['git','apply',str(patch)],cwd=name,capture_output=True,check=True)
        assert all((dest/f).read_bytes()==(project/'src'/f).read_bytes()for f in('main.c','intro.inc'))
    metadata=dict(kind='development_preview',name='c0029',rom_sha256=digest,bytes=target.stat().st_size,checksum=target.read_bytes()[0x18e:0x190].hex().upper(),production_baseline_commit=baseline_commit,stable_version='v0316',stable_rom_sha256=stable,stable_aliases_replaced=False,clean_rebuild_identical=True,source_patch_sha256=sha(patch.read_bytes()),source_sha256={name:sha((project/'src'/name).read_bytes())for name in changed},complete_game_validated=False,source_pixel_regression_gate_passed=False)
    (preview/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    report=ROOT/'analysis/intro_text_irq_preview_c0029_report.json';assert not report.exists()
    report.write_text(json.dumps(dict(preview_ready=True,stable_release_gate_passed=False,preview=metadata,source_frame_comparisons=comparisons,native_callback_work=tick,native_text_forecast=forecast,paired_clock_comparisons=clocks,boot_audio=audio,menu_frame_comparisons=menus,name_matrix_cases=210,start_menu_sfx_cases=4,inventory_cases=6,fresh_d1_routes=routes,third_scene_patterns=planes,evidence=refs,
        excluded_driver_trial=dict(path='validation/menu-raster-v0316/candidate29-routes/md-fresh-d1-ntsc',reason='Driver CLI initially selected v316 while using candidate29 symbols. This is excluded from candidate behavior evidence; fixed two region runs select the tested SHA.'),
        limits=['Development preview; source-visible raster regressions remain in partial image reveals.',
            'Title/fade differences remain after the intro; whole-game fidelity cannot be inferred from6500 no-input frames.',
            'All-phase lower-bound IRQ forecast is verified on130 first-map cases; two uncertain phase cases remain unforced. Attract-loop reentry and provisional boot seed22 remain open.',
            'A complete campaign, global Z80 refresh/RNG fidelity and physical hardware remain unverified on this binary.'],driver_sha256=sha(Path(__file__).read_bytes())),indent=2)+'\n')
    selected=[p for p in base.iterdir()if p.is_dir()and(p.name=='candidate26'or any(p.name.startswith('candidate'+str(n))for n in(27,28,29))or p.name in('logical-clock29','source-loads04','irq-raster-observer01','irq-spans01','text-irq-model01'))]
    paths=[p for folder in selected for p in folder.rglob('*')if p.is_file()]+[base/'text-irq-alignment01.json',report]+list(preview.rglob('*'))
    paths=[p for p in paths if p.is_file()]
    paths += [ROOT/'tools'/n for n in('publish_intro_work_preview_c0029.py','analyze_intro_text_irq_loss.py','build_intro_irq_raster_observer.py','profile_intro_irq_spans.py','validate_intro_tick_work.py','validate_intro_text_irq_forecast.py','validate_name_map_candidate.py','validate_inventory_restore.py','validate_start_menu_sfx.py','natural_dungeon_route.py','validate_intro_third_planes.py','compare_boot_to_sms.py','compare_boot_audio_state.py','run_core.py','build_private_candidate.ps1')]
    archive=ROOT/'analysis/intro-text-irq-preview-c0029';manifest=freeze(ROOT,archive,paths,dict(preview_sha256=digest,stable_sha256=stable,scope='Development previewc0029, source IRQ model, work validation and regressions. Original candidate29 build remains live; closed trials archived before cleanup.'),[p for p in selected if p.name!='candidate29'],cleanup=True)
    assert all(sha((ROOT/name).read_bytes())==digest for name,digest in numbered.items())
    assert sha(target.read_bytes())==sha(rom.read_bytes())==metadata['rom_sha256']and sha((ROOT/'gaw-megadrive.bin').read_bytes())==stable
    removed=sum(p['bytes']for p in manifest['removed_verified_generated']);size=sum(p.stat().st_size for p in archive.rglob('*')if p.is_file())
    (ROOT/'analysis/intro_text_irq_preview_c0029_cleanup_report.json').write_text(json.dumps(dict(passed=True,removed_files=len(manifest['removed_verified_generated']),removed_bytes=removed,archive_bytes=size,net_bytes_freed=removed-size,manifest_sha256=sha((archive/'manifest.json').read_bytes()),stable_numbered_roms_preserved=316,numbered_preview_sha256=metadata['rom_sha256']),indent=2)+'\n')
    print('Numbered development ROM published locally:',target,'SHA',metadata['rom_sha256'],flush=True)

if __name__=='__main__':main()
