"""Build a separate read-only PSG port-write observer; restore the emulator source afterwards."""
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from archive_lossless_evidence import sha

out = root / 'validation/v319-psg-write-observer01'
assert not out.exists(), out
out.mkdir()
core = root.parents[1] / 'work/genesis-plus-gx'
source = core / 'core/sound/psg.c'
target = 'genesis_plus_gx_v319_psg_writes_libretro.dll'
assert not (core / target).exists(), target
original = source.read_bytes()
signature = b'void psg_write(unsigned int clocks, unsigned int data)'
assert original.count(signature) == 1
begin = original.index(signature)
declaration = original.index(b'int index;', begin) + len(b'int index;')
assert declaration - begin < 150
nl = '\r\n' if b'\r\n' in original else '\n'
exports = '''/* Read-only diagnostics: host-side buffer, no emulated cycles/state changed. */
#define GAW_PSG_WRITE_CAPACITY 4096
static unsigned int gaw_psg_write_rows[GAW_PSG_WRITE_CAPACITY*2];
static unsigned int gaw_psg_write_count,gaw_psg_write_overflows;
__declspec(dllexport) void gaw_psg_writes_reset(void)
{ gaw_psg_write_count=0;gaw_psg_write_overflows=0; }
__declspec(dllexport) unsigned int gaw_psg_writes_size(void)
{ return gaw_psg_write_count; }
__declspec(dllexport) unsigned int gaw_psg_writes_errors(void)
{ return gaw_psg_write_overflows; }
__declspec(dllexport) const unsigned int *gaw_psg_writes_data(void)
{ return gaw_psg_write_rows; }

'''.replace('\n', nl).encode()
hook = '''
  if(gaw_psg_write_count<GAW_PSG_WRITE_CAPACITY)
  {
    gaw_psg_write_rows[gaw_psg_write_count*2]=clocks;
    gaw_psg_write_rows[gaw_psg_write_count*2+1]=data;
    gaw_psg_write_count++;
  }
  else gaw_psg_write_overflows++;
'''.replace('\n', nl).encode()
changed = original[:begin] + exports + original[begin:declaration] + hook + original[declaration:]
(out / 'psg-before.c').write_bytes(original)
(out / 'psg-observer.c').write_bytes(changed)
try:
    source.write_bytes(changed)
    subprocess.run([sys.executable, 'tools/build_timing_core.py', '--target', target,
                    '--log', str(out / 'build.log')], cwd=root, check=True)
finally:
    source.write_bytes(original)
assert source.read_bytes() == original
result = dict(passed=True, diagnostic_core=str(core / target),
              core_sha256=sha((core / target).read_bytes()), source_before_sha256=sha(original),
              observer_source_sha256=sha(changed), original_source_restored=True,
              capacity_per_host_read=4096, fields=['frame_relative_master_clocks', 'unmodified_psg_port_data'],
              rom_modifications=0, emulated_clock_modifications=0,
              scope='Separate local diagnostic DLL. Hook appends the supplied clock/data before PSG decoding. '
                    'No CPU counter, sound register, chip update or event schedule changed. '
                    'Observer noninterference still requires comparison to the existing captured states.')
(out / 'build-report.json').write_text(json.dumps(result, indent=2) + '\n')
print('PSG write observer built; original emulator source restored.', flush=True)
