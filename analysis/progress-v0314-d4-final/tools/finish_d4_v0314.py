"""Reach D4's pre-room without clearing persistent zero-HP hazards, then fight."""
import json,shutil
import continue_d8_entry_v0312 as helper
from continue_after_d1_v0314 import ROM
from continue_d8_entry_v0312 import ROOT,COMBAT,report,assert_canonical
from archive_lossless_evidence import sha

helper.EVIDENCE=ROOT/'validation/v0314-d4-finish-sources02'
COMMON=['--assisted-prefix','--max-deaths','0','--collision-aim','--settle-attacks',
        '--doorway-ranges','--ignore-inactive-actors','--equip-axe','--retry-isolated-foes']


def frame(name):return report(ROOT/'validation'/COMBAT/name,'capture.json')['frames']


def finish(name,check):
    r=report(ROOT/'validation'/COMBAT/name,'report.json')
    assert r['failure'] is None and not r.get('deaths',0) and check(r),r
    helper.run('replay_assisted_prefix.py',['--trace',COMBAT+'/'+name]);assert_canonical(COMBAT,name)


def main():
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==ROM
    current='md-auto-v0314-d4-boss-key01';assert_canonical(COMBAT,current)
    prior=report(ROOT/'validation'/COMBAT/current,'report.json')
    assert prior['failure'] is None and prior['new_key_verified'] and prior['last_state']['canoe']==1
    helper.EVIDENCE.mkdir(exist_ok=False);index={}
    for name in ('finish_d4_v0314.py','continue_d8_entry_v0312.py','assisted_boss_route.py',
                 'assisted_prefix.py','natural_dungeon_combat.py','close_assisted_approach.py',
                 'unassisted_fast_prediction.py','unassisted_dungeon_continuation.py',
                 'natural_boss_evasive_planner.py','natural_exit_planner.py','prediction_video_skip.py',
                 'natural_combat_beam.py','replay_assisted_prefix.py'):
        shutil.copyfile(ROOT/'tools'/name,helper.EVIDENCE/name)
        index['tools/'+name]=sha((helper.EVIDENCE/name).read_bytes())
    (helper.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\n',encoding='utf-8')
    helper.run('assisted_boss_route.py',['--boss-room','0x180','--preserve-floor-hurt',
        '--planner','ordinary',*COMMON,'--continuation',current,'--rooms','0x182,0x192,0x191,0x190',
        '--target-room','0x190','--reach-room',
        '--frames',str(frame(current)+12000),'--trial','v0314-d4-pre-boss03'])
    current='md-auto-v0314-d4-pre-boss03'
    finish(current,lambda r:r['target_room_reached'] and r['last_state']['room']==0x190)
    helper.run('close_assisted_approach.py',['--trace',COMBAT+'/'+current,'--before-room','0x180',
        '--trial','v0314-d4-release01'])
    current='md-auto-v0314-d4-release01';finish(current,lambda r:r['passed'])
    helper.run('unassisted_fast_prediction.py',['--planner','evasive','--planning-step','16',
        '--entry-boss-kind','0x6a','--continuation',current,*COMMON,'--rooms','0x190,0x180',
        '--target-room','0x180','--rush-rooms','0x190','--collect-gem',
        '--frames',str(frame(current)+14000),'--trial','v0314-d4-boss01'])
    current='md-auto-v0314-d4-boss01'
    finish(current,lambda r:r['room_cleared'] and r['last_state']['max_health']==64 and not r['last_state']['reward_active'] and not r['new_assistance_writes'])
    helper.run('unassisted_fast_prediction.py',['--planner','exit','--planning-step','32',
        '--continuation',current,*COMMON,'--rooms','0x180,0x190,0x191,0x192,0x1a3,0x1a2,0x1b2,0x1b1,0x1b0,0x1c0,0x1d0,0x1d1,0x1e1,0x1f1,0x1f0',
        '--target-room','0x10','--exit-dungeon','--frames',str(frame(current)+18000),
        '--trial','v0314-d4-exit01'])
    finish('md-auto-v0314-d4-exit01',lambda r:r['full_dungeon_cleared'] and not r['new_assistance_writes'])
    print('V314 FOURTH CRYSTAL AND EXTERIOR RETURN VERIFIED',flush=True)


if __name__=='__main__':main()
