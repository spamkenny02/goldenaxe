"""Build a read-only MD title VRAM-write observer; restore upstream source."""
import argparse,hashlib,json,subprocess,sys
from run_core import ROOT
p=argparse.ArgumentParser();p.add_argument('--out',default='title-row-native-observer02');p.add_argument('--target',default='genesis_plus_gx_title_rows_md_libretro.dll');a=p.parse_args();assert __import__('pathlib').Path(a.target).name==a.target
path=ROOT.parents[1]/'work/genesis-plus-gx/core/vdp_ctrl.c';original=path.read_bytes();out=(ROOT/'validation'/a.out).resolve();assert out.is_relative_to(ROOT/'validation') and not out.exists();out.mkdir(parents=True)
anchor=b'static void vdp_68k_data_w_m5(unsigned int data)\n{';normalized=original.replace(b'\r\n',b'\n');assert normalized.count(anchor)==1
observer=b'\nstatic unsigned gaw_title_rows[8192][5],gaw_title_count;\n__declspec(dllexport) void gaw_title_row_reset(void) {gaw_title_count=0;}\n__declspec(dllexport) unsigned gaw_title_row_count(void) {return gaw_title_count;}\n__declspec(dllexport) const unsigned *gaw_title_row_events(void) {return &gaw_title_rows[0][0];}\nstatic void gaw_title_row_observe(unsigned data) {\n if((code&0xf)==1 && addr>=0xe080 && addr<0xe280 && gaw_title_count<8192) {\n  unsigned *e=gaw_title_rows[gaw_title_count++];\n  e[0]=m68k.cycles;e[1]=addr;e[2]=data;e[3]=v_counter;e[4]=mcycles_vdp;\n }\n}\n'
changed=normalized.replace(anchor,observer+anchor)
a=changed.index(anchor);b=changed.index(b'static unsigned int vdp_68k_data_r_m4',a);part=changed[a:b];needle=b'  /* Write data */\n  vdp_bus_w(data);';assert part.count(needle)==1
part=part.replace(needle,b'  gaw_title_row_observe(data);\n'+needle);changed=changed[:a]+part+changed[b:]
(out/'vdp-rows-observer.c').write_bytes(changed)
try:
 path.write_bytes(changed)
 subprocess.run([sys.executable,str(ROOT/'tools/build_timing_core.py'),'--target',a.target,'--force-source','core/vdp_ctrl.c','--log',str(out/'build.log')],check=True)
finally:path.write_bytes(original)
assert path.read_bytes()==original
(out/'report.json').write_text(json.dumps(dict(source_restored=True,source_sha256=hashlib.sha256(original).hexdigest(),observer_sha256=hashlib.sha256(changed).hexdigest(),core_sha256=hashlib.sha256((ROOT.parents[1]/'work/genesis-plus-gx'/a.target).read_bytes()).hexdigest()),indent=2)+'\n')
