"""Read-only event bridge into a native sprite model, restoring all emulator sources."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
out=root/'validation/v319-chip-events-observer01';assert not out.exists();out.mkdir()
core=root.parents[1]/'work/genesis-plus-gx';paths=[core/'core/vdp_render.c',core/'core/vdp_ctrl.c',core/'core/z80/z80.c'];original={p:p.read_bytes() for p in paths}
target=core/'genesis_plus_gx_v319_chip_events_libretro.dll';assert not target.exists()
declaration=b'void gaw_vdp_native_event(unsigned kind,int line,unsigned hcounter,const unsigned char *regs,const unsigned char *memory,unsigned observed);\n'
render=original[paths[0]]
signature=b'void parse_satb_m4(int line)\r\n{'
if signature not in render:signature=signature.replace(b'\r\n',b'\n')
bridge=b'''typedef void (*gaw_vdp_callback)(unsigned,int,unsigned,const unsigned char *,const unsigned char *,unsigned);
static gaw_vdp_callback gaw_vdp_hook;
__declspec(dllexport) void gaw_vdp_set_hook(gaw_vdp_callback hook) {gaw_vdp_hook=hook;}
void gaw_vdp_native_event(unsigned kind,int line,unsigned hcounter,const unsigned char *regs,const unsigned char *memory,unsigned observed)
{if(gaw_vdp_hook) gaw_vdp_hook(kind,line,hcounter,regs,memory,observed);}
'''
assert render.count(signature)==1
render=render.replace(signature,bridge+signature+b'\n gaw_vdp_native_event(0,line,0,reg,vram,0);')
signature=b'void render_line(int line)\r\n{'
if signature not in render:signature=signature.replace(b'\r\n',b'\n')
assert render.count(signature)==1
render=render.replace(signature,signature+b'\n if(reg[0]&4) gaw_vdp_native_event(1,line,0,reg,vram,0);')
ctrl=original[paths[1]];begin=ctrl.index(b'unsigned int vdp_z80_ctrl_r(');end=ctrl.index(b'  return (temp);',begin)
ctrl=declaration+ctrl[:end]+b'  gaw_vdp_native_event(2,v_counter,hctab[(cycles+SMS_CYCLE_OFFSET+15)%MCYCLES_PER_LINE],reg,vram,temp);\n'+ctrl[end:]
z80=original[paths[2]];signature=b'static void gaw_timing_observe(unsigned pc)\r\n{'
if signature not in z80:signature=signature.replace(b'\r\n',b'\n')
assert z80.count(signature)==1
z80=declaration+z80.replace(signature,signature+b'\n if(pc==0x137) gaw_vdp_native_event(3,v_counter,0,reg,vram,work_ram[0x1b]);')
changed={paths[0]:render,paths[1]:ctrl,paths[2]:z80}
for p in paths:
 (out/(p.stem+'-before.c')).write_bytes(original[p]);(out/(p.stem+'-observer.c')).write_bytes(changed[p])
try:
 for p in paths:p.write_bytes(changed[p])
 command=[sys.executable,str(root/'tools/build_timing_core.py'),'--target',target.name,'--log',str(out/'build.log')]
 for p in paths:command+=['--force-source',p.relative_to(core).as_posix()]
 subprocess.run(command,cwd=root,check=True)
finally:
 for p in paths:p.write_bytes(original[p])
assert all(p.read_bytes()==original[p] for p in paths)
(out/'report.json').write_text(json.dumps(dict(passed=True,core=str(target),core_sha256=sha(target.read_bytes()),original_source_sha256={p.relative_to(core).as_posix():sha(original[p]) for p in paths},original_sources_restored=True,emulated_state_modifications=0,emulated_clock_modifications=0),indent=2)+'\n')
