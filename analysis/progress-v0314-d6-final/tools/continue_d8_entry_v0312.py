"""Continue v312 through the paid route, D8 entry and unassisted intermediate."""
import hashlib,json,shutil,subprocess,sys
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
EVIDENCE=ROOT/'validation/v0312-d8-sources'

def report(folder,filename):
    return json.loads(evidence(folder/filename))

def assert_canonical(family,name):
    folder=ROOT/'validation'/family/name
    c=report(folder,'capture.json')
    proof=folder.with_name(name+f'-assisted-fixed-replay-{c["frames"]}')
    r=report(proof,'replay_report.json')
    assert r['passed'] and r['whole_ram_bytes']==65536 and r['final_png_exact']
    for stem,ext in [('ram','bin'),('frame','png')]:
        filename=f'{stem}_{c["frames"]:05d}.{ext}'
        assert evidence(folder/filename)==evidence(proof/filename)

def run(tool,args):
    print('START',tool,*args,flush=True)
    with (EVIDENCE/'commands.jsonl').open('ab') as log:
        log.write((json.dumps(dict(tool=tool,sha256=sha((ROOT/'tools'/tool).read_bytes()),arguments=args))+'\n').encode())
    subprocess.run([sys.executable,'-u',str(ROOT/'tools'/tool),*args],cwd=ROOT,check=True)

ROUTE = 'natural-dungeon-route'
SERVICE = 'natural-service-route'
COMBAT = 'natural-dungeon-combat'
COMMON = ['--assisted-prefix', '--max-deaths', '0', '--collision-aim',
          '--settle-attacks', '--doorway-ranges', '--ignore-inactive-actors']


def load(family, name, filename='report.json'):
    return report(ROOT / 'validation' / family / name, filename)


def budget(family, name, extra):
    return str(load(family, name, 'capture.json')['frames'] + extra)


def replay(family, name, success):
    filename = 'route_report.json' if family == ROUTE else 'report.json'
    result = load(family, name, filename)
    assert result['failure'] is None and success(result), result
    run('replay_assisted_prefix.py', ['--trace', family + '/' + name])
    assert_canonical(family, name)


def main():
    receipt=json.loads(evidence(ROOT/'analysis/d7_campaign_v0312_report.json'))
    assert receipt['passed'] and receipt['seventh_crystal_and_exterior_return']
    assert receipt['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    EVIDENCE.mkdir(exist_ok=False)
    source = 'md-auto-v0312-d7-03-exit01'
    assert_canonical(COMBAT, source)
    prior = load(COMBAT, source)
    assert prior['full_dungeon_cleared'] and prior['failure'] is None and prior['last_state']['ship'] == 1
    directory = EVIDENCE / 'd8-entry-and-intermediate'
    directory.mkdir()
    names = ('assisted_boss_route.py', 'assisted_prefix.py', 'natural_dungeon_route.py',
             'natural_paid_passage.py', 'natural_dungeon_combat.py', 'close_assisted_approach.py',
             'unassisted_dungeon_continuation.py', 'natural_boss_evasive_planner.py',
             'natural_boss_side_planner.py', 'natural_combat_beam.py', 'replay_assisted_prefix.py',
             'unassisted_fast_prediction.py','prediction_video_skip.py')
    hashes = {}
    for name in names:
        target = directory / name
        shutil.copyfile(ROOT / 'tools' / name, target)
        hashes[name] = hashlib.sha256(target.read_bytes()).hexdigest()
    (directory / 'source_index.json').write_text(json.dumps(hashes, indent=2) + '\n', encoding='utf-8')
    world = ['--boss-room', '0x196', '--assisted-prefix', '--world-route', '--live-room-replan',
             '--axe-terrain', '--rope-terrain','--preserve-floor-hurt']
    route = 'v0312-d8-paid3c-route01'
    run('assisted_boss_route.py', [*world, '--new-assistance-episode', '--prefix-combat', source,
        '--live-prefix-terrain', '--house-outside', '0x3c', '--house-target', '0x9f',
        '--door-entry-direction', '1', '--frames', budget(COMBAT, source, 16000), '--trial', route])
    replay(ROUTE, 'md-' + route, lambda r: r['reached_entrance'] and r['directional_probe_succeeded'])
    assert load(ROUTE, 'md-' + route, 'route_report.json')['last_state']['gold'] >= 10
    payment = 'v0312-d8-paid3c-service01'
    run('natural_paid_passage.py', ['--assisted-prefix', '--prefix', 'md-' + route,
        '--outside', '0x3c', '--trial', payment])
    replay(SERVICE, 'md-' + payment, lambda r: r['passed'] and r['price'] == 10 and r['last_state']['room'] == 0x1a)
    entry = 'v0312-d8-entry01'
    run('assisted_boss_route.py', [*world, '--prefix-service', 'md-' + payment, '--door-index', '8',
        '--frames', budget(SERVICE, 'md-' + payment, 10000), '--trial', entry])
    replay(ROUTE, 'md-' + entry, lambda r: r['reached_entrance'] and r['directional_probe_succeeded'])
    ready = 'v0312-d8-mini-ready01'
    run('assisted_boss_route.py', ['--boss-room', '0x196', '--planner', 'ordinary', *COMMON,
        '--prefix', 'md-' + entry, '--rooms', '0x1ea,0x1da,0x1ca', '--target-room', '0x1ca',
        '--retry-isolated-foes', '--wake-sentinels', '--equip-axe', '--frames', budget(ROUTE, 'md-' + entry, 14000), '--trial', ready])
    replay(COMBAT, 'md-auto-' + ready, lambda r: r['room_cleared'] and not r['deaths'])
    release = 'v0312-d8-guard-release01'
    run('close_assisted_approach.py', ['--trace', COMBAT + '/md-auto-' + ready,
                                      '--before-room', '0x1c9', '--trial', release])
    replay(COMBAT, 'md-auto-' + release, lambda r: r['last_state']['hurt'] == 0)
    fight = 'v0312-d8-midboss01'
    run('unassisted_fast_prediction.py', ['--planner', 'evasive', '--planning-step', '8',
        '--continuation', 'md-auto-' + release, '--rooms', '0x1ca,0x1c9', '--target-room', '0x1c9',
        '--equip-basic', '--frames', budget(COMBAT, 'md-auto-' + release, 12000), '--trial', fight, *COMMON])
    replay(COMBAT, 'md-auto-' + fight, lambda r: r['room_cleared'] and not r['deaths'] and not r['new_assistance_writes'])
    print('D8 ENTRY AND INTERMEDIATE FIGHT VERIFIED', flush=True)


if __name__ == '__main__':
    main()
