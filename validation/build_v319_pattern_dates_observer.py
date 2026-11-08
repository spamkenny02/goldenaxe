"""Capture original032A port dates, separating actual IRQ work, read-only."""
import difflib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
out=root/'validation/v319-pattern-dates-observer01';assert not out.exists();out.mkdir()
core=root.parents[1]/'work/genesis-plus-gx';target=core/'genesis_plus_gx_v319_pattern_dates_libretro.dll';assert not target.exists()
paths=[core/'core/z80/z80.c',core/'core/memz80.c',core/'core/vdp_ctrl.c'];original={p:p.read_bytes() for p in paths}
z80=original[paths[0]];sig=b'static void gaw_timing_observe(unsigned pc)\r\n{'
if sig not in z80:sig=sig.replace(b'\r\n',b'\n')
bridge=b'''static unsigned gaw_pd_rows[40000][8],gaw_pd_count,gaw_pd_overflow,gaw_pd_active,gaw_pd_seen,gaw_pd_pc,gaw_pd_cycle;
static unsigned long long gaw_pd_origin,gaw_pd_irq_origin;
__declspec(dllexport) const unsigned *gaw_pattern_dates(void) {return &gaw_pd_rows[0][0];}
__declspec(dllexport) unsigned gaw_pattern_date_count(void) {return gaw_pd_count;}
__declspec(dllexport) unsigned gaw_pattern_date_overflow(void) {return gaw_pd_overflow;}
__declspec(dllexport) void gaw_pattern_date_reset(void) {gaw_pd_count=gaw_pd_overflow=gaw_pd_active=gaw_pd_seen=0;}
static void gaw_pd_record(unsigned kind,unsigned port,unsigned value,unsigned extra)
{
 unsigned *e;unsigned long long elapsed=gaw_elapsed-gaw_pd_origin+extra;
 if(gaw_pd_count>=40000) {gaw_pd_overflow++;return;}
 e=gaw_pd_rows[gaw_pd_count++];e[0]=kind;e[1]=gaw_pd_active;e[2]=(unsigned)(elapsed-(gaw_irq_elapsed-gaw_pd_irq_origin));
 e[3]=(unsigned)elapsed;e[4]=port;e[5]=value;e[6]=HLD;e[7]=DED;
}
void gaw_pattern_date_out(unsigned port,unsigned data)
{
 if(gaw_pd_active && !gaw_irq_active && ((port&0xc0)==0x80))
  gaw_pd_record(1,port&255,data,Z80.cycles-gaw_pd_cycle);
}
'''
hook=b'''
 gaw_pd_pc=pc;gaw_pd_cycle=Z80.cycles;
 if(!gaw_irq_active && pc==0x032a && work_ram[0x1fff]==6)
 {
  unsigned id=HLD==0x9d74?1:HLD==0xa659?2:0;
  if(id && !(gaw_pd_seen&(1<<id)))
  {gaw_pd_seen|=1<<id;gaw_pd_active=id;gaw_pd_origin=gaw_elapsed;gaw_pd_irq_origin=gaw_irq_elapsed;gaw_pd_record(0,0,0,0);}
 }
 if(gaw_pd_active && !gaw_irq_active && pc==0x0364) {gaw_pd_record(2,0,0,150);gaw_pd_active=0;}
'''
assert z80.count(sig)==1;z80=z80.replace(sig,bridge+sig+hook)
mem=original[paths[1]];sig=b'void z80_ms_port_w(unsigned int port, unsigned char data)\r\n{'
if sig not in mem:sig=sig.replace(b'\r\n',b'\n')
assert mem.count(sig)==1;mem=b'void gaw_pattern_date_out(unsigned,unsigned);\n'+mem.replace(sig,sig+b'\n gaw_pattern_date_out(port,data);')
changed={paths[0]:z80,paths[1]:mem,paths[2]:original[paths[2]]};patch=[]
for p in paths:
 (out/(p.stem+'-before.c')).write_bytes(original[p]);(out/(p.stem+'-observer.c')).write_bytes(changed[p])
 patch.extend(difflib.unified_diff(original[p].decode().splitlines(True),changed[p].decode().splitlines(True),fromfile=p.relative_to(core).as_posix(),tofile=p.relative_to(core).as_posix(),n=0))
(out/'instrumentation.patch').write_text(''.join(patch));(out/'reference-license.txt').write_bytes((core/'LICENSE.txt').read_bytes())
try:
 for p in paths:p.write_bytes(changed[p])
 cmd=[sys.executable,str(root/'tools/build_timing_core.py'),'--target',target.name,'--log',str(out/'build.log')]
 for p in paths:cmd+=['--force-source',p.relative_to(core).as_posix()]
 subprocess.run(cmd,cwd=root,check=True)
finally:
 for p in paths:p.write_bytes(original[p])
assert all(p.read_bytes()==original[p] for p in paths)
(out/'report.json').write_text(json.dumps(dict(passed=True,core=str(target),core_sha256=sha(target.read_bytes()),original_sources_restored=True,original_source_sha256={p.relative_to(core).as_posix():sha(original[p]) for p in paths},emulated_state_modifications=0,emulated_clock_modifications=0,reference_source_url='https://github.com/ekeeke/Genesis-Plus-GX',reference_git_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=core,text=True).strip()),indent=2)+'\n')
