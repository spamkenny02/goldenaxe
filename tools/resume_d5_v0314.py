"""Retire approach aid before D5; fight actual satellites and return outside."""
import json,shutil
import continue_d8_entry_v0312 as helper
from continue_after_d1_v0314 import ROM
from continue_d8_entry_v0312 import ROOT,COMBAT,report,assert_canonical
from archive_lossless_evidence import sha
from cold_replay_stream import ReplayStream
helper.EVIDENCE=ROOT/'validation/v0314-d5-finish-sources02'
COMMON=['--assisted-prefix','--max-deaths','0','--collision-aim','--settle-attacks','--doorway-ranges','--ignore-inactive-actors','--equip-basic','--retry-isolated-foes']
def frame(n):return report(ROOT/'validation'/COMBAT/n,'capture.json')['frames']
def main():
    prior=report(ROOT/'analysis','d5_supplies_v0314_report.json')
    assert prior['passed'] and not prior['fifth_boss_entered'] and prior['md_sha256']==ROM==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    current=prior['ready_trace'].split('/')[-1];assert_canonical(COMBAT,current)
    helper.EVIDENCE.mkdir(exist_ok=False);index={}
    for name in ('resume_d5_v0314.py','unassisted_satellite_arrival.py','continue_d8_entry_v0312.py','assisted_boss_route.py','assisted_prefix.py','natural_dungeon_combat.py','close_assisted_approach.py','unassisted_satellite_boss.py','unassisted_fast_prediction.py','unassisted_dungeon_continuation.py','natural_boss_evasive_planner.py','natural_contact_passage.py','natural_exit_planner.py','natural_combat_beam.py','prediction_video_skip.py','cold_replay_stream.py','run_core.py'):
        shutil.copyfile(ROOT/'tools'/name,helper.EVIDENCE/name);index['tools/'+name]=sha((helper.EVIDENCE/name).read_bytes())
    (helper.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\n')
    stream=ReplayStream(helper.EVIDENCE/'cold-stream')
    def finish(check):
        r=report(ROOT/'validation'/COMBAT/current,'report.json')
        assert r['failure'] is None and not r.get('deaths',0) and check(r),r
        stream.prove(COMBAT+'/'+current);assert_canonical(COMBAT,current)
    try:
        current='md-auto-v0314-d5-release01';assert_canonical(COMBAT,current)
        helper.run('unassisted_satellite_arrival.py',['--planner','evasive','--planning-step','32','--entry-boss-kind','0x65','--continuation',current,*COMMON,'--rooms','0x173,0x163','--target-room','0x163','--collect-gem','--frames',str(frame(current)+16000),'--trial','v0314-d5-boss02'])
        current='md-auto-v0314-d5-boss02';finish(lambda r:r['room_cleared'] and r['last_state']['max_health']==72 and not r['last_state']['reward_active'] and not r['new_assistance_writes'])
        helper.run('unassisted_fast_prediction.py',['--planner','contact','--continuation',current,*COMMON,'--rooms','0x163,0x173,0x174','--target-room','0x174','--contact-room','0x173','--contact-destination','0x174','--frames',str(frame(current)+10000),'--trial','v0314-d5-return-contact02'])
        current='md-auto-v0314-d5-return-contact02';finish(lambda r:r['contact_route_passed'] and not r['new_assistance_writes'])
        helper.run('unassisted_fast_prediction.py',['--planner','exit','--planning-step','32','--continuation',current,*COMMON,'--rooms','0x174,0x155,0x165,0x166,0x176,0x186','--target-room','0x49','--exit-dungeon','--frames',str(frame(current)+16000),'--trial','v0314-d5-exit02'])
        current='md-auto-v0314-d5-exit02';finish(lambda r:r['full_dungeon_cleared'] and not r['new_assistance_writes'])
        print('V314 FIFTH CRYSTAL AND EXTERIOR RETURN VERIFIED',flush=True)
    finally:stream.close()
if __name__=='__main__':main()
