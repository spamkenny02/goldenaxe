"""Reach a gambling host and verify one explicit original-game branch."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_plain_house_census import census_world
from extract_title import rle_planes


def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True)
    p.add_argument('--outside',type=lambda v:int(v,0),default=0x5c)
    p.add_argument('--variant',choices=['play','refuse','poor'],default='play');p.add_argument('--rounds',type=int,choices=[1,2],default=1);a=p.parse_args()
    assert a.outside in (0x13,0x5c,0xa7,0xde)
    label=f'npc-minigame-{a.outside:02x}-{a.variant}';c=Campaign(a.prefix,0x15e,label)
    try:
        c.verify(lambda r:r['passed']);raw=c.raw();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
        selected=None
        for d in range(4):
            w=census_world(raw,a.outside,0x5f,d);path,_=w.route(start)
            if path is not None:selected=d,w;break
        assert selected is not None
        direction,w=selected;n=1
        while (ROOT/f'validation/natural-dungeon-route/sms-sms-{label}-entry{n:02d}').exists():n+=1
        extra=['--house-outside',hex(a.outside),'--house-target','0x5f','--persisted-only',
            '--live-prefix-terrain','--door-entry-direction',str(direction)]
        tool='natural_bell_world_route.py';m=w.arrays['world_room_metadata']
        node=next((m[i:i+4] for i in range(0,len(m)-3,4) if m[i]==a.outside),None)
        clear={x['room']:x['kind'] for x in json.loads((ROOT/'analysis/room_clear_reference.json').read_bytes())['records']}
        if clear.get(a.outside)==7 and not raw[0x100+a.outside]&1:extra+=['--fight-for-entrance']
        if node and not raw[0x100+a.outside]&1:
            cells=bytearray(160);ptr=int.from_bytes(w.arrays['world_room_index'][a.outside*2:a.outside*2+2],'little')
            rle_planes(w.arrays['world_room_streams'],ptr,cells,0,1)
            if cells[node[1]] in (0x13,0x38,0x3d,0x85,0x86):
                tool='natural_frozen_earth_world_route.py' if cells[node[1]]==0x38 else 'natural_earth_world_route.py'
                extra+=['--earth-world-cell',hex(node[1])]
            elif 0x80<=cells[node[1]]<=0x84 and node[1]!=node[2]:extra+=['--required-chop',f'{hex(a.outside)}:{hex(node[1])}']
        c.route(f'entry{n:02d}',extra,tool=tool)
        c.service(f'visit{n:02d}','sms_minigame_service',['--outside',hex(a.outside),'--variant',a.variant,'--rounds',str(a.rounds)])
        result=dict(passed=True,initial_prefix=a.prefix,last_verified_prefix=c.family+'/'+c.current,
            outside=a.outside,variant=a.variant,frame=c.cap()['frames'],all_minigame_variants_complete=False)
        (ROOT/f'analysis/sms_minigame_{a.outside:02x}_{a.variant}_campaign.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result),flush=True)
    finally:c.close()


if __name__=='__main__':main()
