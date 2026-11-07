"""Use real Earth casts and keys to obtain the canoe and fourth crystal."""
import json,shutil
import continue_d8_entry_v0312 as helper
from continue_after_d1_c0046 import ROM
from continue_d8_entry_v0312 import ROOT,COMBAT,ROUTE,SERVICE,report,assert_canonical
from archive_lossless_evidence import sha
from campaign_stream_replay import streamed_replays

helper.EVIDENCE=ROOT/'validation/c0046-d4-sources'
COMMON=['--assisted-prefix','--max-deaths','0','--collision-aim','--settle-attacks',
        '--doorway-ranges','--ignore-inactive-actors','--equip-axe','--retry-isolated-foes']


def frame(family,name):return report(ROOT/'validation'/family/name,'capture.json')['frames']


def finish(family,name,check):
    r=report(ROOT/'validation'/family/name,'route_report.json' if family==ROUTE else 'report.json')
    assert r['failure'] is None and not r.get('deaths',0) and check(r),r
    helper.run('replay_assisted_prefix.py',['--trace',family+'/'+name]);assert_canonical(family,name)


def main():
    prior=report(ROOT/'analysis','earth_learning_c0046_report.json')
    assert prior['passed'] and prior['earth_level']==1 and prior['magic_capacity']==48
    assert prior['md_sha256']==ROM==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    current='md-c0046-earth-learn01';assert_canonical(SERVICE,current)
    helper.EVIDENCE.mkdir(exist_ok=False);index={}
    for name in ('continue_d4_c0046.py','continue_d8_entry_v0312.py','campaign_stream_replay.py','cold_replay_stream.py','assisted_boss_route.py',
                 'assisted_prefix.py','natural_dungeon_route.py','natural_dungeon_combat.py',
                 'natural_item_acquisition.py','natural_earth_passage.py','close_assisted_approach.py',
                 'unassisted_fast_prediction.py','unassisted_dungeon_continuation.py',
                 'natural_boss_evasive_planner.py','natural_exit_planner.py','prediction_video_skip.py',
                 'natural_combat_beam.py','replay_assisted_prefix.py'):
        shutil.copyfile(ROOT/'tools'/name,helper.EVIDENCE/name)
        index['tools/'+name]=sha((helper.EVIDENCE/name).read_bytes())
    (helper.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\n',encoding='utf-8')
    helper.run('assisted_boss_route.py',['--boss-room','0x180','--world-route','--preserve-floor-hurt',
        '--assisted-prefix','--prefix-service',current,'--door-index','4','--axe-terrain','--rope-terrain',
        '--live-prefix-terrain','--live-room-replan','--frames',str(frame(SERVICE,current)+18000),
        '--trial','c0046-d4-entry01'])
    current='md-c0046-d4-entry01';finish(ROUTE,current,lambda r:r['reached_entrance'])
    def step(suffix,planner,rooms,target,extra,check,entry=False):
        nonlocal current
        trial='c0046-d4-'+suffix
        helper.run('assisted_boss_route.py',['--boss-room','0x180','--preserve-floor-hurt',
            '--planner',planner,*COMMON,'--prefix' if entry else '--continuation',current,
            '--rooms',rooms,'--target-room',target,'--frames',str(frame(ROUTE if entry else COMBAT,current)+18000),
            '--trial',trial,*extra])
        current='md-auto-'+trial;finish(COMBAT,current,check)
    step('key01','ordinary','0x1f0,0x1f1','0x1f1',['--collect-key'],lambda r:r['new_key_verified'],entry=True)
    step('earth01','earth','0x1f1,0x1e1,0x1d1','0x1d1',
         ['--earth-room','0x1e1','--earth-cell','0x58','--earth-cast-x','136','--earth-cast-y','112',
          '--earth-direction','0','--passage-destination','0x1d1'],lambda r:r['earth_route_passed'])
    step('a1-key01','ordinary','0x1d1,0x1d0,0x1c0,0x1b0,0x1b1,0x1a1','0x1a1',
         ['--collect-key','--defer-puzzles-rooms','0x1b0','--isolated-retry-limit','6'],lambda r:r['new_key_verified'])
    step('canoe01','item','0x1a1,0x1b1,0x1b2,0x1a2','0x1a2',
         ['--collect-item','12','--collect-item-value','1'],lambda r:r['item_acquisition_passed'])
    step('warp01','earth','0x1a2,0x1a3,0x192','0x192',
         ['--earth-room','0x1a3','--earth-cell','0x5c','--earth-cast-x','200','--earth-cast-y','112',
          '--earth-direction','0','--passage-destination','0x192'],lambda r:r['earth_route_passed'])
    step('boss-key01','ordinary','0x192,0x182','0x182',['--collect-key'],lambda r:r['new_key_verified'])
    # Source zero-HP hazards persist in190. Reach it normally; the separate
    # release audit still forbids any live positive-HP enemy before the boss.
    step('pre-boss01','ordinary','0x182,0x192,0x191,0x190','0x190',
         ['--reach-room'],lambda r:r['target_room_reached'] and r['last_state']['room']==0x190)
    helper.run('close_assisted_approach.py',['--trace',COMBAT+'/'+current,'--before-room','0x180',
        '--trial','c0046-d4-release01'])
    current='md-auto-c0046-d4-release01';finish(COMBAT,current,lambda r:r['passed'])
    helper.run('unassisted_fast_prediction.py',['--planner','evasive','--planning-step','16',
        '--entry-boss-kind','0x6a','--continuation',current,*COMMON,'--rooms','0x190,0x180',
        '--target-room','0x180','--rush-rooms','0x190','--collect-gem','--frames',str(frame(COMBAT,current)+14000),
        '--trial','c0046-d4-boss01'])
    current='md-auto-c0046-d4-boss01'
    finish(COMBAT,current,lambda r:r['room_cleared'] and r['last_state']['max_health']==64 and not r['last_state']['reward_active'] and not r['new_assistance_writes'])
    helper.run('unassisted_fast_prediction.py',['--planner','exit','--planning-step','32',
        '--continuation',current,*COMMON,'--rooms','0x180,0x190,0x191,0x192,0x1a3,0x1a2,0x1b2,0x1b1,0x1b0,0x1c0,0x1d0,0x1d1,0x1e1,0x1f1,0x1f0',
        '--target-room','0x10','--exit-dungeon','--frames',str(frame(COMBAT,current)+18000),
        '--trial','c0046-d4-exit01'])
    finish(COMBAT,'md-auto-c0046-d4-exit01',lambda r:r['full_dungeon_cleared'] and not r['new_assistance_writes'])
    print('V317 CANOE, FOURTH CRYSTAL AND EXTERIOR RETURN VERIFIED',flush=True)


if __name__=='__main__':
    with streamed_replays(helper, ROOT/'validation/c0046-d4-cold-stream'):
        main()
