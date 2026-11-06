"""Measure native map publication entry cycles across the unchanged boot itinerary."""
import contextlib
import ctypes as c
import io
import json
import re
from collections import Counter
from pathlib import Path

from archive_lossless_evidence import sha
from run_core import ROOT,run


def main():
    out=ROOT/'validation/menu-raster-v0316/profile09';out.mkdir(parents=True,exist_ok=False)
    candidate=ROOT/'validation/menu-audio-v0316/candidate09'
    core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_clock_libretro.dll';dll=c.CDLL(str(core))
    dll.gaw_md_config.argtypes=[c.c_uint,c.POINTER(c.c_uint)];dll.gaw_md_event_count.restype=c.c_uint;dll.gaw_md_event_data.restype=c.POINTER(c.c_uint)
    results=[]
    for region,period in [('ntsc',896040),('pal',1070460)]:
        traces=[]
        for tag,rom,symbol_file in [('baseline',ROOT/'gaw-megadrive.bin',ROOT/'megadrive/out/release/symbol.txt'),
                                    ('candidate',candidate/'out/release/rom.bin',candidate/'out/release/symbol.txt')]:
            sy={m[2].split('.lto_priv.')[0]:int(m[1],16)for line in symbol_file.read_text().splitlines()if(m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
            watch=(c.c_uint*1)(sy['draw_map']);dll.gaw_md_config(1,watch);previous=0;events=[]
            def observe(frame,raw):
                nonlocal previous
                count=dll.gaw_md_event_count();assert count<8192;values=dll.gaw_md_event_data()
                for n in range(previous,count):
                    pc,cycles,stack=[int(values[n*3+i])for i in range(3)]
                    address=sy['intro_line']&65535
                    line=int.from_bytes(bytes(raw[(address+i)^1]for i in range(2)),'big')
                    events.append(dict(frame=frame,master_cycles_in_frame=cycles,stack=stack,intro_line=line))
                previous=count
            folder=out/(region+'-'+tag)
            with contextlib.redirect_stdout(io.StringIO()):run(rom,6500,folder,set(),[],skip_intro=False,core=core,
                ram_observer=observe,core_options={'genesis_plus_gx_region_detect':'pal'if region=='pal'else'auto'})
            (folder/'events.json').write_text(json.dumps(events,indent=2)+'\n');traces.append(events)
        assert len(traces[0])==len(traces[1])
        pairs=[dict(index=i,baseline=a,candidate=b,master_cycle_delta=(b['frame']-a['frame'])*period+b['master_cycles_in_frame']-a['master_cycles_in_frame'])for i,(a,b)in enumerate(zip(*traces))]
        histogram=Counter(row['master_cycle_delta']for row in pairs)
        results.append(dict(region=region,events=pairs,master_cycle_delta_counts=dict(sorted(histogram.items()))))
        print(region,'map-entry master-cycle deltas',dict(sorted(histogram.items())),flush=True)
    result=dict(public_md_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),candidate_md_sha256=sha((candidate/'out/release/rom.bin').read_bytes()),
                cases=results,core_sha256=sha(core.read_bytes()),driver_sha256=sha(Path(__file__).read_bytes()),
                ram_writes=0,sram_imports=0,scope='Read-only instruction entry phases. This does not yet repair or prove source raster publication.')
    target=ROOT/'analysis/menu_intro_raster_profile_v0316_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
