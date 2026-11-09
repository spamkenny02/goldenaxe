"""Read-only 68k title VRAM row write timings; no game writes."""
import argparse,contextlib,ctypes as c,hashlib,io,json
from run_core import ROOT,run
p=argparse.ArgumentParser();p.add_argument('--region',choices=['ntsc','pal'],required=True);p.add_argument('--out',required=True);p.add_argument('--rom',type=__import__('pathlib').Path,default=ROOT/'gaw-megadrive.bin');a=p.parse_args()
core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_title_rows_md_libretro.dll';dll=c.CDLL(str(core));dll.gaw_title_row_events.restype=c.POINTER(c.c_uint);dll.gaw_title_row_count.restype=c.c_uint;dll.gaw_title_row_reset()
out=ROOT/'validation'/a.out;assert not out.exists();events=[];previous=0

def observe(frame,ram):
 global previous
 if frame==6300:dll.gaw_title_row_reset();previous=0;return
 count=dll.gaw_title_row_count();ptr=dll.gaw_title_row_events()
 for n in range(previous,count):
  physical,address,data,vcount,vdp=[int(ptr[n*5+k]) for k in range(5)]
  if frame>6300:events.append(dict(frame=frame,physical_master_cycles=physical,address=address,data=data,vcount=vcount,vdp_cycles=vdp))
 previous=count
with contextlib.redirect_stdout(io.StringIO()):run(a.rom,6380,out/'capture',set(),[],core=core,skip_intro=False,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':'pal' if a.region=='pal' else 'auto'})
report=dict(md_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),region=a.region,no_rom_or_ram_writes=True,events=events)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(len(events),'native row writes',a.region)
