"""Use the earned ship for equipment, then play the eighth SMS labyrinth."""
import json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_npc_d4 import COMBAT


def main():
    exit_trace=COMBAT+'/sms-auto-sms-npc-d7-exit01'
    c=Campaign(exit_trace,0x1c9,'npc-d8')
    try:
        c.verify(lambda r:r['full_dungeon_cleared']);assert c.raw()[0xf0]==1
        c.equip(1,'equipaxe01');first=True
        def world(suffix,extra):
            nonlocal first
            c.route(suffix,extra,new_episode=first,exit_proof=exit_trace if first and c.family!=COMBAT else None)
            first=False
        for outside,suffix in [(0xb1,'dragonmail'),(0x6a,'flamesword')]:
            world(suffix+'-entry01',['--house-outside',hex(outside),'--house-target','0x4f'])
            c.service(suffix+'-gift01','natural_house_quest',['--outside',hex(outside)])
        if c.raw()[0xdd]<10:
            world('goldb5-entry01',['--house-outside','0xb5','--house-target','0x3f'])
            c.service('goldb5-gift01','natural_house_service',['--outside','0xb5','--kind','gold','--gold-gain','10'])
        world('healer94-entry01',['--house-outside','0x94','--house-target','0'])
        c.service('healer94-rest01','natural_free_healer',['--allow-full-health'])
        world('paid3c-entry01',['--house-outside','0x3c','--house-target','0x9f','--door-entry-direction','1'])
        c.service('paid3c-service02','natural_paid_passage',['--outside','0x3c'])
        world('entry01',['--door-index','8'])
        c.stage('mini-ready01','ordinary','0x1ea,0x1da,0x1ca','0x1ca',['--equip-axe','--wake-sentinels'])
        c.stage('midboss01','evasive','0x1ca,0x1c9','0x1c9',
                ['--equip-basic','--planning-step','16','--planning-horizon','96','--boss-frames','8000'],coarse=True)
        c.resume('resume01',0x196)
        recipes=json.loads((ROOT/'tools/recipes/d8-thief-route-v0306.json').read_bytes())
        for i,recipe in enumerate(recipes,1):
            tool,*a=recipe['arguments']
            for flag in ['--prefix','--continuation','--trial','--frames']:
                if flag in a:n=a.index(flag);del a[n:n+2]
            attempt='02' if i==6 else '01'
            if i==6:a+=['--mechanism-during-combat']
            a+=['--sms','--continuation',c.current,'--frames',str(c.cap()['frames']+18000),
                '--trial',f'sms-npc-d8-stage{i:02d}-{attempt}','--max-deaths','0']
            gate={'ordinary':'room_cleared','contact':'contact_route_passed',
                  'earth':'earth_route_passed','item':'item_acquisition_passed'}[recipe['planner']]
            c.invoke(tool.removeprefix('tools/'),a,COMBAT,f'sms-auto-sms-npc-d8-stage{i:02d}-{attempt}',lambda r:r[gate])
        c.stage('boss01','evasive','0x1a6,0x196','0x196',
                ['--equip-basic','--planning-step','16','--planning-horizon','96','--boss-frames','8000',
                 '--collect-gem','--expected-gem-capacity','96'],coarse=True)
        c.stage('exit01','ordinary','0x196,0x1a6,0x1a7,0x1eb,0x1ea','0x29',
                ['--equip-axe','--exit-dungeon','--rush-rooms','0x1a6,0x1a7,0x1eb,0x1ea',
                 '--cross-hazard-rooms','0x1a6,0x1a7'],gate='full_dungeon_cleared')
        print('EIGHTH SMS CRYSTAL AND EXTERIOR RETURN VERIFIED',flush=True)
    finally:c.close()


if __name__=='__main__':main()
