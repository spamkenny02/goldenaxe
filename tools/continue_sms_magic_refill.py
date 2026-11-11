"""Reach a magic merchant and buy a refill with existing currency, then replay."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_plain_house_census import census_world


def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);a=p.parse_args()
    c=Campaign(a.prefix,0x15e,'npc-magic-refill')
    try:
        c.verify(lambda r:r['passed']);raw=c.raw()
        assert raw[0xdd]>=20 and raw[0xdb]<raw[0xdc]
        start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
        candidates=[]
        for outside,mode,param in json.loads((ROOT/'analysis/merchant_assets.json').read_bytes())['towns']:
            if mode!=2:continue
            for direction in range(4):
                path,_=census_world(raw,outside,0x2f,direction).route(start)
                if path is not None:candidates.append((len(path),outside,direction))
        assert candidates,'No reachable magic shop proposal'
        _,outside,direction=min(candidates)
        attempt=1
        while (ROOT/f'validation/natural-dungeon-route/sms-sms-npc-magic-refill-{outside:02x}-entry{attempt:02d}').exists():attempt+=1
        c.route(f'{outside:02x}-entry{attempt:02d}',
            ['--house-outside',hex(outside),'--house-target','0x2f','--persisted-only',
             '--door-entry-direction',str(direction)],tool='natural_bell_world_route.py')
        c.service(f'{outside:02x}-buy{attempt:02d}','sms_merchant_key_purchase',
            ['--outside',hex(outside),'--kind','magic'])
        report=dict(passed=True,initial_prefix=a.prefix,last_verified_prefix=c.family+'/'+c.current,
            outside=outside,frame=c.cap()['frames'],magic_before=raw[0xdb],magic_after=c.raw()[0xdb],
            gold_before=raw[0xdd],gold_after=c.raw()[0xdd],
            scope='Real first-option purchase and fixed replay; no resource injection or full merchant-branch claim.')
        (ROOT/'analysis/sms_magic_refill_campaign.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report),flush=True)
    finally:c.close()


if __name__=='__main__':main()
