"""Capture natural title/menu/name transitions for framewise source comparison."""
import argparse
import contextlib
import io
import json
from pathlib import Path

from archive_lossless_evidence import sha
from run_core import ROOT,run
from summarize_initial_world_candidate06 import indexed_pixels


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--pal',action='store_true');p.add_argument('--menu-ack',type=int,default=920);p.add_argument('--new-ack',type=int,default=1050)
    a=p.parse_args();out=a.out.resolve();assert out.is_relative_to(ROOT/'validation');out.mkdir(parents=True,exist_ok=False)
    captures=set(range(a.menu_ack-1,a.menu_ack+76))|set(range(a.new_ack-1,a.new_ack+76))
    inputs=[(200,220,0),(a.menu_ack,a.menu_ack+15,0),(a.new_ack,a.new_ack+15,0)]
    for tag,rom in [('sms',ROOT/'input/original.sms'),('md',a.rom)]:
        with contextlib.redirect_stdout(io.StringIO()):run(rom,a.new_ack+80,out/tag,captures,inputs,skip_intro=False,
            core_options={'genesis_plus_gx_region_detect':'pal'if a.pal else'auto'})
    differences=[];palette_differences=[]
    for frame in sorted(captures):
        s=indexed_pixels(out/'sms'/f'frame_{frame:05d}.png','sms');m=indexed_pixels(out/'md'/f'frame_{frame:05d}.png','md')
        pixels=sum(s[i:i+3]!=m[i:i+3]for i in range(0,len(s),3))
        differences.append(dict(frame=frame,pixels=pixels))
        src=(out/'sms'/f'cram_{frame:05d}.bin').read_bytes();dst=(out/'md'/f'cram_{frame:05d}.bin').read_bytes()
        bad=[];levels=[0,3,5,7]
        for n in range(32):
            value=int.from_bytes(src[n*2:n*2+2],'little')
            expected=levels[value&3]|levels[(value>>2)&3]<<3|levels[(value>>4)&3]<<6
            if int.from_bytes(dst[n*2:n*2+2],'little')!=expected:bad.append(n)
        palette_differences.append(dict(frame=frame,indices=bad))
    result=dict(md_sha256=sha(a.rom.read_bytes()),region='pal'if a.pal else'ntsc',menu_ack=a.menu_ack,new_ack=a.new_ack,
                natural_input_only=True,pixel_differences=differences,palette_differences=palette_differences,
                driver_sha256=sha(Path(__file__).read_bytes()),scope='Natural menu transitions; mismatches are measurements, not a passing whole-game fidelity assertion.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Transition captures:',result['region'],'exact normalized frames',sum(not r['pixels']for r in differences),'/',len(differences),flush=True)


if __name__=='__main__':main()
