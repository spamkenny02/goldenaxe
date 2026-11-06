"""Compare all boot viewport pixels to SMS, auditing every changed baseline pixel."""
import argparse
import contextlib
import hashlib
import io
import json
import zlib
from pathlib import Path

import numpy as np

from archive_lossless_evidence import sha
from run_core import ROOT,run


def palette_lookup(system):
    values=np.arange(65536,dtype=np.uint32)
    channels=[((values>>11)&31)*255//31,((values>>5)&63)*255//63,(values&31)*255//31]
    levels=([0,82,172,255],[0,85,170,255],[0,82,172,255])if system=='sms'else([0,98,172,238],[0,102,170,238],[0,98,172,238])
    result=np.zeros(65536,dtype=np.uint8)
    for n,(channel,steps)in enumerate(zip(channels,levels)):
        index=np.abs(channel.astype(np.int16)[:,None]-np.asarray(steps,dtype=np.int16)).argmin(axis=1)
        result|=index.astype(np.uint8)<<(n*2)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--baseline',type=Path,default=ROOT/'versions/v0316-8b94f2e0/gaw-megadrive-v0316.bin');p.add_argument('--pal',action='store_true');p.add_argument('--frames',type=int,default=6500);a=p.parse_args()
    out=a.out.resolve();assert out.is_relative_to(ROOT/'validation');out.mkdir(parents=True,exist_ok=False)
    region='pal'if a.pal else'ntsc';frames=a.frames;assert frames>0;baseline=[];baseline_hashes=[];changed={};candidate_hashes=[];records=[];frame_errors=[]
    totals=dict(baseline_source_differences=0,candidate_source_differences=0,baseline_exact_frames=0,candidate_exact_frames=0)
    for tag,rom in [('baseline',a.baseline),('candidate',a.rom),('sms',ROOT/'input/original.sms')]:
        lookup=palette_lookup('sms'if tag=='sms'else'md');seen=0;last=bytes(256*192);hashes=bytearray()
        def observe(frame,raw,width,height,pitch,mode):
            nonlocal seen,last
            if raw is not None:
                if mode!=2:raise ValueError(('Unexpected pixel format',mode,width))
                pixels=np.frombuffer(raw,dtype='<u2').reshape(height,pitch//2)[:,:width]
                top=0 if tag=='sms'else 16
                # Match Pillow crop: crop a wider startup mode, and pad a
                # shorter startup mode with black instead of dropping frames.
                view=np.zeros((192,256),dtype=np.uint16)
                rows=max(0,min(192,height-top));columns=min(256,width)
                if rows:view[:rows,:columns]=pixels[top:top+rows,:columns]
                last=lookup[view].tobytes()
            digest=hashlib.sha256(last).digest();hashes.extend(digest);seen+=1
            if tag=='baseline':baseline.append(zlib.compress(last,1));baseline_hashes.append(digest)
            elif tag=='candidate':
                candidate_hashes.append(digest)
                if digest!=baseline_hashes[frame-1]:changed[frame]=last
            else:
                old=np.frombuffer(zlib.decompress(baseline[frame-1]),dtype=np.uint8);source=np.frombuffer(last,dtype=np.uint8)
                old_errors=int(np.count_nonzero(old!=source));totals['baseline_source_differences']+=old_errors
                totals['baseline_exact_frames']+=not old_errors
                if frame in changed:
                    new=np.frombuffer(changed[frame],dtype=np.uint8);different=old!=new;old_correct=old==source;new_correct=new==source
                    new_errors=int(np.count_nonzero(new!=source))
                    records.append(dict(frame=frame,changed_pixels=int(different.sum()),
                        improved_pixels=int((different&~old_correct&new_correct).sum()),
                        degraded_pixels=int((different&old_correct&~new_correct).sum()),
                        neither_matches_source=int((different&~old_correct&~new_correct).sum()),
                        baseline_source_differences=old_errors,candidate_source_differences=new_errors))
                else:new_errors=old_errors
                totals['candidate_source_differences']+=new_errors;totals['candidate_exact_frames']+=not new_errors
                frame_errors.append([old_errors,new_errors])
        folder=out/tag
        with contextlib.redirect_stdout(io.StringIO()):run(rom,frames,folder,{frames},[],skip_intro=False,video_observer=observe,
            core_options={'genesis_plus_gx_region_detect':'pal'if a.pal else'auto'})
        assert seen==frames and len(hashes)==frames*32,'Every emitted frame must be observed'
        (folder/'normalized-frame-hashes.bin').write_bytes(hashes)
        print('Source boot comparison stage complete:',region,tag,flush=True)
    result=dict(region=region,frames=frames,md_sha256=sha(a.rom.read_bytes()),baseline_sha256=sha(a.baseline.read_bytes()),
                source_sha256=sha((ROOT/'input/original.sms').read_bytes()),totals=totals,changed_frames=records,
                improved_pixels=sum(r['improved_pixels']for r in records),degraded_pixels=sum(r['degraded_pixels']for r in records),
                ram_writes=0,sram_imports=0,driver_sha256=sha(Path(__file__).read_bytes()),
                scope='Every no-input boot frame in the normalized192-line viewport. Hardware DAC levels mapped to original2-bit color indices. Does not prove game progression or other inputs.')
    result['no_source_pixel_regression']=not result['degraded_pixels']
    (out/'source-pixel-errors-by-frame.json').write_text(json.dumps(frame_errors)+'\n')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(region,'source comparison:',totals,'improved',result['improved_pixels'],'degraded',result['degraded_pixels'],flush=True)


if __name__=='__main__':main()
