"""Resume after one ordinary leave/re-enter solved an isolated D2 foe."""
from continue_d2_c0046 import helper,COMMON,frame,finish,ROOT,COMBAT,ROUTE

current='md-auto-c0046-d2-key202'
finish(current,lambda r:r['new_key_verified'])
for number,rooms,target in [(3,'0x152,0x151,0x150,0x140,0x130,0x120,0x121,0x131','0x131'),
                            (4,'0x131,0x132,0x133,0x143','0x143')]:
    trial='c0046-d2-'+('key301' if number==3 else 'pre-boss01')
    helper.run('assisted_boss_route.py',['--boss-room','0x144','--preserve-floor-hurt',
        '--planner','ordinary',*COMMON,'--continuation',current,'--rooms',rooms,
        '--target-room',target,'--retry-isolated-foes','--wake-sentinels',
        '--frames',str(frame(COMBAT,current)+24000),'--trial',trial,
        *(['--collect-key'] if number==3 else [])])
    current='md-auto-'+trial
    finish(current,lambda r:r['new_key_verified'] if number==3 else r['room_cleared'])
helper.run('close_assisted_approach.py',['--trace',COMBAT+'/'+current,'--before-room','0x144',
    '--trial','c0046-d2-release01'])
current='md-auto-c0046-d2-release01';finish(current,lambda r:r['passed'])
helper.run('unassisted_fast_prediction.py',['--planner','evasive','--planning-step','32',
    '--entry-boss-kind','0x63','--continuation',current,*COMMON,'--rooms','0x143,0x144',
    '--target-room','0x144','--collect-gem','--frames',str(frame(COMBAT,current)+16000),
    '--trial','c0046-d2-boss01'])
current='md-auto-c0046-d2-boss01'
finish(current,lambda r:r['room_cleared'] and not r['new_assistance_writes'])
helper.run('unassisted_fast_prediction.py',['--planner','ordinary','--continuation',current,*COMMON,
    '--rooms','0x144,0x143,0x133,0x132,0x131,0x121,0x120,0x130,0x140,0x150,0x151,0x161,0x171',
    '--target-room','0xd6','--exit-dungeon','--frames',str(frame(COMBAT,current)+18000),
    '--trial','c0046-d2-exit01'])
finish('md-auto-c0046-d2-exit01',lambda r:r['full_dungeon_cleared'] and not r['new_assistance_writes'])
print('C0046 SECOND CRYSTAL AND EXTERIOR RETURN VERIFIED',flush=True)
