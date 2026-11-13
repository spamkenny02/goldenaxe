"""Check empty Continue slots and black gameplay margins after native splash."""
import argparse
import csv
import hashlib
import json
import numpy as np
from PIL import Image
from run_core import ROOT, run, FrameWrites
from validate_playable_sprite_limit import symbols


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--rom', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--offset-ntsc', required=True, type=int)
    p.add_argument('--offset-pal', required=True, type=int)
    a = p.parse_args()
    rom, out = ROOT / a.rom, ROOT / a.out
    out.mkdir()
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    cases = []
    for region, off in [('ntsc', a.offset_ntsc), ('pal', a.offset_pal)]:
        for fill in [0, 255, 254, "mixed"]:
            folder = out / f'{region}-empty-{fill}'
            source = out / f'sram-{fill}.srm'
            image=bytearray(bytes([fill if isinstance(fill,int) else 255])*32768)
            if fill == 'mixed':
                for slot,name in enumerate([b'A'+bytes([255])*7,bytes([127])+b'ABCDEFG',b'AB'+bytes([254])*6]):
                    for n,c in enumerate(name):image[2*(0x400+slot*0x400+n)+1]=c
            source.write_bytes(image)
            presses = [(200,220,0), (920,935,0), (1000,1010,5), (1050,1065,8),
                       (1250,1260,4), (1300,1310,8)]
            presses = [(lo+off, hi+off, b) for lo,hi,b in presses]
            seen = False

            def observe(f, ram):
                nonlocal seen
                if f == off+1400:
                    assert int.from_bytes(ram[sy['save_service_phase']:sy['save_service_phase']+2], 'little') == 4, 'Invalid slot loaded'
                if f == off+1200:
                    sms = bytes(ram[(sy['sms_vram']+i)^1] for i in range(16384))
                    assert int.from_bytes(ram[0xe3f8:0xe3fa], 'little') == 0
                    assert int.from_bytes(ram[sy['save_service_phase']:sy['save_service_phase']+2], 'little') == 4
                    for slot in range(3):
                        at = 0x38ac+slot*0xc0
                        assert sms[at:at+16] == bytes.fromhex('ff18')*8
                    seen = True

            run(rom, 1500+off, folder, {1200+off,1400+off}, presses,
                skip_intro=False, sram_in=source, ram_observer=observe,
                core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
            assert seen
            vram = (folder / f'vram_{1200+off:05d}.bin').read_bytes()
            # All B-plane cells under the name rows must use the initialized
            # solid backdrop, never the diagnostic's recyclable pattern512.
            for slot in range(3):
                y = (0x38ac+slot*0xc0-0x3800)//64+2
                for x in range(32):
                    at = 0xc000+y*128+x*2
                    assert int.from_bytes(vram[at:at+2], 'little') == 0x4001
            cases.append(dict(region=region, sram_fill=fill, empty_names=True, invalid_slot_load_refused=True,
                              diagnostic_background_tile_absent=True))

        presses = []
        writes = FrameWrites()
        for row in csv.DictReader((ROOT / f'testkit/routes/md_{region}.csv').open()):
            lo,hi,mask,guard = (int(row[k]) for k in ['start','end','mask','guard'])
            if lo > 8000:
                break
            presses.extend((lo+off,hi+off,b) for b in range(16) if mask&(1<<b))
            if guard != -1:
                writes.extend((f+off,sy['hero_hurt'],guard.to_bytes(2,'big')) for f in range(lo,min(hi,8000)+1))
        folder = out / (region+'-game')
        frames = {n+off for n in [2700,4000,6000,8000]}
        run(rom, 8000+off, folder, frames, presses, skip_intro=False, ram_writes=writes,
            core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
        for f in frames:
            pixels = np.asarray(Image.open(folder / f'frame_{f:05d}.png'))
            assert not pixels[:16].any() and not pixels[208:].any(), (region,f,'non-black margin')
            vram = (folder / f'vram_{f:05d}.bin').read_bytes()
            for plane in [0xc000,0xe000]:
                for y in [0,1,26,27]:
                    assert vram[plane+y*128:plane+y*128+64] == bytes(64)
        cases.append(dict(region=region, gameplay_margin_frames=sorted(frames),
                          upper_and_lower_margins_black=True, margin_tilemaps_zero=True))
    result = dict(passed=True, md_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),
                  cases=cases, scope='Actual boot and recorded controls: erased00/FF, nonuniform and invalidFE SRAM name rows and B-plane backgrounds; four early gameplay frames per region with black16-pixel margins and empty margin tilemaps. Existing declared approach protection only. No physical-console confirmation.')
    (out / 'report.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    print(json.dumps(result),flush=True)


if __name__ == '__main__':
    main()
