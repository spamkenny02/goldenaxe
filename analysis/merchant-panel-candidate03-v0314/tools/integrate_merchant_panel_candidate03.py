"""Promote the measured merchant fix only after v314's active campaign closes."""
import json
import shutil
import subprocess
import sys

from archive_lossless_evidence import sha
from run_core import ROOT


def main():
    def report(name):
        return json.loads((ROOT/'analysis'/name).read_bytes())
    proof = report('merchant_panel_candidate03_v0314_report.json')
    final = report('cold_palace_final_v0314_report.json')
    save = report('game_written_save_v0314_report.json')
    assert proof['passed'] and not proof['candidate_promoted']
    assert final['passed'] and final['campaign_from_new_game_completed'] and final['ending_complete']
    assert save['passed'] and save['game_written_save'] and save['source_crystal_markers_exact']==9
    public = proof['public_md_sha256']
    assert final['md_sha256']==save['md_sha256']==public
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==public
    # Active drivers continually resolve root ROM aliases and symbols. Their
    # successful reports alone are insufficient authorization to replace them.
    query = "Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python' -and $_.CommandLine -match 'run_palace_v0314.py|continue_palace_final_v0314.py|continue_after_d9_v0314.py|v0314-nine-crystals-01|v0314-palace-sources.*cold-stream' } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"
    live = subprocess.run(['powershell','-NoProfile','-Command',query],capture_output=True,text=True,check=True)
    assert not live.stdout.strip(), 'Finish existing v314 processes before promotion: '+live.stdout
    project = ROOT/'validation/merchant-panel-v0314/candidate03'
    proposal = json.loads((project/'proposal.json').read_bytes())
    changed = []
    for name, expected in proposal['sources'].items():
        candidate = project/name
        assert sha(candidate.read_bytes())==expected
        target = ROOT/'megadrive/src'/name.removeprefix('src/')
        if candidate.read_bytes()!=target.read_bytes():
            changed.append(name.removeprefix('src/'))
    assert changed==['merchant.inc']
    assert sha((project/'out/release/rom.bin').read_bytes())==proof['md_sha256']
    assert sha((project/'src/merchant.inc').read_bytes())==proof['merchant_source_sha256']
    shutil.copyfile(project/'src/merchant.inc',ROOT/'megadrive/src/merchant.inc')
    with (ROOT/'validation/merchant-panel-v0314/production-build.log').open('wb') as log:
        subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'build.ps1')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==proof['md_sha256'], 'Production differs from tested candidate'
    assert (ROOT/'gaw-title-megadrive.bin').read_bytes()==(ROOT/'gaw-megadrive.bin').read_bytes()
    entries=json.loads((ROOT/'versions/index.json').read_bytes())
    entry=next(e for e in entries if e['sha256']==proof['md_sha256'])
    version=entry['version']
    result=dict(proof,version=version,candidate_promoted=True,
        production_build_matches_tested_candidate=True,
        previous_campaign_version=314,previous_campaign_complete=True,
        current_campaign_complete=False,
        limits=proof['limits']+['The complete campaign/save proof remains tied to v314. Current ROM has the merchant,inventory and intro checks above; do not relabel the older campaign as a run of this binary.'])
    out=ROOT/'analysis'/f'merchant_panel_v{version:04d}_report.json'
    assert not out.exists()
    out.write_text(json.dumps(result,indent=2)+'\n')
    subprocess.run([sys.executable,str(ROOT/'tools/version_rom.py'),'--report',str(out),
        '--notes','Panneau marchand : alignement PAL/NTSC sur SMS,43 transactions,portrait et intro conserves. Campagne complete precedente : v314.'],cwd=ROOT,check=True)
    print('Merchant panel fix integrated as version',version,flush=True)


if __name__=='__main__':
    main()
