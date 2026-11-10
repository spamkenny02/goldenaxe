"""Real gold gifts and second-level magic before the sixth SMS dungeon."""
from run_core import ROOT
from continue_sms_npc_d4 import read,checked,invoke,ROUTE,COMBAT,SERVICE


def main():
    current='sms-npc-d6-equipaxe01';family=SERVICE
    checked(family,current,lambda r:r['passed'])
    first=True
    def route(suffix,outside,target,extra=()):
        nonlocal current,family,first
        cap=read(family+'/'+current,'capture.json');trial='sms-npc-d6-'+suffix;name='sms-'+trial
        args=['--boss-room','0x115','--world-route','--sms','--assisted-prefix',
              '--prefix-service',current,'--axe-terrain','--rope-terrain','--live-room-replan',
              '--frames',str(cap['frames']+18000),'--trial',trial,
              '--house-outside',hex(outside),'--house-target',hex(target),*extra]
        if first:args+=['--new-assistance-episode','--completed-exit-proof',COMBAT+'/sms-auto-sms-npc-d5-exit01']
        if not (ROOT/'validation'/ROUTE/name).exists():invoke('assisted_boss_route.py',args,'d6-'+suffix)
        checked(ROUTE,name,lambda r:r['reached_entrance']);current=name;family=ROUTE;first=False
    def service(suffix,outside,kind,extra):
        nonlocal current,family
        trial='npc-d6-'+suffix;name='sms-'+trial
        if not (ROOT/'validation'/SERVICE/name).exists():
            invoke('run_sms_dialogue_observed.py',['natural_house_service','--dialogue-core',
                str(ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_sms_dialogue03_libretro.dll'),
                '--sms','--assisted-prefix','--prefix',current,'--outside',hex(outside),
                '--kind',kind,'--trial',trial,*extra],'d6-'+suffix)
        checked(SERVICE,name,lambda r:r['passed']);current=name;family=SERVICE
    route('gold7d-entry02',0x7d,0x3f,['--fight-for-entrance'])
    service('gold7d-gift01',0x7d,'gold',['--gold-gain','30'])
    route('golde7-entry01',0xe7,0x3f)
    service('golde7-gift01',0xe7,'gold',['--gold-gain','30'])
    route('gillian2-entry01',0xe6,0xbf)
    service('gillian2-learn01',0xe6,'teacher',['--teacher','0','--expected-level','2'])
    route('battler2-entry01',0xa3,0xbf,['--required-chop','0xa3:0x4a'])
    service('battler2-learn01',0xa3,'teacher',['--teacher','1','--expected-level','2'])
    cap=read(family+'/'+current,'capture.json');trial='sms-npc-d6-entry01';name='sms-'+trial
    if not (ROOT/'validation'/ROUTE/name).exists():
        invoke('assisted_boss_route.py',['--boss-room','0x115','--world-route','--sms',
            '--assisted-prefix','--prefix-service',current,'--axe-terrain','--rope-terrain',
            '--live-room-replan','--door-index','6','--frames',str(cap['frames']+18000),'--trial',trial],'d6-entry')
    checked(ROUTE,name,lambda r:r['reached_entrance'])
    print('SIXTH SMS DUNGEON PREPARATION VERIFIED',flush=True)


if __name__=='__main__':main()
