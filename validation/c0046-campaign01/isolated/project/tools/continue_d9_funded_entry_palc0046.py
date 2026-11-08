"""Continue the verified eight-crystal PAL campaign through D9's first guardian.
The historic route supplies control proposals only; current gameplay and all
canonical replay checks execute against the current release binary.
"""
import json, shutil, sys
from pathlib import Path
sys.path.insert(0,"tools")
import continue_d8_entry_palc0046 as helper
helper.EVIDENCE=helper.ROOT/'validation/palc0046-d9-funded-entry-sources'
helper.COMMON=["--wake-sentinels","--retry-isolated-foes","--isolated-retry-limit","12",*helper.COMMON]
from continue_d8_entry_palc0046 import ROUTE,SERVICE,COMBAT,COMMON,budget,load,replay,assert_canonical,run
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence


def campaign():
    receipt=json.loads(evidence(ROOT/'analysis/palc0046_d9_funding_return_report.json'))
    assert receipt['passed'] and receipt['actual_eighth_crystal_and_exterior']
    assert receipt['rom_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    snapshot=helper.EVIDENCE/'entry-tools'
    snapshot.mkdir(parents=True,exist_ok=False)
    names=('assisted_boss_route.py','assisted_prefix.py','natural_dungeon_route.py',
        'natural_paid_passage.py','natural_bell_world_route.py','natural_earth_then_contact.py',
        'close_assisted_approach.py','unassisted_dungeon_continuation.py',
        'unassisted_fast_prediction.py','prediction_video_skip.py',
        'natural_dungeon_combat.py','natural_combat_beam.py','replay_assisted_prefix.py',
        'continue_d9_funded_entry_palc0046.py','continue_d8_entry_palc0046.py','natural_house_service.py','natural_free_healer.py','cold_replay_stream.py','run_core.py')
    hashes={}
    for name in names:
        target=snapshot/name
        shutil.copyfile(ROOT/'tools'/name,target)
        hashes[name]=sha(target.read_bytes())
    (snapshot/'source_index.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
    source='md-pal-palc0046-d9-funding-d8-exit01'
    assert_canonical(COMBAT,source)
    proof=load(COMBAT,source)
    assert proof['room_cleared'] and proof['dungeon_exit_verified']
    assert proof['failure'] is None and proof['last_state']['dungeon']==0
    from assisted_prefix import recording
    cap=load(COMBAT,source,'capture.json')
    assist,writes=recording(ROOT/'validation'/COMBAT/source,cap)
    last=assist['episodes'][-1]
    assert last['boss_room']==0x1ac and last['first_boss_entry'] is None
    assert last['release_write_frame'] is None and last['first_boss_combat'] is None
    assert receipt['ordinary_coin_collection'] and receipt['stages'][-1]['gold']>=10
    assert not cap['sram_input'] and assist['primary_state_imports']==0
    world=['--pal','--boss-room','0x1ac','--assisted-prefix','--world-route','--live-prefix-terrain','--live-room-replan','--axe-terrain','--rope-terrain','--preserve-floor-hurt']
    family=COMBAT
    origin=['--prefix-combat',source]
    route='palc0046-d9-funded-paid1a-route01'
    run('assisted_boss_route.py',[*world,*origin,'--house-outside','0x1a','--house-target','0x9f','--frames',budget(family,source,12000),'--trial',route])
    replay(ROUTE,'md-pal-'+route,lambda r:r['reached_entrance'] and r['directional_probe_succeeded'])
    payment='palc0046-d9-funded-paid1a-service01'
    run('natural_paid_passage.py',['--assisted-prefix','--prefix','md-pal-'+route,'--outside','0x1a','--trial',payment])
    replay(SERVICE,'md-'+payment,lambda r:r['passed'] and r['price']==10 and r['last_state']['room']==0x3c)
    family,source=SERVICE,'md-'+payment
    origin=['--prefix-service',source]
    entry='palc0046-d9-funded-entry02'
    run('natural_bell_world_route.py',[*world,*origin,'--door-index','9','--frames',budget(family,source,18000),'--trial',entry])
    replay(ROUTE,'md-pal-'+entry,lambda r:r['reached_entrance'] and r['directional_probe_succeeded'])
    base=['--boss-room','0x1ac',*COMMON,'--wake-sentinels','--retry-isolated-foes']
    first='palc0046-d9-funded-switch1de-02'
    run('natural_earth_then_contact.py',[*base,'--planner','earth','--prefix','md-pal-'+entry,'--rooms','0x1fc,0x1fd,0x1fe,0x1ee,0x1de,0x1ce','--target-room','0x1ce','--earth-room','0x1de','--earth-cell','0x34','--earth-cast-x','72','--earth-cast-y','80','--passage-destination','0x1ce','--contact-room','0x1de','--contact-destination','0x1ce','--frames',budget(ROUTE,'md-pal-'+entry,18000),'--trial',first])
    replay(COMBAT,'md-pal-'+first,lambda r:r['passed'])
    earth='palc0046-d9-funded-earth1ce-01'
    run('assisted_boss_route.py',[*base,'--planner','earth','--continuation','md-pal-'+first,'--rooms','0x1ce','--target-room','0x1ce','--earth-room','0x1ce','--earth-cell','0x56','--earth-cast-x','104','--earth-cast-y','112','--earth-action-only','--earth-during-combat','--passage-destination','0x1ce','--frames',budget(COMBAT,'md-pal-'+first,12000),'--trial',earth])
    replay(COMBAT,'md-pal-'+earth,lambda r:r['earth_route_passed'])
    ready='palc0046-d9-funded-mini-ready01'
    run('assisted_boss_route.py',[*base,'--planner','ordinary','--continuation','md-pal-'+earth,'--rooms','0x1ce','--target-room','0x1ce','--equip-axe','--frames',budget(COMBAT,'md-pal-'+earth,12000),'--trial',ready])
    replay(COMBAT,'md-pal-'+ready,lambda r:r['room_cleared'])
    release='palc0046-d9-funded-guard-release01'
    run('close_assisted_approach.py',['--trace',COMBAT+'/md-pal-'+ready,'--before-room','0x1be','--trial',release])
    replay(COMBAT,'md-auto-'+release,lambda r:r['last_state']['hurt']==0)
    fight='palc0046-d9-funded-midboss01'
    run('unassisted_fast_prediction.py',[*COMMON,'--planner','evasive','--planning-step','8','--continuation','md-auto-'+release,'--rooms','0x1ce,0x1be','--target-room','0x1be','--lookahead-rooms','0x1be','--equip-basic','--frames',budget(COMBAT,'md-auto-'+release,12000),'--trial',fight])
    replay(COMBAT,'md-pal-'+fight,lambda r:r['room_cleared'] and not r['deaths'] and not r['new_assistance_writes'])
    print('D9 ENTRY AND FIRST GUARDIAN VERIFIED',flush=True)


def main():
    from cold_replay_stream import ReplayStream
    helper.EVIDENCE.mkdir(exist_ok=False)
    helper.STREAM=ReplayStream(ROOT/'validation/palc0046-d9-funded-entry-cold-stream01')
    try:campaign()
    finally:helper.STREAM.close()


if __name__=='__main__':
    main()
