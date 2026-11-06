"""Integrate the tested attract-loop fixes as an explicitly development v317."""
import json
import shutil
import subprocess
import sys
from pathlib import Path
from archive_lossless_evidence import sha
from run_core import ROOT

def main():
    base=ROOT/'validation/menu-raster-v0316';project=base/'candidate37';rom=project/'out/release/rom.bin';digest=sha(rom.read_bytes())
    previous_sha=sha((ROOT/'gaw-megadrive.bin').read_bytes());assert previous_sha=='8b94f2e022d1027b5bc3cefd18ffd9f79a8895fba7622defc400c10d6fdfff7b'
    assert (base/'candidate37-clean/out/release/rom.bin').read_bytes()==rom.read_bytes()
    source_sha=sha((ROOT/'input/original.sms').read_bytes());assert source_sha==sha(Path('D:/Cartmod/GoldenAxeWarrior/chat/Golden Axe Warrior (USA, Europe).sms').read_bytes())
    baseline_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    changed=[]
    for p in(project/'src').rglob('*'):
        if p.is_file()and p.read_bytes()!=(ROOT/'megadrive/src'/p.relative_to(project/'src')).read_bytes():changed.append(p.relative_to(project/'src').as_posix())
    assert sorted(changed)==['intro.inc','main.c']
    numbered={p.relative_to(ROOT).as_posix():sha(p.read_bytes())for p in(ROOT/'versions').glob('v*/*.bin')};assert len(numbered)==316
    refs={}
    def load(name):
        p=base/name;refs[p.relative_to(ROOT).as_posix()]=sha(p.read_bytes());return json.loads(p.read_bytes())
    matrix=load('candidate37-name-matrix/report.json');audio=load('candidate37-source-audio/report.json');assert matrix['passed']and len(matrix['cases'])==210 and audio['passed']
    assert matrix['md_sha256']==audio['md_sha256']==digest
    inventory=load('candidate37-inventory/inventory_restore_report.json');assert inventory['md_sha256']==digest and len(inventory['cases'])==6 and all(not any(r['static_background_pattern_difference_indices'].values())for r in inventory['cases'])
    sfx=load('candidate37-sfx/natural_start_menu_sfx_report.json');assert sfx['md_sha256']==digest and len(sfx['cases'])==4 and all(r['results']['sms']['events']==r['results']['md']['events']for r in sfx['cases'])
    comparisons=[];menus=[];routes=[];reentry=[]
    timings=load('source-attract02/report.json')
    for region in('ntsc','pal'):
        r=load('candidate37-loops-'+region+'/report.json');assert r['md_sha256']==digest and r['frames']==14000;comparisons.append(r)
        video=load('candidate37-video-'+region+'/report.json');assert video['md_sha256']==digest;selected=[r for r in video['pixel_differences']if r['frame']>=938];assert len(selected)==135 and all(not r['pixels']for r in selected);menus.append(dict(region=region,selected_menu_frames_exact=135,all_frames=len(video['pixel_differences']),all_frames_exact=sum(not r['pixels']for r in video['pixel_differences'])))
        name='md-fresh-d1-ntsc'if region=='ntsc'else'md-pal-fresh-d1-pal';route=load('candidate37-routes/'+name+'/route_report.json');assert route['rom_sha256']==digest and not route['failure']and route['directional_probe_succeeded']and not route['ram_injections'];routes.append(route)
        profile=load('reentry37/report.json');assert profile['md_sha256']==digest and not profile['unsupported_audio_commands'];case=next(r for r in profile['cases']if r['region']==region)
        original=next(r['fonts']for r in timings['cases']if r['region']==region)[1:]
        native=case['native_line_resets'];assert len(native)==len(original)==2
        assert all((s['entry_frame'],s['entry_clock'])==(m['frame'],m['clock'])for s,m in zip(original,native))
        assert all(not r['sprite_pending']and not r['palette_pending']and r['counter']>=6 for r in native)
        reentry.append(dict(region=region,source_entries=original,native_entries=native,entry_frames_and_clocks_exact=True))
    # Do not replace sources or output aliases while any relevant check is live.
    query="Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python' -and $_.CommandLine -match 'profile_intro_reentry.py|compare_boot_to_sms.py|validate_name_map_candidate.py|validate_inventory_restore.py|validate_source_attract_audio.py|natural_dungeon_route.py|validate_start_menu_sfx.py' } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"
    active=subprocess.run(['powershell','-NoProfile','-Command',query],capture_output=True,text=True,check=True);assert not active.stdout.strip(),active.stdout
    out=base/'integration-v0317';out.mkdir(exist_ok=False);backup=out/'previous-production';backup.mkdir()
    for name in changed:
        old=(ROOT/'megadrive/src'/name).read_bytes();assert old==subprocess.check_output(['git','show',baseline_commit+':megadrive/src/'+name],cwd=ROOT)
        (backup/name).write_bytes(old)
    for source,target in[(ROOT/'gaw-megadrive.bin',backup/'gaw-megadrive.bin'),(ROOT/'gaw-title-megadrive.bin',backup/'gaw-title-megadrive.bin'),(ROOT/'megadrive/out/release/symbol.txt',backup/'symbol.txt'),(ROOT/'versions/index.json',backup/'index.json')]:shutil.copyfile(source,target)
    for name in changed:shutil.copyfile(project/'src'/name,ROOT/'megadrive/src'/name)
    with(out/'production-build.log').open('wb')as log:subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'build.ps1')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest,'Production differs from the tested candidate; retain evidence and investigate.'
    assert (ROOT/'gaw-title-megadrive.bin').read_bytes()==rom.read_bytes()
    entry=next(e for e in json.loads((ROOT/'versions/index.json').read_bytes())if e['sha256']==digest);assert entry['version']==317
    report=ROOT/'analysis/attract_v0317_report.json';assert not report.exists()
    result=dict(version=317,development=True,candidate_promoted=True,targeted_checks_passed=True,source_pixel_regression_gate_passed=False,complete_port_verified=False,
        md_sha256=digest,source_sha256=source_sha,previous_md_sha256=previous_sha,baseline_commit=baseline_commit,
        production_build_matches_tested_candidate=True,clean_private_rebuild_identical=True,modified_native_sources={name:sha((ROOT/'megadrive/src'/name).read_bytes())for name in changed},
        source_frame_comparisons=comparisons,source_audio=audio,reentry_comparisons=reentry,selected_menu_visuals=menus,name_matrix_cases=210,start_menu_sfx_cases=4,inventory_cases=6,fresh_d1_routes=routes,evidence=refs,
        fixes=['Preserve DCE2 and clamp it on the source CP6 branch instead of modulo6.',
            'Clear pending intro SAT/palette publications at entry/exit.',
            'Restore the return-to-intro fade, font workload and19 full initial-palette waits.',
            'Maintain the source clock through actual title full waits; disabled-display waits require a new IRQ.',
            'Restore all four first-picture map waits instead of skipping their callbacks with a seed adjustment.',
            'Request the full reveal IRQ before68k preparation so an IRQ during preparation is not counted twice.',
            'Retain the source line-counter configuration across title installs; later024F calls have no initial HINT burst.',
            'Remove the extra81 request delay after fixing the black IRQ wait.'],
        limits=['Development version; source-visible partial-frame reveal and title fade differences remain.',
            '14000 no-input frames cover two complete attract cycles and the start of a third, not arbitrary input or complete gameplay.',
            'Audio gate covers400 reader bytes and8 PSG registers from frame23, with pending command normalization; initial silent setup and PCM are not certified.',
            'Game-to-title, all saved-game palettes, a complete campaign on this ROM, global Z80 refresh/RNG fidelity and physical hardware remain unverified.'],driver_sha256=sha(Path(__file__).read_bytes()))
    report.write_text(json.dumps(result,indent=2)+'\n')
    subprocess.run([sys.executable,str(ROOT/'tools/version_rom.py'),'--development','--report',str(report),'--notes','Developpement : retours intro/titre, horloge, attente IRQ et compteur du feu corriges ; audio SMS et deux boucles verifies. Menus, inventaires et premier donjon controles ; ecarts visuels et parcours complet encore ouverts.'],cwd=ROOT,check=True)
    assert all(sha((ROOT/name).read_bytes())==value for name,value in numbered.items())
    print('Development v0317 integrated; default sources and aliases match the tested ROM.',flush=True)

if __name__=='__main__':main()
