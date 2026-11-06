"""Publish the bounded first-world fix without claiming a new full campaign."""
import json
import shutil
import subprocess
import sys

from archive_lossless_evidence import sha
from run_core import ROOT


def main():
    base=ROOT/'validation/opening-return-v0315';project=base/'candidate06'
    proof_path=ROOT/'analysis/initial_world_candidate06_v0315_report.json'
    proof=json.loads(proof_path.read_bytes())
    assert proof['passed'] and not proof['candidate_promoted']
    assert not proof['complete_campaign_on_this_binary']
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==proof['public_md_sha256']
    query="Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python' -and $_.CommandLine -match 'compare_opening_candidate_campaign.py|probe_initial_world_reveal.py|validate_saved_game_compatibility.py|probe_intro_audio_boot.py|validate_inventory_restore.py' } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"
    live=subprocess.run(['powershell','-NoProfile','-Command',query],capture_output=True,text=True,check=True)
    assert not live.stdout.strip(),'Existing validation still active: '+live.stdout
    proposal=json.loads((project/'proposal.json').read_bytes());changed=[]
    for name,digest in proposal['sources'].items():
        assert sha((project/name).read_bytes())==digest
        if (project/name).read_bytes()!=(ROOT/'megadrive'/name).read_bytes():changed.append(name)
    assert changed==['src/main.c']
    assert sha((project/'src/main.c').read_bytes())==proof['main_source_sha256']
    assert sha((project/'out/release/rom.bin').read_bytes())==proof['md_sha256']
    previous=base/'previous-production';previous.mkdir(exist_ok=False)
    shutil.copyfile(ROOT/'megadrive/src/main.c',previous/'main.c')
    shutil.copyfile(ROOT/'megadrive/out/release/symbol.txt',previous/'symbol.txt')
    shutil.copyfile(project/'src/main.c',ROOT/'megadrive/src/main.c')
    with (base/'production-build.log').open('wb')as log:
        subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'build.ps1')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==proof['md_sha256'],'Production differs from tested candidate'
    assert (ROOT/'gaw-title-megadrive.bin').read_bytes()==(ROOT/'gaw-megadrive.bin').read_bytes()
    entry=next(e for e in json.loads((ROOT/'versions/index.json').read_bytes())if e['sha256']==proof['md_sha256'])
    assert entry['version']==316
    result=dict(proof,version=316,candidate_promoted=True,production_build_matches_tested_candidate=True,
                prior_campaign_version=315,prior_campaign_complete=True,
                previous_symbols_sha256=sha((previous/'symbol.txt').read_bytes()),
                integration_driver_sha256=sha((ROOT/'tools/integrate_initial_world_candidate06.py').read_bytes()))
    target=ROOT/'analysis/initial_world_v0316_report.json';assert not target.exists()
    target.write_text(json.dumps(result,indent=2)+'\n')
    subprocess.run([sys.executable,str(ROOT/'tools/version_rom.py'),'--report',str(target),
                    '--notes','Recit : fondu de sortie restaure ; revelation initiale,16 contours et apparition du heros alignes PAL/NTSC. Reprise et inventaires verifies ; nouveau parcours complet encore requis.'],cwd=ROOT,check=True)
    print('Initial-world fix integrated as v0316; complete campaign remains unverified on this binary.',flush=True)


if __name__=='__main__':main()
