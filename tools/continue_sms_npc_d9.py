"""Open the real Ice Bell passage and play SMS dungeon nine and its guardians."""
from sms_campaign_runner import Campaign
from continue_sms_npc_d4 import COMBAT


def main():
    exit_trace=COMBAT+'/sms-auto-sms-npc-d8-exit01'
    c=Campaign(exit_trace,0x1be,'npc-d9')
    try:
        c.verify(lambda r:r['full_dungeon_cleared']);c.equip(1,'equipaxe01')
        c.route('returnpaid1a-entry01',['--house-outside','0x1a','--house-target','0x9f','--persisted-only'],
                new_episode=True,exit_proof=exit_trace if c.family!=COMBAT else None,tool='natural_bell_world_route.py')
        c.service('returnpaid1a-service01','natural_paid_passage',['--outside','0x1a'])
        c.route('healer94-entry01',['--house-outside','0x94','--house-target','0'])
        c.service('healer94-rest01','natural_free_healer',['--allow-full-health'])
        c.route('entry01',['--door-index','9'],tool='natural_bell_world_route.py')
        c.stage('switch1de01','earth','0x1fc,0x1fd,0x1fe,0x1ee,0x1de,0x1ce','0x1ce',
                ['--equip-axe','--wake-sentinels','--earth-room','0x1de','--earth-cell','0x34',
                 '--earth-cast-x','72','--earth-cast-y','80','--passage-destination','0x1ce',
                 '--contact-room','0x1de','--contact-destination','0x1ce'],gate='passed',
                tool='natural_earth_then_contact.py')
        c.stage('earth1ce01','earth','0x1ce','0x1ce',
                ['--earth-room','0x1ce','--earth-cell','0x56','--earth-cast-x','104','--earth-cast-y','112',
                 '--earth-action-only','--earth-during-combat','--passage-destination','0x1ce'],gate='earth_route_passed')
        c.stage('mini-ready01','ordinary','0x1ce','0x1ce',['--equip-axe','--wake-sentinels'])
        c.stage('midboss01','evasive','0x1ce,0x1be','0x1be',
                ['--equip-basic','--planning-step','16','--planning-horizon','96','--boss-frames','8000'],coarse=True)
        c.resume('resume01',0x19c)
        c.stage('switch1ad01','contact','0x1be,0x1ae,0x1ad','0x1ad',
                ['--equip-basic','--contact-room','0x1ad','--contact-destination','0x1ad'],gate='contact_route_passed')
        c.stage('portal19e-ready01','ordinary','0x1ad,0x1ae,0x19e','0x19e',['--equip-basic','--avoid-portal-rooms','0x19e'])
        c.stage('giant-ready01','ordinary','0x19e,0x19d','0x19d',
                ['--equip-basic','--avoid-portal-rooms','0x19e','--reach-room','--arrival-x','24',
                 '--arrival-y','88'],gate='target_room_reached')
        c.stage('giant01','evasive','0x19d,0x19c','0x19c',
                ['--equip-basic','--planning-step','16','--planning-horizon','96','--boss-frames','8000'],coarse=True)
        c.resume('post-giant-resume01',0x1ac)
        c.stage('balloon01','item','0x19c,0x19b','0x19b',['--equip-axe','--collect-item','11'],gate='item_acquisition_passed')
        c.stage('main-approach01','contact','0x19b,0x19c,0x19d,0x19e,0x1cc,0x1bc,0x1bd,0x1bc,0x1ac','0x1ac',
                ['--equip-basic','--contact-room','0x1bd','--contact-destination','0x1bc',
                 '--avoid-portal-rooms','0x1cc','--wake-sentinels'],gate='contact_route_passed',budget=20000)
        c.stage('boss01','evasive','0x1bc,0x1ac','0x1ac',
                ['--equip-basic','--planning-step','16','--planning-horizon','96','--boss-frames','8000',
                 '--enter-boss-up','--entry-boss-kind','0x6c','--collect-gem','--expected-gem-capacity','104'],coarse=True)
        rooms='0x1ac,0x1bc,0x1cc,0x19e,0x1ae,0x1be,0x1ce,0x1de,0x1ee,0x1fe,0x1fd,0x1fc'
        c.stage('exit01','ordinary',rooms,'0xeb',
                ['--equip-axe','--exit-dungeon','--rush-rooms',rooms,'--cross-hazard-rooms','0x19e'],gate='full_dungeon_cleared')
        print('NINTH SMS CRYSTAL, BALLOON AND EXTERIOR RETURN VERIFIED',flush=True)
    finally:c.close()


if __name__=='__main__':main()
