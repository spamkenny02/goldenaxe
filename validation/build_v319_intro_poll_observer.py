"""Read-only natural F21 polling entry/F2B return snapshots, preserving original emulator source."""
import json
import subprocess
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from archive_lossless_evidence import sha
out = root / 'validation/v319-intro-poll-observer01'
assert not out.exists()
out.mkdir()
core = root.parents[1] / 'work/genesis-plus-gx'
path = core / 'core/z80/z80.c'
target = core / 'genesis_plus_gx_v319_intro_poll_libretro.dll'
assert not target.exists()
original = path.read_bytes()
needle = b'static void gaw_timing_observe(unsigned pc)\r\n{'
if needle not in original: needle = needle.replace(b'\r\n', b'\n')
assert original.count(needle) == 1
observer = b'''/* Native-port read-only F21/F2B source evidence. */
struct gaw_poll_phase {
 unsigned long long master,irq_master;
 unsigned phase[12],refresh,pc;
 unsigned char ram[336],sound[400];
};
struct gaw_poll_record {struct gaw_poll_phase first,last;unsigned polls,pad;};
static struct gaw_poll_record gaw_poll_records[4096];
static unsigned gaw_poll_count,gaw_poll_active,gaw_poll_overflow;
__declspec(dllexport) void gaw_poll_reset(void) {gaw_poll_count=gaw_poll_active=gaw_poll_overflow=0;}
__declspec(dllexport) unsigned gaw_poll_size(void) {return gaw_poll_count;}
__declspec(dllexport) unsigned gaw_poll_errors(void) {return gaw_poll_overflow;}
__declspec(dllexport) unsigned gaw_poll_stride(void) {return sizeof(struct gaw_poll_record);}
__declspec(dllexport) const unsigned char *gaw_poll_data(void) {return (const unsigned char *)gaw_poll_records;}
static void gaw_poll_snapshot(struct gaw_poll_phase *e,unsigned pc) {
 e->master=gaw_elapsed;e->irq_master=gaw_irq_elapsed;
 e->phase[0]=Z80.cycles;e->phase[1]=v_counter;e->phase[2]=mcycles_vdp;
 e->phase[3]=lines_per_frame;e->phase[4]=vc_max;e->phase[5]=interlaced;
 e->phase[6]=reg[1];e->phase[7]=system_hw;e->phase[8]=IFF1;
 e->phase[9]=Z80.after_ei;e->phase[10]=Z80.irq_state;e->phase[11]=reg[0];
 e->refresh=(R&127)|R2;e->pc=pc;
 memcpy(e->ram,work_ram,80);memcpy(e->ram+80,work_ram+0x1d00,256);
 memcpy(e->sound,work_ram+0x1e00,400);
}
static void gaw_poll_observe(unsigned pc) {
 struct gaw_poll_record *e;
 if(pc!=0xf21 && pc!=0xf2b) return;
 if(gaw_poll_count>=4096) {gaw_poll_overflow++;return;}
 e=gaw_poll_records+gaw_poll_count;
 if(pc==0xf21) {
  if(!gaw_poll_active) {memset(e,0,sizeof(*e));gaw_poll_snapshot(&e->first,pc);gaw_poll_active=1;}
  e->polls++;
 } else if(gaw_poll_active) {gaw_poll_snapshot(&e->last,pc);gaw_poll_count++;gaw_poll_active=0;}
}
'''
changed = original.replace(needle, observer + needle + b'\n gaw_poll_observe(pc);')
(out / 'z80-before.c').write_bytes(original)
(out / 'z80-observer.c').write_bytes(changed)
try:
    path.write_bytes(changed)
    subprocess.run([sys.executable, 'tools/build_timing_core.py', '--target', target.name,
                    '--log', str(out / 'build.log')], cwd=root, check=True)
finally: path.write_bytes(original)
assert path.read_bytes() == original
(out / 'report.json').write_text(json.dumps(dict(passed=True, core=str(target), core_sha256=sha(target.read_bytes()),
    original_source_sha256=sha(original), observer_source_sha256=sha(changed), original_source_restored=True,
    emulated_state_modifications=0, emulated_cycle_modifications=0, scope='Snapshots only; runtime observer parity pending.'), indent=2) + '\n')
