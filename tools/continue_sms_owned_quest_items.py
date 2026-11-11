"""Bring genuinely bought quest items before the unclaimed gifts."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from sms_campaign_navigation import enter


def main():
    p=argparse.ArgumentParser();p.add_argument('--cases',required=True);a=p.parse_args()
    specs={
        'j9-owned-apple':('sms_merchant_variant_g1.json',0x92,0x4f,8,
            [dict(kind='silent',room=0x4f,point=[120,72]),dict(kind='talk',room=0x4f,point=[136,72],text_pc=0x8bea)]),
        'kari-owned-oil':('sms_merchant_variant_g5.json',0x55,0x1f,2,
            [dict(kind='travel',room=0x1f,point=[104,24],direction=0,target_room=15),
             dict(kind='talk',room=15,point=[104,56],text_pc=0x90bf),
             dict(kind='travel',room=15,point=[104,152],direction=1,target_room=0x1f)])}
    for key in a.cases.split(','):
        output=ROOT/f'analysis/sms_owned_quest_item_{key}.json'
        if output.exists() and json.loads(output.read_bytes()).get('passed'):continue
        source,outside,house,slot,steps=specs[key];purchase=json.loads((ROOT/'analysis'/source).read_bytes());assert purchase['passed']
        c=Campaign(purchase['trace'],0x15e,'npc-owned-quest-'+key)
        try:
            c.verify(lambda r:r['passed']);raw=c.raw();assert raw[0xe0+slot] and not raw[0x100+outside]&2
            n=enter(c,outside,house,key)
            plan=dict(steps=steps+[dict(kind='travel',room=house,point=[136,160],direction=1,target_room=outside)])
            c.service(f'contact{n:02d}','sms_contact_plan',['--plan',json.dumps(plan)])
            output.write_text(json.dumps(dict(passed=True,key=key,trace=c.family+'/'+c.current,
                item_bought_trace=purchase['trace'],inventory_slot=slot,gift_unclaimed_before_and_after=True),indent=2)+'\n')
            print('OWNED QUEST ITEM REPLY VERIFIED',key,flush=True)
        finally:c.close()


if __name__=='__main__':main()
