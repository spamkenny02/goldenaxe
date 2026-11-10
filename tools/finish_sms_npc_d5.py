"""Fight the actual SMS satellites/core, then traverse the return mechanism."""
from run_core import ROOT
from continue_sms_npc_d4 import read,checked,invoke,ROUTE,COMBAT,COMMON


def main():
    common=[x for x in COMMON if x!='--equip-axe']+['--equip-basic']
    current='sms-auto-sms-npc-d5-contact02'
    checked(COMBAT,current,lambda r:r['contact_route_passed'])
    cap=read(COMBAT+'/'+current,'capture.json');trial='sms-npc-d5-approach01';name='sms-auto-'+trial
    if not (ROOT/'validation'/COMBAT/name).exists():
        invoke('assisted_boss_route.py',['--boss-room','0x163','--planner','ordinary',*common,
            '--continuation',current,'--rooms','0x172,0x173','--target-room','0x173',
            '--frames',str(cap['frames']+16000),'--trial',trial],'d5-approach')
    checked(COMBAT,name,lambda r:r['room_cleared']);current=name
    cap=read(COMBAT+'/'+current,'capture.json');trial='sms-npc-d5-boss01';name='sms-auto-'+trial
    if not (ROOT/'validation'/COMBAT/name).exists():
        invoke('assisted_boss_coarse_route.py',['--planning-step','32','--planning-horizon','192',
            '--moving-health-premium','80','--target-satellites','--enter-boss-up',
            '--boss-room','0x163','--planner','evasive','--boss-frames','8000',*common,
            '--continuation',current,'--rooms','0x173,0x163','--target-room','0x163',
            '--collect-gem','--expected-gem-capacity','72','--frames',str(cap['frames']+18000),
            '--trial',trial],'d5-boss')
    checked(COMBAT,name,lambda r:r['room_cleared'] and r['last_state']['max_health']==72);current=name
    cap=read(COMBAT+'/'+current,'capture.json');trial='sms-npc-d5-return-contact01';name='sms-auto-'+trial
    if not (ROOT/'validation'/COMBAT/name).exists():
        invoke('natural_contact_passage.py',[*common,'--continuation',current,
            '--rooms','0x163,0x173,0x174','--target-room','0x174','--contact-room','0x173',
            '--contact-destination','0x174','--frames',str(cap['frames']+16000),'--trial',trial],'d5-return-contact')
    checked(COMBAT,name,lambda r:r['contact_route_passed']);current=name
    cap=read(COMBAT+'/'+current,'capture.json');trial='sms-npc-d5-exit01';name='sms-auto-'+trial
    if not (ROOT/'validation'/COMBAT/name).exists():
        invoke('natural_dungeon_combat.py',[*common,'--continuation',current,
            '--rooms','0x174,0x155,0x165,0x166,0x176,0x186','--target-room','0x49',
            '--exit-dungeon','--frames',str(cap['frames']+18000),'--trial',trial],'d5-exit')
    checked(COMBAT,name,lambda r:r['full_dungeon_cleared'])
    print('FIFTH SMS CRYSTAL AND EXTERIOR RETURN VERIFIED',flush=True)


if __name__=='__main__':main()
