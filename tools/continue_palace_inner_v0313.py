"""Continue the verified v313 giant through real portals, Earth and mechanisms."""
import json,shutil
import continue_d8_entry_v0312 as helper
from continue_after_d9_v0313 import ROM
from continue_d8_entry_v0312 import ROOT,COMBAT,report,assert_canonical
from archive_lossless_evidence import sha

helper.EVIDENCE=ROOT/'validation/v0313-palace-sources'
COMMON=['--assisted-prefix','--max-deaths','0','--collision-aim','--settle-attacks',
        '--doorway-ranges','--ignore-inactive-actors']


def finish(name,condition):
    result=report(ROOT/'validation'/COMBAT/name,'report.json')
    assert result['failure'] is None and not result['deaths'] and condition(result),result
    helper.run('replay_assisted_prefix.py',['--trace',COMBAT+'/'+name])
    assert_canonical(COMBAT,name)


def main():
    receipt=report(ROOT/'analysis','cold_palace_giant_v0313_report.json')
    assert receipt['passed'] and receipt['cold_palace_giant_defeated']
    assert receipt['md_sha256']==ROM==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    snapshot=helper.EVIDENCE/'inner-tools';snapshot.mkdir(exist_ok=False)
    names=('resume_after_intermediate.py','assisted_boss_route.py','assisted_prefix.py',
           'natural_dungeon_combat.py','natural_earth_passage.py','natural_contact_passage.py',
           'natural_combat_beam.py','replay_assisted_prefix.py',
           'continue_palace_inner_v0313.py','continue_d8_entry_v0312.py')
    hashes={}
    for name in names:
        target=snapshot/name;shutil.copyfile(ROOT/'tools'/name,target)
        hashes['tools/'+name]=sha(target.read_bytes())
    (snapshot/'source_index.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
    name='md-auto-v0313-cold-palace-resume01'
    helper.run('resume_after_intermediate.py',['--trace',receipt['current_campaign_trace'].removeprefix('validation/'),
        '--boss-room','0x14c','--trial',name.removeprefix('md-auto-')])
    finish(name,lambda r:r['passed'] and r['resumed_after_verified_intermediate'])
    def step(suffix,planner,rooms,target,extra,check):
        nonlocal name
        before=report(ROOT/'validation'/COMBAT/name,'capture.json')['frames']
        trial='v0313-cold-palace-'+suffix
        helper.run('assisted_boss_route.py',['--boss-room','0x14c','--preserve-floor-hurt',
            *COMMON,'--retry-isolated-foes','--wake-sentinels','--equip-basic',
            '--planner',planner,'--continuation',name,'--rooms',rooms,'--target-room',target,
            '--frames',str(before+18000),'--trial',trial,*extra])
        name='md-auto-'+trial;finish(name,check)
    step('portal14e04','ordinary','0x15e,0x15d,0x16d,0x16c,0x14d,0x14e','0x14e',
         ['--avoid-portal-rooms','0x14d','--defer-puzzles-rooms','0x16c','--rush-rooms','0x16c'],
         lambda r:r['room_cleared'] and not any(a['hp'] for a in r['last_actors']))
    step('earth14e01','earth','0x14e,0x119','0x119',
         ['--earth-room','0x14e','--earth-cell','0x58','--earth-cast-x','136',
          '--earth-cast-y','112','--earth-direction','0','--passage-destination','0x119'],
         lambda r:r['earth_route_passed'])
    step('earth11a01','earth','0x119,0x11a,0x12a','0x12a',
         ['--earth-during-combat','--earth-room','0x11a','--earth-cell','0x35',
          '--earth-cast-x','88','--earth-cast-y','80','--earth-direction','0','--passage-destination','0x12a'],
         lambda r:r['earth_route_passed'])
    step('switch12901','contact','0x12a,0x129,0x12a,0x11c','0x11c',
         ['--mechanism-during-combat','--contact-room','0x129','--contact-destination','0x12a'],
         lambda r:r['contact_route_passed'])
    print('V313 PALACE INNER MECHANISMS VERIFIED',flush=True)


if __name__=='__main__':main()
