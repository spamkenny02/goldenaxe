"""Compare SMS C02F to actual native intro callback counts, without state writes."""
import argparse
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
    parser=argparse.ArgumentParser();parser.add_argument('--project',type=Path,default=ROOT/'validation/menu-raster-v0316/candidate10');parser.add_argument('--out',type=Path,default=ROOT/'validation/menu-raster-v0316/logical-clock10');a=parser.parse_args()
    project=a.project.resolve();out=a.out.resolve()
    out.mkdir(parents=True,exist_ok=False)
    sy={m[2].split('.lto_priv.')[0]:int(m[1],16)for l in (project/'out/release/symbol.txt').read_text().splitlines()if(m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',l))}
    core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_clock_libretro.dll';dll=c.CDLL(str(core))
    dll.gaw_md_config.argtypes=[c.c_uint,c.POINTER(c.c_uint)];dll.gaw_md_event_count.restype=c.c_uint
    results=[]
    for region in ('ntsc','pal'):
        systems={}
        for tag,rom in [('sms',ROOT/'input/original.sms'),('md',project/'out/release/rom.bin')]:
            rows=[]
            if tag=='md':
                watch=(c.c_uint*1)(sy['intro_tick']);dll.gaw_md_config(1,watch)
            def observe(frame,raw):
                if tag=='sms':
                    row=dict(clock=raw[0x2f],callback=int.from_bytes(raw[0x1cec:0x1cee],'little'),counter=raw[0x1ce2],line=raw[0x1ce0])
                else:
                    def word(name):return int.from_bytes(bytes(raw[((sy[name]&65535)+i)^1]for i in range(2)),'big')
                    row=dict(ticks=int(dll.gaw_md_event_count()),counter=word('intro_counter'),line=word('intro_line'),running=word('intro_running'),scene=word('intro_scene'),logic_clock=word('intro_logic_clock')if 'intro_logic_clock'in sy else None)
                rows.append(dict(frame=frame,**row))
            folder=out/(region+'-'+tag)
            with contextlib.redirect_stdout(io.StringIO()):run(rom,5950,folder,set(),[],skip_intro=False,
                core=core if tag=='md'else None,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':'pal'if region=='pal'else'auto'})
            assert tag!='md'or rows[-1]['ticks']<8192
            (folder/'observations.json').write_text(json.dumps(rows,indent=2)+'\n');systems[tag]=rows
        groups=[]
        for first,last in [(150,1600),(1900,3500),(3800,5800)]:
            values=Counter((s['clock']-m['ticks'])&255 for s,m in zip(systems['sms'],systems['md'])if first<=s['frame']<=last)
            groups.append(dict(first_frame=first,last_frame=last,seed_counts=dict(values)))
        results.append(dict(region=region,groups=groups));print(region,groups,flush=True)
    (out/'report.json').write_text(json.dumps(dict(md_sha256=sha((project/'out/release/rom.bin').read_bytes()),cases=results,
        source_sha256=sha((ROOT/'input/original.sms').read_bytes()),driver_sha256=sha(Path(__file__).read_bytes()),
        ram_writes=0,sram_imports=0,scope='Clock observation only; no counter alignment or production mutation.'),indent=2)+'\n')


if __name__=='__main__':main()
