"""Measure original scene loads, full-IRQ waits and asset work, read-only."""
import contextlib
import ctypes as c
import io
import json
from pathlib import Path

from archive_lossless_evidence import sha
from run_core import ROOT,run


def main():
    out=ROOT/'validation/menu-raster-v0316/source-loads01';out.mkdir(parents=True,exist_ok=False)
    core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_intro_loader_libretro.dll';dll=c.CDLL(str(core))
    dll.gaw_timing_events.restype=c.POINTER(c.c_uint64);dll.gaw_timing_count.restype=c.c_uint
    selected={0xce0,0xe54,0xe57,0xe66,0xe72,0xe83,0xea0,0xdd2,0xea5,0xefa,0xf09,0xf1e,0x384,0x396,0xbb3}
    cases=[]
    for region in ('ntsc','pal'):
        dll.gaw_timing_reset();previous=0;events=[];rows=[];scene=0
        def observe(frame,raw):
            nonlocal previous,scene
            count=dll.gaw_timing_count();assert count<32768
            ptr=dll.gaw_timing_events()
            for n in range(previous,count):
                pc,cycles,irq,room,clock,hl,de,bc=[int(ptr[n*8+i])for i in range(8)]
                if pc==0xe54:scene+=1
                elif pc==0xdd2:scene=3
                if pc in selected:events.append(dict(frame=frame,scene=scene,pc=pc,master_cycles=cycles,irq_master_cycles=irq,clock=clock,hl=hl,de=de,bc=bc))
            previous=count
            rows.append(dict(frame=frame,clock=raw[0x2f],callback=int.from_bytes(raw[0x1cec:0x1cee],'little'),counter=raw[0x1ce2],line=raw[0x1ce0]))
        folder=out/region
        with contextlib.redirect_stdout(io.StringIO()):run(ROOT/'input/original.sms',3800,folder,set(),[],skip_intro=False,core=core,
            ram_observer=observe,core_options={'genesis_plus_gx_region_detect':'pal'if region=='pal'else'auto'})
        expected=json.loads((ROOT/'validation/menu-raster-v0316/logical-clock10'/(region+'-sms')/'observations.json').read_bytes())[:3800]
        assert rows==expected,'Observer must preserve the official core source clock/scene trace'
        (folder/'events.json').write_text(json.dumps(events,indent=2)+'\n');loads=[]
        for number in (1,2,3):
            start=next(e for e in events if e['scene']==number and e['pc']in(0xe54,0xdd2))
            ready=next(e for e in events if e['scene']==number and e['pc']==0xe83)
            full=[e for e in events if start['master_cycles']<e['master_cycles']<ready['master_cycles'] and e['pc']==0xbb3]
            entry=next((e for e in events if e['scene']==number and e['pc']==0xe57),None)
            finish=next((e for e in events if e['scene']==number and e['pc']==0xe72),None)
            work=None
            if entry and finish:
                work=((finish['master_cycles']-entry['master_cycles'])-(finish['irq_master_cycles']-entry['irq_master_cycles']))//15
            loads.append(dict(scene=number,start_frame=start['frame'],start_clock=start['clock'],ready_frame=ready['frame'],ready_clock=ready['clock'],
                              full_irq_returns=[dict(frame=e['frame'],clock=e['clock'])for e in full],asset_foreground_tstates=work))
        seed=next(e['clock']for e in events if e['pc']==0xce0)
        cases.append(dict(region=region,initial_logic_clock=seed,loads=loads,official_clock_trace_exact_frames=3800))
        print(region,'source loads:',loads,'clock at CE0',seed,flush=True)
    (out/'report.json').write_text(json.dumps(dict(source_sha256=sha((ROOT/'input/original.sms').read_bytes()),core_sha256=sha(core.read_bytes()),
        cases=cases,ram_writes=0,sram_imports=0,driver_sha256=sha(Path(__file__).read_bytes())),indent=2)+'\n')


if __name__=='__main__':main()
