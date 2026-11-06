"""Extend the living, unassisted D2 fight using shorter input decisions."""
from continue_d2_c0046 import helper,COMMON,frame,finish,ROOT,COMBAT
import json
current='md-auto-c0046-d2-boss01'
report=json.loads((ROOT/'validation'/COMBAT/current/'report.json').read_bytes())
assert report['failure']=='frame_limit' and not report['deaths'] and not report['new_assistance_writes']
helper.run('replay_assisted_prefix.py',['--trace',COMBAT+'/'+current])
helper.assert_canonical(COMBAT,current)
helper.run('unassisted_fast_prediction.py',['--planner','evasive','--planning-step','16',
    '--entry-boss-kind','0x63','--continuation',current,*COMMON,'--rooms','0x144',
    '--target-room','0x144','--collect-gem','--frames',str(frame(COMBAT,current)+8000),
    '--trial','c0046-d2-boss02'])
current='md-auto-c0046-d2-boss02'
finish(current,lambda r:r['room_cleared'] and not r['new_assistance_writes'])
helper.run('unassisted_fast_prediction.py',['--planner','ordinary','--continuation',current,*COMMON,
    '--rooms','0x144,0x143,0x133,0x132,0x131,0x121,0x120,0x130,0x140,0x150,0x151,0x161,0x171',
    '--target-room','0xd6','--exit-dungeon','--frames',str(frame(COMBAT,current)+18000),
    '--trial','c0046-d2-exit01'])
finish('md-auto-c0046-d2-exit01',lambda r:r['full_dungeon_cleared'] and not r['new_assistance_writes'])
print('C0046 SECOND CRYSTAL AND EXTERIOR RETURN VERIFIED',flush=True)
