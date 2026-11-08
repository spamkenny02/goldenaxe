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
p = argparse.ArgumentParser(); p.add_argument('--profile', choices=['callback','window'], required=True)
p.add_argument('--fire', action='store_true');p.add_argument('--revision',type=int,default=1)
p.add_argument('--actors',choices=['second','third']);p.add_argument('--irq-status',action='store_true');p.add_argument('--init',action='store_true');p.add_argument('--reveal',action='store_true');p.add_argument('--sequence',action='store_true');p.add_argument('--skip',action='store_true');a=p.parse_args()
if a.skip:a.sequence=True
if a.sequence:a.reveal=True
if a.reveal:
 assert not(a.actors or a.fire or a.init) and a.profile=='callback'
 a.actors='second';a.irq_status=True
assert not a.irq_status or a.actors
assert not a.init or (a.actors and a.profile=='callback')
assert not(a.fire and a.actors)
assert 1<=a.revision<=99
kind='actors_'+a.actors if a.actors else 'fire' if a.fire else 'empty'
if a.init:kind='init_'+kind
if a.reveal:kind='reveal'
if a.sequence:kind='reveal_sequence'
if a.skip:kind='reveal_skip'
out=root/'validation'/('v319-intro-'+kind+'-'+a.profile+f'-observer{a.revision:02}');assert not out.exists();out.mkdir()
core=root.parents[1]/'work/genesis-plus-gx';path=core/'core/z80/z80.c'
suffix='' if a.revision==1 else f'_r{a.revision:02}'
target=core/('genesis_plus_gx_v319_intro_'+kind+'_'+a.profile+suffix+'_libretro.dll');assert not target.exists()
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
if a.fire or a.actors:
 observer=observer.replace(b'unsigned char ram[336],sound[400];',b'unsigned char ram[336],sound[400],extra[80];')
 observer=observer.replace(b'memcpy(e->sound,work_ram+0x1e00,400);',b'''memcpy(e->sound,work_ram+0x1e00,400);
 memcpy(e->extra,work_ram+0x1ca0,72);e->extra[72]=work_ram[0x1fff];
 e->extra[73]=work_ram[0x1cec];e->extra[74]=work_ram[0x1ced];''')
 observer=observer.replace(b'work_ram[0x1cec]==0x36',b'work_ram[0x1cec]==0x37')
if a.actors:
 observer=observer.replace(b'extra[80]',b'extra[848]')
 observer=observer.replace(b'e->extra[74]=work_ram[0x1ced];',b'e->extra[74]=work_ram[0x1ced];memcpy(e->extra+80,work_ram+0x300,768);')
 observer=observer.replace(b'work_ram[0x1cec]==0x37',b'work_ram[0x1cec]=='+(b'0x55' if a.actors=='second' else b'0x4a'))
 observer=observer.replace(b'work_ram[0x1ced]==0x0f',b'work_ram[0x1ced]==0x10')
if a.init:
 observer=observer.replace(b'pc==0xf09 && SP>=0xc000 &&\n    work_ram[0x1cec]=='+(b'0x55' if a.actors=='second' else b'0x4a')+b' && work_ram[0x1ced]==0x10',
                           b'pc=='+(b'0xf51' if a.actors=='second' else b'0xf54')+b' && SP>=0xc000')
 assert b'pc==0xf09 &&' not in observer
 observer=observer.replace(b'e->pad=gaw_poll_return_pc;gaw_poll_active=1;',b'e->pad=gaw_poll_return_pc;e->polls=HL;gaw_poll_active=1;')
if a.irq_status:
 observer=observer.replace(b'unsigned polls,pad;}',b'unsigned polls,pad,irq_count,irq_status[8];}')
 observer=observer.replace(b' if(gaw_poll_active && pc==0xf21) e->polls++;',b''' if(gaw_poll_active && pc==0x137) {
  if(e->irq_count>=8) gaw_poll_overflow++;else e->irq_status[e->irq_count++]=work_ram[0x1b];
 }
 if(gaw_poll_active && pc==0xf21) e->polls++;''')
if a.reveal:
 observer=observer.replace(b'extra[848]',b'extra[848]')
 observer=observer.replace(b'unsigned polls,pad,irq_count,irq_status[8];}',b'unsigned polls,pad,irq_count,irq_status[8],events[6912][2];}')
 observer=observer.replace(b'[4096]',b'[128]').replace(b'>=4096',b'>=128')
 observer=observer.replace(b'pc==gaw_poll_return_pc',b'pc==0xea0')
 observer=observer.replace(b'pc==0xf09 && SP>=0xc000 &&\n    work_ram[0x1cec]==0x55 && work_ram[0x1ced]==0x10',b'pc==0xe8b')
 observer=observer.replace(b'e->extra[74]=work_ram[0x1ced];',b'e->extra[74]=work_ram[0x1ced];e->extra[75]=Z80.hl2.b.l;e->extra[76]=Z80.hl2.b.h;e->extra[77]=Z80.de2.b.l;e->extra[78]=Z80.de2.b.h;e->extra[79]=E;')
 observer=observer.replace(b' if(gaw_poll_active && pc==0xf21) e->polls++;',b''' if(gaw_poll_active && (pc==0xe8d || pc==0xe8f || pc==0xe99)) {
  if(e->polls>=6912) gaw_poll_overflow++;
  else {e->events[e->polls][0]=(unsigned)(gaw_elapsed-e->first.master)+180;
   e->events[e->polls++][1]=pc==0xe8d?0xbf00|L:pc==0xe8f?0xbf00|H:0xbe00|E;}
 }''')
 assert b'pc==0xf09 &&' not in observer
if a.sequence:
 observer=observer.replace(b'extra[848]',b'extra[856]')
 observer=observer.replace(b'e->extra[79]=E;',b'e->extra[79]=E;e->extra[848]=D;')
 observer=observer.replace(b'pc==0xea0',b'pc==0xea4').replace(b'pc==0xe8b',b'pc==0xe79')
 observer=observer.replace(b'irq_status[8]',b'irq_status[64]').replace(b'irq_count>=8',b'irq_count>=64')
 observer=observer.replace(b'6912',b'55296').replace(b'[128]',b'[32]').replace(b'>=128',b'>=32')
if a.skip:
 observer=observer.replace(b'pc==0xea4',b'(pc==0xea4 || pc==0xd0b)')
 observer=observer.replace(b'irq_status[64],events',b'irq_status[64],irq_joy[64],events')
 observer=observer.replace(b' if(gaw_poll_active && pc==0x137)',b' if(gaw_poll_active && pc==0x1bc && e->irq_count) e->irq_joy[e->irq_count-1]=(~A)&63;\n if(gaw_poll_active && pc==0x137)')
 observer+=b'''__declspec(dllexport) unsigned gaw_skip_target(void) {
 const struct gaw_poll_record *e=gaw_poll_records+gaw_poll_count;
 return gaw_poll_active?(e->first.extra[73]|(e->first.extra[74]<<8)):0;
}
__declspec(dllexport) unsigned gaw_skip_events(void) {
 return gaw_poll_active?gaw_poll_records[gaw_poll_count].polls:0;
}
__declspec(dllexport) unsigned gaw_skip_return(void) {
 return gaw_poll_count?gaw_poll_records[gaw_poll_count-1].last.pc:0;
}
'''
original=path.read_bytes();needle=b'static void gaw_timing_observe(unsigned pc)\r\n{'
if needle not in original:needle=needle.replace(b'\r\n',b'\n')
assert original.count(needle)==1
changed=original.replace(needle,observer+needle+b'\n gaw_poll_observe(pc);')
(out/'z80-before.c').write_bytes(original);(out/'z80-observer.c').write_bytes(changed)
try:
 path.write_bytes(changed)
 subprocess.run([sys.executable,'tools/build_timing_core.py','--target',target.name,'--log',str(out/'build.log'),
                 '--force-source','core/z80/z80.c'],cwd=root,check=True)
finally:path.write_bytes(original)
assert path.read_bytes()==original
(out/'report.json').write_text(json.dumps(dict(passed=True,profile=a.profile,core=str(target),core_sha256=sha(target.read_bytes()),
 original_source_sha256=sha(original),observer_source_sha256=sha(changed),original_source_restored=True,
 emulated_state_modifications=0,emulated_cycle_modifications=0,irq_status=a.irq_status,init=a.init,reveal=a.reveal,sequence=a.sequence,skip=a.skip,
 entry_pc=(0xe79 if a.sequence else 0xe8b if a.reveal else (0xf51 if a.actors=='second' else 0xf54) if a.init else 0xf09 if a.profile=='callback' else 0xf1e),
 callback_target=None if a.reveal else (0x1055 if a.actors=='second' else 0x104a) if a.actors else 0xf37 if a.fire else 0xf36,
 scope='Natural calls only; source first/actual caller-return entry snapshots. Runtime parity pending.'),indent=2)+'\n')
