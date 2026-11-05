"""Play remaining palace mechanisms, Death Adder and credits on unchanged v314."""
import json, shutil
import continue_d8_entry_v0314 as helper
from continue_after_d9_v0314 import ROM
from continue_d8_entry_v0314 import ROOT, COMBAT, report, assert_canonical
from archive_lossless_evidence import sha

helper.EVIDENCE = ROOT/'validation/v0314-palace-sources'
COMMON = ['--assisted-prefix', '--max-deaths', '0', '--collision-aim',
          '--settle-attacks', '--doorway-ranges', '--ignore-inactive-actors']


def campaign():
    receipt = report(ROOT/'analysis', 'cold_palace_guardian_v0314_report.json')
    assert receipt['passed'] and receipt['actual_golden_axe_acquired']
    assert receipt['md_sha256'] == ROM == sha((ROOT/'gaw-megadrive.bin').read_bytes())
    snapshot = helper.EVIDENCE/'final-tools'
    snapshot.mkdir(exist_ok=False)
    names = ('assisted_boss_route.py', 'assisted_prefix.py', 'natural_dungeon_combat.py',
             'natural_earth_passage.py', 'natural_contact_passage.py',
             'close_assisted_approach.py', 'unassisted_dungeon_continuation.py',
             'unassisted_fast_prediction.py', 'prediction_video_skip.py',
             'natural_combat_beam.py', 'natural_boss_evasive_planner.py',
             'continue_recorded_ending.py', 'replay_assisted_prefix.py',
             'continue_palace_final_v0314.py', 'continue_d8_entry_v0314.py')
    index = {}
    for name in names:
        target = snapshot/name
        shutil.copyfile(ROOT/'tools'/name, target)
        index['tools/'+name] = sha(target.read_bytes())
    proposal_path = ROOT/'tools/recipes/palace-final-v0309.json'
    shutil.copyfile(proposal_path, snapshot/'cold_palace_final_route_proposal_v0309.json')
    (snapshot/'source_index.json').write_text(json.dumps(index, indent=2)+'\n', encoding='utf-8')
    proposal = json.loads(proposal_path.read_bytes())
    assert proposal['status'] == 'unexecuted_proposal'
    current = receipt['current_campaign_trace'].split('/')[-1]
    assert_canonical(COMBAT, current)
    for stage in proposal['stages']:
        name = stage['name']
        trial = 'v0314-cold-palace-'+name+'01'
        before = report(ROOT/'validation'/COMBAT/current, 'capture.json')['frames']
        if name == 'release':
            tool = 'close_assisted_approach.py'
            args = ['--trace', COMBAT+'/'+current, '--before-room', stage['before_room']]
        elif name == 'final':
            tool = 'unassisted_fast_prediction.py'
            args = ['--planner', 'evasive', '--planning-step', '32',
                    '--entry-boss-kind', stage['entry_boss_kind'], '--stop-on-ending',
                    '--continuation', current, *COMMON, '--equip-axe',
                    '--rooms', stage['rooms'], '--target-room', stage['target'],
                    '--frames', str(before+18000)]
        elif name == 'ending':
            tool = 'continue_recorded_ending.py'
            args = ['--trace', COMBAT+'/'+current]
        else:
            tool = 'assisted_boss_route.py'
            args = ['--boss-room', '0x14c', '--preserve-floor-hurt', *COMMON,
                    '--retry-isolated-foes', '--wake-sentinels', '--equip-axe',
                    '--planner', stage['planner'], '--continuation', current,
                    '--rooms', stage['rooms'], '--target-room', stage['target'],
                    '--frames', str(before+(30000 if name == 'switch17c' else 18000))]
            if stage.get('avoid'):
                args += ['--avoid-portal-rooms', stage['avoid']]
            if name == 'switch17c':
                args += ['--isolated-retry-portal', '0x13e', '--isolated-retry-limit', '8']
            if stage['planner'] == 'earth':
                args += ['--earth-room', stage['earth_room'], '--earth-cell', stage['earth_cell'],
                         '--earth-cast-x', str(stage['cast'][0]), '--earth-cast-y', str(stage['cast'][1]),
                         '--earth-direction', str(stage['cast'][2]), '--passage-destination', stage['target']]
            if stage['planner'] == 'contact':
                args += ['--contact-room', stage['contact_room'], '--contact-destination', stage['contact_destination']]
        helper.run(tool, [*args, '--trial', trial])
        current = 'md-auto-'+trial
        result = report(ROOT/'validation'/COMBAT/current, 'report.json')
        assert result['failure'] is None and not result.get('deaths', 0), result
        if name == 'final':
            assert result['ending_handoff_passed'] and not result['new_assistance_writes']
        elif name == 'ending':
            assert result['ending_complete'] and not result['new_assistance_writes']
        helper.STREAM.prove(COMBAT+'/'+current)
        assert_canonical(COMBAT, current)
    print('V314 DEATH ADDER, COMPLETE CREDITS AND RETURN TO INTRO VERIFIED', flush=True)


def main():
    from cold_replay_stream import ReplayStream
    helper.EVIDENCE.mkdir(exist_ok=True)
    helper.STREAM=ReplayStream(helper.EVIDENCE/'final-cold-stream')
    try:campaign()
    finally:helper.STREAM.close()


if __name__=='__main__':main()
