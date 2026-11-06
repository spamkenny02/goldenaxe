"""Obtain the actual gold gift and buy Earth through the normal teacher UI."""
import json,shutil
import continue_d8_entry_v0312 as helper
from continue_after_d1_v0317 import ROM
from continue_d8_entry_v0312 import ROOT,COMBAT,ROUTE,SERVICE,report,assert_canonical
from archive_lossless_evidence import sha
from campaign_stream_replay import streamed_replays

helper.EVIDENCE=ROOT/'validation/v0317-earth-learning-sources'


def frame(family,name):return report(ROOT/'validation'/family/name,'capture.json')['frames']


def finish(family,name,check):
    r=report(ROOT/'validation'/family/name,'route_report.json' if family==ROUTE else 'report.json')
    assert r['failure'] is None and check(r),r
    helper.run('replay_assisted_prefix.py',['--trace',family+'/'+name]);assert_canonical(family,name)


def main():
    prior=report(ROOT/'analysis','d3_campaign_v0317_report.json')
    assert prior['passed'] and prior['three_crystals_and_exterior_return']
    assert prior['md_sha256']==ROM==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    current='md-auto-v0317-d3-exit01';assert_canonical(COMBAT,current)
    helper.EVIDENCE.mkdir(exist_ok=False);index={}
    for name in ('continue_earth_learning_v0317.py','continue_d8_entry_v0312.py','campaign_stream_replay.py','cold_replay_stream.py','assisted_boss_route.py',
                 'assisted_prefix.py','natural_dungeon_route.py','natural_house_service.py','replay_assisted_prefix.py'):
        shutil.copyfile(ROOT/'tools'/name,helper.EVIDENCE/name)
        index['tools/'+name]=sha((helper.EVIDENCE/name).read_bytes())
    (helper.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\n',encoding='utf-8')
    helper.run('assisted_boss_route.py',['--boss-room','0x180','--world-route',
        '--new-assistance-episode','--preserve-floor-hurt','--assisted-prefix','--prefix-combat',current,
        '--house-outside','0xf4','--house-target','0x3f','--axe-terrain','--rope-terrain',
        '--live-prefix-terrain','--live-room-replan','--frames',str(frame(COMBAT,current)+18000),
        '--trial','v0317-gold-entry01'])
    current='md-v0317-gold-entry01';finish(ROUTE,current,lambda r:r['reached_entrance'])
    helper.run('natural_house_service.py',['--prefix',current,'--assisted-prefix','--outside','0xf4',
        '--kind','gold','--gold-gain','50','--trial','v0317-gold50-01'])
    current='md-v0317-gold50-01'
    finish(SERVICE,current,lambda r:r['passed'] and r['last_state']['gold']-r['first_state']['gold']==50)
    helper.run('assisted_boss_route.py',['--boss-room','0x180','--world-route','--preserve-floor-hurt',
        '--assisted-prefix','--prefix-service',current,'--house-outside','0xa3','--house-target','0xbf',
        '--axe-terrain','--rope-terrain','--live-prefix-terrain','--live-room-replan',
        '--required-chop','0xa3:0x4a','--frames',str(frame(SERVICE,current)+18000),
        '--trial','v0317-earth-entry01'])
    current='md-v0317-earth-entry01';finish(ROUTE,current,lambda r:r['reached_entrance'] and r['required_chop_verified'])
    helper.run('natural_house_service.py',['--prefix',current,'--assisted-prefix','--outside','0xa3',
        '--kind','teacher','--teacher','1','--expected-level','1','--trial','v0317-earth-learn01'])
    finish(SERVICE,'md-v0317-earth-learn01',lambda r:r['passed'] and r['first_state']['gold']-r['last_state']['gold']==50)
    print('V317 ACTUAL GOLD GIFT AND EARTH PURCHASE VERIFIED',flush=True)


if __name__=='__main__':
    with streamed_replays(helper, ROOT/'validation/v0317-earth-cold-stream'):
        main()
