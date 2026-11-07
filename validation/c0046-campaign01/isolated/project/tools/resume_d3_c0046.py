"""Continue D3 after avoiding the unintended return portal on the rope route."""
import json,shutil
import continue_d3_c0046 as original
from continue_d3_c0046 import helper,ROOT,COMBAT,ROUTE,SERVICE,frame,finish,COMMON
from archive_lossless_evidence import sha
helper.EVIDENCE=ROOT/'validation/c0046-d3-sources03'
helper.EVIDENCE.mkdir(exist_ok=False)
index={}
for name in ['resume_d3_c0046.py','continue_d3_c0046.py','continue_d8_entry_v0312.py',
             'assisted_boss_route.py','assisted_prefix.py','natural_dungeon_combat.py',
             'natural_item_acquisition.py','natural_contact_passage.py','close_assisted_approach.py',
             'unassisted_fast_prediction.py','unassisted_dungeon_continuation.py',
             'natural_exit_planner.py','prediction_video_skip.py','replay_assisted_prefix.py']:
    shutil.copyfile(ROOT/'tools'/name,helper.EVIDENCE/name)
    index['tools/'+name]=sha((helper.EVIDENCE/name).read_bytes())
(helper.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\n')
current='md-auto-c0046-d3-rope03'
finish(COMBAT,current,lambda r:r['item_acquisition_passed'] and not r['item_acquisition_state_writes'])
def stage(suffix,planner,rooms,target,extra,check):
    global current
    trial='c0046-d3-'+suffix
    helper.run('assisted_boss_route.py',['--boss-room','0x1c3','--preserve-floor-hurt',
        '--planner',planner,*COMMON,'--retry-isolated-foes','--wake-sentinels',
        '--continuation',current,'--rooms',rooms,'--target-room',target,
        '--frames',str(frame(COMBAT,current)+16000),'--trial',trial,*extra])
    current='md-auto-'+trial;finish(COMBAT,current,check)
stage('switch01','contact','0x1f4,0x1f3,0x1e3','0x1e3',
    ['--mechanism-during-combat','--contact-room','0x1e3','--contact-destination','0x1e3'],lambda r:r['contact_route_passed'])
stage('key01','ordinary','0x1e3,0x1f3,0x1f2,0x1e2,0x1d2','0x1d2',
    ['--collect-key','--rush-rooms','0x1e3','--avoid-portal-rooms','0x1e2'],lambda r:r['new_key_verified'])
stage('pre-boss01','ordinary','0x1d2,0x1e2,0x1e3,0x1d3','0x1d3',
    ['--rush-rooms','0x1e3','--avoid-portal-rooms','0x1e2'],lambda r:r['room_cleared'])
helper.run('close_assisted_approach.py',['--trace',COMBAT+'/'+current,'--before-room','0x1c3','--trial','c0046-d3-release01'])
current='md-auto-c0046-d3-release01';finish(COMBAT,current,lambda r:r['passed'])
helper.run('unassisted_fast_prediction.py',['--planner','evasive','--planning-step','16',
    '--entry-boss-kind','0x69','--continuation',current,*COMMON,'--rooms','0x1d3,0x1c3',
    '--target-room','0x1c3','--collect-gem','--frames',str(frame(COMBAT,current)+16000),'--trial','c0046-d3-boss01'])
current='md-auto-c0046-d3-boss01'
finish(COMBAT,current,lambda r:r['room_cleared'] and r['last_state']['max_health']==56 and not r['last_state']['reward_active'] and not r['new_assistance_writes'])
helper.run('unassisted_fast_prediction.py',['--planner','exit','--planning-step','32',
    '--continuation',current,*COMMON,'--rooms','0x1c3,0x1d3,0x1e3,0x1e2,0x1e7,0x1f7,0x1f8',
    '--avoid-portal-rooms','0x1e7','--target-room','0x62','--exit-dungeon',
    '--frames',str(frame(COMBAT,current)+16000),'--trial','c0046-d3-exit01'])
finish(COMBAT,'md-auto-c0046-d3-exit01',lambda r:r['full_dungeon_cleared'] and not r['new_assistance_writes'])
print('C0046 ROPE, THIRD CRYSTAL AND EXTERIOR RETURN VERIFIED',flush=True)
