"""Verify visible diagnostic stops in emulator; this cannot validate a flashkit."""
import argparse
import hashlib
import json
from pathlib import Path
from run_core import ROOT, run
from finalize_md_rom import md_checksum


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--rom', required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    rom = ROOT / a.rom
    out = ROOT / a.out
    out.mkdir()
    raw = rom.read_bytes()
    assert len(raw) == 2097152 and md_checksum(raw) == int.from_bytes(raw[0x18e:0x190], 'big')
    cases = []
    for region in ['ntsc', 'pal']:
        folder = out / region
        last = None
        events = []
        captures = {100, 2000, 3000}
        intro_seen = False

        def observe(frame, ram):
            nonlocal last, intro_seen
            w = lambda n: int.from_bytes(ram[n:n+2], 'little')
            stage = w(0xe4c4)
            if stage != last:
                events.append(dict(frame=frame, stage=stage))
                last = stage
                if stage:
                    captures.add(frame+5)
            if stage == 9 and w(0xd310):
                intro_seen = True
            assert not w(0x2d12), 'Audio engine error'

        run(rom, 3000, folder, captures, [], skip_intro=False, ram_observer=observe,
            core_options={'genesis_plus_gx_region_detect': 'pal' if region == 'pal' else 'auto'})
        assert [e['stage'] for e in events] == list(range(10)), events
        assert intro_seen
        for event in events[1:]:
            f = event['frame'] + 5
            vram = (folder / f'vram_{f:05d}.bin').read_bytes()
            at = 0xe000 + 10*128 + 28
            assert int.from_bytes(vram[at:at+2], 'little') == 512+16+event['stage']
        cases.append(dict(region=region, passed=True, events=events,
                          all_nine_stage_digits_verified_in_rendered_tilemap=True,
                          original_intro_reached=True, audio_engine_errors=0))
    result = dict(passed=True, md_sha256=hashlib.sha256(raw).hexdigest(),
                  bytes=len(raw), diagnostic=True, hardware_validation_pending=True,
                  known_v325_hardware_failure=True, cases=cases,
                  scope='Instrumented boot diagnosis only. Each stage intentionally pauses90 frames. No full-campaign qualification and no claim to fix the reported physical black screen. No injected SRAM or game state.')
    (out / 'report.json').write_text(json.dumps(result, indent=2)+'\n', newline='\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
