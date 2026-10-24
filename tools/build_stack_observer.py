"""Build a separate GX core with read-only, every-instruction SP minima."""
import json, subprocess, sys
from run_core import ROOT
from archive_lossless_evidence import sha


def main():
 folder=ROOT/'validation/stack-observer-build';assert not folder.exists();folder.mkdir()
 source=ROOT.parents[1]/'work/genesis-plus-gx/core/m68k/m68kcpu.c';original=source.read_bytes()
 (folder/'m68kcpu-before.c').write_bytes(original)
 addition=b'''static unsigned gaw_stack_min=65535,gaw_stack_pc;
__declspec(dllexport) void gaw_stack_reset(void) {gaw_stack_min=65535;gaw_stack_pc=0;}
__declspec(dllexport) unsigned gaw_stack_sp(void) {return gaw_stack_min;}
__declspec(dllexport) unsigned gaw_stack_at(void) {return gaw_stack_pc;}
'''
 old=b'static void gaw_md_observe(unsigned pc) {'
 assert original.count(old)==1
 patched=original.replace(old,addition+old+b'\n unsigned sp=REG_SP&65535;if(sp<gaw_stack_min){gaw_stack_min=sp;gaw_stack_pc=pc;}')
 target='genesis_plus_gx_stack_libretro.dll'
 try:
  source.write_bytes(patched)
  (folder/'m68kcpu-stack.c').write_bytes(patched)
  result=subprocess.run([sys.executable,str(ROOT/'tools/build_timing_core.py'),'--target',target],capture_output=True)
  (folder/'build.log').write_bytes(result.stdout+result.stderr);assert result.returncode==0,(result.stdout+result.stderr)[-3000:]
  core=ROOT.parents[1]/'work/genesis-plus-gx'/target
  (folder/target).write_bytes(core.read_bytes())
 finally:source.write_bytes(original)
 assert source.read_bytes()==original
 report=dict(core_sha256=sha(core.read_bytes()),before_sha256=sha(original),patched_sha256=sha(patched),source_restored=True,read_only=True,scope='SP/PC sampled before each normal m68k_run instruction. Separate DLL; no register, RAM, VDP, input or game changes.')
 (folder/'report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(report)


if __name__=='__main__':main()
