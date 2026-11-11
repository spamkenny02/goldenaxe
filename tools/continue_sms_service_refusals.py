"""Tour all static merchant/healer/save contexts; refuse without resource edits.

Successful transactions, passage branches and gambling remain separate audits.
"""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_plain_house_census import census_world
from extract_title import rle_planes


def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True)
    p.add_argument('--limit',type=int,default=0);a=p.parse_args()
    output=ROOT/'analysis/sms_service_refusal_campaign.json'
    old=json.loads(output.read_bytes()) if output.exists() else {}
    completed=old.get('completed_visits',[])
    transports=old.get('completed_transports',[])
    c=Campaign(completed[-1]['trace'] if completed else a.prefix,0x15e,'npc-service-refusals')
    doors=json.loads((ROOT/'analysis/doors_reference.json').read_bytes())['direct_unconditional_doors']
    targets=[]
    for kind in ['merchant','healer','save']:
        assets=json.loads((ROOT/'analysis'/f'{kind}_assets.json').read_bytes())
        houses={n[0] for n in assets['nodes']}
        if kind=='merchant':outsides={n[0] for n in assets['towns']}
        elif kind=='healer':outsides={n[0] for n in assets['prices']}
        else:outsides={d['room'] for d in doors if d['target'] in houses}
        for outside in sorted(outsides):
            matches=[d for d in doors if d['room']==outside and d['target'] in houses]
            assert len(matches)==1,(kind,outside,matches)
            targets.append(dict(kind=kind,outside=outside,room=matches[0]['target']))
    assert len(targets)==48
    seen={(x['kind'],x['outside'],x['room']) for x in completed}
    pending=[t for t in targets if (t['kind'],t['outside'],t['room']) not in seen]
    clear={x['room']:x['kind'] for x in json.loads((ROOT/'analysis/room_clear_reference.json').read_bytes())['records']}
    verified=c.family+'/'+c.current
    def save(status):
        output.write_text(json.dumps(dict(status=status,initial_prefix=a.prefix,last_verified_prefix=verified,
            completed_visits=completed,completed_transports=transports,pending=pending,all_npcs_complete=False,all_service_variants_complete=False,
            scope='48 static merchant/healer/save contexts, refusal and exterior return only. No successful transaction or complete side-quest claim.'),indent=2)+'\n')
    try:
        c.verify(lambda r:r['passed'])
        while pending:
            raw=c.raw();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
            ordered=sorted(pending,key=lambda t:abs((t['outside']&15)-(start[0]&15))+abs((t['outside']>>4)-(start[0]>>4)))
            chosen=None
            for t in ordered:
                for direction in range(4):
                    w=census_world(raw,t['outside'],t['room'],direction);path,_=w.route(start)
                    if path is not None:chosen=t,direction,w;break
                if chosen:break
            if chosen is None:
                routes=json.loads((ROOT/'analysis/paid_passage_reference.json').read_bytes())['routes']
                passage=None
                for outside,destination,y,x in routes:
                    entrance_direction=None
                    for d in range(4):
                        path,_=census_world(raw,outside,0x9f,d).route(start)
                        if path is not None:entrance_direction=d;break
                    if entrance_direction is None:continue
                    # The arrival map differs from the current live map; only
                    # its recorded permanent flags may be proposed here.
                    for target in pending:
                        for d in range(4):
                            onward=census_world(raw,target['outside'],target['room'],d)
                            onward.live_room=None;onward.live_map=None
                            path,_=onward.route((destination,x,y))
                            if path is not None:passage=(outside,destination,entrance_direction);break
                        if passage:break
                    if passage:break
                if passage is None or raw[0xdd]<10:save('needs_transport_terrain_or_currency');return
                outside,destination,d=passage;n=1
                while (ROOT/f'validation/natural-dungeon-route/sms-sms-npc-service-refusals-passage-{outside:02x}-entry{n:02d}').exists():n+=1
                c.route(f'passage-{outside:02x}-entry{n:02d}',['--house-outside',hex(outside),'--house-target','0x9f',
                    '--persisted-only','--live-prefix-terrain','--door-entry-direction',str(d)],tool='natural_bell_world_route.py')
                c.service(f'passage-{outside:02x}-pay{n:02d}','natural_paid_passage',['--outside',hex(outside)])
                assert int.from_bytes(c.raw()[0xb9:0xbb],'little')==destination
                verified=c.family+'/'+c.current
                transports.append(dict(outside=outside,destination=destination,trace=verified,frame=c.cap()['frames']))
                save('running');continue
            t,direction,w=chosen;outside=t['outside'];suffix=f'{outside:02x}-{t["kind"]}'
            attempt=1
            while (ROOT/f'validation/natural-dungeon-route/sms-sms-npc-service-refusals-{suffix}-entry{attempt:02d}').exists():attempt+=1
            extra=['--house-outside',hex(outside),'--house-target',hex(t['room']),
                '--persisted-only','--live-prefix-terrain','--door-entry-direction',str(direction)]
            tool='natural_bell_world_route.py';metadata=w.arrays['world_room_metadata']
            node=next((metadata[i:i+4] for i in range(0,len(metadata)-3,4) if metadata[i]==outside),None)
            if clear.get(outside)==7 and not raw[0x100+outside]&1:extra+=['--fight-for-entrance']
            if node and not raw[0x100+outside]&1:
                cells=bytearray(160);ptr=int.from_bytes(w.arrays['world_room_index'][outside*2:outside*2+2],'little')
                rle_planes(w.arrays['world_room_streams'],ptr,cells,0,1)
                if cells[node[1]] in (0x13,0x38,0x3d,0x85,0x86):
                    assert raw[0xdb]>=8;tool='natural_frozen_earth_world_route.py' if cells[node[1]]==0x38 else 'natural_earth_world_route.py';extra+=['--earth-world-cell',hex(node[1])]
                elif 0x80<=cells[node[1]]<=0x84 and node[1]!=node[2]:extra+=['--required-chop',f'{hex(outside)}:{hex(node[1])}']
            c.route(suffix+f'-entry{attempt:02d}',extra,tool=tool)
            c.service(suffix+f'-refuse{attempt:02d}','sms_service_refusal',['--outside',hex(outside),'--kind',t['kind']])
            verified=c.family+'/'+c.current
            completed.append(dict(**t,trace=verified,frame=c.cap()['frames'],variant='refusal'))
            pending.remove(t);save('running');print('SERVICE REFUSAL VERIFIED',suffix,flush=True)
            if a.limit and len(completed)>=a.limit:save('limit_reached_remaining_not_claimed');return
        save('all_48_static_service_refusals_and_exits_replayed')
    except Exception:
        save('failed_objective_not_counted');raise
    finally:c.close()


if __name__=='__main__':main()
