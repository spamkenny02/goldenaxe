"""Playable old/new hero conversion pixels and function-entry CPU spans."""
import contextlib
import argparse
import ctypes as c
import io
import json
import re
import statistics
import subprocess
from run_core import ROOT, run
from rebase_natural_campaign import evidence
from validate_actor_tick import PRESSES
from archive_lossless_evidence import sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trial', default='02')
    args = parser.parse_args()
    base = ROOT / ('validation/hero-pattern-fast-v0286-' + args.trial)
    baseline = base / 'baseline'
    baseline.mkdir(parents=True, exist_ok=True)
    for name in ['symbol.txt', 'rom.out']:
        (baseline / name).write_bytes(evidence(ROOT / 'validation/stack-v0285-d2-keys-all' / name))
    old = ROOT / 'versions/v0285-9961a313/gaw-megadrive-v0285.bin'
    new = ROOT / 'gaw-megadrive.bin'
    core = ROOT.parents[1] / 'work/genesis-plus-gx/genesis_plus_gx_clock_libretro.dll'
    dll = c.CDLL(str(core))
    dll.gaw_md_config.argtypes = [c.c_uint, c.POINTER(c.c_uint)]
    dll.gaw_md_event_count.restype = c.c_uint
    dll.gaw_md_event_data.restype = c.POINTER(c.c_uint)
    cases = []
    for region, lines in [('auto', 262), ('pal', 313)]:
        results = {}
        for tag, rom, build in [('old', old, baseline), ('new', new, ROOT / 'megadrive/out/release')]:
            raw_symbols = (build / 'symbol.txt').read_text()
            sy = {m[2].split('.lto_priv.')[0]: int(m[1], 16) for line in raw_symbols.splitlines()
                  if (m := re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)', line))}
            name = next(line.split()[2] for line in raw_symbols.splitlines() if ' prepare_hero_patterns' in line)
            asm = subprocess.check_output([str(ROOT.parents[1] / 'work/sgdk/bin/objdump.exe'), '-d',
                                           '--disassemble=' + name, str(build / 'rom.out')], text=True)
            returns = {int(m[1], 16) for line in asm.splitlines() if '\trts' in line and
                       (m := re.match(r'\s*([0-9a-fA-F]+):', line))}
            assert returns
            watched = {sy['prepare_hero_patterns'], sy['world_vint']} | returns
            pcs = (c.c_uint * len(watched))(*watched)
            dll.gaw_md_config(len(watched), pcs)
            pending = None
            interrupted = False
            spans = []
            states = []
            previous_pose = None

            def observe(frame, ram):
                nonlocal pending, interrupted, previous_pose
                frame_spans = []
                count = dll.gaw_md_event_count()
                assert count < 8192
                data = dll.gaw_md_event_data()
                for i in range(count):
                    pc, cycles = int(data[i * 3]), int(data[i * 3 + 1])
                    timestamp = (frame - 1) * lines * 3420 + cycles
                    if pc == sy['prepare_hero_patterns']:
                        assert pending is None
                        pending, interrupted = timestamp, False
                    elif pc == sy['world_vint'] and pending is not None:
                        interrupted = True
                    elif pc in returns and pending is not None:
                        if not interrupted and timestamp - pending > 2000:
                            frame_spans.append(timestamp - pending)
                        pending = None
                dll.gaw_md_config(len(watched), pcs)
                pose_address = sy['hero_loaded_pose'] & 65535
                pose = int.from_bytes(bytes(ram[(pose_address + k) ^ 1] for k in range(2)), 'big')
                if previous_pose is not None and pose != previous_pose:
                    spans.extend(frame_spans)
                previous_pose = pose
                if 2600 <= frame <= 3160:
                    data_ram = lambda name, size: bytes(ram[((sy[name] + k) & 65535) ^ 1] for k in range(size))
                    states.append(dict(frame=frame, pose=int.from_bytes(data_ram('hero_loaded_pose', 2), 'big'),
                                       tiles=int.from_bytes(data_ram('hero_pattern_tiles', 2), 'big'),
                                       pixels=sha(data_ram('md_patterns', 16384)[496 * 32:512 * 32])))

            folder = base / f'{region}-{tag}'
            assert not folder.exists()
            with contextlib.redirect_stdout(io.StringIO()):
                run(rom, 3160, folder, {2600, 2800, 3000, 3160}, PRESSES,
                    core=core, ram_observer=observe, core_options={'genesis_plus_gx_region_detect': region})
            assert spans
            results[tag] = dict(sha256=sha(rom.read_bytes()), spans=spans, states=states)
            (folder / 'observations.json').write_text(json.dumps(results[tag], indent=2) + '\n')
        differences = [a['frame'] for a, b in zip(results['old']['states'], results['new']['states']) if a != b]
        before = statistics.median(results['old']['spans'])
        after = statistics.median(results['new']['spans'])
        assert not differences, (region, differences[:20])
        assert after < before
        cases.append(dict(region=region, frames=561, hero_pose_and_packed_pixels_exact=True,
                          old_median_master_cycles=before, new_median_master_cycles=after,
                          reduction_percent=round((before - after) * 100 / before, 2),
                          old_spans=len(results['old']['spans']), new_spans=len(results['new']['spans'])))
    report = dict(passed=True, md_sha256=sha(new.read_bytes()), baseline_sha256=sha(old.read_bytes()),
                  cases=cases, read_only=True, full_game_validated=False,
                  limits=['Function spans exclude overlapping IRQs and unchanged-pose calls. This is hero preparation CPU cost, not global FPS or complete source-clock parity.','Natural scripted hero/three-scroll sequence only; long campaign recordings may diverge and must be regenerated.'])
    (ROOT / 'validation/hero_pattern_fast_v0286_report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
