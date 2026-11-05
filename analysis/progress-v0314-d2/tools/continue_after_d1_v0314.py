"""Collect the axe and first life fairy normally, then enter D2 on v314."""
import json, shutil
import continue_d8_entry_v0312 as helper
from continue_d8_entry_v0312 import ROOT, COMBAT, ROUTE, SERVICE, report, assert_canonical
from archive_lossless_evidence import sha

ROM = 'c53381c459a1e6254a8c9f1cfad1b8cda482cc0614697ad566133b28335e07a7'
helper.EVIDENCE = ROOT/'validation/v0314-after-d1-sources'
COMMON = ['--assisted-prefix', '--collision-aim', '--settle-attacks',
          '--doorway-ranges', '--ignore-inactive-actors', '--max-deaths', '0']


def run(tool, args):
    trial = args[args.index('--trial')+1]
    family = SERVICE if tool == 'natural_fairy_service.py' else ROUTE if '--world-route' in args else COMBAT
    name = ('md-auto-' if family == COMBAT else 'md-')+trial
    folder = ROOT/'validation'/family/name
    filename = 'route_report.json' if family == ROUTE else 'report.json'
    if (folder/filename).exists():
        result = report(folder,filename)
        assert result['failure'] is None and result['rom_sha256'] == ROM
        print('REUSE completed controller stage',name,flush=True)
    else:
        helper.run(tool,args)


def frames(family, name): return report(ROOT/'validation'/family/name, 'capture.json')['frames']


def finish(family, name, condition):
    filename = 'route_report.json' if family == ROUTE else 'report.json'
    result = report(ROOT/'validation'/family/name, filename)
    assert result['failure'] is None and not result.get('deaths',0) and condition(result), result
    end = frames(family,name)
    proof = ROOT/'validation'/family/(name+'-assisted-fixed-replay-'+str(end))
    if not proof.exists(): helper.run('replay_assisted_prefix.py', ['--trace', family+'/'+name])
    assert_canonical(family, name)


def main():
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes()) == ROM
    prior = 'md-auto-v0314-d1-cold01'; assert_canonical(COMBAT, prior)
    first = report(ROOT/'validation'/COMBAT/prior, 'report.json')
    assert first['passed'] and first['full_dungeon_cleared'] and first['dungeon_exit_verified']
    resumed = helper.EVIDENCE.exists()
    helper.EVIDENCE.mkdir(exist_ok=True)
    names = ('continue_after_d1_v0314.py','continue_d8_entry_v0312.py','assisted_boss_route.py',
             'assisted_prefix.py','natural_dungeon_combat.py','natural_dungeon_route.py',
             'natural_item_acquisition.py','natural_fairy_service.py','replay_assisted_prefix.py')
    if resumed:
        index=report(helper.EVIDENCE,'source_index.json')
        for name,digest in index.items():
            assert sha((helper.EVIDENCE/name.split('/')[-1]).read_bytes()) == digest
            if name != 'tools/continue_after_d1_v0314.py':
                assert sha((ROOT/name).read_bytes()) == digest
        target=helper.EVIDENCE/'resumed-driver01.py'
        assert not target.exists()
        target.write_bytes((ROOT/'tools/continue_after_d1_v0314.py').read_bytes())
    else:
        index = {}
        for name in names:
            shutil.copyfile(ROOT/'tools'/name, helper.EVIDENCE/name)
            index['tools/'+name] = sha((helper.EVIDENCE/name).read_bytes())
        (helper.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\n',encoding='utf-8')
    run('assisted_boss_route.py', ['--boss-room','0x144','--world-route',
        '--new-assistance-episode','--preserve-floor-hurt','--assisted-prefix',
        '--prefix-combat',prior,'--door-index','1','--frames',str(frames(COMBAT,prior)+6000),
        '--trial','v0314-d1-axe-entry01'])
    current = 'md-v0314-d1-axe-entry01'
    finish(ROUTE,current,lambda r:r['reached_entrance'] and r['directional_probe_succeeded'])
    def combat(suffix, rooms, target, extra, check, prefix=False):
        nonlocal current
        family = ROUTE if prefix else COMBAT
        trial = 'v0314-'+suffix
        run('assisted_boss_route.py',['--boss-room','0x144','--preserve-floor-hurt',
            '--planner','ordinary',*COMMON,'--prefix' if prefix else '--continuation',current,
            '--rooms',rooms,'--target-room',target,'--frames',str(frames(family,current)+12000),
            '--trial',trial,*extra])
        current='md-auto-'+trial;finish(COMBAT,current,check)
    combat('d1-axe-key01','0x1e4,0x1d4,0x1c4,0x1b4,0x1b5,0x1c5','0x1c5',
           ['--equip-basic','--collect-key'],lambda r:r['new_key_verified'],prefix=True)
    combat('d1-axe01','0x1c5,0x1b5,0x1b6','0x1b6',
           ['--equip-basic','--collect-item','1','--collect-item-value','1'],
           lambda r:r['room_cleared'] and r['last_state']['weapon']==1 and r['last_state']['item_value']==1 and not r['last_state']['reward_active'])
    combat('d1-axe-exit01','0x1b6,0x1b5,0x1b4,0x1c4,0x1d4,0x1e4','0xb9',
           ['--equip-axe','--exit-dungeon'],lambda r:r['dungeon_exit_verified'])
    run('assisted_boss_route.py',['--boss-room','0x144','--world-route',
        '--preserve-floor-hurt','--assisted-prefix','--prefix-combat',current,
        '--house-outside','0xc9','--house-target','0xaf','--axe-terrain','--live-prefix-terrain',
        '--live-room-replan','--frames',str(frames(COMBAT,current)+12000),'--trial','v0314-fairy-route01'])
    current='md-v0314-fairy-route01';finish(ROUTE,current,lambda r:r['reached_entrance'])
    run('natural_fairy_service.py',['--prefix',current,'--assisted-prefix','--outside','0xc9',
        '--trial','v0314-fairy-service01'])
    current='md-v0314-fairy-service01';finish(SERVICE,current,lambda r:r['passed'])
    run('assisted_boss_route.py',['--boss-room','0x144','--world-route',
        '--preserve-floor-hurt','--assisted-prefix','--prefix-service',current,'--door-index','2',
        '--axe-terrain','--live-prefix-terrain','--live-room-replan',
        '--frames',str(frames(SERVICE,current)+18000),'--trial','v0314-d2-entry01'])
    finish(ROUTE,'md-v0314-d2-entry01',lambda r:r['reached_entrance'])
    print('V314 ACTUAL AXE, LIFE FAIRY AND D2 ENTRANCE VERIFIED',flush=True)


if __name__=='__main__': main()
