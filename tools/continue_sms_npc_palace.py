"""Play the actual SMS palace, obtain Golden Axe, defeat Death Adder and wait for credits."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_npc_d4 import COMBAT


def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix');p.add_argument('--label',default='npc-palace');p.add_argument('--curse-remedy',action='store_true');a=p.parse_args()
    assert not a.prefix or a.label!='npc-palace','Use a new label to preserve the historical palace recording'
    exit_trace=a.prefix or COMBAT+'/sms-auto-sms-npc-d9-exit01'
    c=Campaign(exit_trace,0x15e,a.label)
    try:
        c.verify(lambda r:r.get('full_dungeon_cleared') or r.get('passed'));assert c.raw()[0xdf]==1
        assert all(b&128 for b in c.raw()[0xcf:0xd8])
        assist=json.loads((ROOT/'validation'/c.family/c.current/'assistance.json').read_bytes())
        c.route('entry01',['--door-index','10'],new_episode=bool(assist.get('first_boss_combat')),tool='natural_palace_world_route.py')
        c.stage('switch16d01','contact','0x18d,0x17d,0x16d','0x16d',
                ['--equip-basic','--mechanism-during-combat','--contact-room','0x16d','--contact-destination','0x16d'],gate='contact_route_passed')
        if a.curse_remedy:
            c.stage('curse-entry01','ordinary','0x16d,0x17d,0x18d,0x18e','0x18e',
                ['--equip-basic','--reach-room','--allow-live-arrival','--arrival-x','128','--arrival-y','128',
                 '--rush-rooms','0x18e'],gate='target_room_reached')
            trial='sms-'+c.label+'-curse-remedy01'
            c.invoke('sms_curse_remedy.py',['--sms','--trace',c.family+'/'+c.current,'--trial',trial],
                COMBAT,'sms-auto-'+trial,lambda r:r['curse_remedy_passed'])
        c.stage('pregiant01','contact','0x18e,0x17e,0x16e' if a.curse_remedy else '0x16d,0x17d,0x18d,0x18e,0x17e,0x16e','0x16e',
                ['--equip-basic','--wake-sentinels','--rush-rooms','0x16d','--contact-room','0x16e','--contact-destination','0x16e'],gate='contact_route_passed')
        c.stage('giant01','evasive','0x16e,0x15e','0x15e',
                ['--equip-basic','--planning-step','32','--planning-horizon','96','--entry-boss-kind','0x7b',
                 '--enter-boss-up','--boss-frames','10000'],coarse=True)
        c.resume('resume01',0x11e)
        c.stage('portal14e01','ordinary','0x15e,0x15d,0x16d,0x16c,0x14d,0x14e','0x14e',
                ['--equip-basic','--avoid-portal-rooms','0x14d','--defer-puzzles-rooms','0x16c','--rush-rooms','0x16d,0x16c'])
        c.stage('earth14e01','earth','0x14e,0x119','0x119',
                ['--equip-basic','--earth-room','0x14e','--earth-cell','0x58','--earth-cast-x','136',
                 '--earth-cast-y','112','--earth-direction','0','--passage-destination','0x119'],gate='earth_route_passed')
        c.stage('earth11a01','earth','0x119,0x11a,0x12a','0x12a',
                ['--equip-basic','--earth-during-combat','--earth-room','0x11a','--earth-cell','0x35',
                 '--earth-cast-x','88','--earth-cast-y','80','--earth-direction','0','--passage-destination','0x12a'],gate='earth_route_passed')
        c.stage('switch12901','contact','0x12a,0x129,0x12a,0x11c','0x11c',
                ['--equip-basic','--mechanism-during-combat','--contact-room','0x129','--contact-destination','0x12a'],gate='contact_route_passed')
        c.stage('switch12c01','contact','0x12a,0x11c,0x12c','0x12c',
                ['--equip-basic','--mechanism-during-combat','--contact-room','0x12c','--contact-destination','0x12c'],gate='contact_route_passed')
        c.stage('preguardian01','ordinary','0x12c,0x11c,0x11b,0x12b,0x12c,0x12d,0x12e','0x12e',
                ['--equip-basic','--rush-rooms','0x12c','--wake-sentinels'])
        c.stage('guardian01','evasive','0x12e,0x11e','0x11e',
                ['--equip-basic','--planning-step','32','--planning-horizon','96','--entry-boss-kind','0x7c',
                 '--enter-boss-up','--boss-frames','10000'],coarse=True,budget=20000)
        c.resume('resume-final01',0x14c)
        c.stage('goldenaxe01','item','0x11e,0x11d','0x11d',
                ['--equip-axe','--collect-item','1','--collect-item-value','2'],gate='item_acquisition_passed')
        proposal=json.loads((ROOT/'tools/recipes/palace-final-v0309.json').read_bytes())
        for e in proposal['stages']:
            name=e['name']
            if name in ('release','final','ending'):continue
            extra=['--equip-axe','--wake-sentinels']
            if e.get('avoid'):extra+=['--avoid-portal-rooms',e['avoid']]
            if name=='switch17c':extra+=['--isolated-retry-portal','0x13e','--isolated-retry-limit','8']
            if e['planner']=='earth':
                extra+=['--earth-room',e['earth_room'],'--earth-cell',e['earth_cell'],
                        '--earth-cast-x',str(e['cast'][0]),'--earth-cast-y',str(e['cast'][1]),
                        '--earth-direction',str(e['cast'][2]),'--passage-destination',e['target']]
            if e['planner']=='contact':extra+=['--contact-room',e['contact_room'],'--contact-destination',e['contact_destination']]
            gate={'ordinary':'room_cleared','earth':'earth_route_passed','contact':'contact_route_passed'}[e['planner']]
            c.stage(name+'01',e['planner'],e['rooms'],e['target'],extra,gate=gate,budget=30000 if name=='switch17c' else 18000)
        e=next(e for e in proposal['stages'] if e['name']=='final')
        c.stage('final01','evasive',e['rooms'],e['target'],
                ['--equip-axe','--planning-step','32','--planning-horizon','96','--entry-boss-kind',
                 e['entry_boss_kind'],'--enter-boss-up','--stop-on-ending'],coarse=True,gate='ending_handoff_passed')
        trial='sms-'+c.label+'-ending01'
        c.invoke('continue_recorded_ending.py',['--sms','--trace',c.family+'/'+c.current,
                 '--trial',trial,'--extra-frames','18000'],COMBAT,'sms-auto-'+trial,lambda r:r['ending_complete'])
        print('SMS DEATH ADDER, COMPLETE CREDITS AND RETURN TO INTRO VERIFIED',flush=True)
    finally:c.close()


if __name__=='__main__':main()
