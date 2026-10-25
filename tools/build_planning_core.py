"""Expose the GX refresh phase omitted by its public save-state format.

Primary game calls only the getter. The setter restores this field only in
the disposable secondary core, after loading the primary snapshot.
"""
import json,subprocess,sys
from run_core import ROOT
from archive_lossless_evidence import sha


def main():
 folder=ROOT/'validation/planning-core-build';assert not folder.exists();folder.mkdir()
 path=ROOT.parents[1]/'work/genesis-plus-gx/core/m68k/m68kcpu.c';original=path.read_bytes();(folder/'m68kcpu-before.c').write_bytes(original)
 marker=b'/* GAW_RESEARCH_CLOCK: read-only, configured instruction entry observations. */'
 extra=b'''/* Primary getter only; setter belongs exclusively to secondary prediction. */
__declspec(dllexport) int gaw_refresh_get(void) {return m68k.refresh_cycles;}
__declspec(dllexport) void gaw_refresh_set(int value) {m68k.refresh_cycles=value;}
'''
 assert original.count(marker)==1;patched=original.replace(marker,extra+marker);target='genesis_plus_gx_planning_libretro.dll'
 try:
  path.write_bytes(patched);(folder/'m68kcpu-planning.c').write_bytes(patched)
  built=subprocess.run([sys.executable,str(ROOT/'tools/build_timing_core.py'),'--target',target],capture_output=True)
  (folder/'build.log').write_bytes(built.stdout+built.stderr);assert built.returncode==0,(built.stdout+built.stderr)[-3000:]
  core=ROOT.parents[1]/'work/genesis-plus-gx'/target;(folder/target).write_bytes(core.read_bytes())
 finally:path.write_bytes(original)
 assert path.read_bytes()==original
 report=dict(core_sha256=sha(core.read_bytes()),original_source_sha256=sha(original),patched_source_sha256=sha(patched),source_restored=True,scope='No CPU execution changes. Getter reads refresh_cycles in primary; setter is called only on a separate planning DLL. Public save-state omits this field; cold official-core replay remains required.')
 (folder/'report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(report)


if __name__=='__main__':main()
