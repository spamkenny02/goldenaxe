"""Observe CPU checkpoints and status reads, not reference sprite events."""
import difflib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
out=root/'validation/v319-sprite-clock-observer01';assert not out.exists();out.mkdir()
core=root.parents[1]/'work/genesis-plus-gx';target=core/'genesis_plus_gx_v319_sprite_clock_libretro.dll';assert not target.exists()
paths=[core/'core/z80/z80.c',core/'core/vdp_ctrl.c'];original={p:p.read_bytes() for p in paths}
z80=original[paths[0]];signature=b'static void gaw_timing_observe(unsigned pc)\r\n{'
if signature not in z80:signature=signature.replace(b'\r\n',b'\n')
bridge=b'''typedef void (*gaw_sprite_clock_callback)(unsigned,unsigned,unsigned,const unsigned char *,const unsigned char *,unsigned);
static gaw_sprite_clock_callback gaw_sprite_clock_hook;
__declspec(dllexport) void gaw_sprite_clock_set_hook(gaw_sprite_clock_callback hook) {gaw_sprite_clock_hook=hook;}
void gaw_sprite_clock_event(unsigned kind,unsigned cycles,unsigned lines,const unsigned char *regs,const unsigned char *memory,unsigned observed)
{if(gaw_sprite_clock_hook) gaw_sprite_clock_hook(kind,cycles,lines,regs,memory,observed);}
'''
assert z80.count(signature)==1
z80=z80.replace(signature,bridge+signature+b'\n gaw_sprite_clock_event(0,Z80.cycles,lines_per_frame,reg,vram,0);')
ctrl=original[paths[1]];begin=ctrl.index(b'unsigned int vdp_z80_ctrl_r(');end=ctrl.index(b'  return (temp);',begin)
ctrl=ctrl[:end]+b'  gaw_sprite_clock_event(1,cycles,lines_per_frame,reg,vram,temp);\n'+ctrl[end:]
ctrl=b'void gaw_sprite_clock_event(unsigned,unsigned,unsigned,const unsigned char *,const unsigned char *,unsigned);\n'+ctrl
changed={paths[0]:z80,paths[1]:ctrl};patch=[]
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
report=dict(passed=True,core=str(target),core_sha256=sha(target.read_bytes()),original_sources_restored=True,
 original_source_sha256={p.relative_to(core).as_posix():sha(original[p]) for p in paths},emulated_state_modifications=0,emulated_clock_modifications=0,
 reference_source_url='https://github.com/ekeeke/Genesis-Plus-GX',reference_git_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=core,text=True).strip(),
 input_events='CPU instruction checkpoints and status-read completion times only. No parse/render source hook.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
