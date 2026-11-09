"""Original SMS live IRQ/audio work snapshots, cold boot without writes."""
import argparse,contextlib,ctypes as c,hashlib,io,json,struct
from compression import zstd
from run_core import ROOT,run
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--region',choices=['ntsc','pal'],required=True);p.add_argument('--core',type=__import__('pathlib').Path);a=p.parse_args()
out=ROOT/'validation'/a.out;assert not out.exists();core=a.core or ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_title_irq_snapshot07_libretro.dll';dll=c.CDLL(str(core));dll.gaw_title_snapshot_size.restype=c.c_uint;dll.gaw_title_snapshot_data.restype=c.POINTER(c.c_uint8);dll.gaw_title_snapshot_reset()
def observe(frame,raw):
 if frame==6300:dll.gaw_title_snapshot_reset()
with contextlib.redirect_stdout(io.StringIO()):run(ROOT/'input/original.sms',6380,out/'capture',set(),[],core=core,skip_intro=False,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':'pal' if a.region=='pal' else 'auto'})
count=dll.gaw_title_snapshot_size();assert count<4096;raw=c.string_at(dll.gaw_title_snapshot_data(),count*800);(out/'snapshots.bin.zst').write_bytes(zstd.compress(raw,level=3))
mode=dll.gaw_title_video_mode();report=dict(vdp_reg0=mode&255,vdp_reg1=(mode>>8)&255,vdp_reg10=(mode>>16)&255,source_sha256=hashlib.sha256((ROOT/'input/original.sms').read_bytes()).hexdigest(),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),region=a.region,records=count,record_bytes=800,payload='64byte header (8LEu64:PC,elapsed,IRQelapsed,physical,vcount,vdpclock,lines,DE);336byte IRQ RAM(C000..C04F,DD00..DDFF);400byte audio(DE00..DF8F)',no_rom_or_ram_writes=True)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(a.region,count,'snapshots')
