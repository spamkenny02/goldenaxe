"""Build an isolated read-only intro observer with physical Z80 frame cycles."""
import json
import subprocess
import sys
from archive_lossless_evidence import sha
from run_core import ROOT

def main():
    out=ROOT/'validation/menu-raster-v0316/irq-raster-observer01';out.mkdir(parents=True,exist_ok=False)
    core=ROOT.parents[1]/'work/genesis-plus-gx';source=core/'core/z80/z80.c';original=source.read_bytes();target='genesis_plus_gx_intro_irq_raster_libretro.dll';assert not(core/target).exists()
    pcs=(0x137,0xbb3,0xf09,0xf32,0xf12,0x384,0x396,0xd6d,0xd8b,0xd3c,0xd4f,0xd5f,0xd6b,0xf2f)
    begin=original.index(b'  if(pc==0x70f2');end=original.index(b'\n  {',begin)
    changed=original[:begin]+('  if('+ ' || '.join('pc==0x%x'%pc for pc in pcs)+')').encode()+original[end:]
    changed=changed.replace(b'e[3]=work_ram[0xb9]|(work_ram[0xba]<<8);',b'e[3]=Z80.cycles;')
    assert changed!=original and b'e[3]=Z80.cycles;'in changed
    changed=changed.replace(b'gaw_events[32768][8]',b'gaw_events[65536][8]').replace(b'gaw_event_count>=32768',b'gaw_event_count>=65536')
    (out/'z80-before.c').write_bytes(original);(out/'z80-observer.c').write_bytes(changed)
    try:
        source.write_bytes(changed)
        subprocess.run([sys.executable,str(ROOT/'tools/build_timing_core.py'),'--target',target,'--log',str(out/'build.log')],cwd=ROOT,check=True)
    finally:source.write_bytes(original)
    assert source.read_bytes()==original
    (out/'report.json').write_text(json.dumps(dict(core_sha256=sha((core/target).read_bytes()),original_instrumentation_sha256=sha(original),observer_source_sha256=sha(changed),source_restored=True,watched_pcs=pcs,slot3='Z80.cycles:physical master cycles in current frame',rom_writes=0),indent=2)+'\n')

if __name__=='__main__':main()
