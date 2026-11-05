"""Verify the actual D6 guard release outside the boss room on v312."""
import json
from archive_lossless_evidence import sha
from assisted_prefix import recording
from rebase_natural_campaign import evidence
from run_core import ROOT


def main():
    refs = {}

    def read(path):
        raw = evidence(ROOT / path)
        refs[path] = sha(raw)
        return raw

    def load(path):
        return json.loads(read(path))

    prior = load('analysis/d6_progress_v0312_report.json')
    digest = sha(read('gaw-megadrive.bin'))
    assert prior['passed'] and prior['md_sha256'] == digest
    start = prior['ready_trace']
    old = load(start + '/capture.json')
    before, writes_before = recording(ROOT / start, old)
    trace = 'validation/natural-dungeon-combat/md-auto-v0312-d6-release03'
    cap = load(trace + '/capture.json')
    r = load(trace + '/report.json')
    aid, writes = recording(ROOT / trace, cap)
    read(trace + '/assistance.json')
    frame = cap['frames']
    assert frame == old['frames'] + 1
    assert cap['rom_sha256'] == r['rom_sha256'] == digest and cap['sram_input'] is None
    assert r['passed'] and r['failure'] is None and not r['primary_state_imports']
    assert r['live_approach_release_requested'] and not r['room_cleared']
    assert r['closed_before_room'] == 0x115 and aid['closure_prefix'] == start.removeprefix('validation/')
    assert not before['first_boss_entry'] and not aid['first_boss_entry'] and not aid['boss_assistance']
    assert writes[:-1] == writes_before
    assert writes[-1] == (frame, writes_before[-1][1], b'\0\0')
    assert aid['release_write_frame'] == frame and aid['approach_closed_early']
    events = load(trace + '/events.json')
    assert len(events) == 2 and events[-1]['hurt'] == 0
    assert all(row['room'] == 0x125 and row['game'] == 12 for row in events)
    for key in ('room','health','gold','keys','magic','items','crystals'):
        assert events[0][key] == events[1][key]
    # The actual residual entities are ordinary splitting enemies, not bosses.
    assert events[-1]['live_approach_actors']
    assert all(e['kind'] == 0x4b for e in events[-1]['live_approach_actors'])
    proof_root = trace + f'-assisted-fixed-replay-{frame}'
    proof = load(proof_root + '/replay_report.json')
    assert proof['passed'] and proof['rom_sha256'] == digest and not proof['feedback_reads']
    assert proof['whole_ram_bytes'] == 65536 and proof['final_png_exact']
    for name in ('capture.json','controls.json','assistance.json'):
        assert proof['evidence'][name] == sha(read(trace + '/' + name))
    for stem, ext in (('ram','bin'), ('frame','png')):
        name = f'/{stem}_{frame:05d}.{ext}'
        assert read(trace + name) == read(proof_root + name)
    helper = sha(read('tools/close_assisted_approach.py'))
    assert r['driver_sha256'] == helper
    result = dict(passed=True, version=312, md_sha256=digest,
                  production_rom_unchanged=True, trace=trace, frames=frame,
                  guard_release_before_room=0x115, room=0x125,
                  live_ordinary_approach_actors=events[-1]['live_approach_actors'],
                  resources_unchanged=True, whole_ram_png_exact=True,
                  sixth_boss_entered=False, sixth_crystal_validated=False,
                  full_game_validated=False, evidence=refs,
                  limits=['Release only: one neutral frame and the final zero write outside the boss room.',
                          'Ordinary residual approach actors are retained; this is not a claim of a cleared room.',
                          'All boss and return inputs still require a separate unassisted execution and cold replay.'])
    (ROOT/'analysis/d6_guard_release_v0312_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('D6 approach guard released and cold-replayed at',frame)


if __name__ == '__main__':
    main()
