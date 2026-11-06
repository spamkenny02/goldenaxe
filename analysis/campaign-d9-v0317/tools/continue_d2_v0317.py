"""Collect D2 keys, release approach aid before144, fight and return outside."""
import json, shutil
import continue_d8_entry_v0312 as helper
from continue_after_d1_v0317 import ROM
from continue_d8_entry_v0312 import ROOT, COMBAT, ROUTE, report, assert_canonical
from archive_lossless_evidence import sha

helper.EVIDENCE=ROOT/'validation/v0317-d2-sources'
COMMON=['--assisted-prefix','--collision-aim','--settle-attacks',
        '--doorway-ranges','--ignore-inactive-actors','--max-deaths','0','--equip-axe']


def frame(family,name): return report(ROOT/'validation'/family/name,'capture.json')['frames']


def finish(name,condition):
    r=report(ROOT/'validation'/COMBAT/name,'report.json')
    assert r['failure'] is None and not r.get('deaths',0) and condition(r),r
    helper.run('replay_assisted_prefix.py',['--trace',COMBAT+'/'+name])
    assert_canonical(COMBAT,name)


def main():
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==ROM
    current='md-v0317-d2-entry01';assert_canonical(ROUTE,current)
    helper.EVIDENCE.mkdir(exist_ok=False);index={}
    names=('continue_d2_v0317.py','continue_d8_entry_v0312.py','assisted_boss_route.py',
           'assisted_prefix.py','natural_dungeon_combat.py','natural_boss_evasive_planner.py',
           'natural_combat_beam.py','close_assisted_approach.py','unassisted_dungeon_continuation.py',
           'unassisted_fast_prediction.py','prediction_video_skip.py','replay_assisted_prefix.py')
    for name in names:
        shutil.copyfile(ROOT/'tools'/name,helper.EVIDENCE/name)
        index['tools/'+name]=sha((helper.EVIDENCE/name).read_bytes())
    (helper.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\n',encoding='utf-8')
    for number,rooms,target in [(1,'0x171,0x161,0x160','0x160'),
                                (2,'0x160,0x161,0x151,0x152','0x152'),
                                (3,'0x152,0x151,0x150,0x140,0x130,0x120,0x121,0x131','0x131'),
                                (4,'0x131,0x132,0x133,0x143','0x143')]:
        trial='v0317-d2-'+('key'+str(number)+'01' if number<4 else 'pre-boss01')
        helper.run('assisted_boss_route.py',['--boss-room','0x144','--preserve-floor-hurt',
            '--planner','ordinary',*COMMON,'--prefix' if number==1 else '--continuation',current,
            '--rooms',rooms,'--target-room',target,'--frames',str(frame(ROUTE if number==1 else COMBAT,current)+14000),
            '--trial',trial,*(['--collect-key'] if number<4 else [])])
        current='md-auto-'+trial
        finish(current,lambda r:r['new_key_verified'] if number<4 else r['room_cleared'])
    helper.run('close_assisted_approach.py',['--trace',COMBAT+'/'+current,'--before-room','0x144',
        '--trial','v0317-d2-release01'])
    current='md-auto-v0317-d2-release01';finish(current,lambda r:r['passed'])
    helper.run('unassisted_fast_prediction.py',['--planner','evasive','--planning-step','32',
        '--entry-boss-kind','0x63','--continuation',current,*COMMON,'--rooms','0x143,0x144',
        '--target-room','0x144','--frames',str(frame(COMBAT,current)+10000),'--trial','v0317-d2-boss01'])
    current='md-auto-v0317-d2-boss01';finish(current,lambda r:r['room_cleared'] and not r['new_assistance_writes'])
    helper.run('unassisted_fast_prediction.py',['--planner','ordinary','--continuation',current,*COMMON,
        '--rooms','0x144,0x143,0x133,0x132,0x131,0x121,0x120,0x130,0x140,0x150,0x151,0x161,0x171',
        '--target-room','0xd6','--exit-dungeon','--frames',str(frame(COMBAT,current)+18000),
        '--trial','v0317-d2-exit01'])
    finish('md-auto-v0317-d2-exit01',lambda r:r['full_dungeon_cleared'] and not r['new_assistance_writes'])
    print('V317 SECOND CRYSTAL AND EXTERIOR RETURN VERIFIED',flush=True)


if __name__=='__main__':main()
