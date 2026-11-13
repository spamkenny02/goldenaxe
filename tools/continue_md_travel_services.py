"""Replay and film paid inns or the six paid passage directions on MD."""
import argparse,json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film,fund_wallet,refill_magic,entry_options
from continue_sms_plain_house_census import census_world

def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--rom',required=True);p.add_argument('--kind',choices=['inn','passage'],required=True);a=p.parse_args()
    output=ROOT/f'analysis/md_{a.kind}_campaign.json';old=json.loads(output.read_bytes()) if output.exists() else {};done=old.get('completed_visits',[])
    c=Campaign(old.get('last_verified_prefix',a.prefix),a.rom,'annex-'+a.kind);verified=c.trace
    doors=json.loads((ROOT/'analysis/doors_reference.json').read_bytes())['direct_unconditional_doors']
    if a.kind=='inn':
        assets=json.loads((ROOT/'analysis/healer_assets.json').read_bytes());houses={r[0] for r in assets['nodes']}
        targets=[dict(outside=outside,price=cost,house=next(d['target'] for d in doors if d['room']==outside and d['target'] in houses)) for outside,cost in assets['prices']]
    else:
        assets=json.loads((ROOT/'analysis/paid_passage_reference.json').read_bytes())
        targets=[dict(outside=row[0],destination=row[1],price=assets['prices'][assets['towns'].index(row[0])],house=0x9f) for row in assets['routes']]
    def save(status):output.write_bytes((json.dumps(dict(status=status,last_verified_prefix=verified,completed_visits=done,required_contexts=len(targets),all_contexts_replayed_filmed=len(done)==len(targets),all_npcs_complete=False),indent=2)+'\n').encode())
    try:
        c.verify(lambda r:r['passed'])
        while len(done)<len(targets):
            raw=c.sms_view();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311]);candidates=[]
            for target in targets:
                if any(row['outside']==target['outside'] for row in done):continue
                for d in range(4):
                    world=census_world(raw,target['outside'],target['house'],d);proposal=entry_options(raw,target['outside'],target['house'],d,world)
                    if not proposal:continue
                    path,_=world.route(start)
                    if path is not None:candidates.append((len(path),target['outside'],target));break
            assert candidates,'No pending service currently reachable with genuine progression'
            target=min(candidates,key=lambda row:row[:2])[2]
            if c.sms_view()[0xdb]<8:refill_magic(c);verified=c.trace;save('actual_magic_refill_filmed')
            if target['price']:fund_wallet(c,target['price'])
            verified=c.trace;save('existing_gold_or_genuine_gift_verified')
            outside=target['outside'];tag=f'{outside:02x}';attempt=enter(c,outside,target['house'],tag);first=c.cap()['frames']+1
            c.service(tag+f'-pay{attempt:02d}','md_paid_healer' if a.kind=='inn' else 'natural_paid_passage',['--outside',hex(outside)])
            raw=c.sms_view()
            if a.kind=='passage':assert int.from_bytes(raw[0xb9:0xbb],'little')==target['destination']
            else:assert raw[0xd9]==raw[0xda]
            name=f'md-{c.label}-{tag}-pay{attempt:02d}';film(c,name,first);verified=c.trace
            done.append(dict(**target,trace=verified,video_report=f'videos/md-annexes-2026-11-12/{name}/report.json'));save('paid_service_played_replayed_filmed')
        save('all_known_contexts_paid_replayed_filmed')
    except Exception:save('failed_stage_not_counted');raise
    finally:c.close()

if __name__=='__main__':main()
