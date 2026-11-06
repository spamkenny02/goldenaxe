"""Measure original font, fade and title boundaries across attract loops."""
import argparse
import contextlib
import ctypes as c
import io
import json
from pathlib import Path
from run_core import ROOT,run
from archive_lossless_evidence import sha

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=ROOT/'validation/menu-raster-v0316/source-attract01');parser.add_argument('--core',type=Path,default=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_intro_reentry_libretro.dll');a=parser.parse_args()
    out=a.out.resolve();assert out.is_relative_to(ROOT/'validation');out.mkdir(parents=True,exist_ok=False)
    core=a.core.resolve();dll=c.CDLL(str(core));dll.gaw_timing_events.restype=c.POINTER(c.c_uint64);dll.gaw_timing_count.restype=c.c_uint;cases=[]
    for region in('ntsc','pal'):
        dll.gaw_timing_reset();previous=0;events=[];rows=[]
        def observe(frame,raw):
            nonlocal previous
            n=dll.gaw_timing_count();assert n<65536;p=dll.gaw_timing_events()
            for i in range(previous,n):
                pc,elapsed,irq,raster,clock,hl,de,bc=[int(p[i*8+j])for j in range(8)];events.append(dict(frame=frame,pc=pc,elapsed=elapsed,irq=irq,raster=raster,clock=clock,hl=hl,de=de,bc=bc))
            previous=n;rows.append(dict(frame=frame,clock=raw[0x2f],counter=raw[0x1ce2],line=raw[0x1ce0],callback=int.from_bytes(raw[0x1cec:0x1cee],'little'),timer=raw[0x30]))
        folder=out/region
        with contextlib.redirect_stdout(io.StringIO()):run(ROOT/'input/original.sms',14000,folder,set(),[],skip_intro=False,core=core,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':'pal'if region=='pal'else'auto'})
        expected=json.loads((ROOT/f'validation/menu-raster-v0316/reentry29/{region}-sms/observations.json').read_bytes());assert rows==expected
        (folder/'events.json').write_text(json.dumps(events,indent=2)+'\n');fonts=[]
        for start in(e for e in events if e['pc']==0xc98):
            first=next(e for e in events if e['elapsed']>=start['elapsed']and e['pc']==0xb56)
            last=next(e for e in events if e['elapsed']>first['elapsed']and e['pc']==0xcda)
            finish=next(e for e in events if e['elapsed']>last['elapsed']and e['pc']==0xce0)
            work=((last['elapsed']-first['elapsed'])-(last['irq']-first['irq']))//15
            fonts.append(dict(entry_frame=start['frame'],entry_clock=start['clock'],after_fade_frame=first['frame'],after_fade_clock=first['clock'],music_queue_frame=last['frame'],font_foreground_tstates=work,ready_frame=finish['frame'],ready_clock=finish['clock']))
        titles=[]
        for start in(e for e in events if e['pc']==0x1470):
            first=next(e for e in events if e['elapsed']>start['elapsed']and e['pc']==0xb56)
            end=next((e for e in events if e['elapsed']>first['elapsed']and e['pc']==0x14cf),None)
            if end:titles.append(dict(entry_frame=start['frame'],asset_start_frame=first['frame'],asset_end_frame=end['frame'],foreground_tstates=((end['elapsed']-first['elapsed'])-(end['irq']-first['irq']))//15))
        cases.append(dict(region=region,official_clock_trace_exact_frames=14000,fonts=fonts,titles=titles));print(region,fonts,flush=True)
    (out/'report.json').write_text(json.dumps(dict(cases=cases,source_sha256=sha((ROOT/'input/original.sms').read_bytes()),core_sha256=sha(core.read_bytes()),driver_sha256=sha(Path(__file__).read_bytes()),ram_writes=0),indent=2)+'\n')

if __name__=='__main__':main()
