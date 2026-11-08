"""Continue the canonical PAL palace route from its giant to the credits."""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0,'tools')
import continue_d8_entry_palc0046 as helper
from continue_d8_entry_palc0046 import COMBAT, COMMON, assert_canonical, budget, load, replay, run
from archive_lossless_evidence import sha
from cold_replay_stream import ReplayStream
from run_core import ROOT

work=ROOT/'validation/palc0046-pal-palace-inner-sources'
helper.EVIDENCE=work

def campaign():
    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    audited=json.loads((ROOT/'analysis/palc0046_palace_giant_report.json').read_bytes())
    assert audited['passed'] and audited['giant_defeated'] and audited['rom_sha256']==digest

    checkpoints=ROOT/'validation/palc0046-pal-palace-entry-sources/cold-stream/completed.json'
    proof=json.loads(checkpoints.read_bytes())
    current='md-pal-palc0046-palace-giant01'
    assert proof['passed'] and proof['rom_sha256']==digest and proof['cold_boot_count']==1
    assert proof['checkpoints'][-1]['trace']==COMBAT+'/'+current
    assert proof['checkpoints'][-1]['whole_ram_png_exact']
    assert_canonical(COMBAT,current)
    giant=load(COMBAT,current)
    assert giant['room_cleared'] and not giant['deaths'] and not giant['new_assistance_writes']

    snapshot=work/'sources'
    snapshot.mkdir()
    names=('assisted_boss_route.py','resume_after_intermediate.py',
           'close_assisted_approach.py','unassisted_fast_prediction.py',
           'natural_dungeon_combat.py','natural_earth_passage.py','natural_contact_passage.py',
           'natural_item_acquisition.py','replay_assisted_prefix.py',
           'unassisted_dungeon_continuation.py','continue_recorded_ending.py',
           'continue_palace_inner_c0046.py','continue_palace_guardian_c0046.py',
           'continue_palace_final_c0046.py','recipes/palace-final-v0309.json',
           'continue_d8_entry_palc0046.py','cold_replay_stream.py','continue_pal_palace_inner_c0046.py','run_core.py')
    hashes={}
    for name in names:
        target=snapshot/Path(name).name
        shutil.copyfile(ROOT/'tools'/name,target)
        hashes[name]=sha(target.read_bytes())
    (snapshot/'source_index.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')

    def ordinary(suffix,planner,rooms,target,extra,check,limit=18000):
        nonlocal current
        trial='palc0046-palace-'+suffix
        run('assisted_boss_route.py',['--pal','--boss-room','0x14c','--preserve-floor-hurt',
            *COMMON,'--retry-isolated-foes','--wake-sentinels','--planner',planner,
            '--continuation',current,'--rooms',rooms,'--target-room',target,
            '--frames',budget(COMBAT,current,limit),'--trial',trial,*extra])
        current='md-pal-'+trial
        replay(COMBAT,current,check)

    def resume(suffix):
        nonlocal current
        trial='palc0046-palace-'+suffix
        run('resume_after_intermediate.py',['--trace',COMBAT+'/'+current,
            '--boss-room','0x14c','--trial',trial])
        current='md-auto-'+trial
        replay(COMBAT,current,lambda r:r['resumed_after_verified_intermediate'])

    def release(suffix,room):
        nonlocal current
        trial='palc0046-palace-'+suffix
        run('close_assisted_approach.py',['--trace',COMBAT+'/'+current,
            '--before-room',room,'--trial',trial])
        current='md-auto-'+trial
        replay(COMBAT,current,lambda r:r['last_state']['hurt']==0)

    def fight(suffix,kind,rooms,target,step,extra,check):
        nonlocal current
        trial='palc0046-palace-'+suffix
        run('unassisted_fast_prediction.py',['--pal',*COMMON,'--planner','evasive',
            '--planning-step',str(step),'--entry-boss-kind',kind,
            '--continuation',current,'--rooms',rooms,'--target-room',target,
            '--frames',budget(COMBAT,current,20000),'--trial',trial,*extra])
        current='md-pal-'+trial
        replay(COMBAT,current,lambda r:not r['deaths'] and not r['new_assistance_writes'] and check(r))

    resume('resume-giant01')
    ordinary('portal14e01','ordinary','0x15e,0x15d,0x16d,0x16c,0x14d,0x14e','0x14e',
        ['--equip-basic','--avoid-portal-rooms','0x14d','--defer-puzzles-rooms','0x16c',
         '--rush-rooms','0x16d,0x16c'],lambda r:r['room_cleared'] and not any(a['hp'] for a in r['last_actors']))
    ordinary('earth14e01','earth','0x14e,0x119','0x119',
        ['--equip-basic','--earth-room','0x14e','--earth-cell','0x58',
         '--earth-cast-x','136','--earth-cast-y','112','--earth-direction','0',
         '--passage-destination','0x119'],lambda r:r['earth_route_passed'])
    ordinary('earth11a01','earth','0x119,0x11a,0x12a','0x12a',
        ['--equip-basic','--earth-during-combat','--earth-room','0x11a','--earth-cell','0x35',
         '--earth-cast-x','88','--earth-cast-y','80','--earth-direction','0',
         '--passage-destination','0x12a'],lambda r:r['earth_route_passed'])
    ordinary('switch12901','contact','0x12a,0x129,0x12a,0x11c','0x11c',
        ['--equip-basic','--mechanism-during-combat','--contact-room','0x129',
         '--contact-destination','0x12a'],lambda r:r['contact_route_passed'])
    ordinary('switch12c01','contact','0x12a,0x11c,0x12c','0x12c',
        ['--equip-basic','--mechanism-during-combat','--contact-room','0x12c',
         '--contact-destination','0x12c'],lambda r:r['contact_route_passed'])
    ordinary('pre-guardian01','ordinary','0x12c,0x11c,0x11b,0x12b,0x12c,0x12d,0x12e','0x12e',
        ['--equip-basic','--rush-rooms','0x12c'],lambda r:r['room_cleared'])
    release('guardian-release01','0x11e')
    fight('guardian01','0x7c','0x12e,0x11e','0x11e',16,
        ['--equip-basic'],lambda r:r['room_cleared'])
    resume('resume-final01')
    ordinary('goldenaxe01','item','0x11e,0x11d','0x11d',
        ['--equip-axe','--collect-item','1','--collect-item-value','2'],
        lambda r:r['item_acquisition_passed'])
    print('PAL GOLDEN AXE VERIFIED',flush=True)

    proposal=json.loads((snapshot/'palace-final-v0309.json').read_bytes())
    assert proposal['status']=='unexecuted_proposal'
    for stage in proposal['stages']:
        name=stage['name']
        if name=='release':
            release('release-final01',stage['before_room'])
        elif name=='final':
            fight('final01',stage['entry_boss_kind'],stage['rooms'],stage['target'],16,
                ['--stop-on-ending','--equip-axe'],lambda r:r['ending_handoff_passed'])
        elif name=='ending':
            trial='palc0046-palace-ending01'
            run('continue_recorded_ending.py',['--trace',COMBAT+'/'+current,'--trial',trial])
            current='md-auto-'+trial
            replay(COMBAT,current,lambda r:r['ending_complete'] and not r['new_assistance_writes'])
        else:
            extra=['--equip-axe']
            planner=stage['planner']
            if stage.get('avoid'):
                extra+=['--avoid-portal-rooms',stage['avoid']]
            if name=='switch17c':
                extra+=['--isolated-retry-portal','0x13e','--isolated-retry-limit','8']
            if planner=='earth':
                extra+=['--earth-room',stage['earth_room'],'--earth-cell',stage['earth_cell'],
                    '--earth-cast-x',str(stage['cast'][0]),'--earth-cast-y',str(stage['cast'][1]),
                    '--earth-direction',str(stage['cast'][2]),'--passage-destination',stage['target']]
            if planner=='contact':
                extra+=['--contact-room',stage['contact_room'],'--contact-destination',stage['contact_destination']]
            criteria={'earth':'earth_route_passed','contact':'contact_route_passed','ordinary':'room_cleared'}
            ordinary(name+'01',planner,stage['rooms'],stage['target'],extra,
                lambda r:r[criteria[planner]],30000 if name=='switch17c' else 18000)
    print('PAL DEATH ADDER, CREDITS AND RETURN TO INTRO VERIFIED',flush=True)

if __name__=='__main__':
    work.mkdir(exist_ok=False)
    helper.STREAM=ReplayStream(work/'cold-stream')
    try:
        campaign()
    finally:
        helper.STREAM.close()
