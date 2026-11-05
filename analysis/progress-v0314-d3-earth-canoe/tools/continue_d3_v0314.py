"""Play D3 from the verified oil gift, including actual rope and unguarded boss."""
import json,shutil
import continue_d8_entry_v0312 as helper
from continue_after_d1_v0314 import ROM
from continue_d8_entry_v0312 import ROOT,COMBAT,ROUTE,SERVICE,report,assert_canonical
from archive_lossless_evidence import sha

helper.EVIDENCE=ROOT/'validation/v0314-d3-sources02'
COMMON=['--assisted-prefix','--max-deaths','0','--collision-aim','--settle-attacks',
        '--doorway-ranges','--ignore-inactive-actors','--equip-axe']


def frame(family,name):return report(ROOT/'validation'/family/name,'capture.json')['frames']


def finish(family,name,check):
    r=report(ROOT/'validation'/family/name,'route_report.json' if family==ROUTE else 'report.json')
    assert r['failure'] is None and not r.get('deaths',0) and check(r),r
    helper.run('replay_assisted_prefix.py',['--trace',family+'/'+name]);assert_canonical(family,name)


def main():
    prior=report(ROOT/'analysis','oil_service_v0314_report.json')
    assert prior['passed'] and prior['real_oil_gift'] and prior['md_sha256']==ROM==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    current='md-v0314-oil-service01';assert_canonical(SERVICE,current)
    helper.EVIDENCE.mkdir(exist_ok=False);index={}
    for name in ('continue_d3_v0314.py','continue_d8_entry_v0312.py','assisted_boss_route.py',
                 'assisted_prefix.py','natural_dungeon_route.py','natural_dungeon_combat.py',
                 'natural_item_acquisition.py','natural_contact_passage.py','close_assisted_approach.py',
                 'unassisted_fast_prediction.py','unassisted_dungeon_continuation.py',
                 'natural_boss_evasive_planner.py','natural_exit_planner.py','prediction_video_skip.py',
                 'natural_combat_beam.py','replay_assisted_prefix.py'):
        shutil.copyfile(ROOT/'tools'/name,helper.EVIDENCE/name)
        index['tools/'+name]=sha((helper.EVIDENCE/name).read_bytes())
    (helper.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\n',encoding='utf-8')
    # The preceding world excursion declared a still-unreached future target.
    # Its bookkeeping is corrected at the first dungeon stage; no game state or extra episode is imported.
    helper.run('assisted_boss_route.py',['--boss-room','0x195',
        '--world-route','--preserve-floor-hurt','--assisted-prefix','--prefix-service',current,
        '--door-index','3','--axe-terrain','--live-prefix-terrain','--live-room-replan',
        '--frames',str(frame(SERVICE,current)+14000),'--trial','v0314-d3-entry01'])
    current='md-v0314-d3-entry01';finish(ROUTE,current,lambda r:r['reached_entrance'])
    def stage(suffix,planner,rooms,target,extra,check,entry=False):
        nonlocal current
        trial='v0314-d3-'+suffix
        helper.run('assisted_boss_route.py',['--boss-room','0x1c3','--preserve-floor-hurt',
            '--planner',planner,*COMMON,*(['--retarget-pending-boss'] if entry else []),'--prefix' if entry else '--continuation',current,
            '--rooms',rooms,'--target-room',target,'--frames',str(frame(ROUTE if entry else COMBAT,current)+16000),
            '--trial',trial,*extra])
        current='md-auto-'+trial;finish(COMBAT,current,check)
    stage('rope01','item','0x1f8,0x1f7,0x1e7,0x1e2,0x1f2,0x1f3,0x1f4','0x1f4',
          ['--collect-item','13','--collect-item-value','1'],lambda r:r['item_acquisition_passed'],entry=True)
    stage('switch01','contact','0x1f4,0x1f3,0x1e3','0x1e3',
          ['--mechanism-during-combat','--contact-room','0x1e3','--contact-destination','0x1e3'],
          lambda r:r['contact_route_passed'])
    stage('key01','ordinary','0x1e3,0x1f3,0x1f2,0x1e2,0x1d2','0x1d2',
          ['--collect-key','--rush-rooms','0x1e3'],lambda r:r['new_key_verified'])
    stage('pre-boss01','ordinary','0x1d2,0x1e2,0x1e3,0x1d3','0x1d3',
          ['--rush-rooms','0x1e3'],lambda r:r['room_cleared'])
    helper.run('close_assisted_approach.py',['--trace',COMBAT+'/'+current,
        '--before-room','0x1c3','--trial','v0314-d3-release01'])
    current='md-auto-v0314-d3-release01';finish(COMBAT,current,lambda r:r['passed'])
    helper.run('unassisted_fast_prediction.py',['--planner','evasive','--planning-step','16',
        '--entry-boss-kind','0x69','--continuation',current,*COMMON,'--rooms','0x1d3,0x1c3',
        '--target-room','0x1c3','--collect-gem','--frames',str(frame(COMBAT,current)+12000),
        '--trial','v0314-d3-boss01'])
    current='md-auto-v0314-d3-boss01'
    finish(COMBAT,current,lambda r:r['room_cleared'] and r['last_state']['max_health']==56 and not r['last_state']['reward_active'] and not r['new_assistance_writes'])
    helper.run('unassisted_fast_prediction.py',['--planner','exit','--planning-step','32',
        '--continuation',current,*COMMON,'--rooms','0x1c3,0x1d3,0x1e3,0x1e2,0x1e7,0x1f7,0x1f8',
        '--target-room','0x62','--exit-dungeon','--frames',str(frame(COMBAT,current)+16000),
        '--trial','v0314-d3-exit01'])
    finish(COMBAT,'md-auto-v0314-d3-exit01',lambda r:r['full_dungeon_cleared'] and not r['new_assistance_writes'])
    print('V314 ROPE, THIRD CRYSTAL AND EXTERIOR RETURN VERIFIED',flush=True)


if __name__=='__main__':main()
