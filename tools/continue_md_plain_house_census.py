"""Replay known SMS ordinary-house visits on MD, then film each real branch."""
import argparse,json,subprocess,sys
from run_core import ROOT
from md_campaign_runner import Campaign
from continue_sms_plain_house_census import census_world,COMBAT_ENTRANCES
from natural_dungeon_route import World
from extract_title import rle_planes
from md_campaign_navigation import entry_options,enter,refill_magic

def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--rom',required=True);p.add_argument('--limit',type=int,default=0);a=p.parse_args()
    output=ROOT/'analysis/md_plain_house_census_campaign.json';old=json.loads(output.read_bytes()) if output.exists() else {};done=old.get('completed_houses',[])
    sms=json.loads((ROOT/'analysis/sms_npc_coverage_report.json').read_bytes());refs={}
    for visit in sms['visits']:
        key=visit['outside'],visit['room'];stage=visit.get('stage')
        if stage:refs.setdefault(key,'natural-service-route/'+stage.removeprefix('natural-service-route/'))
    census=json.loads((ROOT/'analysis/sms_plain_house_census_campaign.json').read_bytes())
    for visit in census['completed_houses']:refs.setdefault((visit['outside'],visit['room']),visit['trace'])
    contexts=json.loads((ROOT/'analysis/plain_house_dialogue_reference.json').read_bytes())['contexts'];groups={}
    for row in contexts:groups.setdefault((row['outside'],row['room']),[]).append(row)
    assert all(k in refs for k in groups),('No played SMS reference',set(groups)-set(refs))
    pending={k:v for k,v in groups.items() if not any((d['outside'],d['room'])==k for d in done)}
    c=Campaign(old.get('last_verified_prefix',a.prefix) if done else a.prefix,a.rom,'annex-plain');verified=c.trace
    def save(status):
        output.write_bytes((json.dumps(dict(status=status,rom_sha256=c.cap()['rom_sha256'],last_verified_prefix=verified,completed_houses=done,pending=[dict(outside=k[0],room=k[1],npc_contexts=len(v),sms_reference=refs[k]) for k,v in pending.items()],all_known_ordinary_contexts_complete=not pending,all_npcs_complete=False),indent=2)+'\n').encode())
    try:
        c.verify(lambda r:r['passed'])
        while pending:
            if c.sms_view()[0xdb]<8:
                refill_magic(c);verified=c.trace;save('real_magic_refill_played_replayed_filmed')
            raw=c.sms_view();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311]);chosen=None
            ordered=sorted(pending,key=lambda k:abs((k[0]&15)-(start[0]&15))+abs((k[0]>>4)-(start[0]>>4)))
            for key in ordered:
                for direction in range(4):
                    world=census_world(raw,*key,direction);path,_=world.route(start)
                    if path is not None and entry_options(raw,*key,direction,world):chosen=key,direction,world;break
                if chosen:break
            assert chosen is not None,'No reachable pending house; transport/terrain needs a separate played branch'
            (outside,room),direction,world=chosen;tag=f'{outside:02x}-{room:02x}';attempt=1
            while (ROOT/f'validation/natural-dungeon-route/md-annex-plain-{tag}-entry{attempt:02d}').exists():attempt+=1
            print('MD HOUSE START',tag,'remaining',len(pending),flush=True)
            attempt=enter(c,outside,room,tag);entry_end=c.cap()['frames']
            reference=refs[outside,room];source=ROOT/'validation'/reference
            if not (source/'report.json').exists():subprocess.run([sys.executable,str(ROOT/'tools/restore_validation_cache.py'),'--prefix','validation/'+reference],cwd=ROOT,check=True)
            c.npc(tag+f'-visit{attempt:02d}',reference);verified=c.trace
            report=json.loads((ROOT/'validation'/c.trace/'report.json').read_bytes());assert len(report['visited'])==len(pending[outside,room])
            video_name='maison-'+tag+f'-ntsc{attempt:02d}'
            with (ROOT/'validation'/(video_name+'-video.log')).open('w') as log:subprocess.run([sys.executable,str(ROOT/'tools/record_md_annex.py'),'--trace',c.trace,'--rom',str(c.rom),'--from-frame',str(entry_end+1),'--name',video_name],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
            done.append(dict(outside=outside,room=room,sms_reference=reference,trace=c.trace,frame=c.cap()['frames'],conversations=report['visited'],video_report='videos/md-annexes-2026-11-12/'+video_name+'/report.json'))
            del pending[outside,room];save('running_verified_and_filmed')
            subprocess.run([sys.executable,str(ROOT/'tools/summarize_md_annex_replay.py')],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
            if a.limit and len(done)>=a.limit:save('staged_limit_reached');return
        save('all_known_ordinary_contexts_played_replayed_and_filmed')
    except Exception:save('failed_stage_not_counted');raise
    finally:c.close()
if __name__=='__main__':main()
