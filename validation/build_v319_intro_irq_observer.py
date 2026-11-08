"""Observe source full-IRQ requests and F32 callbacks without changing emulated state/cycles."""
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from archive_lossless_evidence import sha
out = root / 'validation/v319-intro-irq-observer01'
assert not out.exists()
out.mkdir()
core = root.parents[1] / 'work/genesis-plus-gx'
source = core / 'core/z80/z80.c'
target = core / 'genesis_plus_gx_v319_intro_irq_libretro.dll'
assert not target.exists()
original = source.read_bytes()
needle = b'static void gaw_timing_observe(unsigned pc)\r\n{'
if needle not in original:
    needle = needle.replace(b'\r\n', b'\n')
assert original.count(needle) == 1
exports = b'''/* GAW read-only source request/callback entry records. */
static unsigned gaw_intro_rows[8192][6],gaw_intro_count,gaw_intro_overflow;
__declspec(dllexport) void gaw_intro_reset(void) {gaw_intro_count=gaw_intro_overflow=0;}
__declspec(dllexport) unsigned gaw_intro_size(void) {return gaw_intro_count;}
__declspec(dllexport) unsigned gaw_intro_errors(void) {return gaw_intro_overflow;}
__declspec(dllexport) const unsigned *gaw_intro_data(void) {return &gaw_intro_rows[0][0];}
static void gaw_intro_observe(unsigned pc) {
 unsigned *row;
 if(pc!=0xb95 && pc!=0xbb3 && pc!=0xf09 && pc!=0xf0c && pc!=0xf32 && pc!=0x137 && pc!=0x1dd && pc!=0xce0) return;
 if(gaw_intro_count>=8192) {gaw_intro_overflow++;return;}
 row=gaw_intro_rows[gaw_intro_count++];row[0]=pc;row[1]=Z80.cycles;
 row[2]=work_ram[0x2f];row[3]=work_ram[0x2e];row[4]=SP;row[5]=work_ram[0x30];
}
'''
changed = original.replace(needle, exports + needle + b'\n  gaw_intro_observe(pc);', 1)
(out / 'z80-before.c').write_bytes(original)
(out / 'z80-observer.c').write_bytes(changed)
try:
    source.write_bytes(changed)
    subprocess.run([sys.executable, 'tools/build_timing_core.py', '--target', target.name,
                    '--log', str(out / 'build.log')], cwd=root, check=True)
finally:
    source.write_bytes(original)
assert source.read_bytes() == original
result = dict(passed=True, core=str(target), core_sha256=sha(target.read_bytes()),
    original_source_sha256=sha(original), observer_source_sha256=sha(changed), original_source_restored=True,
    fields=['source_pc', 'supplied_core_master_clock', 'C02F_full_irq_clock', 'C02E_request', 'SP', 'C030_timer'],
    emulated_state_modifications=0, emulated_cycle_modifications=0, capacity_per_host_read=8192,
    observer_noninterference_pending=True)
(out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
print('Source full-IRQ observer compiled; original source restored.')
