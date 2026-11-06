"""Compare every emitted framebuffer on two MD binaries, without disk frame dumps."""
import argparse
import contextlib
import hashlib
import io
import json
import struct
from pathlib import Path

from archive_lossless_evidence import sha
from run_core import ROOT,run


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--baseline',type=Path,default=ROOT/'versions/v0316-8b94f2e0/gaw-megadrive-v0316.bin');a=p.parse_args()
    out=a.out.resolve();assert out.is_relative_to(ROOT/'validation');out.mkdir(parents=True,exist_ok=False)
    results=[]
    for region in ('ntsc','pal'):
        streams=[]
        for tag,rom in [('baseline',a.baseline),('candidate',a.rom)]:
            hashes=bytearray();last=None
            def video(frame,raw,width,height,pitch,mode):
                nonlocal last
                if raw is not None:
                    row_bytes=width*(4 if mode==1 else 2)
                    pixels=raw if pitch==row_bytes else b''.join(raw[y*pitch:y*pitch+row_bytes]for y in range(height))
                    last=hashlib.sha256(struct.pack('<3I',width,height,mode)+pixels).digest()
                hashes.extend(last or bytes(32))
            folder=out/(tag+'-'+region)
            with contextlib.redirect_stdout(io.StringIO()):run(rom,6500,folder,{6500},[],skip_intro=False,
                video_observer=video,core_options={'genesis_plus_gx_region_detect':'pal'if region=='pal'else'auto'})
            assert len(hashes)==6500*32,'Every frame must reach the observer'
            (folder/'framebuffer-hashes.bin').write_bytes(hashes);streams.append(hashes)
        differences=[f for f in range(1,6501)if streams[0][(f-1)*32:f*32]!=streams[1][(f-1)*32:f*32]]
        results.append(dict(region=region,compared_frames=6500,difference_frames=differences))
        print('Emitted framebuffer comparison:',region,'different frames',len(differences),differences[:12],flush=True)
    result=dict(passed=all(not r['difference_frames']for r in results),md_sha256=sha(a.rom.read_bytes()),
                baseline_sha256=sha(a.baseline.read_bytes()),cases=results,ram_writes=0,sram_imports=0,
                driver_sha256=sha(Path(__file__).read_bytes()),frontend_sha256=sha((ROOT/'tools/run_core.py').read_bytes()),
                scope='All6500 emitted no-input boot frames per region, baseline versus candidate; not whole-source fidelity.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
