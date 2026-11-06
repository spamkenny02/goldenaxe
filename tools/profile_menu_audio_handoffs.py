"""Observe existing SMS timing hooks around menu font transfers; no ROM writes."""
import contextlib
import ctypes as c
import io
import json
from pathlib import Path

from archive_lossless_evidence import sha
from run_core import ROOT, run
from validate_actor_tick import PRESSES


def main():
    core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_clock_libretro.dll'
    dll=c.CDLL(str(core));dll.gaw_timing_events.restype=c.POINTER(c.c_uint64);dll.gaw_timing_count.restype=c.c_uint
    base=ROOT/'validation/menu-audio-v0316/source-profile01';base.mkdir(parents=True,exist_ok=False)
    reports=[]
    for pal in (False,True):
        region='pal' if pal else 'ntsc';events=[];rows=[];previous=0
        def observe(frame,raw):
            nonlocal previous
            if frame==800:dll.gaw_timing_reset();previous=0
            if frame<800:return
            count=dll.gaw_timing_count();assert count<32768
            values=dll.gaw_timing_events()
            for n in range(previous,count):
                pc,cycles,irq,room,clock,hl,de,bc=[int(values[n*8+i])for i in range(8)]
                events.append(dict(frame=frame,pc=pc,master_cycles=cycles,irq_master_cycles=irq,clock=clock,hl=hl,de=de,bc=bc))
            previous=count
            rows.append(dict(frame=frame,clock=raw[0x2f],irq_pending=raw[0x2e],game=raw[0x1d],
                             audio=list(raw[0x1e00:0x1e10])))
        folder=base/region
        with contextlib.redirect_stdout(io.StringIO()):
            run(ROOT/'input/original.sms',1250,folder,set(),[(200,220,0)]+PRESSES[:6],
                core=core,skip_intro=False,ram_observer=observe,
                core_options={'genesis_plus_gx_region_detect':'pal' if pal else 'auto'})
        (folder/'events.json').write_text(json.dumps(events,indent=2)+'\n')
        (folder/'observations.json').write_text(json.dumps(rows,indent=2)+'\n')
        reports.append(dict(region=region,events=len(events),counter_holds=[r['frame']for a,r in zip(rows,rows[1:])if a['audio'][4]==r['audio'][4]]))
        print(region,'selected events near phase changes',[(e['frame'],hex(e['pc']),hex(e['de']),hex(e['bc']))for e in events if 947<=e['frame']<=952 or 1199<=e['frame']<=1203],flush=True)
    (base/'report.json').write_text(json.dumps(dict(source_sha256=sha((ROOT/'input/original.sms').read_bytes()),
        core_sha256=sha(core.read_bytes()),driver_sha256=sha(Path(__file__).read_bytes()),cases=reports,
        ram_writes=0,sram_imports=0),indent=2)+'\n')


if __name__=='__main__':main()
