"""Reach unclaimed positive gifts until an actual wallet target is met."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_plain_house_census import census_world
from extract_title import rle_planes


def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True)
    p.add_argument('--target',type=int,default=250);p.add_argument('--resume',action='store_true');a=p.parse_args()
    assert 0<a.target<=255
    output=ROOT/'analysis/sms_gold_funding_campaign.json'
    old=json.loads(output.read_bytes()) if output.exists() and a.resume else {}
    completed=old.get('completed_gifts',[])
    c=Campaign(completed[-1]['trace'] if completed else a.prefix,0x15e,'npc-gold-funding')
    gifts=json.loads((ROOT/'analysis/house_gold_reference.json').read_bytes())['records']
    verified=c.family+'/'+c.current
    def save(status):
        stable=ROOT/'validation'/verified
        capture=json.loads((stable/'capture.json').read_bytes())
        actual_gold=(stable/f'ram_{capture["frames"]:05d}.bin').read_bytes()[0xdd]
        output.write_text(json.dumps(dict(status=status,initial_prefix=a.prefix,target=a.target,
            last_verified_prefix=verified,completed_gifts=completed,gold=actual_gold,
            all_gold_houses_complete=False,scope='Real positive unclaimed gifts for purchases; taxes and repeat-visit variants remain separate.'),indent=2)+'\n')
    try:
        c.verify(lambda r:r['passed'])
        while c.raw()[0xdd]<a.target:
            raw=c.raw();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
            candidates=[(n,v) for n,v in gifts if 0<v<128 and not raw[0x100+n]&2]
            candidates.sort(key=lambda t:(-t[1],abs((t[0]&15)-(start[0]&15))+abs((t[0]>>4)-(start[0]>>4))))
            chosen=None
            for outside,gain in candidates:
                for d in range(4):
                    w=census_world(raw,outside,0x3f,d);path,_=w.route(start)
                    if path is not None:chosen=outside,gain,d,w;break
                if chosen:break
            if chosen is None:save('needs_transport_or_another_currency_source');return
            outside,gain,d,w=chosen;n=1
            while (ROOT/f'validation/natural-dungeon-route/sms-sms-npc-gold-funding-{outside:02x}-entry{n:02d}').exists():n+=1
            extra=['--house-outside',hex(outside),'--house-target','0x3f','--persisted-only',
                '--live-prefix-terrain','--door-entry-direction',str(d)]
            tool='natural_bell_world_route.py';m=w.arrays['world_room_metadata']
            node=next((m[i:i+4] for i in range(0,len(m)-3,4) if m[i]==outside),None)
            if node and not raw[0x100+outside]&1:
                cells=bytearray(160);ptr=int.from_bytes(w.arrays['world_room_index'][outside*2:outside*2+2],'little')
                rle_planes(w.arrays['world_room_streams'],ptr,cells,0,1)
                if cells[node[1]] in (0x13,0x38,0x3d,0x85,0x86):
                    assert raw[0xdb]>=8;tool='natural_frozen_earth_world_route.py' if cells[node[1]]==0x38 else 'natural_earth_world_route.py';extra+=['--earth-world-cell',hex(node[1])]
                elif 0x80<=cells[node[1]]<=0x84 and node[1]!=node[2]:extra+=['--required-chop',f'{hex(outside)}:{hex(node[1])}']
            c.route(f'{outside:02x}-entry{n:02d}',extra,tool=tool)
            before=c.raw()[0xdd]
            c.service(f'{outside:02x}-gift{n:02d}','natural_house_service',
                ['--outside',hex(outside),'--kind','gold','--gold-gain',str(gain)])
            assert c.raw()[0xdd]==min(255,before+gain)
            verified=c.family+'/'+c.current
            completed.append(dict(outside=outside,gain=gain,gold_before=before,gold_after=c.raw()[0xdd],
                trace=verified,frame=c.cap()['frames']))
            save('running');print('GOLD GIFT VERIFIED',hex(outside),c.raw()[0xdd],flush=True)
        save('wallet_target_obtained_by_real_gifts')
    except Exception:save('failed_objective_not_counted');raise
    finally:c.close()


if __name__=='__main__':main()
