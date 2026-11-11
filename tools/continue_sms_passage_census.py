"""Pay and actually traverse all six passage directions with original inputs."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_plain_house_census import census_world
from extract_title import rle_planes


def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);a=p.parse_args()
    output=ROOT/'analysis/sms_passage_census_campaign.json'
    old=json.loads(output.read_bytes()) if output.exists() else {}
    completed=old.get('completed_passages',[]);prefix=old.get('last_verified_prefix',a.prefix)
    pending=[r for r in json.loads((ROOT/'analysis/paid_passage_reference.json').read_bytes())['routes']
             if not any(c['outside']==r[0] for c in completed)]
    c=Campaign(prefix,0x15e,'npc-passage-census');verified=prefix
    def save(status):
        output.write_text(json.dumps(dict(status=status,last_verified_prefix=verified,
            completed_passages=completed,pending=pending,all_passage_variants_complete=False),indent=2)+'\n')
    try:
        c.verify(lambda r:r['passed'])
        while pending:
            raw=c.raw();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
            chosen=None
            for route in sorted(pending,key=lambda r:abs((r[0]&15)-(start[0]&15))+abs((r[0]>>4)-(start[0]>>4))):
                for direction in range(4):
                    w=census_world(raw,route[0],0x9f,direction)
                    if w.route(start)[0] is not None:chosen=route,direction,w;break
                if chosen:break
            if chosen is None or raw[0xdd]<10:save('needs_reachable_access_or_currency');return
            route,d,w=chosen;outside,destination,y,x=route;n=1
            while (ROOT/f'validation/natural-dungeon-route/sms-sms-npc-passage-census-{outside:02x}-entry{n:02d}').exists():n+=1
            extra=['--house-outside',hex(outside),'--house-target','0x9f','--persisted-only',
                '--live-prefix-terrain','--door-entry-direction',str(d)]
            tool='natural_bell_world_route.py';m=w.arrays['world_room_metadata']
            node=next((m[i:i+4] for i in range(0,len(m)-3,4) if m[i]==outside),None)
            if node and not raw[0x100+outside]&1:
                cells=bytearray(160);ptr=int.from_bytes(w.arrays['world_room_index'][outside*2:outside*2+2],'little')
                rle_planes(w.arrays['world_room_streams'],ptr,cells,0,1)
                if cells[node[1]] in (0x13,0x38,0x3d,0x85,0x86):
                    assert raw[0xdb]>=8
                    tool='natural_frozen_earth_world_route.py' if cells[node[1]]==0x38 else 'natural_earth_world_route.py'
                    extra+=['--earth-world-cell',hex(node[1])]
                elif 0x80<=cells[node[1]]<=0x84 and node[1]!=node[2]:extra+=['--required-chop',f'{hex(outside)}:{hex(node[1])}']
            c.route(f'{outside:02x}-entry{n:02d}',extra,tool=tool)
            c.service(f'{outside:02x}-pay{n:02d}','natural_paid_passage',['--outside',hex(outside)])
            assert int.from_bytes(c.raw()[0xb9:0xbb],'little')==destination
            verified=c.family+'/'+c.current
            completed.append(dict(outside=outside,destination=destination,trace=verified,frame=c.cap()['frames']))
            pending.remove(route);save('running');print('PAID PASSAGE VERIFIED',hex(outside),hex(destination),flush=True)
        save('all_six_paid_passage_directions_and_destinations_replayed')
    except Exception:save('failed_objective_not_counted');raise
    finally:c.close()


if __name__=='__main__':main()
