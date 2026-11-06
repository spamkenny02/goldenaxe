"""Collect the skipped real second key before the first c0046 boss."""
from pathlib import Path
bootstrap=Path(__file__).with_name('run_d1.py')
exec(compile(bootstrap.read_text().split("current=replay('md-'+region+'-c46-d1-key01'")[0],str(bootstrap),'exec'))
current='md-'+region+'-c46-d1-ready01'
run('assisted_boss_route.py',region_args+['--boss-room','0x175','--planner','ordinary',
    *common,'--continuation',current,'--rooms','0x185,0x184,0x194,0x193',
    '--target-room','0x193','--collect-key','--retry-isolated-foes','--frames','40000','--trial','c46-d1-key2-01'])
current=replay('md-'+region+'-c46-d1-key2-01',lambda r:r['new_key_verified'])
run('assisted_boss_route.py',region_args+['--boss-room','0x175','--planner','ordinary',
    *common,'--continuation',current,'--rooms','0x193,0x194,0x184,0x185',
    '--target-room','0x185','--frames','46000','--trial','c46-d1-ready02'])
current=replay('md-'+region+'-c46-d1-ready02',lambda r:r['room_cleared'] and r['last_state']['keys']>=1)
run('close_assisted_approach.py',['--trace',family+'/'+current,'--before-room','0x175',
    '--trial','c46-'+region+'-d1-release02'])
current=replay('md-auto-c46-'+region+'-d1-release02',lambda r:r['last_state']['hurt']==0)
run('unassisted_fast_prediction.py',region_args+common+['--planner','evasive','--planning-step','16',
    '--entry-boss-kind','0x68','--continuation',current,'--rooms','0x185,0x175',
    '--target-room','0x175','--collect-gem','--frames','60000','--trial','c46-d1-boss02'])
current=replay('md-'+region+'-c46-d1-boss02',lambda r:r['room_cleared'] and not r['new_assistance_writes'])
run('unassisted_dungeon_continuation.py',region_args+common+['--planner','ordinary',
    '--continuation',current,'--rooms',
    '0x175,0x185,0x184,0x194,0x1a4,0x1a5,0x1b5,0x1b4,0x1c4,0x1d4,0x1e4',
    '--target-room','0xb9','--exit-dungeon','--frames','70000','--trial','c46-d1-exit02'])
current=replay('md-'+region+'-c46-d1-exit02',lambda r:r['dungeon_exit_verified'] and not r['new_assistance_writes'])
print('C0046 FIRST CRYSTAL AND EXTERIOR VERIFIED',region,current,flush=True)
