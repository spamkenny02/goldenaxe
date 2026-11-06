"""Build a separate read-only source observer, restoring the instrumentation source."""
import json
import subprocess
import sys

from archive_lossless_evidence import sha
from run_core import ROOT


def main():
    out=ROOT/'validation/menu-raster-v0316/source-loader-observer';out.mkdir(parents=True,exist_ok=False)
    core=ROOT.parents[1]/'work/genesis-plus-gx';source=core/'core/z80/z80.c';original=source.read_bytes()
    target='genesis_plus_gx_intro_loader_libretro.dll';assert not (core/target).exists()
    (out/'z80-before.c').write_bytes(original)
    pcs=(0xd02,0xd30,0xd59,0xd6d,0xdd2,0xe0c,0xea5,0xefa,0xf09,0xf1e,0xf32,0x384,0x396)
    anchor=b'if(pc==0x70f2';assert original.count(anchor)==1
    changed=original.replace(anchor,('if('+''.join('pc==0x%04x || '%pc for pc in pcs)+'pc==0x70f2').encode(),1)
    (out/'z80-observer.c').write_bytes(changed)
    try:
        source.write_bytes(changed)
        subprocess.run([sys.executable,str(ROOT/'tools/build_timing_core.py'),'--target',target,'--log',str(out/'build.log')],cwd=ROOT,check=True)
    finally:
        source.write_bytes(original)
    assert source.read_bytes()==original
    report=dict(core=(core/target).as_posix(),core_sha256=sha((core/target).read_bytes()),
                original_instrumentation_sha256=sha(original),observed_instrumentation_sha256=sha(changed),
                original_source_restored=True,watched_pcs=list(pcs),rom_modifications=0)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
