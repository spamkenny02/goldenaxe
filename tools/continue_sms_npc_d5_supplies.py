"""Play fifth-dungeon boots, a gold NPC, key purchase and ordinary return."""
from run_core import ROOT
from continue_sms_npc_d4 import read,checked,invoke,ROUTE,COMBAT,SERVICE,COMMON


def main():
    current='sms-sms-npc-d5-entry01';family=ROUTE
    checked(family,current,lambda r:r['reached_entrance'])
    def stage(suffix,planner,rooms,target,extra,predicate):
        nonlocal current,family
        cap=read(family+'/'+current,'capture.json');trial='sms-npc-d5-'+suffix;name='sms-auto-'+trial
        if not (ROOT/'validation'/COMBAT/name).exists():
            invoke('assisted_boss_route.py',['--boss-room','0x163','--planner',planner,*COMMON,
                '--prefix' if family==ROUTE else '--continuation',current,'--rooms',rooms,
                '--target-room',target,'--frames',str(cap['frames']+18000),'--trial',trial,*extra],'d5-'+suffix)
        checked(COMBAT,name,predicate);current=name;family=COMBAT
    stage('key01','ordinary','0x186,0x176','0x176',['--collect-key'],lambda r:r['new_key_verified'])
    stage('earth01','earth','0x176,0x166','0x166',
          ['--earth-room','0x176','--earth-cell','0x4a','--earth-cast-x','168','--earth-cast-y','96',
           '--earth-direction','0','--passage-destination','0x166'],lambda r:r['earth_route_passed'])
    stage('boots01','item','0x166,0x156,0x157','0x157',
          ['--collect-item','14','--collect-item-value','1'],lambda r:r['item_acquisition_passed'])
    stage('supply-exit01','ordinary','0x157,0x156,0x166,0x176,0x186','0x49',
          ['--exit-dungeon','--exit-before-crystal'],lambda r:r['dungeon_exit_verified'])
    def route(suffix,extra):
        nonlocal current,family
        cap=read(family+'/'+current,'capture.json');trial='sms-npc-d5-'+suffix;name='sms-'+trial
        if not (ROOT/'validation'/ROUTE/name).exists():
            invoke('assisted_boss_route.py',['--boss-room','0x163','--world-route','--sms',
                '--assisted-prefix','--prefix-combat' if family==COMBAT else '--prefix-service',current,
                '--axe-terrain','--rope-terrain','--live-room-replan','--frames',str(cap['frames']+18000),
                '--trial',trial,*extra],'d5-'+suffix)
        checked(ROUTE,name,lambda r:r['reached_entrance']);current=name;family=ROUTE
    route('golda1-entry01',['--house-outside','0xa1','--house-target','0x3f','--fight-for-entrance'])
    name='sms-npc-gold-a1-gift01'
    if not (ROOT/'validation'/SERVICE/name).exists():
        invoke('run_sms_dialogue_observed.py',['natural_house_service','--dialogue-core',
            str(ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_sms_dialogue03_libretro.dll'),
            '--sms','--assisted-prefix','--prefix',current,'--outside','0xa1','--kind','gold',
            '--gold-gain','30','--trial','npc-gold-a1-gift01'],'d5-golda1-gift')
    checked(SERVICE,name,lambda r:r['passed']);current=name;family=SERVICE
    route('merchant94-entry01',['--house-outside','0x94','--house-target','0'])
    name='sms-npc-key94-buy01'
    if not (ROOT/'validation'/SERVICE/name).exists():
        invoke('run_sms_dialogue_observed.py',['sms_merchant_key_purchase','--dialogue-core',
            str(ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_sms_dialogue03_libretro.dll'),
            '--sms','--assisted-prefix','--prefix',current,'--outside','0x94',
            '--trial','npc-key94-buy01'],'d5-key94-buy')
    checked(SERVICE,name,lambda r:r['passed']);current=name;family=SERVICE
    route('healer94-entry01',['--house-outside','0x94','--house-target','0'])
    name='sms-npc-healer94-rest01'
    if not (ROOT/'validation'/SERVICE/name).exists():
        invoke('run_sms_dialogue_observed.py',['natural_free_healer','--dialogue-core',
            str(ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_sms_dialogue03_libretro.dll'),
            '--sms','--assisted-prefix','--prefix',current,'--allow-full-health',
            '--trial','npc-healer94-rest01'],'d5-healer94-rest')
    checked(SERVICE,name,lambda r:r['passed']);current=name;family=SERVICE
    route('return-entry02',['--door-index','5'])
    stage('warp02','earth','0x186,0x176,0x166,0x165,0x155,0x154,0x155,0x165,0x164,0x154,0x153,0x162','0x162',
          ['--earth-room','0x153','--earth-cell','0x44','--earth-cast-x','72','--earth-cast-y','96',
           '--earth-direction','0','--passage-destination','0x162','--earth-during-combat'],lambda r:r['earth_route_passed'])
    stage('contact02','contact','0x162,0x172','0x172',
          ['--contact-room','0x162','--contact-destination','0x172','--mechanism-during-combat'],lambda r:r['contact_route_passed'])
    print('SMS BOOTS, SUPPLIES AND FIFTH DUNGEON CONTACT VERIFIED',flush=True)


if __name__=='__main__':main()
