"""Obtain Sid's Dragon Shield with real ordinary inputs and fixed replay."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_plain_house_census import census_world


def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);a=p.parse_args()
    c=Campaign(a.prefix,0x15e,'npc-dragon-shield')
    try:
        c.verify(lambda r:r['passed']);raw=c.raw()
        assert raw[0xf2]<3 and raw[0xd4]&128
        start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311]);direction=None
        for d in range(4):
            path,_=census_world(raw,0x4c,9,d).route(start)
            if path is not None:direction=d;break
        assert direction is not None
        n=1
        while (ROOT/f'validation/natural-dungeon-route/sms-sms-npc-dragon-shield-entry{n:02d}').exists():n+=1
        c.route(f'entry{n:02d}',['--house-outside','0x4c','--house-target','9','--persisted-only',
            '--live-prefix-terrain','--door-entry-direction',str(direction)],tool='natural_bell_world_route.py')
        c.service(f'gift{n:02d}','natural_house_quest',['--outside','0x4c'])
        assert c.raw()[0xf2]==3 and c.raw()[0x14c]&2
        result=dict(passed=True,initial_prefix=a.prefix,last_verified_prefix=c.family+'/'+c.current,
            frame=c.cap()['frames'],shield_before=raw[0xf2],shield_after=c.raw()[0xf2],
            scope='Actual gift after crystal six and original acknowledgment/exit. Other giver/hint variants are separate.')
        (ROOT/'analysis/sms_dragon_shield_campaign.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result),flush=True)
    finally:c.close()


if __name__=='__main__':main()
