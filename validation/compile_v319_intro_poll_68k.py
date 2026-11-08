"""Run original F21/F2B snapshot vectors through the actual compiled68000 helper."""
import argparse
import contextlib
import io
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from run_core import run
from archive_lossless_evidence import sha
from validate_native_source_wait import MODULES

p = argparse.ArgumentParser()
p.add_argument('--work', default='v319-native-intro-poll01')
p.add_argument('--kernel-name', default='kernel')
a = p.parse_args()
work = root / 'validation' / a.work
assert work.resolve().is_relative_to(root / 'validation')
assert re.fullmatch(r'kernel[0-9]*', a.kernel_name)
project = work / a.kernel_name
assert not project.exists()
src = project / 'src'; src.mkdir(parents=True)
shutil.copyfile(root / 'megadrive/src/rom_header.c', src / 'rom_header.c')
inc = project / 'inc'; inc.mkdir()
(inc / 'source_intro_wait.h').write_text('#include "../../../../megadrive/src/source_intro_wait.h"\n')
for module in ['source_intro_wait', 'source_wait_restore', *MODULES]:
    (src / (module + '.c')).write_text('#include "../../../../megadrive/src/' + module + '.c"\n')
(src / 'wrapper.c').write_text('#include "../../wrapper.c"\n')
image = (root / 'input/original.sms').read_bytes()
def array(raw): return '{' + ','.join(map(str, raw)) + '}'
cases = [case for region in ('ntsc', 'pal') for case in json.loads((work / region / 'native-cases.json').read_bytes())]
lines = ['static const u8 low[32768]=' + array(image[:32768]) + ';',
         'static const u8 bank[16384]=' + array(image[0x18000:0x1c000]) + ';',
         'typedef struct {u32 phase[12];u8 refresh,ram[336],audio[400],after_ram[336],after_audio[400];u32 expected[18];} PollCase;',
         'static const PollCase cases[]={']
for case in cases:
    lines.append('{' + ','.join([array(case['phase']), str(case['refresh']), array(case['input_ram']),
        array(case['input_audio']), array(case['expected_ram']), array(case['expected_audio']), array(case['expected'])]) + '},')
lines.append('};')
(src / 'expected.h').write_text('\n'.join(lines) + '\n')
(src / 'main.c').write_text('''#include <genesis.h>
#include "expected.h"
u8 poll_case(const u32 *,u8,u8 *,u8 *,const u8 *,const u8 *,u32 *);
volatile u16 intro_poll_done,intro_poll_first_failure;
volatile u32 intro_poll_cases,intro_poll_errors,intro_poll_reads;
int main(bool hard_reset)
{
 u16 n,i;u8 ram[336],audio[400];u32 output[18];(void)hard_reset;VDP_setEnable(FALSE);
 for(n=0;n<sizeof(cases)/sizeof(cases[0]);n++)
 {
  const PollCase *entry=cases+n;
  memcpy(ram,entry->ram,336);memcpy(audio,entry->audio,400);
  if(!poll_case(entry->phase,entry->refresh,ram,audio,low,bank,output)) intro_poll_errors++;
  else {
   for(i=0;i<18;i++) if(output[i]!=entry->expected[i]) intro_poll_errors++;
   for(i=0;i<336;i++) if(ram[i]!=entry->after_ram[i]) intro_poll_errors++;
   for(i=0;i<400;i++) if(audio[i]!=entry->after_audio[i]) intro_poll_errors++;
   intro_poll_reads+=output[12];
  }
  if(intro_poll_errors && !intro_poll_first_failure) intro_poll_first_failure=n+1;
  intro_poll_cases++;
 }
 intro_poll_done=1;while(TRUE) SYS_doVBlankProcess();return 0;
}
''')
subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
    str(root / 'tools/build_private_candidate.ps1'), '-Project', str(project), '-PaddingByte', '255'], cwd=root, check=True)
sy = {m[2].split('.lto_priv.')[0]: int(m[1], 16) & 65535 for line in (project / 'out/release/symbol.txt').read_text().splitlines()
      if (m := re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)', line))}
results = []
for region in ('ntsc', 'pal'):
    stats = {}
    def observe(frame, raw):
        for name, size in [('intro_poll_done',2), ('intro_poll_cases',4), ('intro_poll_errors',4),
                           ('intro_poll_reads',4), ('intro_poll_first_failure',2)]:
            stats[name] = int.from_bytes(bytes(raw[(sy[name] + i) ^ 1] for i in range(size)), 'big')
        stats['frame'] = frame
    with contextlib.redirect_stdout(io.StringIO()):
        run(project / 'out/release/rom.bin', 5000, work / ('compiled-' + region), set(), [], skip_intro=False,
            ram_observer=observe, stop_when=lambda: bool(stats.get('intro_poll_done')),
            core_options={'genesis_plus_gx_region_detect': 'pal' if region == 'pal' else 'auto'})
    assert stats['intro_poll_done'] == 1 and stats['intro_poll_errors'] == 0, stats
    assert stats['intro_poll_cases'] == len(cases) and stats['intro_poll_reads'] == 172770
    results.append(dict(region=region, **stats)); print(region, stats, flush=True)
report = dict(passed=True, diagnostic_only=True, source_vector_cases=len(cases), results=results,
    kernel_sha256=sha((project / 'out/release/rom.bin').read_bytes()),
    scope='Compiled68000 source semantic helper checked against172 natural original source poll vectors, '
          'including both source region phases on each target region. No physical publication scheduler or PCM claim.')
(work / 'compiled-report.json').write_text(json.dumps(report, indent=2) + '\n')
