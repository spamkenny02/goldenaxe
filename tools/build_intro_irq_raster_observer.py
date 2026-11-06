"""Build an isolated read-only intro observer with physical Z80 frame cycles."""
import argparse
import json
import subprocess
import sys
from archive_lossless_evidence import sha
from pathlib import Path
from run_core import ROOT

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=ROOT/'validation/menu-raster-v0316/irq-raster-observer01');parser.add_argument('--target',default='genesis_plus_gx_intro_irq_raster_libretro.dll');parser.add_argument('--profile',choices=['text','reentry'],default='text');parser.add_argument('--extra-pc',type=lambda value:int(value,0),action='append',default=[]);a=parser.parse_args()
    out=a.out.resolve();assert out.is_relative_to(ROOT/'validation');out.mkdir(parents=True,exist_ok=False)
    core=ROOT.parents[1]/'work/genesis-plus-gx';source=core/'core/z80/z80.c';original=source.read_bytes();target=a.target;assert Path(target).name==target and not(core/target).exists()
    pcs=(0x137,0xbb3,0xf09,0xf32,0xf12,0x384,0x396,0xd6d,0xd8b,0xd3c,0xd4f,0xd5f,0xd6b,0xf2f)
    if a.profile=='reentry':pcs=(0xc98,0xb48,0xb56,0xcd5,0xcda,0xce0,0xe54,0xe83,0xea0,0x1470,0x14d2,0x14d5,0x161d,0x165c,0x169c)
    pcs=pcs+tuple(a.extra_pc)
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
