"""Cold continuation of public v313 through D9's first guardian.
The historic route supplies control proposals only; current gameplay and all
canonical replay checks execute against the current release binary.
"""
import json, shutil
import continue_d8_entry_v0312 as helper
from continue_d8_entry_v0312 import ROUTE,SERVICE,COMBAT,COMMON,budget,load,replay,assert_canonical,run
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
helper.EVIDENCE=ROOT/'validation/v0313-d9-sources02'


def main():
    receipt=json.loads(evidence(ROOT/'analysis/startup_v0313_report.json'))
    assert receipt['passed'] and receipt['eighth_crystal_and_exterior_return']
    assert receipt['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    helper.EVIDENCE.mkdir(exist_ok=False)
    snapshot=helper.EVIDENCE/'entry-tools'
    snapshot.mkdir()
    names=('assisted_boss_route.py','assisted_prefix.py','natural_dungeon_route.py',
        'natural_paid_passage.py','natural_bell_world_route.py','natural_earth_then_contact.py',
        'close_assisted_approach.py','unassisted_dungeon_continuation.py',
        'unassisted_fast_prediction.py','prediction_video_skip.py',
        'natural_dungeon_combat.py','natural_combat_beam.py','replay_assisted_prefix.py',
        'continue_d9_entry_v0313.py','continue_d8_entry_v0312.py')
    hashes={}
    for name in names:
        target=snapshot/name
        shutil.copyfile(ROOT/'tools'/name,target)
        hashes[name]=sha(target.read_bytes())
    (snapshot/'source_index.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
    shutil.copyfile(ROOT/'validation/v0310-d7-sources/d9_entry.py',helper.EVIDENCE/'historical_control_proposal.py')
    source='md-auto-v0313-d8-cold01'
    assert_canonical(COMBAT,source)
    proof=load(COMBAT,source)
    assert proof['passed'] and proof['full_dungeon_cleared'] and proof['dungeon_exit_verified']
    assert proof['failure'] is None and proof['last_state']['dungeon']==0
    from assisted_prefix import recording
    cap=load(COMBAT,source,'capture.json')
    assist,writes=recording(ROOT/'validation'/COMBAT/source,cap)
    last=assist['episodes'][-1]
    assert last['release_write_frame'] < last['first_boss_combat']['frame']
    assert max(frame for frame,_,_ in writes)==last['release_write_frame']
    assert not cap['sram_input'] and assist['primary_state_imports']==0
    world=['--boss-room','0x1ac','--assisted-prefix','--world-route','--live-prefix-terrain','--live-room-replan','--axe-terrain','--rope-terrain','--preserve-floor-hurt']
    route='v0313-d9-paid1a-route01'
    run('assisted_boss_route.py',[*world,'--new-assistance-episode','--prefix-combat',source,'--house-outside','0x1a','--house-target','0x9f','--door-entry-direction','0','--frames',budget(COMBAT,source,16000),'--trial',route])
    replay(ROUTE,'md-'+route,lambda r:r['reached_entrance'] and r['directional_probe_succeeded'] and r['last_state']['gold']>=10)
    paid='v0313-d9-paid1a-service01'
    run('natural_paid_passage.py',['--assisted-prefix','--prefix','md-'+route,'--outside','0x1a','--trial',paid])
    replay(SERVICE,'md-'+paid,lambda r:r['passed'] and r['price']==10 and r['last_state']['room']==0x3c)
    entry='v0313-d9-entry01'
    run('natural_bell_world_route.py',[*world,'--prefix-service','md-'+paid,'--door-index','9','--frames',budget(SERVICE,'md-'+paid,12000),'--trial',entry])
    replay(ROUTE,'md-'+entry,lambda r:r['reached_entrance'] and r['directional_probe_succeeded'])
    base=['--boss-room','0x1ac',*COMMON,'--wake-sentinels','--retry-isolated-foes']
    first='v0313-d9-switch1de-02'
    run('natural_earth_then_contact.py',[*base,'--planner','earth','--prefix','md-'+entry,'--rooms','0x1fc,0x1fd,0x1fe,0x1ee,0x1de,0x1ce','--target-room','0x1ce','--earth-room','0x1de','--earth-cell','0x34','--earth-cast-x','72','--earth-cast-y','80','--passage-destination','0x1ce','--contact-room','0x1de','--contact-destination','0x1ce','--frames',budget(ROUTE,'md-'+entry,18000),'--trial',first])
    replay(COMBAT,'md-auto-'+first,lambda r:r['passed'])
    earth='v0313-d9-earth1ce-01'
    run('assisted_boss_route.py',[*base,'--planner','earth','--continuation','md-auto-'+first,'--rooms','0x1ce','--target-room','0x1ce','--earth-room','0x1ce','--earth-cell','0x56','--earth-cast-x','104','--earth-cast-y','112','--earth-action-only','--earth-during-combat','--passage-destination','0x1ce','--frames',budget(COMBAT,'md-auto-'+first,12000),'--trial',earth])
    replay(COMBAT,'md-auto-'+earth,lambda r:r['earth_route_passed'])
    ready='v0313-d9-mini-ready01'
    run('assisted_boss_route.py',[*base,'--planner','ordinary','--continuation','md-auto-'+earth,'--rooms','0x1ce','--target-room','0x1ce','--equip-axe','--frames',budget(COMBAT,'md-auto-'+earth,12000),'--trial',ready])
    replay(COMBAT,'md-auto-'+ready,lambda r:r['room_cleared'])
    release='v0313-d9-guard-release01'
    run('close_assisted_approach.py',['--trace',COMBAT+'/md-auto-'+ready,'--before-room','0x1be','--trial',release])
    replay(COMBAT,'md-auto-'+release,lambda r:r['last_state']['hurt']==0)
    fight='v0313-d9-midboss01'
    run('unassisted_fast_prediction.py',[*COMMON,'--planner','evasive','--planning-step','8','--continuation','md-auto-'+release,'--rooms','0x1ce,0x1be','--target-room','0x1be','--lookahead-rooms','0x1be','--equip-basic','--frames',budget(COMBAT,'md-auto-'+release,12000),'--trial',fight])
    replay(COMBAT,'md-auto-'+fight,lambda r:r['room_cleared'] and not r['deaths'] and not r['new_assistance_writes'])
    print('D9 ENTRY AND FIRST GUARDIAN VERIFIED',flush=True)


if __name__=='__main__':
    main()
