"""Replace premature exit qualifications with longer actual controls and videos."""
import json,subprocess,sys
from pathlib import Path
from run_core import ROOT
from validate_playable_sprite_limit import symbols
def main():
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');rom='validation/dialogue-empty-width03/candidate.bin';jobs=[]
    for p in sorted((ROOT/'videos/md-annexes-2026-11-12').glob('*/report.json')):
        v=json.loads(p.read_bytes());folder=ROOT/'validation'/v['trace'];r=json.loads((folder/'report.json').read_bytes());cap=json.loads((folder/'capture.json').read_bytes())
        if not v.get('passed') or not r.get('passed') or not ('visited' in r or r.get('variant') in ('post_reward_silent_return','refusal')):continue
        raw=(folder/f'ram_{cap["frames"]:05d}.bin').read_bytes();w=lambda n:raw[sy[n]]|(raw[sy[n]+1]<<8)
        if not(w('resume_phase') or w('world_graphics_class') or raw[sy['door_transition_loading']^1] or (r.get('variant')=='refusal' and not(r.get('actual_exterior_movement_verified') or r.get('actual_exterior_movement_frame') or r.get('actual_exterior_menu_roundtrip_verified')))):continue
        jobs.append((v,p.parent.name))
    for v,name in jobs:
        trial='settled-'+v['trace'].split('/')[-1];trace='natural-service-route/md-'+trial;folder=ROOT/'validation'/trace;movie_name='settled-'+name
        def run(tool,args,label):
            with (ROOT/'validation'/(movie_name+'-'+label+'.log')).open('w') as log:subprocess.run([sys.executable,str(ROOT/'tools'/tool),*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        print('REPAIR MD EXIT',v['trace'],flush=True)
        if not folder.exists():run('settle_md_house_exit.py',['--trace',v['trace'],'--rom',rom,'--trial',trial],'extend')
        cap=json.loads((folder/'capture.json').read_bytes());assisted=bool(cap['test_ram_writes']);proof=folder.with_name(folder.name+(f'-assisted-fixed-replay-{cap["frames"]}' if assisted else '-fixed-replay'))/'replay_report.json'
        if not proof.exists():run('replay_assisted_prefix.py' if assisted else 'replay_natural_campaign.py',['--trace',trace,'--rom',rom],'replay')
        target=ROOT/'videos/md-annexes-2026-11-12'/movie_name
        if not (target/'report.json').exists():run('record_md_annex.py',['--trace',trace,'--rom',rom,'--from-frame',str(v['first_emulated_frame']),'--name',movie_name],'video')
        assert json.loads((target/'report.json').read_bytes())['passed']
        subprocess.run([sys.executable,str(ROOT/'tools/summarize_md_annex_replay.py')],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        print('MD SETTLED EXIT VERIFIED AND FILMED',trace,flush=True)
    print('All selected premature endpoints extended:',len(jobs),flush=True)
if __name__=='__main__':main()
