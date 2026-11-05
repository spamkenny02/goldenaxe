"""Observe IY at original A82D without modifying emulated instructions or timing."""
import json,subprocess,sys
from run_core import ROOT
from archive_lossless_evidence import sha

def main():
    folder=ROOT/'validation/iy-trace-core-v0314-02';folder.mkdir(exist_ok=False)
    path=ROOT.parents[1]/'work/genesis-plus-gx/core/z80/z80.c';original=path.read_bytes();(folder/'z80-before.c').write_bytes(original)
    anchor=b'OP(fd,77) { EAY; WM( EA, A );'
    assert original.count(anchor)==1
    extra=b'\nstatic unsigned int gaw_iytrace_count;\nstatic unsigned int gaw_iytrace_rows[4096][8];\n__declspec(dllexport) void gaw_iytrace_reset(void) { gaw_iytrace_count=0; }\n__declspec(dllexport) unsigned int gaw_iytrace_size(void) { return gaw_iytrace_count; }\n__declspec(dllexport) const unsigned int *gaw_iytrace_data(void) { return &gaw_iytrace_rows[0][0]; }\nstatic void gaw_iytrace_record(void)\n{\n if(PC==0xa82f && gaw_iytrace_count<4096)\n {\n  unsigned int *e=gaw_iytrace_rows[gaw_iytrace_count++];\n  e[0]=PC;e[1]=IX;e[2]=IY;e[3]=A;e[4]=work_ram[0x600];e[5]=work_ram[0x601];e[6]=work_ram[0xba];e[7]=work_ram[0xa2];\n }\n}\n'
    patched=original.replace(anchor,extra+anchor.replace(b'{ EAY;',b'{ gaw_iytrace_record(); EAY;'))
    (folder/'z80-iy-trace.c').write_bytes(patched);target='genesis_plus_gx_iytrace_libretro.dll'
    common=ROOT/'validation/timing-core-build-python.log';previous_log=common.read_bytes() if common.exists() else None
    try:
        path.write_bytes(patched)
        built=subprocess.run([sys.executable,str(ROOT/'tools/build_timing_core.py'),'--target',target],capture_output=True)
        (folder/'build.log').write_bytes(built.stdout+built.stderr)
        if common.exists():(folder/'compiler.log').write_bytes(common.read_bytes())
        assert built.returncode==0,(built.stdout+built.stderr)[-3000:]
        core=ROOT.parents[1]/'work/genesis-plus-gx'/target;(folder/target).write_bytes(core.read_bytes())
    finally:
        path.write_bytes(original)
        if previous_log is not None:common.write_bytes(previous_log)
    assert path.read_bytes()==original
    report=dict(built=True,core_sha256=sha(core.read_bytes()),source_before_sha256=sha(original),instrumented_source_sha256=sha(patched),source_restored=True,scope='Read-only host records before original LD(IY+o),A atA82D; emulated instruction and cycle accounting unchanged. Not a production ROM change.')
    (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
