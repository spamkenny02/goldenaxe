"""Measure natural first-village merchant entry without game-state fixtures."""
import argparse
import contextlib
import io
import json
from pathlib import Path

from PIL import Image
from archive_lossless_evidence import sha
from run_core import ROOT, run
from validate_actor_tick import PRESSES
from validate_playable_sprite_limit import symbols


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rom', type=Path, default=ROOT/'gaw-megadrive.bin')
    parser.add_argument('--symbols', type=Path, default=ROOT/'megadrive/out/release/symbol.txt')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--region', choices=['auto', 'pal'], default='pal')
    args = parser.parse_args()
    out = args.out.resolve()
    assert out.is_relative_to(ROOT/'validation') and not out.exists()
    out.mkdir(parents=True)
    sy = symbols(args.symbols)
    inputs = PRESSES[:11] + [(2950,2958,7),(3000,3020,4),(3350,3490,6),
        (3520,3650,4),(3700,3708,7),(3750,3850,4),(4000,4010,8),(4200,4210,0)]
    results = {}
    for tag, rom in [('sms', ROOT/'input/original.sms'), ('md', args.rom)]:
        states = []
        def observe(frame, raw):
            if not 3700 <= frame <= 3900:
                return
            if tag == 'sms':
                state = raw[0x1d]
                room = int.from_bytes(raw[0xb9:0xbb], 'little')
            else:
                def word(name):
                    return int.from_bytes(bytes(raw[(sy[name]+i)^1] for i in range(2)), 'big')
                state, room = word('game_state'), word('room_id')
            states.append((frame, room, state))
        folder = out/tag
        with contextlib.redirect_stdout(io.StringIO()):
            run(rom,3900,folder,set(range(3700,3901)),
                ([(200,220,0)] if tag=='sms' else [])+inputs,
                ram_observer=observe,
                core_options={'genesis_plus_gx_region_detect':args.region})
        cap = json.loads((folder/'capture.json').read_bytes())
        assert not cap['test_ram_writes'] and cap['sram_input'] is None and not cap['save_states']
        start = next(f for f,room,state in states if room==0 and state==22)
        dy = 0 if tag=='sms' else 16
        final = Image.open(folder/'frame_03900.png').convert('RGB')
        panel = final.crop((0,dy,256,dy+160)).tobytes()
        black, full, empty, disabled = [], [], [], []
        for f in range(start-1,3901):
            picture = Image.open(folder/f'frame_{f:05d}.png').convert('RGB')
            field = picture.crop((0,dy,256,dy+160)).tobytes()
            if not any(field): black.append(f)
            if field==panel: full.append(f)
            if not picture.crop((0,dy+160,256,dy+192)).getbbox(): empty.append(f)
            if not (folder/f'vdp_regs_{f:05d}.bin').read_bytes()[1]&0x40: disabled.append(f)
        assert full and not empty and not disabled
        results[tag] = dict(rom_sha256=cap['rom_sha256'],first_service_state=start,
            first_settled_panel=full[0],playfield_black_frames=black,
            hud_empty_frames=empty,display_disabled_frames=disabled)
    result = dict(region=args.region,observations=results,
        settled_panel_delta_frames=results['md']['first_settled_panel']-results['sms']['first_settled_panel'],
        black_window_exact=results['md']['playfield_black_frames']==results['sms']['playfield_black_frames'],
        driver_sha256=sha(Path(__file__).read_bytes()),symbols_sha256=sha(args.symbols.read_bytes()),
        scope='Natural first-village walk and controller input only. Measures complete settled panel and black window; not all towns,portrait masks,audio or whole-source timing.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':
    main()
