"""Acquire D5 boots and supplies normally; prove each step in one cold stream."""
import json,shutil
import continue_d8_entry_v0312 as helper
from continue_after_d1_v0317 import ROM
from continue_d8_entry_v0312 import ROOT,COMBAT,ROUTE,SERVICE,report,assert_canonical
from archive_lossless_evidence import sha
from cold_replay_stream import ReplayStream
helper.EVIDENCE=ROOT/'validation/v0317-d5-supplies-sources'
COMMON=['--assisted-prefix','--max-deaths','0','--collision-aim','--settle-attacks','--doorway-ranges','--ignore-inactive-actors','--equip-axe','--retry-isolated-foes','--isolated-retry-limit','12']
def frame(f,n):return report(ROOT/'validation'/f/n,'capture.json')['frames']
def main():
    prior=report(ROOT/'analysis','fire_sword_v0317_report.json')
    assert prior['passed'] and prior['d5_entrance_reached'] and prior['md_sha256']==ROM==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    current='md-v0317-d5-entry01';family=ROUTE;assert_canonical(family,current)
    helper.EVIDENCE.mkdir(exist_ok=False);index={}
    for name in ('continue_d5_supplies_v0317.py','continue_d8_entry_v0312.py','assisted_boss_route.py','assisted_prefix.py','natural_dungeon_route.py','natural_dungeon_combat.py','natural_item_acquisition.py','natural_earth_passage.py','natural_contact_passage.py','natural_house_service.py','natural_merchant_purchase.py','cold_replay_stream.py','run_core.py'):
        shutil.copyfile(ROOT/'tools'/name,helper.EVIDENCE/name);index['tools/'+name]=sha((helper.EVIDENCE/name).read_bytes())
    (helper.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\n')
    stream=ReplayStream(helper.EVIDENCE/'cold-stream')
    def finish(check):
        r=report(ROOT/'validation'/family/current,'route_report.json' if family==ROUTE else 'report.json')
        assert r['failure'] is None and not r.get('deaths',0) and check(r),r
        stream.prove(family+'/'+current);assert_canonical(family,current)
    def step(suffix,planner,rooms,target,extra,check):
        nonlocal current,family
        trial='v0317-d5-'+suffix
        helper.run('assisted_boss_route.py',['--boss-room','0x163','--preserve-floor-hurt','--planner',planner,*COMMON,'--prefix' if family==ROUTE else '--continuation',current,'--rooms',rooms,'--target-room',target,'--frames',str(frame(family,current)+18000),'--trial',trial,*extra])
        current='md-auto-'+trial;family=COMBAT;finish(check)
    def route(suffix,extra):
        nonlocal current,family
        trial='v0317-d5-'+suffix
        helper.run('assisted_boss_route.py',['--boss-room','0x163','--world-route','--preserve-floor-hurt','--assisted-prefix','--prefix-combat' if family==COMBAT else '--prefix-service',current,'--axe-terrain','--rope-terrain','--live-prefix-terrain','--live-room-replan','--frames',str(frame(family,current)+18000),'--trial',trial,*extra])
        current='md-'+trial;family=ROUTE;finish(lambda r:r['reached_entrance'])
    def gold(suffix,outside):
        nonlocal current,family
        helper.run('natural_house_service.py',['--prefix',current,'--assisted-prefix','--outside',outside,'--kind','gold','--gold-gain','30','--trial','v0317-d5-'+suffix])
        current='md-v0317-d5-'+suffix;family=SERVICE;finish(lambda r:r['passed'])
    try:
        step('key01','ordinary','0x186,0x176','0x176',['--collect-key'],lambda r:r['new_key_verified'])
        step('earth01','earth','0x176,0x166','0x166',['--earth-room','0x176','--earth-cell','0x4a','--earth-cast-x','168','--earth-cast-y','96','--earth-direction','0','--passage-destination','0x166'],lambda r:r['earth_route_passed'])
        step('boots01','item','0x166,0x156,0x157','0x157',['--collect-item','14','--collect-item-value','1'],lambda r:r['item_acquisition_passed'])
        step('supply-exit01','ordinary','0x157,0x156,0x166,0x176,0x186','0x49',['--exit-dungeon','--exit-before-crystal'],lambda r:r['room_cleared'])
        route('golda1-entry01',['--house-outside','0xa1','--house-target','0x3f']);gold('golda1-gift01','0xa1')
        route('goldb4-entry01',['--house-outside','0xb4','--house-target','0x3f']);gold('goldb4-gift01','0xb4')
        route('merchant94-entry01',['--house-outside','0x94','--house-target','0'])
        helper.run('natural_merchant_purchase.py',['--prefix',current,'--assisted-prefix','--outside','0x94','--count','1','--heal-after','--trial','v0317-d5-key94-buy01'])
        current='md-v0317-d5-key94-buy01';family=SERVICE;finish(lambda r:r['passed'])
        route('return-entry01',['--door-index','5'])
        step('warp01','earth','0x186,0x176,0x166,0x165,0x155,0x154,0x155,0x165,0x164,0x154,0x153,0x162','0x162',['--earth-room','0x153','--earth-cell','0x44','--earth-cast-x','72','--earth-cast-y','96','--earth-direction','0','--passage-destination','0x162','--earth-during-combat'],lambda r:r['earth_route_passed'])
        step('contact01','contact','0x162,0x172','0x172',['--contact-room','0x162','--contact-destination','0x172','--mechanism-during-combat'],lambda r:r['contact_route_passed'])
        print('V317 D5 BOOTS, SUPPLIES AND CONTACT VERIFIED',flush=True)
    finally:stream.close()
if __name__=='__main__':main()
