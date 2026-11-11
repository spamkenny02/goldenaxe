"""Purchase the intermediate shield before collecting the Dragon Shield."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_plain_house_census import census_world


def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);a=p.parse_args()
    c=Campaign(a.prefix,0x15e,'npc-knight-shield')
    try:
        c.verify(lambda r:r['passed']);raw=c.raw();assert raw[0xf2]<2 and raw[0xdd]>=250
        start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311]);assets=json.loads((ROOT/'analysis/merchant_assets.json').read_bytes())
        doors=json.loads((ROOT/'analysis/doors_reference.json').read_bytes())['direct_unconditional_doors']
        houses={n[0] for n in assets['nodes']};chosen=[]
        for outside,mode,group in assets['towns']:
            if mode!=0 or assets['goods'][group][0][0]!=25:continue
            house=next(d['target'] for d in doors if d['room']==outside and d['target'] in houses)
            for direction in range(4):
                path,_=census_world(raw,outside,house,direction).route(start)
                if path is not None:chosen.append((len(path),outside,house,direction))
        assert chosen;_,outside,house,direction=min(chosen);n=1
        while (ROOT/f'validation/natural-dungeon-route/sms-sms-npc-knight-shield-{outside:02x}-entry{n:02d}').exists():n+=1
        c.route(f'{outside:02x}-entry{n:02d}',['--house-outside',hex(outside),'--house-target',hex(house),
            '--persisted-only','--live-prefix-terrain','--door-entry-direction',str(direction)],tool='natural_bell_world_route.py')
        c.service(f'{outside:02x}-buy{n:02d}','sms_merchant_key_purchase',['--outside',hex(outside),'--kind','shield'])
        assert c.raw()[0xf2]==2 and c.raw()[0xdd]==raw[0xdd]-250
        result=dict(passed=True,initial_prefix=a.prefix,last_verified_prefix=c.family+'/'+c.current,
            outside=outside,shield_before=raw[0xf2],shield_after=c.raw()[0xf2],gold_before=raw[0xdd],gold_after=c.raw()[0xdd],frame=c.cap()['frames'])
        (ROOT/'analysis/sms_knight_shield_campaign.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result),flush=True)
    finally:c.close()


if __name__=='__main__':main()
