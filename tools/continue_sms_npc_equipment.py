"""Play the reachable armor/Long Sword gifts before the fifth SMS dungeon."""
from run_core import ROOT
from continue_sms_npc_d4 import read,checked,invoke,ROUTE,COMBAT,SERVICE


def main():
    current='sms-auto-sms-npc-d4-exit03';family=COMBAT
    checked(family,current,lambda r:r['full_dungeon_cleared'])
    # B1/Dragon Mail needs the later sea route; keep it on the NPC checklist.
    for outside,field,level in [(0x27,'armor',2),(0x50,'basic',2)]:
        tag=f'{outside:02x}'
        trial='sms-npc-equipment-'+tag+('-entry03' if outside==0x27 else '-entry01');name='sms-'+trial
        cap=read(family+'/'+current,'capture.json')
        if not (ROOT/'validation'/ROUTE/name).exists():
            invoke('assisted_boss_route.py',['--world-route','--boss-room','0x163','--sms','--assisted-prefix',
                *(['--new-assistance-episode'] if family==COMBAT else []),
                '--prefix-combat' if family==COMBAT else '--prefix-service',current,
                '--house-outside',hex(outside),'--house-target','0x4f','--axe-terrain','--rope-terrain',
                '--fight-for-entrance',
                '--live-room-replan','--frames',str(cap['frames']+18000),'--trial',trial],'equipment-'+tag+'-entry')
        checked(ROUTE,name,lambda r:r['reached_entrance'])
        current=name;family=ROUTE
        trial='npc-equipment-'+tag+'-gift01';name='sms-'+trial
        if not (ROOT/'validation'/SERVICE/name).exists():
            invoke('run_sms_dialogue_observed.py',['natural_house_quest','--dialogue-core',
                str(ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_sms_dialogue03_libretro.dll'),
                '--sms','--assisted-prefix','--prefix',current,'--outside',hex(outside),
                '--trial',trial],'equipment-'+tag+'-gift')
        checked(SERVICE,name,lambda r:r['passed'] and r['last_state'][field]==level)
        current=name;family=SERVICE
    cap=read(family+'/'+current,'capture.json');trial='sms-npc-d5-entry01';name='sms-'+trial
    if not (ROOT/'validation'/ROUTE/name).exists():
        invoke('assisted_boss_route.py',['--world-route','--boss-room','0x163','--sms','--assisted-prefix',
            '--prefix-service',current,'--door-index','5','--axe-terrain','--rope-terrain',
            '--live-room-replan','--frames',str(cap['frames']+18000),'--trial',trial],'d5-entry')
    checked(ROUTE,name,lambda r:r['reached_entrance'])
    print('SMS ARMOR2, LONG SWORD AND FIFTH DUNGEON ENTRY VERIFIED',flush=True)


if __name__=='__main__':main()
