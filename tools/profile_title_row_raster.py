"""Read-only physical SMS title-row OUTI trace; no ROM or RAM writes."""
import argparse,contextlib,ctypes as c,hashlib,io,json
from run_core import ROOT,run
p=argparse.ArgumentParser();p.add_argument('--region',choices=['ntsc','pal'],required=True);p.add_argument('--out',required=True);p.add_argument('--core',type=__import__('pathlib').Path);a=p.parse_args()
core=a.core or ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_title_row_raster_libretro.dll';dll=c.CDLL(str(core));dll.gaw_timing_events.restype=c.POINTER(c.c_uint64);dll.gaw_timing_count.restype=c.c_uint;dll.gaw_timing_reset()
out=ROOT/'validation'/a.out;assert not out.exists();events=[];previous=0

def observe(frame,ram):
 global previous
 if frame==6300:dll.gaw_timing_reset();previous=0;return
 count=dll.gaw_timing_count();ptr=dll.gaw_timing_events()
 for n in range(previous,count):
  pc,elapsed,irq,physical,clock,hl,de,bc=[int(ptr[n*8+k]) for k in range(8)]
  if frame>6300 and ((pc==0x38e and 0x7900<=de<0x7b00) or pc in [0x137,0xbb3,0x1647,0x164a]):events.append(dict(frame=frame,pc=pc,elapsed=elapsed,irq=irq,physical_master_cycles=physical,clock=clock,hl=hl,de=de,bc=bc))
 previous=count
with contextlib.redirect_stdout(io.StringIO()):run(ROOT/'input/original.sms',6380,out/'capture',set(),[],core=core,skip_intro=False,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':'pal' if a.region=='pal' else 'auto'})
assert len([e for e in events if e['pc']==0x38e])==512
report=dict(source_sha256=hashlib.sha256((ROOT/'input/original.sms').read_bytes()).hexdigest(),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),region=a.region,no_rom_or_ram_writes=True,events=events)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('512 original logo OUTIs observed',a.region)
