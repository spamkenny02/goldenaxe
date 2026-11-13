"""Play both crystal-dependent shield hints and the post-reward C7 chimney."""
import argparse,json,os,subprocess,sys,time
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film
from cold_replay_stream import ReplayStream

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',required=True);p.add_argument('--wait-for-passage-tour',action='store_true');a=p.parse_args()
    if a.wait_for_passage_tour:
        deadline=time.monotonic()+10800
        while True:
            r=json.loads((ROOT/'analysis/md_passage_campaign.json').read_bytes())
            if r.get('all_contexts_replayed_filmed'):break
            assert r['status']!='failed_stage_not_counted','Passage tour needs attention first'
            assert time.monotonic()<deadline,'Queued branch wait expired'
            time.sleep(5)
    output=ROOT/'analysis/md_shield_and_c7_branches.json';old=json.loads(output.read_bytes()) if output.exists() else {};done=old.get('completed_visits',[])
    for key,crystals,outside,house in [('shield-before-crystal',5,0x4c,9),('shield-after-crystal-hint',6,0x4c,9),('c7-return',None,0xc7,0x1f)]:
        if any(row['key']==key for row in done):continue
        reference=('natural-service-route/sms-npc-equipment-returns-c7-return01' if key=='c7-return' else json.loads((ROOT/f'analysis/sms_equipment_prerequisite_{key}.json').read_bytes())['trace'])
        folder=ROOT/'validation'/reference
        if not (folder/'report.json').exists():subprocess.run([sys.executable,str(ROOT/'tools/restore_validation_cache.py'),'--prefix','validation/'+reference],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        sr=json.loads((folder/'report.json').read_bytes());assert sr['passed']
        prefix='natural-service-route/md-annex-late-equipment-equipment-55-return01'
        if crystals is not None:
            tag=f'annex-campaign-{crystals}-crystals-shield01';prefix='natural-service-route/md-'+tag
            if not (ROOT/'validation'/prefix/'report.json').exists():
                with (ROOT/'validation'/(tag+'.log')).open('w') as log:subprocess.run([sys.executable,str(ROOT/'tools/md_annex_campaign_prefix.py'),'--rom',a.rom,'--crystals',str(crystals),'--trial',tag],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
            folder=ROOT/'validation'/prefix;cap=json.loads((folder/'capture.json').read_bytes())
            proof=folder.with_name(folder.name+f'-assisted-fixed-replay-{cap["frames"]}')/'replay_report.json'
            if not proof.exists():
                stream=ReplayStream(ROOT/'validation'/(tag+'-prefix-proof'),rom=ROOT/a.rom)
                try:stream.prove(prefix)
                finally:stream.close()
        c=Campaign(prefix,a.rom,'annex-'+key)
        try:
            c.verify(lambda r:r['passed']);raw=c.sms_view()
            if crystals is not None:assert bool(raw[0xd4]&128)==(crystals==6) and not raw[0x100+outside]&2
            else:assert raw[0x100+outside]&2
            attempt=enter(c,outside,house,key);first=c.cap()['frames']+1
            c.service(f'contact{attempt:02d}','md_contact_plan',['--plan',json.dumps(sr['plan']),'--sms-reference',reference]);name=f'md-{key}-contact{attempt:02d}';film(c,name,first)
            done.append(dict(key=key,trace=c.trace,sms_reference=reference,video_report=f'videos/md-annexes-2026-11-12/{name}/report.json'))
            output.write_bytes((json.dumps(dict(status='played_replayed_filmed',completed_visits=done,all_three_complete=len(done)==3,all_npcs_complete=False),indent=2)+'\n').encode())
        finally:c.close()

if __name__=='__main__':main()
