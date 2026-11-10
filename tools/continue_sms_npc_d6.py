"""Adapt proven map-action proposals to actual SMS inputs, with cold replays."""
import json
import continue_sms_npc_d4 as campaign
from cold_replay_stream import ReplayStream
from run_core import ROOT
from continue_sms_npc_d4 import read,checked,invoke,ROUTE,COMBAT,COMMON


def main():
    current='sms-sms-npc-d6-entry01';family=ROUTE
    checked(family,current,lambda r:r['reached_entrance'])
    recipes=json.loads((ROOT/'tools/recipes/d6-route-v0312.json').read_bytes())
    for i,entry in enumerate(recipes):
        args=entry['arguments'][1:]
        for flag in ['--prefix','--continuation','--trial','--frames']:
            if flag in args:
                n=args.index(flag);del args[n:n+2]
        if '--sms' not in args:args+=['--sms']
        if entry['kind']=='item':args[args.index('--planner')+1]='item'
        cap=read(family+'/'+current,'capture.json');trial=f'sms-npc-d6-stage{i+1:02d}-01';name='sms-auto-'+trial
        args+=['--prefix' if family==ROUTE else '--continuation',current,
               '--frames',str(cap['frames']+18000),'--trial',trial]
        if not (ROOT/'validation'/COMBAT/name).exists():invoke('assisted_boss_route.py',args,f'd6-stage{i+1:02d}')
        key={'key':'new_key_verified','earth':'earth_route_passed','contact':'contact_route_passed',
             'item':'item_acquisition_passed','clear':'room_cleared'}[entry['kind']]
        checked(COMBAT,name,lambda r:r[key]);current=name;family=COMBAT
    cap=read(family+'/'+current,'capture.json');trial='sms-npc-d6-boss02';name='sms-auto-'+trial
    basic=COMMON
    if not (ROOT/'validation'/COMBAT/name).exists():
        invoke('assisted_boss_coarse_route.py',['--planning-step','32','--planning-horizon','96',
            '--short-stance-candidates','--enter-boss-up','--entry-boss-kind','0x64',
            '--boss-room','0x115','--planner','evasive','--boss-frames','8000',*basic,
            '--continuation',current,'--rooms','0x125,0x115','--target-room','0x115',
            '--collect-gem','--expected-gem-capacity','80','--frames',str(cap['frames']+18000),
            '--trial',trial],'d6-boss')
    checked(COMBAT,name,lambda r:r['room_cleared'] and r['last_state']['max_health']==80);current=name
    cap=read(COMBAT+'/'+current,'capture.json');trial='sms-npc-d6-exit02';name='sms-auto-'+trial
    if not (ROOT/'validation'/COMBAT/name).exists():
        invoke('natural_dungeon_combat.py',[*basic,'--continuation',current,
            '--rooms','0x115,0x125,0x124,0x123,0x113,0x114,0x138,0x169,0x168,0x178,0x177,0x187',
            '--rush-rooms','0x125,0x124,0x123,0x113,0x114,0x138,0x169,0x168,0x178,0x177,0x187',
            '--cross-hazard-rooms','0x114,0x138',
            '--target-room','0x8b','--exit-dungeon','--frames',str(cap['frames']+18000),
            '--trial',trial],'d6-exit')
    checked(COMBAT,name,lambda r:r['full_dungeon_cleared'])
    print('SIXTH SMS CRYSTAL AND EXTERIOR RETURN VERIFIED',flush=True)


if __name__=='__main__':
    number=1
    while (ROOT/f'validation/sms-npc-d6-cold-stream{number:02d}').exists():number+=1
    stream=ReplayStream(ROOT/f'validation/sms-npc-d6-cold-stream{number:02d}',sms=True)
    campaign.STREAM=stream
    try:main()
    finally:stream.close()
