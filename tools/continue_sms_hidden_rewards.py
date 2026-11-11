"""Obtain the J9 apple and Kari-Kari hidden-room oil through actual inputs."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_plain_house_census import census_world
from extract_title import rle_planes


def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);a=p.parse_args()
    output=ROOT/'analysis/sms_hidden_rewards_campaign.json'
    saved=json.loads(output.read_bytes()) if output.exists() else {};visits=saved.get('completed_rewards',[])
    c=Campaign(visits[-1]['trace'] if visits else a.prefix,0x15e,'npc-hidden-rewards')
    verified=c.family+'/'+c.current
    def save(status):
        output.write_text(json.dumps(dict(status=status,initial_prefix=a.prefix,last_verified_prefix=verified,
            completed_rewards=visits,all_side_quests_complete=False),indent=2)+'\n')
    try:
        c.verify(lambda r:r['passed'])
        for outside,house,slot,module in [(0x92,0x4f,8,'natural_house_quest'),(0x55,0x1f,2,'natural_oil_stairs_service')]:
            if any(v['outside']==outside for v in visits):continue
            raw=c.raw();assert not raw[0xe0+slot]
            start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311]);selected=None
            for d in range(4):
                w=census_world(raw,outside,house,d);path,_=w.route(start)
                if path is not None:selected=d,w;break
            assert selected is not None
            d,w=selected;n=1
            while (ROOT/f'validation/natural-dungeon-route/sms-sms-npc-hidden-rewards-{outside:02x}-entry{n:02d}').exists():n+=1
            extra=['--house-outside',hex(outside),'--house-target',hex(house),'--persisted-only',
                '--live-prefix-terrain','--door-entry-direction',str(d)]
            tool='natural_bell_world_route.py';m=w.arrays['world_room_metadata']
            node=next((m[i:i+4] for i in range(0,len(m)-3,4) if m[i]==outside),None)
            if node and not raw[0x100+outside]&1:
                cells=bytearray(160);ptr=int.from_bytes(w.arrays['world_room_index'][outside*2:outside*2+2],'little')
                rle_planes(w.arrays['world_room_streams'],ptr,cells,0,1)
                if cells[node[1]] in (0x13,0x38,0x3d,0x85,0x86):
                    tool='natural_frozen_earth_world_route.py' if cells[node[1]]==0x38 else 'natural_earth_world_route.py'
                    extra+=['--earth-world-cell',hex(node[1])]
            c.route(f'{outside:02x}-entry{n:02d}',extra,tool=tool)
            c.service(f'{outside:02x}-gift{n:02d}',module,['--outside',hex(outside)])
            assert c.raw()[0xe0+slot]==1
            verified=c.family+'/'+c.current
            visits.append(dict(outside=outside,inventory_slot=slot,trace=verified,frame=c.cap()['frames']))
            save('running');print('HIDDEN REWARD VERIFIED',hex(outside),slot,flush=True)
        save('j9_apple_and_hidden_kari_kari_oil_obtained_and_replayed')
    except Exception:save('failed_objective_not_counted');raise
    finally:c.close()


if __name__=='__main__':main()
