"""Continue v313 after the first D9 guardian using ordinary game controls."""
import json,shutil
import continue_d8_entry_v0312 as helper
from continue_d8_entry_v0312 import COMBAT,load,replay as validate,assert_canonical,run as execute
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
helper.EVIDENCE=ROOT/'validation/v0313-d9-sources02'


def run(label, argv):
    print(label, flush=True)
    tool, *args = argv
    execute(tool.removeprefix('tools/'), args)


def end(name):
    return load(COMBAT, name, 'capture.json')['frames']


def replay(name, passed=lambda r: True):
    validate(COMBAT, name, lambda r: not r.get('deaths', 0) and passed(r))


def main():
    receipt=json.loads(evidence(ROOT/'analysis/d9_midboss_v0313_report.json'))
    assert receipt['passed'] and receipt['first_intermediate_defeated']
    assert receipt['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    snapshot=helper.EVIDENCE/'finish-tools'
    snapshot.mkdir(exist_ok=False)
    names=('resume_after_intermediate.py','assisted_boss_route.py',
           'close_assisted_approach.py','unassisted_dungeon_continuation.py',
           'unassisted_fast_prediction.py','prediction_video_skip.py',
           'natural_dungeon_combat.py','natural_combat_beam.py',
           'natural_boss_evasive_planner.py','replay_assisted_prefix.py',
           'continue_d9_finish_v0313.py','continue_d8_entry_v0312.py')
    hashes={}
    for name in names:
        target=snapshot/name
        shutil.copyfile(ROOT/'tools'/name,target)
        hashes['tools/'+name]=sha(target.read_bytes())
    (snapshot/'source_index.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
    shutil.copyfile(ROOT/'validation/v0310-d7-sources/d9_finish.py',snapshot/'historical_control_proposal.py')
    guardian = 'md-auto-v0313-d9-midboss01'
    assert_canonical(COMBAT, guardian)
    proof = load(COMBAT, guardian)
    assert proof['room_cleared'] and not proof['deaths'] and not proof['new_assistance_writes']
    run('resume',['tools/resume_after_intermediate.py','--trace','natural-dungeon-combat/md-auto-v0313-d9-midboss01','--boss-room','0x1ac','--trial','v0313-d9-approach-resume01'])
    replay('md-auto-v0313-d9-approach-resume01')
    base=['tools/assisted_boss_route.py','--max-deaths','0','--boss-room','0x1ac','--preserve-floor-hurt','--assisted-prefix','--collision-aim','--settle-attacks','--doorway-ranges','--ignore-inactive-actors','--wake-sentinels','--retry-isolated-foes']
    def step(previous,trial,planner,args,extra=14000):
     run(trial,base+['--planner',planner,'--continuation',previous,'--frames',str(end(previous)+extra),'--trial','v0313-d9-'+trial,*args]);name='md-auto-v0313-d9-'+trial;replay(name);return name
    name=step('md-auto-v0313-d9-approach-resume01','switch1ad-01','contact',['--rooms','0x1be,0x1ae,0x1ad','--target-room','0x1ad','--contact-room','0x1ad','--contact-destination','0x1ad','--equip-basic'])
    name=step(name,'portal19e-ready01','ordinary',['--rooms','0x1ad,0x1ae,0x19e','--target-room','0x19e','--avoid-portal-rooms','0x19e','--equip-basic'])
    # Four62 have zero HP and remain alive as hazards; reach a safe west-door point.
    name=step(name,'giant-ready02','ordinary',['--rooms','0x19e,0x19d','--target-room','0x19d','--avoid-portal-rooms','0x19e','--reach-room','--arrival-x','24','--arrival-y','88','--equip-basic'],6000)
    run('giant-release',['tools/close_assisted_approach.py','--trace','natural-dungeon-combat/'+name,'--before-room','0x19c','--trial','v0313-d9-giant-release01'])
    name='md-auto-v0313-d9-giant-release01';replay(name)
    run('giant-fight',['tools/unassisted_fast_prediction.py','--planner','evasive','--planning-step','8','--continuation',name,'--assisted-prefix','--rooms','0x19d,0x19c','--target-room','0x19c','--lookahead-rooms','0x19c','--max-deaths','0','--equip-basic','--collision-aim','--settle-attacks','--doorway-ranges','--ignore-inactive-actors','--frames',str(end(name)+12000),'--trial','v0313-d9-giant01'])
    replay('md-auto-v0313-d9-giant01', lambda r: r['room_cleared'] and not r['new_assistance_writes'])
    run('giant-resume',['tools/resume_after_intermediate.py','--trace','natural-dungeon-combat/md-auto-v0313-d9-giant01','--boss-room','0x1ac','--trial','v0313-d9-post-giant-resume01'])
    replay('md-auto-v0313-d9-post-giant-resume01')
    name=step('md-auto-v0313-d9-post-giant-resume01','balloon01','item',['--rooms','0x19c,0x19b','--target-room','0x19b','--collect-item','11','--equip-axe'])
    assert load(COMBAT,name)['item_acquisition_passed']
    start=end(name)
    run('approach',['tools/assisted_boss_route.py','--boss-room','0x1ac','--max-deaths','0','--planner','contact','--preserve-floor-hurt','--continuation','md-auto-v0313-d9-balloon01','--assisted-prefix','--rooms','0x19b,0x19c,0x19d,0x19e,0x1cc,0x1bc,0x1bd,0x1bc,0x1ac','--target-room','0x1ac','--contact-room','0x1bd','--contact-destination','0x1bc','--avoid-portal-rooms','0x1cc','--equip-basic','--collision-aim','--settle-attacks','--doorway-ranges','--ignore-inactive-actors','--wake-sentinels','--retry-isolated-foes','--frames',str(start+20000),'--trial','v0313-d9-main-approach01'])
    replay('md-auto-v0313-d9-main-approach01')
    run('release',['tools/close_assisted_approach.py','--trace','natural-dungeon-combat/md-auto-v0313-d9-main-approach01','--before-room','0x1ac','--trial','v0313-d9-main-release01'])
    replay('md-auto-v0313-d9-main-release01')
    start=end('md-auto-v0313-d9-main-release01')
    base=['tools/unassisted_fast_prediction.py','--max-deaths','0','--assisted-prefix','--collision-aim','--settle-attacks','--doorway-ranges','--ignore-inactive-actors']
    run('boss',base+['--planner','evasive','--planning-step','16','--entry-boss-kind','0x6c','--continuation','md-auto-v0313-d9-main-release01','--rooms','0x1bc,0x1ac','--target-room','0x1ac','--collect-gem','--equip-basic','--frames',str(start+14000),'--trial','v0313-d9-boss01'])
    replay('md-auto-v0313-d9-boss01', lambda r: r['room_cleared'] and r['last_state']['progress']==128 and not r['new_assistance_writes'])
    start=end('md-auto-v0313-d9-boss01')
    run('exit',base+['--planner','exit','--planning-step','8','--continuation','md-auto-v0313-d9-boss01','--rooms','0x1ac,0x1bc,0x1cc,0x19e,0x1ae,0x1be,0x1ce,0x1de,0x1ee,0x1fe,0x1fd,0x1fc','--target-room','0xeb','--exit-dungeon','--equip-axe','--frames',str(start+12000),'--trial','v0313-d9-exit01'])
    replay('md-auto-v0313-d9-exit01', lambda r: r['full_dungeon_cleared'] and not r['new_assistance_writes'])
    print('NINTH CRYSTAL AND EXIT VERIFIED', flush=True)


if __name__ == '__main__':
    main()
