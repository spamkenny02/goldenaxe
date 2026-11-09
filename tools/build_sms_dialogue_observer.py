"""Read-only original dialogue observer; include the common service frontend."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from run_core import ROOT
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--target',required=True);a=p.parse_args()
out=(ROOT/'validation'/a.out).resolve();assert out.is_relative_to(ROOT/'validation') and not out.exists();out.mkdir(parents=True);assert Path(a.target).name==a.target
source=ROOT.parents[1]/'work/genesis-plus-gx/core/z80/z80.c';original=source.read_bytes();normalized=original.replace(b'\r\n',b'\n')
helper=r'''
static unsigned char gaw_dialogue_records[4096][656];
static unsigned gaw_dialogue_count;
__declspec(dllexport) unsigned gaw_dialogue_size(void) {return gaw_dialogue_count;}
__declspec(dllexport) const unsigned char *gaw_dialogue_data(void) {return &gaw_dialogue_records[0][0];}
static void gaw_dialogue_observe(unsigned pc) {
 unsigned *h;unsigned char *r;
 if((pc!=0x050c && pc!=0x0524 && pc!=0x06e3 && pc!=0x627a) || gaw_dialogue_count>=4096) return;
 r=gaw_dialogue_records[gaw_dialogue_count++];h=(unsigned *)r;
 h[0]=pc;h[1]=HLD;h[2]=work_ram[0xb9]|(work_ram[0xba]<<8);h[3]=work_ram[0xbb];
 h[4]=work_ram[0x312]|(work_ram[0x313]<<8);h[5]=work_ram[0x310]|(work_ram[0x311]<<8);
 h[6]=work_ram[0x318];h[7]=work_ram[0xdf];h[8]=work_ram[0xdd];h[9]=work_ram[0xde];
 h[10]=work_ram[0x2f];h[11]=Z80.cycles;h[12]=SPD;h[13]=RM(SPD)|(RM((SPD+1)&0xffff)<<8);
 h[14]=work_ram[0x21];h[15]=work_ram[0x37];memcpy(r+64,work_ram+0xb0,592);
}
'''
anchor=b'static void gaw_timing_observe(unsigned pc)';assert normalized.count(anchor)==1;changed=normalized.replace(anchor,helper.encode()+anchor)
anchor=b'      gaw_timing_observe(pc);';assert changed.count(anchor)==1;changed=changed.replace(anchor,b'      gaw_dialogue_observe(pc);\n'+anchor)
(out/'z80-dialogue-observer.c').write_bytes(changed)
try:
 source.write_bytes(changed)
 subprocess.run([sys.executable,str(ROOT/'tools/build_timing_core.py'),'--target',a.target,'--force-source','core/z80/z80.c','--log',str(out/'build.log')],check=True)
finally:source.write_bytes(original)
assert source.read_bytes()==original
(out/'report.json').write_text(json.dumps(dict(source_restored=True,source_sha256=hashlib.sha256(original).hexdigest(),observer_sha256=hashlib.sha256(changed).hexdigest(),core_sha256=hashlib.sha256((ROOT.parents[1]/'work/genesis-plus-gx'/a.target).read_bytes()).hexdigest(),record_bytes=656,no_emulated_writes=True),indent=2)+'\n')
