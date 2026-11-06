"""Trade the actual oil for Fire, receive Long Sword, and enter D5 normally."""
import json,shutil
import continue_d8_entry_v0312 as helper
from continue_after_d1_v0317 import ROM
from continue_d8_entry_v0312 import ROOT,COMBAT,ROUTE,SERVICE,report,assert_canonical
from archive_lossless_evidence import sha
from campaign_stream_replay import streamed_replays

helper.EVIDENCE=ROOT/'validation/v0317-fire-sword-sources'


def frame(family,name):return report(ROOT/'validation'/family/name,'capture.json')['frames']


def finish(family,name,check):
    r=report(ROOT/'validation'/family/name,'route_report.json' if family==ROUTE else 'report.json')
    assert r['failure'] is None and check(r),r
    helper.run('replay_assisted_prefix.py',['--trace',family+'/'+name]);assert_canonical(family,name)


def main():
    prior=report(ROOT/'analysis','d4_campaign_v0317_report.json')
    assert prior['passed'] and prior['fourth_crystal_and_exterior_return']
    assert prior['md_sha256']==ROM==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    current='md-auto-v0317-d4-exit01';family=COMBAT;assert_canonical(family,current)
    helper.EVIDENCE.mkdir(exist_ok=False);index={}
    for name in ('continue_fire_sword_v0317.py','continue_d8_entry_v0312.py','campaign_stream_replay.py','cold_replay_stream.py','assisted_boss_route.py',
                 'assisted_prefix.py','natural_dungeon_route.py','natural_house_service.py',
                 'natural_house_quest.py','replay_assisted_prefix.py'):
        shutil.copyfile(ROOT/'tools'/name,helper.EVIDENCE/name)
        index['tools/'+name]=sha((helper.EVIDENCE/name).read_bytes())
    (helper.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\n',encoding='utf-8')
    def route(trial,extra,new=False):
        nonlocal current,family
        helper.run('assisted_boss_route.py',['--boss-room','0x163','--world-route',
            '--preserve-floor-hurt','--assisted-prefix',*(['--new-assistance-episode']if new else []),
            '--prefix-combat'if family==COMBAT else '--prefix-service',current,
            '--axe-terrain','--rope-terrain','--live-prefix-terrain','--live-room-replan',
            '--frames',str(frame(family,current)+18000),'--trial',trial,*extra])
        current='md-'+trial;family=ROUTE;finish(family,current,lambda r:r['reached_entrance'])
    def teacher(trial,level):
        nonlocal current,family
        helper.run('natural_house_service.py',['--prefix',current,'--assisted-prefix','--outside','0xe6',
            '--kind','teacher','--teacher','0','--expected-level',str(level),'--trial',trial])
        current='md-'+trial;family=SERVICE;finish(family,current,lambda r:r['passed'] and r['last_state']['level']==level)
    route('v0317-fire-entry01',['--house-outside','0xe6','--house-target','0xbf'],new=True)
    teacher('v0317-fire-intro01',0)
    route('v0317-fire-entry02',['--house-outside','0xe6','--house-target','0xbf'])
    teacher('v0317-fire-learn01',1)
    route('v0317-sword2-entry01',['--house-outside','0x50','--house-target','0x4f'])
    helper.run('natural_house_quest.py',['--prefix',current,'--assisted-prefix','--outside','0x50',
        '--trial','v0317-sword2-gift01'])
    current='md-v0317-sword2-gift01';family=SERVICE
    finish(family,current,lambda r:r['passed'] and r['last_state']['basic']==2)
    route('v0317-d5-entry01',['--door-index','5'])
    print('V317 OIL-TO-FIRE, LONG SWORD AND D5 ENTRANCE VERIFIED',flush=True)


if __name__=='__main__':
    with streamed_replays(helper,ROOT/'validation/v0317-fire-sword-cold-stream'):
        main()
