"""Visit all 33 once-only money houses and attempt the actual return contact."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_plain_house_census import census_world
from extract_title import rle_planes


def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);a=p.parse_args()
    output=ROOT/'analysis/sms_gold_house_census_campaign.json'
    old=json.loads(output.read_bytes()) if output.exists() else {};completed=old.get('completed_houses',[])
    transports=old.get('completed_transports',[]);prefix=old.get('last_verified_prefix',a.prefix)
    c=Campaign(prefix,0x15e,'npc-gold-census');verified=prefix
    gifts=json.loads((ROOT/'analysis/house_gold_reference.json').read_bytes())['records']
    doors=json.loads((ROOT/'analysis/doors_reference.json').read_bytes())['direct_unconditional_doors']
    unresolved=[dict(outside=n,gain=v if v<128 else v-256,reason='No direct 3F entrance; conditional/indirect reachability still requires audit') for n,v in gifts if not any(d['room']==n and d['target']==0x3f for d in doors)]
    pending=[dict(outside=n,gain=v if v<128 else v-256) for n,v in gifts if not any(h['outside']==n for h in completed) and not any(u['outside']==n for u in unresolved)]
    def save(status):
        output.write_text(json.dumps(dict(status=status,initial_prefix=a.prefix,last_verified_prefix=verified,
            completed_houses=completed,completed_transports=transports,pending=pending,unresolved_table_entries=unresolved,
            all_npcs_complete=False,all_side_quests_complete=False),indent=2)+'\n')
    def enter(outside,direction,w,suffix):
        raw=c.raw();extra=['--house-outside',hex(outside),'--house-target','0x3f','--persisted-only',
            '--live-prefix-terrain','--door-entry-direction',str(direction)]
        tool='natural_bell_world_route.py';m=w.arrays['world_room_metadata']
        node=next((m[i:i+4] for i in range(0,len(m)-3,4) if m[i]==outside),None)
        if node and not raw[0x100+outside]&1:
            cells=bytearray(160);ptr=int.from_bytes(w.arrays['world_room_index'][outside*2:outside*2+2],'little')
            rle_planes(w.arrays['world_room_streams'],ptr,cells,0,1)
            if cells[node[1]] in (0x13,0x38,0x3d,0x85,0x86):
                assert raw[0xdb]>=8;tool='natural_frozen_earth_world_route.py' if cells[node[1]]==0x38 else 'natural_earth_world_route.py'
                extra+=['--earth-world-cell',hex(node[1])]
            elif 0x80<=cells[node[1]]<=0x84 and node[1]!=node[2]:extra+=['--required-chop',f'{hex(outside)}:{hex(node[1])}']
        c.route(suffix,extra,tool=tool)
    try:
        c.verify(lambda r:r['passed'])
        while pending:
            raw=c.raw();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
            ordered=sorted(pending,key=lambda t:(t['gain']>0,abs((t['outside']&15)-(start[0]&15))+abs((t['outside']>>4)-(start[0]>>4))))
            chosen=None
            for t in ordered:
                for d in range(4):
                    w=census_world(raw,t['outside'],0x3f,d);path,_=w.route(start)
                    if path is not None:chosen=t,d,w;break
                if chosen:break
            if chosen is None:
                passage=None
                for outside,destination,y,x in json.loads((ROOT/'analysis/paid_passage_reference.json').read_bytes())['routes']:
                    direction=None
                    for d in range(4):
                        path,_=census_world(raw,outside,0x9f,d).route(start)
                        if path is not None:direction=d;break
                    if direction is None:continue
                    for target in pending:
                        for d in range(4):
                            w=census_world(raw,target['outside'],0x3f,d);w.live_room=None;w.live_map=None
                            path,_=w.route((destination,x,y))
                            if path is not None:passage=outside,destination,direction;break
                        if passage:break
                    if passage:break
                if passage is None or raw[0xdd]<10:save('needs_transport_terrain_or_currency');return
                outside,destination,d=passage;n=1
                while (ROOT/f'validation/natural-dungeon-route/sms-sms-npc-gold-census-passage-{outside:02x}-entry{n:02d}').exists():n+=1
                c.route(f'passage-{outside:02x}-entry{n:02d}',['--house-outside',hex(outside),'--house-target','0x9f',
                    '--persisted-only','--live-prefix-terrain','--door-entry-direction',str(d)],tool='natural_bell_world_route.py')
                c.service(f'passage-{outside:02x}-pay{n:02d}','natural_paid_passage',['--outside',hex(outside)])
                assert int.from_bytes(c.raw()[0xb9:0xbb],'little')==destination
                verified=c.family+'/'+c.current;transports.append(dict(outside=outside,destination=destination,trace=verified))
                save('running');continue
            t,d,w=chosen;outside=t['outside'];n=1
            while (ROOT/f'validation/natural-dungeon-route/sms-sms-npc-gold-census-{outside:02x}-entry{n:02d}').exists():n+=1
            already=bool(raw[0x100+outside]&2)
            enter(outside,d,w,f'{outside:02x}-entry{n:02d}')
            c.service(f'{outside:02x}-contact{n:02d}','natural_house_service',
                ['--outside',hex(outside),'--kind','gold','--gold-gain',str(t['gain'])]+(['--revisit'] if already else []))
            verified=c.family+'/'+c.current;first_trace=verified
            if not already:
                raw=c.raw();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
                w=census_world(raw,outside,0x3f,d);assert w.route(start)[0] is not None
                enter(outside,d,w,f'{outside:02x}-return-entry{n:02d}')
                c.service(f'{outside:02x}-return-contact{n:02d}','natural_house_service',
                    ['--outside',hex(outside),'--kind','gold','--revisit'])
                verified=c.family+'/'+c.current
            completed.append(dict(**t,previously_collected=already,first_contact_trace=first_trace,
                trace=verified,return_without_second_gift_verified=True,frame=c.cap()['frames']))
            pending.remove(t);save('running');print('GOLD HOUSE AND RETURN VERIFIED',hex(outside),flush=True)
        assert all(c.raw()[0x100+n]&2 for n,v in gifts if not any(u['outside']==n for u in unresolved))
        save('all_direct_money_house_contacts_replayed_two_table_entries_unresolved' if unresolved else 'all_33_money_houses_and_return_contacts_replayed')
    except Exception:save('failed_objective_not_counted');raise
    finally:c.close()


if __name__=='__main__':main()
