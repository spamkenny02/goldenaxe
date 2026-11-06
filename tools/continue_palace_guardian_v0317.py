"""Open the remaining palace mechanism, defeat11E and collect Golden Axe2."""
import json,shutil
import continue_d8_entry_v0317 as helper
from continue_after_d9_v0317 import ROM
from continue_d8_entry_v0317 import ROOT,COMBAT,report,assert_canonical
from archive_lossless_evidence import sha

helper.EVIDENCE=ROOT/'validation/v0317-palace-sources'
COMMON=['--assisted-prefix','--max-deaths','0','--collision-aim','--settle-attacks',
        '--doorway-ranges','--ignore-inactive-actors']


def frame(name):return report(ROOT/'validation'/COMBAT/name,'capture.json')['frames']


def finish(name,condition):
    result=report(ROOT/'validation'/COMBAT/name,'report.json')
    assert result['failure'] is None and not result['deaths'] and condition(result),result
    helper.STREAM.prove(COMBAT+'/'+name)
    assert_canonical(COMBAT,name)


def campaign():
    prior=report(ROOT/'analysis','cold_palace_inner_v0317_report.json')
    assert prior['passed'] and prior['cold_palace_inner_mechanisms_verified']
    assert prior['md_sha256']==ROM==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    snapshot=helper.EVIDENCE/'guardian-tools';snapshot.mkdir(exist_ok=False)
    names=('assisted_boss_route.py','assisted_prefix.py','natural_dungeon_combat.py',
           'natural_contact_passage.py','natural_item_acquisition.py',
           'close_assisted_approach.py','resume_after_intermediate.py',
           'unassisted_dungeon_continuation.py','unassisted_fast_prediction.py',
           'prediction_video_skip.py','natural_combat_beam.py','natural_boss_evasive_planner.py',
           'replay_assisted_prefix.py','continue_palace_guardian_v0317.py','continue_d8_entry_v0317.py')
    hashes={}
    for name in names:
        target=snapshot/name;shutil.copyfile(ROOT/'tools'/name,target)
        hashes['tools/'+name]=sha(target.read_bytes())
    (snapshot/'source_index.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
    current=prior['current_campaign_trace'].split('/')[-1]
    def step(suffix,planner,rooms,target,extra,condition):
        nonlocal current
        trial='v0317-cold-palace-'+suffix
        helper.run('assisted_boss_route.py',['--boss-room','0x14c','--preserve-floor-hurt',
            *COMMON,'--retry-isolated-foes','--wake-sentinels','--planner',planner,
            '--continuation',current,'--rooms',rooms,'--target-room',target,
            '--frames',str(frame(current)+18000),'--trial',trial,*extra])
        current='md-auto-'+trial;finish(current,condition)
    step('switch12c01','contact','0x12a,0x11c,0x12c','0x12c',
         ['--equip-basic','--mechanism-during-combat','--contact-room','0x12c','--contact-destination','0x12c'],
         lambda r:r['contact_route_passed'])
    step('pre-guardian01','ordinary','0x12c,0x11c,0x11b,0x12b,0x12c,0x12d,0x12e','0x12e',
         ['--equip-basic','--rush-rooms','0x12c'],lambda r:r['room_cleared'])
    helper.run('close_assisted_approach.py',['--trace',COMBAT+'/'+current,
        '--before-room','0x11e','--trial','v0317-cold-palace-guardian-release01'])
    current='md-auto-v0317-cold-palace-guardian-release01';finish(current,lambda r:r['passed'])
    helper.run('unassisted_fast_prediction.py',['--planner','evasive','--planning-step','32',
        '--entry-boss-kind','0x7c','--continuation',current,'--rooms','0x12e,0x11e',
        '--target-room','0x11e','--equip-basic',*COMMON,'--frames',str(frame(current)+20000),
        '--trial','v0317-cold-palace-guardian01'])
    current='md-auto-v0317-cold-palace-guardian01'
    finish(current,lambda r:r['room_cleared'] and not r['new_assistance_writes'])
    helper.run('resume_after_intermediate.py',['--trace',COMBAT+'/'+current,
        '--boss-room','0x14c','--trial','v0317-cold-palace-resume-final01'])
    current='md-auto-v0317-cold-palace-resume-final01';finish(current,lambda r:r['passed'])
    step('goldenaxe01','item','0x11e,0x11d','0x11d',
         ['--equip-axe','--collect-item','1','--collect-item-value','2'],lambda r:r['item_acquisition_passed'])
    print('V317 GOLDEN AXE GUARDIAN AND ACQUISITION VERIFIED',flush=True)


def main():
    from cold_replay_stream import ReplayStream
    helper.EVIDENCE.mkdir(exist_ok=True)
    helper.STREAM=ReplayStream(helper.EVIDENCE/'guardian-cold-stream')
    try:campaign()
    finally:helper.STREAM.close()


if __name__=='__main__':main()
