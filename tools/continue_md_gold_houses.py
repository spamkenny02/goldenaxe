"""Visit the 31 retained direct money houses and verify their return contacts."""
import argparse,json,subprocess,sys,time
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film,entry_options,refill_magic,fund_wallet
from continue_sms_plain_house_census import census_world

def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--rom',required=True);p.add_argument('--wait-for-reward-returns',action='store_true');p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);a=p.parse_args();assert 0<=a.shard<a.shards
    if a.wait_for_reward_returns:
        deadline=time.monotonic()+10800
        while True:
            r=json.loads((ROOT/'analysis/md_reward_returns_campaign.json').read_bytes())
            if len(r['completed_visits'])==12 and r['status']!='failed_stage_not_counted':break
            assert r['status']!='failed_stage_not_counted' and time.monotonic()<deadline,'Reward return tour needs attention'
            time.sleep(5)
    source=json.loads((ROOT/'analysis/sms_gold_house_census_campaign.json').read_bytes());all_targets=source['completed_houses'];assert len(all_targets)==31
    targets=[t for i,t in enumerate(all_targets) if i%a.shards==a.shard]
    suffix='' if a.shards==1 else f'-shard{a.shard}of{a.shards}'
    output=ROOT/('analysis/md_gold_house_campaign'+suffix+'.json')
    old=json.loads(output.read_bytes()) if output.exists() else {}
    if not old and a.shards>1:
        legacy=json.loads((ROOT/'analysis/md_gold_house_campaign.json').read_bytes())
        old=dict(completed_houses=[d for d in legacy.get('completed_houses',[]) if any(t['outside']==d['outside'] for t in targets)],last_verified_prefix=legacy.get('last_verified_prefix',a.prefix))
    done=old.get('completed_houses',[])
    c=Campaign(old.get('last_verified_prefix',a.prefix),a.rom,'annex-gold-houses'+suffix);verified=c.trace;transports=old.get('completed_transports',[])
    def save(status):
        result=dict(status=status,last_verified_prefix=verified,completed_houses=done,completed_transports=transports,shard=a.shard,shards=a.shards,required_contexts=len(targets),shard_complete=len(done)==len(targets),all_31_direct_contexts_and_returns_verified=a.shards==1 and len(done)==31,unresolved_source_table_entries=source['unresolved_table_entries'],all_npcs_complete=False)
        from write_atomic_report import write_bytes
        write_bytes(output,(json.dumps(result,indent=2)+'\n').encode())
        if a.shards>1:
            union={}
            legacy_path=ROOT/'analysis/md_gold_house_campaign.json'
            if legacy_path.exists():
                for row in json.loads(legacy_path.read_bytes()).get('completed_houses',[]):union[row['outside']]=row
            branches=[]
            for n in range(a.shards):
                path=ROOT/f'analysis/md_gold_house_campaign-shard{n}of{a.shards}.json'
                if not path.exists():continue
                branch=json.loads(path.read_bytes());branches.append(dict(shard=n,report=path.relative_to(ROOT).as_posix(),last_verified_prefix=branch['last_verified_prefix'],complete=branch['shard_complete']))
                for row in branch['completed_houses']:union[row['outside']]=row
            aggregate=dict(status='all_31_direct_money_houses_and_returns_played_replayed_filmed' if len(union)==31 else 'independent_branches_in_progress',completed_houses=[union[k] for k in sorted(union)],branches=branches,separate_branches=True,canonical_single_continuation=False,all_31_direct_contexts_and_returns_verified=len(union)==31,unresolved_source_table_entries=source['unresolved_table_entries'],all_npcs_complete=False)
            if len(branches)==a.shards and all(b['complete'] for b in branches):write_bytes(legacy_path,(json.dumps(aggregate,indent=2)+'\n').encode())
    def proposal(raw,outside,house):
        start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
        for d in range(4):
            world=census_world(raw,outside,house,d)
            if entry_options(raw,outside,house,d,world):
                path,_=world.route(start)
                if path is not None:return len(path)
        return None
    try:
        c.verify(lambda r:r['passed'])
        while len(done)<len(targets):
            if c.sms_view()[0xdb]<8:refill_magic(c);verified=c.trace;save('genuine_magic_refill_filmed')
            raw=c.sms_view();pending=[r for r in targets if not any(d['outside']==r['outside'] for d in done)];choices=[]
            room=int.from_bytes(raw[0xb9:0xbb],'little')
            pending.sort(key=lambda t:(t['gain']>0,abs((t['outside']&15)-(room&15))+abs((t['outside']>>4)-(room>>4))))
            for target in pending:
                length=proposal(raw,target['outside'],0x3f)
                if length is not None:choices.append((target['gain']>0,length,target['outside'],target));break
            if not choices:
                candidates=[]
                for outside,destination,y,x in json.loads((ROOT/'analysis/paid_passage_reference.json').read_bytes())['routes']:
                    length=proposal(raw,outside,0x9f)
                    if length is None:continue
                    for target in pending:
                        world=census_world(raw,target['outside'],0x3f,0);world.live_room=None;world.live_map=None
                        if world.route((destination,x,y))[0] is not None:candidates.append((length,outside,destination));break
                assert candidates,'Remaining money houses require another actual access route'
                _,outside,destination=min(candidates);fund_wallet(c,10);n=enter(c,outside,0x9f,f'transport-{outside:02x}');first=c.cap()['frames']+1
                c.service(f'transport-{outside:02x}-pay{n:02d}','natural_paid_passage',['--outside',hex(outside)]);film(c,f'md-gold-transport-{outside:02x}-pay{n:02d}',first)
                assert int.from_bytes(c.sms_view()[0xb9:0xbb],'little')==destination
                verified=c.trace;transports.append(dict(outside=outside,destination=destination,trace=verified));save('actual_transport_filmed');continue
            target=min(choices,key=lambda r:r[:3])[3];outside=target['outside'];tag=f'{outside:02x}';n=enter(c,outside,0x3f,tag);first=c.cap()['frames']+1
            reference=target['trace']
            if not (ROOT/'validation'/reference/'report.json').exists():subprocess.run([sys.executable,str(ROOT/'tools/restore_validation_cache.py'),'--prefix','validation/'+reference],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
            c.service(tag+f'-contact-return{n:02d}','md_gold_and_return',['--outside',hex(outside),'--gain',str(target['gain']),'--sms-reference',reference]);name=f'md-gold-{tag}-contact-return{n:02d}';film(c,name,first);verified=c.trace
            report=json.loads((ROOT/'validation'/verified/'report.json').read_bytes());done.append(dict(outside=outside,gain=target['gain'],trace=verified,sms_reference=reference,previously_collected=report['previously_collected'],first_contact_and_reentry_verified=not report['previously_collected'],post_reward_silent_contact_verified=True,video_report=f'videos/md-annexes-2026-11-12/{name}/report.json'));save('contact_and_return_played_replayed_filmed')
        save('all_31_direct_money_houses_and_returns_played_replayed_filmed')
    except Exception:save('failed_stage_not_counted');raise
    finally:c.close()

if __name__=='__main__':main()
