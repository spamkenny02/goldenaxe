"""Release approach aid before D6 and fight the source64 boss normally."""
import json,shutil
import continue_d8_entry_v0312 as helper
from continue_after_d1_v0317 import ROM
from continue_d8_entry_v0312 import ROOT,COMBAT,report,assert_canonical
from archive_lossless_evidence import sha
from cold_replay_stream import ReplayStream
helper.EVIDENCE=ROOT/'validation/v0317-d6-finish-sources'
COMMON=['--assisted-prefix','--max-deaths','0','--collision-aim','--settle-attacks','--doorway-ranges','--ignore-inactive-actors','--equip-axe','--retry-isolated-foes']
def frame(n):return report(ROOT/'validation'/COMBAT/n,'capture.json')['frames']
def main():
    prior=report(ROOT/'analysis','d6_progress_v0317_report.json')
    assert prior['passed'] and not prior['sixth_boss_entered'] and prior['ice_bell_acquired'] and prior['md_sha256']==ROM==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    current=prior['ready_trace'].split('/')[-1];assert_canonical(COMBAT,current)
    helper.EVIDENCE.mkdir(exist_ok=False);index={}
    for name in ('finish_d6_v0317.py','unassisted_stance_prediction.py','unassisted_arrival_prediction.py','continue_d8_entry_v0312.py','assisted_boss_route.py','assisted_prefix.py','natural_dungeon_combat.py','close_assisted_approach.py','unassisted_fast_prediction.py','unassisted_dungeon_continuation.py','natural_boss_evasive_planner.py','natural_contact_passage.py','natural_exit_planner.py','natural_combat_beam.py','prediction_video_skip.py','cold_replay_stream.py','run_core.py'):
        shutil.copyfile(ROOT/'tools'/name,helper.EVIDENCE/name);index['tools/'+name]=sha((helper.EVIDENCE/name).read_bytes())
    (helper.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\n')
    stream=ReplayStream(helper.EVIDENCE/'cold-stream')
    def finish(check):
        r=report(ROOT/'validation'/COMBAT/current,'report.json')
        assert r['failure'] is None and not r.get('deaths',0) and check(r),r
        stream.prove(COMBAT+'/'+current);assert_canonical(COMBAT,current)
    try:
        helper.run('close_assisted_approach.py',['--trace',COMBAT+'/'+current,'--before-room','0x115','--allow-live-approach','--trial','v0317-d6-release01'])
        current='md-auto-v0317-d6-release01';finish(lambda r:r['passed'])
        helper.run('unassisted_stance_prediction.py',['--planner','evasive','--planning-step','32','--entry-boss-kind','0x64','--continuation',current,*COMMON,'--rooms','0x125,0x115','--target-room','0x115','--collect-gem','--frames',str(frame(current)+16000),'--trial','v0317-d6-boss01'])
        current='md-auto-v0317-d6-boss01';finish(lambda r:r['room_cleared'] and r['last_state']['max_health']==80 and not r['last_state']['reward_active'] and not r['new_assistance_writes'])
        helper.run('unassisted_fast_prediction.py',['--planner','exit','--planning-step','8','--continuation',current,*COMMON,'--rooms','0x115,0x125,0x124,0x123,0x113,0x114,0x138,0x169,0x168,0x178,0x177,0x187','--target-room','0x8b','--exit-dungeon','--frames',str(frame(current)+16000),'--trial','v0317-d6-exit01'])
        current='md-auto-v0317-d6-exit01';finish(lambda r:r['full_dungeon_cleared'] and not r['new_assistance_writes'])
        print('V317 SIXTH CRYSTAL AND EXTERIOR RETURN VERIFIED',flush=True)
    finally:stream.close()
if __name__=='__main__':main()
