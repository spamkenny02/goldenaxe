"""Controlled ordinary UP approach to town27's water-side house, SMS versus MD."""
import argparse
import contextlib
import io
import json
from pathlib import Path
from run_core import ROOT, run
from extract_world import initial_room
from extract_title import rle_planes
from validate_key_door_gameplay import maps
from validate_actor_tick import PRESSES
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--trial', required=True)
    a = p.parse_args()
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    source = (ROOT / 'input/original.sms').read_bytes()
    _, meta, _, _, arrays, _ = initial_room(source)
    cells = bytearray(160)
    rle_planes(arrays['world_room_streams'], int.from_bytes(arrays['world_room_index'][0x4e:0x50], 'little'), cells, 0, 1)
    smsmap, mdmap = maps(cells, meta)
    door = next(d for d in json.loads((ROOT / 'analysis/doors_reference.json').read_bytes())['direct_unconditional_doors'] if d['room'] == 0x27)
    results = []
    for region in ['auto', 'pal']:
        traces = {}
        for tag in ['sms', 'md']:
            folder = ROOT / f'validation/canoe-house-{a.trial}/{region}-{tag}'
            assert not folder.exists()
            if tag == 'sms':
                writes = [(3400, 0xb9, b'\x27\0'), (3400, 0xa4, door['script_entry'].to_bytes(2, 'little')),
                          (3400, 0xec, b'\x01'), (3400, 0x127, b'\0'), (3400, 0x1c00, bytes(cells)),
                          (3400, 0x1600, smsmap), (3400, 0x600, bytes(768)),
                          (3400, 0x301, b'\x01'), (3400, 0x303, b'\x03\0\0'), (3400, 0x30a, b'\0'),
                          (3400, 0x310, (104 << 8).to_bytes(2, 'little') + (120 << 8).to_bytes(2, 'little') + bytes(4))]
            else:
                writes = [(3400, sy['hero_items'] + 12, b'\x01'),
                          (3400, sy['game_save_state'] + 0x77, b'\0'),
                          (3400, sy['scratch'] + 0x800, bytes(cells)), (3400, sy['sms_vram'] + 0x3800, smsmap),
                          (3400, sy['world_new_md'], mdmap), (3400, sy['world_actor_state'], bytes(768))]
                for name, value in [('room_id', 0x27), ('world_graphics_class', 0), ('hero_x', 120 << 8),
                                    ('hero_y', 104 << 8), ('hero_dx', 0), ('hero_dy', 0), ('hero_state', 1),
                                    ('hero_flags', 3), ('hero_counter', 0), ('hero_hurt', 0), ('hero_direction', 0)]:
                    writes.append((3400, sy[name], value.to_bytes(2, 'big')))
            rows = []

            def observe(f, raw):
                if f < 3400:
                    return
                if tag == 'sms':
                    row = dict(frame=f, room=int.from_bytes(raw[0xb9:0xbb], 'little'), game=raw[0x1d],
                               hero=raw[0x301], x=int.from_bytes(raw[0x312:0x314], 'little'),
                               y=int.from_bytes(raw[0x310:0x312], 'little'), counter=raw[0x304])
                else:
                    word = lambda n: int.from_bytes(bytes(raw[(sy[n] + i) ^ 1] for i in range(2)), 'big')
                    row = dict(frame=f, room=word('room_id'), game=word('game_state'), hero=word('hero_state'),
                               x=word('hero_x'), y=word('hero_y'), counter=word('hero_counter'))
                if f % 10 == 0 or not rows or row['room'] != rows[-1]['room']:
                    rows.append(row)

            inputs = ([(200, 220, 0)] if tag == 'sms' else []) + PRESSES[:8] + [(3400, 3600, 4)]
            with contextlib.redirect_stdout(io.StringIO()):
                run(ROOT / ('input/original.sms' if tag == 'sms' else 'gaw-megadrive.bin'), 3750, folder,
                    {3400, 3420, 3480, 3750}, inputs, ram_writes=writes, ram_observer=observe,
                    core_options={'genesis_plus_gx_region_detect': region})
            traces[tag] = dict(entered=any(r['room'] == 0x4f for r in rows), last=rows[-1], rows=rows)
        results.append(dict(region=region, **traces))
        print(region, {tag: traces[tag]['entered'] for tag in traces}, flush=True)
    report = dict(source_sha256=sha(source), md_sha256=sha((ROOT / 'gaw-megadrive.bin').read_bytes()),
                  controlled_fixtures=True, driver_sha256=sha(Path(__file__).read_bytes()), cases=results,
                  scope='Explicit exterior map, canoe, stationary hero and empty-actor setup at3400, then ordinary UP inputs; no forced doorway velocity or house-room injection.')
    (ROOT / f'analysis/canoe_house_{a.trial}_report.json').write_bytes((json.dumps(report, indent=2) + '\n').encode())


if __name__ == '__main__':
    main()
