"""Current v317 palace mechanisms and first unassisted giant."""
import json,shutil
import continue_d8_entry_v0317 as helper
from archive_lossless_evidence import sha
helper.EVIDENCE=helper.ROOT/'validation/v0317-palace-sources'

from continue_after_d9_v0317 import ROM
from continue_d8_entry_v0317 import COMBAT,ROUTE,COMMON,load,replay as validate
from continue_d8_entry_v0317 import ROOT,assert_canonical,run as execute
helper.EVIDENCE=ROOT/'validation/v0317-palace-sources'


def run(label, argv):
    print(label, flush=True)
    tool, *args = argv
    if tool.endswith(('assisted_boss_route.py', 'unassisted_dungeon_continuation.py')):
        args += ['--max-deaths', '0']
    execute(tool.removeprefix('tools/'), args)


def frames(family, name):
    return load(family, name, 'capture.json')['frames']


def replay(name, success=lambda r: True):
    validate(COMBAT, name, lambda r: r['rom_sha256'] == ROM
             and not r.get('deaths', 0) and success(r))


def campaign():
    entry = 'md-v0317-cold-palace-entry02'
    assert_canonical(ROUTE, entry)
    proof = load(ROUTE, entry, 'route_report.json')
    assert proof['palace_gate_verified'] and not proof['palace_new_map_or_resource_writes']
    assert load(ROUTE, entry, 'capture.json')['rom_sha256'] == ROM
    start = frames(ROUTE, entry)
    root = ROOT
    helper.EVIDENCE.mkdir(exist_ok=True)
    snapshot=helper.EVIDENCE/'giant-tools02';snapshot.mkdir()
    names=('assisted_boss_route.py','assisted_prefix.py','natural_dungeon_combat.py',
           'natural_contact_passage.py','close_assisted_approach.py',
           'unassisted_fast_prediction.py','unassisted_dungeon_continuation.py',
           'prediction_video_skip.py','natural_combat_beam.py',
           'natural_boss_evasive_planner.py','replay_assisted_prefix.py',
           'continue_palace_giant_v0317.py','continue_d8_entry_v0317.py')
    hashes={}
    for name in names:
        target=snapshot/name;shutil.copyfile(ROOT/'tools'/name,target)
        hashes['tools/'+name]=sha(target.read_bytes())
    (snapshot/'source_index.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
    base = ['tools/assisted_boss_route.py', '--boss-room', '0x14c',
            '--preserve-floor-hurt', *[arg for arg in COMMON if arg not in ('--max-deaths', '0')],
            '--retry-isolated-foes', '--equip-basic']

    def stage(name, planner, prior, rooms, target, extra):
        prefix = 'md-auto-v0317-cold-palace-' + prior
        trial = 'v0317-cold-palace-' + name
        run(name, base + ['--wake-sentinels', '--planner', planner,
            '--continuation', prefix, '--rooms', rooms, '--target-room', target,
            '--frames', str(frames(COMBAT, prefix) + 14000), '--trial', trial, *extra])
        name = 'md-auto-' + trial
        replay(name)
        return name

    run('switch16d',base+['--planner','contact','--mechanism-during-combat','--prefix',entry,'--rooms','0x18d,0x17d,0x16d','--target-room','0x16d','--contact-room','0x16d','--contact-destination','0x16d','--frames',str(start+12000),'--trial','v0317-cold-palace-switch16d02'])
    replay('md-auto-v0317-cold-palace-switch16d02',lambda r:r['contact_route_passed'] and not r['contact_state_writes'])
    run('pregiant',base+['--planner','contact','--wake-sentinels','--rush-rooms','0x16d','--continuation','md-auto-v0317-cold-palace-switch16d02','--rooms','0x16d,0x17d,0x18d,0x18e,0x17e,0x16e','--target-room','0x16e','--contact-room','0x16e','--contact-destination','0x16e','--frames',str(frames('natural-dungeon-combat','md-auto-v0317-cold-palace-switch16d02')+14000),'--trial','v0317-cold-palace-pre-giant02'])
    replay('md-auto-v0317-cold-palace-pre-giant02')
    run('release',['tools/close_assisted_approach.py','--trace','natural-dungeon-combat/md-auto-v0317-cold-palace-pre-giant02','--before-room','0x15e','--trial','v0317-cold-palace-giant-release02'])
    replay('md-auto-v0317-cold-palace-giant-release02')
    run('giant',['tools/unassisted_fast_prediction.py','--planner','evasive','--planning-step','32','--entry-boss-kind','0x7b','--continuation','md-auto-v0317-cold-palace-giant-release02','--assisted-prefix','--rooms','0x16e,0x15e','--target-room','0x15e','--equip-basic','--collision-aim','--settle-attacks','--doorway-ranges','--ignore-inactive-actors','--frames',str(frames('natural-dungeon-combat','md-auto-v0317-cold-palace-giant-release02')+12000),'--trial','v0317-cold-palace-giant02'])
    replay('md-auto-v0317-cold-palace-giant02', lambda r: r['room_cleared'] and not r['new_assistance_writes'])
    print('V0317 PALACE FIRST GIANT VERIFIED',flush=True)


def main():
    from cold_replay_stream import ReplayStream
    helper.EVIDENCE.mkdir(exist_ok=True)
    helper.STREAM=ReplayStream(helper.EVIDENCE/'giant-cold-stream02')
    try:campaign()
    finally:helper.STREAM.close()


if __name__=='__main__':main()
