"""Record fresh routes, then losslessly archive closed opening experiments."""
import json
import subprocess
import sys
from pathlib import Path

from archive_lossless_evidence import freeze, sha
from run_core import ROOT


def main():
    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    release=ROOT/'analysis/initial_world_v0316_report.json'
    proof=json.loads(release.read_bytes());assert proof['md_sha256']==digest and proof['candidate_promoted']
    cases=[];folders=[]
    for region,prefix in [('ntsc','md'),('pal','md-pal')]:
        folder=ROOT/'validation/natural-dungeon-route'/(prefix+'-v0316-fresh-first-dungeon01')
        path=folder/'route_report.json';report=json.loads(path.read_bytes())
        capture=json.loads((folder/'capture.json').read_bytes())
        assert report['rom_sha256']==capture['rom_sha256']==digest
        assert report['failure'] is None and report['reached_entrance'] and report['directional_probe_succeeded']
        assert not report['ram_injections'] and not report['sram_checkpoint_injection']
        assert not capture['test_ram_writes'] and capture['sram_input']is None
        assert report['last_state']['room']==0x1e4 and report['last_state']['health']>0
        cases.append(dict(region=region,report_sha256=sha(path.read_bytes()),frames=capture['frames'],
                          ready_frame=report['first_controllable_frame'],normal_continues=report['normal_continues'],
                          final_state=report['last_state']))
        folders.append(folder)
    route_path=ROOT/'analysis/initial_world_route_v0316_report.json';assert not route_path.exists()
    route_path.write_text(json.dumps(dict(passed=True,md_sha256=digest,cases=cases,ram_writes=0,sram_imports=0,
        complete_campaign_on_this_binary=False,scope='Fresh normal New Game to the first dungeon entrance and directional movement, in both regions. Does not prove dungeon completion or bosses.'),indent=2)+'\n')
    subprocess.run([sys.executable,str(ROOT/'tools/version_rom.py'),'--report',str(release),'--report',str(route_path),
                    '--notes','Recit : fondu de sortie restaure ; revelation initiale,16 contours et apparition du heros alignes PAL/NTSC. Trajets frais au premier donjon,reprise et inventaires verifies ; parcours complet encore requis.'],cwd=ROOT,check=True)
    roots=[ROOT/'validation/opening-return-v0315',ROOT/'validation/initial-world-source-v0315']+folders
    paths=[p for folder in roots for p in folder.rglob('*')if p.is_file()]
    tools=['build_private_candidate.ps1','compare_opening_candidate_campaign.py','diagnose_opening_campaign_inputs.py',
           'probe_house_cadence.py','probe_house_entry_clock.py','probe_initial_world_reveal.py','probe_opening_audio_clock.py',
           'profile_initial_world_source.py','summarize_initial_world_candidate06.py','integrate_initial_world_candidate06.py',
           'finalize_initial_world_v0316.py','validate_saved_game_compatibility.py']
    paths += [ROOT/'tools'/name for name in tools]+[release,route_path,ROOT/'analysis/initial_world_candidate06_v0315_report.json']
    archive=ROOT/'analysis/initial-world-v0316'
    manifest=freeze(ROOT,archive,paths,dict(md_sha256=digest,version=316,
        scope='Opening candidates01..06, including failed/rejected experiments, natural source traces, input diagnosis, target regressions and two fresh dungeon-entry routes. No complete v316 campaign claim.'),roots,cleanup=True)
    removed=manifest['removed_verified_generated'];archive_bytes=sum(p.stat().st_size for p in archive.rglob('*')if p.is_file())
    numbered=list((ROOT/'versions').glob('v*/*.bin'));assert len(numbered)==316
    original=ROOT/'input/original.sms';assert sha(original.read_bytes())=='852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9'
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest
    cleanup=ROOT/'analysis/initial_world_cleanup_v0316_report.json'
    cleanup.write_text(json.dumps(dict(passed=True,md_sha256=digest,manifest_sha256=sha((archive/'manifest.json').read_bytes()),
        removed_generated_files=len(removed),removed_generated_bytes=sum(p['bytes']for p in removed),
        archive_bytes=archive_bytes,net_artifact_bytes_freed=sum(p['bytes']for p in removed)-archive_bytes,
        numbered_roms_preserved=len(numbered),original_rom_preserved=True,all_archived_objects_readback_verified=True),indent=2)+'\n')
    print('v316 evidence archived; numbered ROMs and original preserved.',flush=True)


if __name__=='__main__':main()
