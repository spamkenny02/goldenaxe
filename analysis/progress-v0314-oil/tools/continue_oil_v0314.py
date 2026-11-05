"""Visit C7 normally after D2, take the real oil gift, and return upstairs/outside."""
import json,shutil
import continue_d8_entry_v0312 as helper
from continue_after_d1_v0314 import ROM
from continue_d8_entry_v0312 import ROOT,COMBAT,ROUTE,SERVICE,report,assert_canonical
from archive_lossless_evidence import sha

helper.EVIDENCE=ROOT/'validation/v0314-oil-sources'


def main():
    prior=report(ROOT/'analysis','d2_campaign_v0314_report.json')
    assert prior['passed'] and prior['second_crystal_and_exterior_return']
    assert prior['md_sha256']==ROM==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    current=prior['current_campaign_trace'].split('/')[-1];assert_canonical(COMBAT,current)
    helper.EVIDENCE.mkdir(exist_ok=False);index={}
    for name in ('continue_oil_v0314.py','continue_d8_entry_v0312.py','assisted_boss_route.py',
                 'assisted_prefix.py','natural_dungeon_route.py','natural_oil_stairs.py','replay_assisted_prefix.py'):
        shutil.copyfile(ROOT/'tools'/name,helper.EVIDENCE/name)
        index['tools/'+name]=sha((helper.EVIDENCE/name).read_bytes())
    (helper.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\n',encoding='utf-8')
    f=report(ROOT/'validation'/COMBAT/current,'capture.json')['frames']
    helper.run('assisted_boss_route.py',['--boss-room','0x195','--world-route',
        '--new-assistance-episode','--preserve-floor-hurt','--assisted-prefix','--prefix-combat',current,
        '--house-outside','0xc7','--house-target','0x1f','--axe-terrain','--live-prefix-terrain',
        '--live-room-replan','--frames',str(f+14000),'--trial','v0314-oil-route01'])
    current='md-v0314-oil-route01';r=report(ROOT/'validation'/ROUTE/current,'route_report.json')
    assert r['failure'] is None and r['reached_entrance']
    helper.run('replay_assisted_prefix.py',['--trace',ROUTE+'/'+current]);assert_canonical(ROUTE,current)
    helper.run('natural_oil_stairs.py',['--prefix',current,'--assisted-prefix','--trial','v0314-oil-service01'])
    current='md-v0314-oil-service01';r=report(ROOT/'validation'/SERVICE/current,'report.json')
    assert r['passed'] and r['failure'] is None and not r['new_assistance_writes']
    helper.run('replay_assisted_prefix.py',['--trace',SERVICE+'/'+current]);assert_canonical(SERVICE,current)
    print('V314 ACTUAL OIL GIFT, BOTH STAIRS AND EXTERIOR RETURN VERIFIED',flush=True)


if __name__=='__main__':main()
