"""Observe native menu function entries and current audio work without writes."""
import argparse
import contextlib
import ctypes as c
import io
import json
import re
from pathlib import Path

from archive_lossless_evidence import sha
from run_core import ROOT, run
from validate_actor_tick import PRESSES


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--project',type=Path,default=ROOT)
    parser.add_argument('--out',type=Path,required=True);parser.add_argument('--pal',action='store_true');args=parser.parse_args()
    project=args.project.resolve();out=args.out.resolve();assert out.is_relative_to(ROOT/'validation');out.mkdir(parents=True,exist_ok=False)
    sy={m[2].split('.lto_priv.')[0]:int(m[1],16)for line in (project/'megadrive/out/release/symbol.txt').read_text().splitlines()if(m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
    core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_clock_libretro.dll';dll=c.CDLL(str(core))
    dll.gaw_md_config.argtypes=[c.c_uint,c.POINTER(c.c_uint)];dll.gaw_md_event_count.restype=c.c_uint;dll.gaw_md_event_data.restype=c.POINTER(c.c_uint)
    watched={value:name for name,value in sy.items()if name in ('draw_map','enter_character_name','update_name_sprites','fade_opening_palette','sound_queue_request')}
    pcs=(c.c_uint*len(watched))(*watched);dll.gaw_md_config(len(watched),pcs)
    rows=[];events=[];previous=0
    def observe(frame,raw):
        nonlocal previous
        count=dll.gaw_md_event_count();assert count<8192;p=dll.gaw_md_event_data()
        for n in range(previous,count):
            pc,cycles,stack=[int(p[n*3+i])for i in range(3)]
            if frame>=800:events.append(dict(frame=frame,function=watched[pc],master_cycles_in_frame=cycles))
        previous=count
        if frame<800:return
        def data(name,size):return bytes(raw[((sy[name]&65535)+i)^1]for i in range(size))
        audio=data('sound_ram',16)
        rows.append(dict(frame=frame,audio=list(audio),track=int.from_bytes(data('sound_current_track',2),'big'),
                         audio_work_tstates=int.from_bytes(data('sound_source_work',4),'big')))
    with contextlib.redirect_stdout(io.StringIO()):run(project/'gaw-megadrive.bin',1250,out,set(),[(200,220,0)]+PRESSES[:6],
        skip_intro=False,ram_observer=observe,core=core,core_options={'genesis_plus_gx_region_detect':'pal' if args.pal else 'auto'})
    (out/'events.json').write_text(json.dumps(events,indent=2)+'\n');(out/'observations.json').write_text(json.dumps(rows,indent=2)+'\n')
    report=dict(md_sha256=sha((project/'gaw-megadrive.bin').read_bytes()),core_sha256=sha(core.read_bytes()),
                driver_sha256=sha(Path(__file__).read_bytes()),ram_writes=0,sram_imports=0)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Native menu entries:',[e for e in events if e['function']!='update_name_sprites'],flush=True)


if __name__=='__main__':main()
