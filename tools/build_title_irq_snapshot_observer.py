"""Read-only original title IRQ snapshots; restore the exact upstream file."""
import argparse,hashlib,json,subprocess,sys
from run_core import ROOT
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--target',required=True);a=p.parse_args();assert __import__('pathlib').Path(a.target).name==a.target
out=(ROOT/'validation'/a.out).resolve();assert out.is_relative_to(ROOT/'validation') and not out.exists();out.mkdir(parents=True)
source=ROOT.parents[1]/'work/genesis-plus-gx/core/z80/z80.c';original=source.read_bytes();normalized=original.replace(b'\r\n',b'\n')
helper=r"""
__declspec(dllexport) unsigned gaw_title_video_mode(void) {return reg[0]|(reg[1]<<8)|(reg[10]<<16);}
static unsigned char gaw_title_snapshots[4096][800];
static unsigned gaw_title_snapshot_count,gaw_title_first_poll;
__declspec(dllexport) void gaw_title_snapshot_reset(void) {gaw_title_snapshot_count=0;}
__declspec(dllexport) unsigned gaw_title_snapshot_size(void) {return gaw_title_snapshot_count;}
__declspec(dllexport) const unsigned char *gaw_title_snapshot_data(void) {return &gaw_title_snapshots[0][0];}
static void gaw_title_snapshot(unsigned pc) {
 unsigned char *e;unsigned long long h[8];
 if(pc==0xb95) gaw_title_first_poll=1;
 if(pc==0xbad) {if(!gaw_title_first_poll) return;gaw_title_first_poll=0;}
 if(pc!=0x25e && pc!=0x38 && pc!=0x137 && pc!=0x1a2 && pc!=0x1a5 && pc!=0xbb3 && pc!=0xb95 && pc!=0xbad && !(pc==0x38e && DED==0x7900)) return;
 if(gaw_title_snapshot_count>=4096) return;
 e=gaw_title_snapshots[gaw_title_snapshot_count++];
 h[0]=pc;h[1]=gaw_elapsed;h[2]=gaw_irq_elapsed;h[3]=Z80.cycles;
 h[4]=v_counter;h[5]=mcycles_vdp;h[6]=lines_per_frame;h[7]=DED;
 memcpy(e,h,64);memcpy(e+64,work_ram,80);memcpy(e+144,work_ram+0x1d00,256);memcpy(e+400,work_ram+0x1e00,400);
}
"""
anchor=b'static void gaw_timing_observe(unsigned pc)';assert normalized.count(anchor)==1
changed=normalized.replace(anchor,helper.encode()+anchor)
anchor=b' gaw_timing_observe(PCD);'
if anchor not in changed:anchor=b' gaw_timing_observe(pc);'
assert changed.count(anchor)==1
changed=changed.replace(anchor,b' gaw_title_snapshot(PCD);\n'+anchor)
(out/'z80-snapshot-observer.c').write_bytes(changed)
try:
 source.write_bytes(changed)
 subprocess.run([sys.executable,str(ROOT/'tools/build_timing_core.py'),'--target',a.target,'--force-source','core/z80/z80.c','--log',str(out/'build.log')],check=True)
finally:source.write_bytes(original)
assert source.read_bytes()==original
(out/'report.json').write_text(json.dumps(dict(source_restored=True,original_sha256=hashlib.sha256(original).hexdigest(),observer_sha256=hashlib.sha256(changed).hexdigest(),core_sha256=hashlib.sha256((ROOT.parents[1]/'work/genesis-plus-gx'/a.target).read_bytes()).hexdigest(),record_bytes=800),indent=2)+'\n')
