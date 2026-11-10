"""Continue the selected SMS NPC route through Earth, canoe and crystal four.

Use ordinary recorded input and inherited/declared approach protection. Stop on
any failed objective or independent replay; never overwrite an existing trial.
"""
import json
import subprocess
import sys
from run_core import ROOT
from assisted_prefix import prefix_writes

ROUTE='natural-dungeon-route'
COMBAT='natural-dungeon-combat'
SERVICE='natural-service-route'
STREAM=None
COMMON=['--sms','--assisted-prefix','--max-deaths','0','--collision-aim',
        '--settle-attacks','--doorway-ranges','--ignore-inactive-actors','--equip-axe',
        '--retry-isolated-foes']


def read(folder,name):return json.loads((ROOT/'validation'/folder/name).read_bytes())


def invoke(tool,args,label):
    log=ROOT/'validation'/('sms-npc-d4-'+label+'.log')
    with log.open('w',encoding='utf-8') as output:
        subprocess.run([sys.executable,str(ROOT/'tools'/tool),*args],cwd=ROOT,
                       stdout=output,stderr=subprocess.STDOUT,check=True)


def checked(family,name,predicate):
    folder=family+'/'+name
    report=read(folder,'route_report.json' if family==ROUTE else 'report.json')
    assert report['failure'] is None and not report.get('deaths',0) and predicate(report),(folder,report)
    cap=read(folder,'capture.json')
    proof=ROOT/'validation'/(folder+f'-assisted-fixed-replay-{cap["frames"]}')/'replay_report.json'
    if not proof.exists():
        if STREAM is not None:STREAM.prove(folder)
        else:invoke('replay_assisted_prefix.py',['--trace',folder],name+'-replay')
    prefix_writes(ROOT/'validation'/folder,cap,True)
    print('VERIFIED',folder,cap['frames'],flush=True)


def main():
    current='sms-npc-earth-learn01';family=SERVICE
    cap=read(family+'/'+current,'capture.json')
    prefix_writes(ROOT/'validation'/family/current,cap,True)
    report=read(family+'/'+current,'report.json')
    assert report['passed'] and report['last_state']['level']==1
    trial='sms-npc-d4-entry01';name='sms-'+trial
    if not (ROOT/'validation'/ROUTE/name).exists():
        invoke('assisted_boss_route.py',['--world-route','--boss-room','0x180',
            '--sms','--assisted-prefix','--prefix-service',current,'--door-index','4',
            '--axe-terrain','--rope-terrain','--live-room-replan',
            '--frames',str(cap['frames']+18000),'--trial',trial],'entry')
    checked(ROUTE,name,lambda r:r['reached_entrance'])
    current=name;family=ROUTE
    def stage(suffix,planner,rooms,target,extra,predicate):
        nonlocal current,family
        cap=read(family+'/'+current,'capture.json')
        trial='sms-npc-d4-'+suffix;name='sms-auto-'+trial
        if not (ROOT/'validation'/COMBAT/name).exists():
            invoke('assisted_boss_route.py',['--boss-room','0x180','--planner',planner,*COMMON,
                '--prefix' if family==ROUTE else '--continuation',current,
                '--rooms',rooms,'--target-room',target,'--frames',str(cap['frames']+18000),
                '--trial',trial,*extra],suffix)
        checked(COMBAT,name,predicate)
        current=name;family=COMBAT
    stage('key01','ordinary','0x1f0,0x1f1','0x1f1',['--collect-key'],lambda r:r['new_key_verified'])
    stage('earth01','earth','0x1f1,0x1e1,0x1d1','0x1d1',
          ['--earth-room','0x1e1','--earth-cell','0x58','--earth-cast-x','136','--earth-cast-y','112',
           '--earth-direction','0','--passage-destination','0x1d1'],lambda r:r['earth_route_passed'])
    stage('a1-key02','ordinary','0x1d1,0x1d0,0x1c0,0x1b0,0x1b1,0x1a1','0x1a1',
          ['--collect-key','--defer-puzzles-rooms','0x1b0','--isolated-retry-limit','6',
           '--rush-rooms','0x1c0'],lambda r:r['new_key_verified'])
    stage('canoe01','item','0x1a1,0x1b1,0x1b2,0x1a2','0x1a2',
          ['--collect-item','12','--collect-item-value','1'],lambda r:r['item_acquisition_passed'])
    stage('warp01','earth','0x1a2,0x1a3,0x192','0x192',
          ['--earth-room','0x1a3','--earth-cell','0x5c','--earth-cast-x','200','--earth-cast-y','112',
           '--earth-direction','0','--passage-destination','0x192'],lambda r:r['earth_route_passed'])
    stage('boss-key01','ordinary','0x192,0x182','0x182',['--collect-key'],lambda r:r['new_key_verified'])
    stage('pre-boss01','ordinary','0x182,0x192,0x191,0x190','0x190',
          ['--reach-room'],lambda r:r['target_room_reached'])
    cap=read(COMBAT+'/'+current,'capture.json');trial='sms-npc-d4-boss01';name='sms-auto-'+trial
    if not (ROOT/'validation'/COMBAT/name).exists():
        invoke('assisted_boss_coarse_route.py',['--planning-step','16','--moving-health-premium','40',
            '--boss-room','0x180','--planner','evasive','--boss-frames','4000',*COMMON,
            '--continuation',current,'--rooms','0x190,0x180','--target-room','0x180',
            '--rush-rooms','0x190','--collect-gem','--expected-gem-capacity','64',
            '--frames',str(cap['frames']+18000),'--trial',trial],'boss')
    first=read(COMBAT+'/'+name,'report.json')
    if not first['room_cleared']:
        assert first['failure']=='frame_limit' and first['last_state']['health']>0
        partial=COMBAT+'/'+name;cap=read(partial,'capture.json')
        proof=ROOT/'validation'/(partial+f'-assisted-fixed-replay-{cap["frames"]}')/'replay_report.json'
        if not proof.exists():invoke('replay_assisted_prefix.py',['--trace',partial],name+'-replay')
        prefix_writes(ROOT/'validation'/partial,cap,True)
        current=name;trial='sms-npc-d4-boss02';name='sms-auto-'+trial
        if not (ROOT/'validation'/COMBAT/name).exists():
            invoke('assisted_boss_coarse_route.py',['--planning-step','32','--planning-horizon','192',
                '--moving-health-premium','40','--boss-room','0x180','--planner','evasive',
                '--boss-frames','5000',*COMMON,'--continuation',current,'--rooms','0x180',
                '--target-room','0x180','--collect-gem','--expected-gem-capacity','64',
                '--frames',str(cap['frames']+18000),'--trial',trial],'boss02')
    checked(COMBAT,name,lambda r:r['room_cleared'] and r['last_state']['max_health']==64)
    current=name;cap=read(COMBAT+'/'+current,'capture.json');trial='sms-npc-d4-exit03';name='sms-auto-'+trial
    if not (ROOT/'validation'/COMBAT/name).exists():
        invoke('natural_dungeon_combat.py',[*COMMON,'--continuation',current,
            '--rooms','0x180,0x190,0x191,0x192,0x1a3,0x1a2,0x1b2,0x1b1,0x1b0,0x1c0,0x1d0,0x1d1,0x1e1,0x1f1,0x1f0',
            '--target-room','0x10','--exit-dungeon','--rush-rooms','0x190,0x1c0',
            '--cross-hazard-rooms','0x190,0x1c0','--defer-puzzles-rooms','0x1b0',
            '--frames',str(cap['frames']+18000),'--trial',trial],'exit03')
    checked(COMBAT,name,lambda r:r['full_dungeon_cleared'])
    print('FOURTH SMS CRYSTAL AND EXTERIOR RETURN VERIFIED',flush=True)


if __name__=='__main__':main()
