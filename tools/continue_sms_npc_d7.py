"""Actual SMS seventh-dungeon keys, mechanisms, intermediate, ship and crystal."""
import json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_npc_d4 import COMBAT


def main():
    exit_trace=COMBAT+'/sms-auto-sms-npc-d6-exit02'
    c=Campaign(exit_trace,0x1b8,'npc-d7')
    try:
        c.verify(lambda r:r['full_dungeon_cleared']);c.equip(1,'equipaxe01')
        first=True
        def world(suffix,extra):
            nonlocal first
            c.route(suffix,extra,new_episode=first,exit_proof=exit_trace if first and c.family!=COMBAT else None)
            first=False
        if c.raw()[0xde]<1:
            if c.raw()[0xdd]<60:
                world('goldac-entry01',['--house-outside','0xac','--house-target','0x3f'])
                c.service('goldac-gift01','natural_house_service',['--outside','0xac','--kind','gold','--gold-gain','30'])
            assert c.raw()[0xdd]>=60,'Earn additional actual gold before buying the D7 entry key'
            world('key94-entry01',['--house-outside','0x94','--house-target','0'])
            c.service('key94-buy01','sms_merchant_key_purchase',['--outside','0x94'])
        world('healer94-entry01',['--house-outside','0x94','--house-target','0'])
        c.service('healer94-rest01','natural_free_healer',['--allow-full-health'])
        world('entry01',['--door-index','7'])
        commands=[json.loads(line) for line in (ROOT/'tools/recipes/d7-preparation-v0310.jsonl').read_text().splitlines() if line.strip()]
        for suffix in ['key01','key03','earth01','earth02']:
            command=next(row for row in commands if '--trial' in row and row[row.index('--trial')+1]=='v0310-d7-healed-'+suffix)
            a=command[command.index('tools/assisted_boss_route.py')+1:]
            for flag in ['--prefix','--continuation','--frames','--trial']:
                if flag in a:n=a.index(flag);del a[n:n+2]
            trial='sms-npc-d7-'+suffix
            a+=['--sms','--prefix' if c.family!=COMBAT else '--continuation',c.current,
                '--frames',str(c.cap()['frames']+18000),'--trial',trial]
            gate='earth_route_passed' if '--earth-action-only' in a else 'new_key_verified'
            c.invoke('assisted_boss_route.py',a,COMBAT,'sms-auto-'+trial,lambda r:r[gate])
        c.stage('contact01','contact','0x1b9,0x1b8','0x1b8',
                ['--equip-axe','--contact-room','0x1b9','--contact-destination','0x1b8'],gate='contact_route_passed')
        c.stage('midboss01','evasive','0x1b8','0x1b8',
                ['--equip-basic','--planning-step','16','--planning-horizon','192','--enter-boss-up',
                 '--entry-boss-kind','0x78','--boss-frames','8000'],coarse=True)
        c.resume('resume02',0x179)
        c.stage('south01','ordinary','0x1b8,0x1b7,0x1c7,0x1c6,0x1d6','0x1d6',['--equip-axe','--avoid-portal-rooms','0x1b7'])
        c.stage('remote01','contact','0x1d6,0x1e6,0x1d6,0x1d5','0x1d5',
                ['--equip-axe','--avoid-portal-rooms','0x1e6','--contact-room','0x1e6','--contact-destination','0x1d6'],gate='contact_route_passed')
        c.stage('ship01','item','0x1d6,0x1d5','0x1d5',['--equip-axe','--collect-item','16','--item-first-when-blocked'],gate='item_acquisition_passed')
        c.stage('north01','ordinary','0x1d5,0x1d6,0x1c6,0x1c7,0x1b7,0x1b8','0x1b8',
                ['--equip-axe','--avoid-portal-rooms','0x1b7','--rush-rooms','0x1d5'])
        c.stage('warp01','earth','0x1b8,0x1a8,0x198','0x198',
                ['--equip-axe','--avoid-portal-rooms','0x198','--earth-room','0x1a8','--earth-cell','0x34',
                 '--earth-cast-x','72','--earth-cast-y','80','--passage-destination','0x198'],gate='earth_route_passed')
        c.stage('approach01','ordinary','0x198,0x199,0x189','0x189',['--equip-axe','--avoid-portal-rooms','0x198','--wake-sentinels'])
        c.stage('boss01','evasive','0x189,0x179','0x179',
                ['--equip-basic','--planning-step','16','--planning-horizon','192','--collect-gem',
                 '--expected-gem-capacity','88','--boss-frames','8000'],coarse=True)
        c.stage('return-earth01','earth','0x179,0x189,0x199,0x198,0x1a8,0x1b8,0x1b7,0x1cb,0x1db','0x1b',
                ['--exit-dungeon','--earth-room','0x1b7','--earth-cell','0x57','--earth-cast-x','120',
                 '--earth-cast-y','112','--earth-during-combat','--earth-action-only','--passage-destination','0x1b7','--equip-axe'],gate='earth_route_passed')
        c.stage('exit01','ordinary','0x1b7,0x1cb,0x1db','0x1b',['--exit-dungeon','--equip-axe'],gate='full_dungeon_cleared')
        print('SEVENTH SMS CRYSTAL, SHIP AND EXTERIOR RETURN VERIFIED',flush=True)
    finally:c.close()


if __name__=='__main__':main()
