"""Bound the first input divergence without importing state or changing ROMs."""
import contextlib
import io
import json
from pathlib import Path

from archive_lossless_evidence import sha
from run_core import ROOT, run
from validate_playable_sprite_limit import symbols


def main():
    base = ROOT/'validation/opening-return-v0315'
    out = base/'input-diagnosis06'
    out.mkdir(exist_ok=False)
    source = base/'campaign-comparison06/candidate06/capture.json'
    capture = json.loads(source.read_bytes())
    presses = [tuple(row) for row in capture['presses'] if row[0] <= 3400]
    reports = []
    for tag, rom, symbol_file, delay in [
        ('v315-original', ROOT/'versions/v0315-004b593b/gaw-megadrive-v0315.bin', ROOT/'megadrive/out/release/symbol.txt', 0),
        ('candidate06-original', base/'candidate06/out/release/rom.bin', base/'candidate06/out/release/symbol.txt', 0),
        ('candidate06-delay7', base/'candidate06/out/release/rom.bin', base/'candidate06/out/release/symbol.txt', 7),
        ('sms-original', ROOT/'input/original.sms', None, 0),
        ('sms-delay7', ROOT/'input/original.sms', None, 7),
    ]:
        sy = symbols(symbol_file) if symbol_file else None
        rows = []
        def observe(frame, raw):
            if frame < 2400: return
            if sy:
                def word(name):
                    return int.from_bytes(bytes(raw[(sy[name]+i)^1] for i in range(2)), 'big')
                row = dict(room=word('room_id'), game=word('game_state'), hero=word('hero_state'),
                           x=word('hero_x')>>8, y=word('hero_y')>>8, counter=word('hero_counter'))
            else:
                row = dict(room=int.from_bytes(raw[0xb9:0xbb], 'little'), game=raw[0x1d],
                           hero=raw[0x301], x=raw[0x313], y=raw[0x311])
            rows.append(dict(frame=frame, **row))
        inputs = [(a+delay if a>=2501 else a, b+delay if a>=2501 else b, key) for a,b,key in presses]
        folder = out/tag
        with contextlib.redirect_stdout(io.StringIO()):
            run(rom, 3400, folder, {2501,2507,2512,2600,3000,3400}, inputs,
                skip_intro=False, ram_observer=observe, core_options=capture['core_options'])
        (folder/'observations.json').write_text(json.dumps(rows, indent=2)+'\n')
        ready = next(row for row in rows if row['room']==149 and row['game']==12 and row['hero']==1)
        moved = next(row for row in rows if row['room']==149 and row['game']==12 and (row['x'],row['y'])!=(136,112))
        reports.append(dict(tag=tag, first_ready=ready, first_movement=moved, final=rows[-1],
                            rom_sha256=sha(rom.read_bytes()), gameplay_input_delay=delay))
    result = dict(runs=reports, ram_writes=0, sram_imports=0,
                  recording_sha256=sha(source.read_bytes()), driver_sha256=sha(Path(__file__).read_bytes()),
                  scope='Short initial route only; delaying controls is a diagnostic, not proof of a completed campaign.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2), flush=True)


if __name__=='__main__': main()
