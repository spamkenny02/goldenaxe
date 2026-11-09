"""Cold-boot MD NPC visits, with final dialogue bitmap checked against played SMS."""
import argparse
import contextlib
import hashlib
import io
import json
import re
from pathlib import Path

from run_core import ROOT, FrameWrites, compile_fixed_inputs, run
from assisted_prefix import prefix_writes, recording
from natural_dungeon_combat import walk
from validate_playable_sprite_limit import symbols


def load(path):
    return json.loads(path.read_bytes())


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--prefix', required=True, help='Relative to validation')
    p.add_argument('--sms-reference', required=True, help='Verified NPC visit trace relative to validation')
    p.add_argument('--out', required=True)
    p.add_argument('--assisted-prefix', action='store_true')
    p.add_argument('--candidate', type=Path, help='Explicit private overlay ROM with verified sibling build-report.json')
    a = p.parse_args()
    prefix = (ROOT / 'validation' / a.prefix).resolve()
    source = (ROOT / 'validation' / a.sms_reference).resolve()
    out = (ROOT / 'validation' / a.out).resolve()
    assert all(q.is_relative_to(ROOT / 'validation') for q in (prefix, source, out)) and not out.exists()
    cap = load(prefix / 'capture.json')
    reference = load(source / 'report.json')
    observations = load(source / 'dialogue_observations.json')['events']
    assert reference['passed'] and cap['sram_input'] is None
    rom = a.candidate.resolve() if a.candidate else ROOT / 'gaw-megadrive.bin'
    digest = hashlib.sha256(rom.read_bytes()).hexdigest()
    published = '89c5833351312ffaa591efb1939161910a298af06437080e2cf84fb3fb8ac86e'
    assert cap['rom_sha256'] == published
    if a.candidate:
        assert rom.is_relative_to(ROOT / 'validation')
        build = load(rom.parent / 'build-report.json')
        assert build['private_candidate'] and build['base_sha256'] == published and build['md_sha256'] == digest
        assert build['all_other_bytes_identical']
    else:
        assert digest == published
    writes = prefix_writes(prefix, cap, a.assisted_prefix)
    targets = reference['required_targets']
    data_source = (ROOT / 'megadrive/src/plain_house_data.c').read_text().split('plain_house_dialogues[][5]=', 1)[1]
    table = [tuple(map(int, row.split(','))) for row in re.findall(r'\{([\d,]+)\}', data_source)]
    for t in targets:
        t['md_index'] = next(row[4] for row in table if row[:3] == (t['room'], t['coordinate'], t['outside']))
        visit = next(v for v in reference['visited'] if v['text_pc'] == t['text_pc'])
        completion = next(e for e in observations if e['event_pc'] == 0x627a and visit['entry_frame'] < e['frame'] < visit['acknowledged_and_walked_away_frame'])
        raw = (source / f'ram_{completion["frame"] + 1:05d}.bin').read_bytes()
        t['sms_bitmap_sha256'] = hashlib.sha256(raw[0x1100:0x1510]).hexdigest()
    start = cap['frames']
    presses = list(map(tuple, cap['presses']))
    prior = load(prefix / 'controls.json')
    for i, row in enumerate(prior):
        stop = prior[i + 1]['frame'] - 1 if i + 1 < len(prior) else start
        presses.extend((row['frame'], min(stop, start), key) for key in row['buttons'])
    masks = compile_fixed_inputs(presses, start)
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    state = {}
    controls = []
    captures = set()
    visits = []
    events = []
    bitmap_samples = {}
    index = 0
    last_direction = 0
    active = False
    matched = None
    entry = None
    done = failure = None
    observed = start

    def observe(frame, raw):
        nonlocal active, matched, entry, done, failure, observed
        observed = frame
        if frame < start:
            return
        data = lambda name, length: bytes(raw[(sy[name] + n) ^ 1] for n in range(length))
        word = lambda name: int.from_bytes(data(name, 2), 'big')
        state.update(room=word('room_id'), game=word('game_state'), hero=word('hero_state'),
                     counter=word('hero_counter'), x=word('hero_x') >> 8, y=word('hero_y') >> 8,
                     health=word('hero_health'), modal=word('house_dialogue_active'),
                     dialogue_index=word('house_dialogue_index'), audio_error=word('sound_unhandled_command'))
        state['tilemap'] = data('sms_vram', 0x4000)[0x3800:0x3e00]
        if not state['health'] or state['audio_error']:
            failure = 'hero_died_or_audio_error'
        if index < len(targets) and state['modal']:
            target = targets[index]
            if state['dialogue_index'] != target['md_index']:
                failure = 'unexpected_dialogue_index'
            if not active:
                active = True
                entry = frame
                events.append(dict(frame=frame, text_pc=target['text_pc'], md_index=state['dialogue_index'], event='opened'))
            bitmap = data('scratch', 0x410)
            bitmap_hash = hashlib.sha256(bitmap).hexdigest()
            bitmap_samples.setdefault(bitmap_hash, dict(first_frame=frame, text_pc=target['text_pc'], bitmap_hex=bitmap.hex()))
            if matched is None and bitmap_hash == target['sms_bitmap_sha256']:
                matched = frame
                captures.add(frame + 1)
                events.append(dict(frame=frame, text_pc=target['text_pc'], event='final_bitmap_exact_sms', bytes=1040))
        if index == len(targets) and state['room'] == reference['outside'] and state['game'] == 12 and state['hero'] == 1 and done is None:
            done = frame
            captures.add(frame + 30)

    def choose(frame):
        nonlocal index, last_direction, active, matched, entry, failure
        if frame <= start:
            return [key for key in range(16) if masks[frame] & (1 << key)]
        if failure or done is not None:
            return []
        if active:
            if state['modal']:
                if matched is not None and frame >= matched + 30:
                    return [8] if frame % 4 == 0 else []
                return [8] if frame - entry > 180 and frame % 60 == 0 else []
            if matched is None:
                failure = 'dialogue_closed_without_matching_sms_bitmap'
                return []
            target = targets[index]
            if state['counter'] == 0 and (state['x'], state['y']) != tuple(target['point']):
                visits.append(dict(text_pc=target['text_pc'], coordinate=target['coordinate'],
                                   md_index=target['md_index'], entry_frame=entry,
                                   bitmap_exact_frame=matched, bitmap_exact_bytes=1040,
                                   sms_bitmap_sha256=target['sms_bitmap_sha256'],
                                   acknowledged_and_walked_away_frame=frame))
                index += 1
                active = False
                matched = entry = None
                return []
            return [5]
        if state.get('room') != reference['room'] or state['hero'] not in (0, 1):
            return []
        if state['counter']:
            return [4 + last_direction]
        target = tuple(targets[index]['point']) if index < len(targets) else (136, 160)
        point = state['x'], state['y']
        if point == target:
            last_direction = 0 if index < len(targets) else 1
            return [4 + last_direction]
        route = walk(state['tilemap'], point, lambda q: q == target)
        if route:
            last_direction = route[0]
            return [4 + last_direction]
        failure = 'npc_point_unreachable'
        return []

    def controller(frame):
        buttons = choose(frame)
        if frame > start and (not controls or controls[-1]['buttons'] != buttons):
            controls.append(dict(frame=frame, buttons=buttons))
        return buttons

    with contextlib.redirect_stdout(io.StringIO()):
        run(rom, start + 12000, out, captures, cap['presses'], skip_intro=False,
            ram_writes=FrameWrites(writes), ram_observer=observe, input_provider=controller,
            stop_when=lambda: bool(failure) or done is not None and observed >= done + 30,
            core_options=cap['core_options'])
    actual = load(out / 'capture.json')
    actual['presses'] = presses
    (out / 'capture.json').write_text(json.dumps(actual, indent=2) + '\n')
    result = dict(passed=done is not None and len(visits) == len(targets) and not failure,
                  failure=failure or (None if done is not None else 'frame_limit'),
                  rom_sha256=digest, sms_reference=a.sms_reference, prefix=a.prefix,
                  room=reference['room'], outside=reference['outside'], visited=visits,
                  events=events, last_state={k: v for k, v in state.items() if k != 'tilemap'},
                  ram_injections=bool(writes), new_assistance_writes=0,
                  sram_checkpoint_injection=False, primary_state_imports=0,
                  scope='Ordinary cold-boot walking and acknowledgment. Native selected dialogue and final 1040-byte bitmap match the played SMS reference. Intermediate pages, full physical pixels/audio/timing and conditional variants are not certified.')
    for name, value in [('report', result), ('controls', controls)]:
        (out / (name + '.json')).write_text(json.dumps(value, indent=2) + '\n')
    (out / 'bitmap_samples.json').write_text(json.dumps(bitmap_samples, indent=2) + '\n')
    if writes:
        (out / 'assistance.json').write_bytes((prefix / 'assistance.json').read_bytes())
        recording(out, actual)
    print(json.dumps(result), flush=True)
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
