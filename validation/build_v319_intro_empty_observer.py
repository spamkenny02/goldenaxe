"""Natural source F09/F1E calls with F36 empty callback: entry/actual caller-return snapshots."""
import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from archive_lossless_evidence import sha
p = argparse.ArgumentParser(); p.add_argument('--profile', choices=['callback','window'], required=True); a=p.parse_args()
out=root/'validation'/('v319-intro-empty-'+a.profile+'-observer01');assert not out.exists();out.mkdir()
core=root.parents[1]/'work/genesis-plus-gx';path=core/'core/z80/z80.c'
target=core/('genesis_plus_gx_v319_intro_empty_'+a.profile+'_libretro.dll');assert not target.exists()
tree=ast.parse((root/'validation/build_v319_intro_poll_observer.py').read_text())
observer=next(ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign) and
              any(isinstance(t,ast.Name) and t.id=='observer' for t in node.targets))
start=observer.index(b'static void gaw_poll_observe(unsigned pc)')
observer=observer[:start]+b'''static unsigned gaw_poll_return_pc;
static void gaw_poll_observe(unsigned pc) {
 struct gaw_poll_record *e;
 if(gaw_poll_count>=4096) {gaw_poll_overflow++;return;}
 e=gaw_poll_records+gaw_poll_count;
 if(gaw_poll_active && pc==gaw_poll_return_pc) {
  gaw_poll_snapshot(&e->last,pc);gaw_poll_count++;gaw_poll_active=0;
  if(gaw_poll_count>=4096) return;
  e=gaw_poll_records+gaw_poll_count;
 }
 if(!gaw_poll_active && pc==ENTRY_PC && SP>=0xc000 &&
    work_ram[0x1cec]==0x36 && work_ram[0x1ced]==0x0f) {
  memset(e,0,sizeof(*e));gaw_poll_snapshot(&e->first,pc);
  gaw_poll_return_pc=work_ram[SP&0x1fff]|(work_ram[(SP+1)&0x1fff]<<8);
  e->pad=gaw_poll_return_pc;gaw_poll_active=1;
 }
 if(gaw_poll_active && pc==0xf21) e->polls++;
}
'''.replace(b'ENTRY_PC',b'0xf09' if a.profile=='callback' else b'0xf1e')
original=path.read_bytes();needle=b'static void gaw_timing_observe(unsigned pc)\r\n{'
if needle not in original:needle=needle.replace(b'\r\n',b'\n')
assert original.count(needle)==1
changed=original.replace(needle,observer+needle+b'\n gaw_poll_observe(pc);')
(out/'z80-before.c').write_bytes(original);(out/'z80-observer.c').write_bytes(changed)
try:
 path.write_bytes(changed)
 subprocess.run([sys.executable,'tools/build_timing_core.py','--target',target.name,'--log',str(out/'build.log')],cwd=root,check=True)
finally:path.write_bytes(original)
assert path.read_bytes()==original
(out/'report.json').write_text(json.dumps(dict(passed=True,profile=a.profile,core=str(target),core_sha256=sha(target.read_bytes()),
 original_source_sha256=sha(original),observer_source_sha256=sha(changed),original_source_restored=True,
 emulated_state_modifications=0,emulated_cycle_modifications=0,callback_target=0xf36,
 scope='Natural calls only; source first/actual caller-return entry snapshots. Runtime parity pending.'),indent=2)+'\n')
