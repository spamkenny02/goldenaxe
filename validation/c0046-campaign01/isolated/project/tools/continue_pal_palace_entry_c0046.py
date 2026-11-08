"""Continue the V318 PAL campaign into the palace and past its first giant."""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0,'tools')
import continue_d8_entry_palc0046 as helper
from continue_d8_entry_palc0046 import COMBAT, ROUTE, COMMON, assert_canonical, budget, load, replay, run
from archive_lossless_evidence import sha
from cold_replay_stream import ReplayStream
from run_core import ROOT

work=ROOT/'validation/palc0046-pal-palace-entry-sources'
helper.EVIDENCE=work
source='md-pal-palc0046-d9-exit01'

def campaign():
    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    audited=json.loads((ROOT/'analysis/palc0046_d9_report.json').read_bytes())
    published=json.loads((ROOT/'analysis/pal_d9_v0319_report.json').read_bytes())
    assert audited['passed'] and audited['actual_ninth_crystal_and_exterior']
    assert audited['rom_sha256']==digest and published['passed']
    assert published['pal_crystals_and_exterior_returns_verified']==9

    prior=ROOT/'validation/palc0046-d9-funded-finish-cold-stream01/completed.json'
    receipt=json.loads(prior.read_bytes())
    assert receipt['passed'] and receipt['rom_sha256']==digest and receipt['cold_boot_count']==1
    assert receipt['checkpoints'][-1]['trace']==COMBAT+'/'+source
    assert receipt['checkpoints'][-1]['whole_ram_png_exact']
    assert_canonical(COMBAT,source)
    exit_report=load(COMBAT,source)
    assert exit_report['full_dungeon_cleared'] and exit_report['dungeon_exit_verified']
    assert exit_report['last_state']['dungeon']==0 and not exit_report['new_assistance_writes']
    assert load(COMBAT,source,'capture.json')['sram_input'] is None
    snapshot=work/'sources'
    snapshot.mkdir()
    names=('natural_owned_overview.py','natural_palace_world_route.py',
           'natural_dungeon_route.py','assisted_boss_route.py',
           'close_assisted_approach.py','unassisted_fast_prediction.py',
           'unassisted_dungeon_continuation.py','prediction_video_skip.py',
           'continue_after_d9_c0046.py','continue_palace_giant_c0046.py',
           'continue_d8_entry_palc0046.py','cold_replay_stream.py','continue_pal_palace_entry_c0046.py','run_core.py')
    hashes={}
    for name in names:
        target=snapshot/name
        shutil.copyfile(ROOT/'tools'/name,target)
        hashes[name]=sha(target.read_bytes())
    (snapshot/'source_index.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')

    trial='palc0046-owned-overview01'
    run('natural_owned_overview.py',['--trace',COMBAT+'/'+source,
        '--assisted-prefix','--trial',trial])
    overview='md-auto-'+trial
    replay(COMBAT,overview,lambda r:r['passed'] and r['actual_owned_balloon']
        and r['modal_resources_unchanged'] and not r['new_assistance_writes'])

    trial='palc0046-cold-palace-entry01'
    run('natural_palace_world_route.py',['--pal','--boss-room','0x14c',
        '--new-assistance-episode','--completed-exit-proof',COMBAT+'/'+source,
        '--world-route','--preserve-floor-hurt','--assisted-prefix',
        '--prefix-completed-action','--prefix-combat',overview,'--door-index','10',
        '--live-prefix-terrain','--live-room-replan','--axe-terrain','--rope-terrain',
        '--frames',budget(COMBAT,overview,20000),'--trial',trial])
    entry='md-pal-'+trial
    replay(ROUTE,entry,lambda r:r['reached_entrance'] and r['palace_gate_verified']
        and not r['palace_new_map_or_resource_writes'])
    print('PAL PALACE ENTRY VERIFIED',flush=True)

    base=['--pal','--boss-room','0x14c','--preserve-floor-hurt',*COMMON,
          '--retry-isolated-foes','--equip-basic']
    trial='palc0046-palace-switch16d01'
    run('assisted_boss_route.py',[*base,'--planner','contact','--mechanism-during-combat',
        '--prefix',entry,'--rooms','0x18d,0x17d,0x16d','--target-room','0x16d',
        '--contact-room','0x16d','--contact-destination','0x16d',
        '--frames',budget(ROUTE,entry,12000),'--trial',trial])
    switch='md-pal-'+trial
    replay(COMBAT,switch,lambda r:r['contact_route_passed'] and not r['contact_state_writes'])

    trial='palc0046-palace-pre-giant01'
    run('assisted_boss_route.py',[*base,'--planner','contact','--wake-sentinels',
        '--rush-rooms','0x16d','--continuation',switch,
        '--rooms','0x16d,0x17d,0x18d,0x18e,0x17e,0x16e','--target-room','0x16e',
        '--contact-room','0x16e','--contact-destination','0x16e',
        '--frames',budget(COMBAT,switch,14000),'--trial',trial])
    pre='md-pal-'+trial
    replay(COMBAT,pre,lambda r:r['contact_route_passed'])

    trial='palc0046-palace-giant-release01'
    run('close_assisted_approach.py',['--trace',COMBAT+'/'+pre,
        '--before-room','0x15e','--trial',trial])
    release='md-auto-'+trial
    replay(COMBAT,release,lambda r:r['last_state']['hurt']==0)

    trial='palc0046-palace-giant01'
    run('unassisted_fast_prediction.py',['--pal',*COMMON,'--planner','evasive',
        '--planning-step','8','--entry-boss-kind','0x7b','--continuation',release,
        '--rooms','0x16e,0x15e','--target-room','0x15e','--equip-basic',
        '--frames',budget(COMBAT,release,12000),'--trial',trial])
    replay(COMBAT,'md-pal-'+trial,
        lambda r:r['room_cleared'] and not r['deaths'] and not r['new_assistance_writes'])
    print('PAL PALACE FIRST GIANT VERIFIED',flush=True)

if __name__=='__main__':
    work.mkdir(exist_ok=False)
    helper.STREAM=ReplayStream(work/'cold-stream')
    try:
        campaign()
    finally:
        helper.STREAM.close()
