"""Read-only raw SMS port observer, restoring every modified reference file."""
import difflib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
out=root/'validation/v319-port-mirror-observer01';assert not out.exists();out.mkdir()
core=root.parents[1]/'work/genesis-plus-gx';target=core/'genesis_plus_gx_v319_port_mirror_libretro.dll';assert not target.exists()
paths=[core/'core/z80/z80.c',core/'core/vdp_ctrl.c',core/'core/memz80.c'];original={p:p.read_bytes() for p in paths}
decl=b'void gaw_port_mirror_event(unsigned,unsigned,unsigned,unsigned);\n'
z80=original[paths[0]];sig=b'static void gaw_timing_observe(unsigned pc)\r\n{'
if sig not in z80:sig=sig.replace(b'\r\n',b'\n')
assert z80.count(sig)==1;z80=decl+z80.replace(sig,sig+b'\n gaw_port_mirror_event(0,Z80.cycles,lines_per_frame,0);')
ctrl=original[paths[1]];sig=b'unsigned int vdp_z80_ctrl_r(unsigned int cycles)'
bridge=b'''typedef void (*gaw_port_callback)(unsigned,unsigned,unsigned,unsigned,const unsigned char *,const unsigned char *,const unsigned char *,const unsigned *);
static gaw_port_callback gaw_port_hook;
__declspec(dllexport) void gaw_port_mirror_set_hook(gaw_port_callback hook) {gaw_port_hook=hook;}
void gaw_port_mirror_event(unsigned kind,unsigned cycles,unsigned lines,unsigned observed)
{
 unsigned ports[5]={addr,code,pending,addr_latch,fifo[0]};
 if(gaw_port_hook) gaw_port_hook(kind,cycles,lines,observed,reg,vram,cram,ports);
}
'''
assert ctrl.count(sig)==1;ctrl=ctrl.replace(sig,bridge+sig)
begin=ctrl.index(sig);end=ctrl.index(b'  return (temp);',begin);ctrl=ctrl[:end]+b'  gaw_port_mirror_event(1,cycles,lines_per_frame,temp);\n'+ctrl[end:]
begin=ctrl.index(b'static unsigned int vdp_z80_data_r_m4(void)\r\n{' if b'static unsigned int vdp_z80_data_r_m4(void)\r\n{' in ctrl else b'static unsigned int vdp_z80_data_r_m4(void)\n{')
end=ctrl.index(b'  return data;',begin);ctrl=ctrl[:end]+b'  gaw_port_mirror_event(3,Z80.cycles,lines_per_frame,data);\n'+ctrl[end:]
mem=original[paths[2]];sig=b'void z80_ms_port_w(unsigned int port, unsigned char data)';assert mem.count(sig)==1
mem=mem.replace(sig,b'static void gaw_original_ms_port_w(unsigned int port, unsigned char data)')
sig=b'unsigned char z80_ms_port_r(unsigned int port)';assert mem.count(sig)==1
wrapper=b'''void z80_ms_port_w(unsigned int port,unsigned char data)
{
 if((port&0xc0)==0x80) gaw_port_mirror_event(2,Z80.cycles,lines_per_frame,((port&255)<<8)|data);
 gaw_original_ms_port_w(port,data);
 if((port&0xc0)==0x80) gaw_port_mirror_event(4,Z80.cycles,lines_per_frame,0);
}
'''
mem=decl+mem.replace(sig,wrapper+sig)
changed={paths[0]:z80,paths[1]:ctrl,paths[2]:mem};patch=[]
for p in paths:
 (out/(p.stem+'-before.c')).write_bytes(original[p]);(out/(p.stem+'-observer.c')).write_bytes(changed[p])
 patch.extend(difflib.unified_diff(original[p].decode().splitlines(True),changed[p].decode().splitlines(True),fromfile=p.relative_to(core).as_posix(),tofile=p.relative_to(core).as_posix(),n=0))
(out/'instrumentation.patch').write_text(''.join(patch));(out/'reference-license.txt').write_bytes((core/'LICENSE.txt').read_bytes())
try:
 for p in paths:p.write_bytes(changed[p])
 command=[sys.executable,str(root/'tools/build_timing_core.py'),'--target',target.name,'--log',str(out/'build.log')]
 for p in paths:command+=['--force-source',p.relative_to(core).as_posix()]
 subprocess.run(command,cwd=root,check=True)
finally:
 for p in paths:p.write_bytes(original[p])
assert all(p.read_bytes()==original[p] for p in paths)
(out/'report.json').write_text(json.dumps(dict(passed=True,core=str(target),core_sha256=sha(target.read_bytes()),original_sources_restored=True,original_source_sha256={p.relative_to(core).as_posix():sha(original[p]) for p in paths},emulated_state_modifications=0,emulated_clock_modifications=0,reference_source_url='https://github.com/ekeeke/Genesis-Plus-GX',reference_git_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=core,text=True).strip()),indent=2)+'\n')
