"""Run original F21/F2B snapshot vectors through the actual compiled68000 helper."""
import argparse
import contextlib
import io
import json
import os
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
p.add_argument('--source-region', choices=['both','ntsc','pal'], default='both')
p.add_argument('--case-start',type=int,default=0)
p.add_argument('--case-count',type=int)
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
profile_report=json.loads((work/'report.json').read_bytes())
fire=profile_report.get('fire',False);actors=profile_report.get('actors');irq_status=profile_report.get('irq_status',False)
if fire: (inc/'source_intro_fire.h').write_text('#include "../../../../megadrive/src/source_intro_fire.h"\n')
if actors:(inc/'source_intro_actors.h').write_text('#include "../../../../megadrive/src/source_intro_actors.h"\n')
for module in (['source_intro_fire'] if fire else [])+(['source_intro_actors'] if actors else [])+['source_intro_wait', 'source_wait_restore', *MODULES]:
    prefix='#define source_irq_interrupt source_irq_interrupt_impl\n' if irq_status and module=='source_irq_context' else ''
    (src / (module + '.c')).write_text(prefix+'#include "../../../../megadrive/src/' + module + '.c"\n')
(src / 'wrapper.c').write_text('#include "../../wrapper.c"\n')
image = (root / 'input/original.sms').read_bytes()
def array(raw): return '{' + ','.join(map(str, raw)) + '}'
source_regions = ('ntsc','pal') if a.source_region == 'both' else (a.source_region,)
cases = [case for region in source_regions for case in json.loads((work / region / 'native-cases.json').read_bytes())]
assert a.case_start>=0 and (a.case_count is None or a.case_count>0)
cases=cases[a.case_start:None if a.case_count is None else a.case_start+a.case_count]
assert cases
ram_bytes=len(cases[0]['input_ram'])
expected_reads = sum(case['expected'][12] for case in cases)
lines = ['static const u8 low[32768]=' + array(image[:32768]) + ';',
         'static const u8 bank[16384]=' + array(image[0x18000:0x1c000]) + ';',
         f'#define RAM_BYTES {ram_bytes}',
         'typedef struct {u32 phase[12];u8 refresh,ram[RAM_BYTES],audio[400],after_ram[RAM_BYTES],after_audio[400];u32 expected[18];} PollCase;',
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
 u16 n,i;u8 ram[RAM_BYTES],audio[400];u32 output[18];(void)hard_reset;VDP_setEnable(FALSE);
 for(n=0;n<sizeof(cases)/sizeof(cases[0]);n++)
 {
  const PollCase *entry=cases+n;
  memcpy(ram,entry->ram,RAM_BYTES);memcpy(audio,entry->audio,400);
  if(!poll_case(entry->phase,entry->refresh,ram,audio,low,bank,output)) intro_poll_errors++;
  else {
   for(i=0;i<18;i++) if(output[i]!=entry->expected[i]) intro_poll_errors++;
   for(i=0;i<RAM_BYTES;i++) if(ram[i]!=entry->after_ram[i]) intro_poll_errors++;
   for(i=0;i<400;i++) if(audio[i]!=entry->after_audio[i]) intro_poll_errors++;
   intro_poll_reads+=output[12];
  }
  if(intro_poll_errors && !intro_poll_first_failure) intro_poll_first_failure=n+1;
  intro_poll_cases++;
 }
 intro_poll_done=1;while(TRUE) SYS_doVBlankProcess();return 0;
}
''')
build_env=dict(os.environ)
for key in ('TMPDIR','TMP','TEMP'):build_env[key]='.'
built=subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
    str(root / 'tools/build_private_candidate.ps1'), '-Project', str(project), '-PaddingByte', '255'], cwd=root, env=build_env)
if built.returncode:
    failure=(project/'build.log').read_bytes()
    failure=failure.decode('utf-16' if failure.startswith(b'\xff\xfe') else 'utf-8')
    if 'Cannot create temporary file' not in failure or 'lto-wrapper failed' not in failure:
        raise subprocess.CalledProcessError(built.returncode,built.args)
    subprocess.run([sys.executable,str(root/'validation/relink_v319_kernel_serial.py'),'--project',str(project)],cwd=root,check=True)
sy = {m[2].split('.lto_priv.')[0]: int(m[1], 16) & 65535 for line in (project / 'out/release/symbol.txt').read_text().splitlines()
      if (m := re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)', line))}
results = []
partitioned=a.case_start>0 or a.case_count is not None
run_prefix='compiled-'+a.source_region+('-'+a.kernel_name if partitioned else '')
for region in ('ntsc', 'pal'):
    stats = {}
    def observe(frame, raw):
        for name, size in [('intro_poll_done',2), ('intro_poll_cases',4), ('intro_poll_errors',4),
                           ('intro_poll_reads',4), ('intro_poll_first_failure',2)]:
            stats[name] = int.from_bytes(bytes(raw[(sy[name] + i) ^ 1] for i in range(size)), 'big')
        stats['frame'] = frame
    with contextlib.redirect_stdout(io.StringIO()):
        run(project / 'out/release/rom.bin', 5000, work / (run_prefix + '-' + region), set(), [], skip_intro=False,
            ram_observer=observe, stop_when=lambda: bool(stats.get('intro_poll_done')),
            core_options={'genesis_plus_gx_region_detect': 'pal' if region == 'pal' else 'auto'})
    assert stats['intro_poll_done'] == 1 and stats['intro_poll_errors'] == 0, stats
    assert stats['intro_poll_cases'] == len(cases) and stats['intro_poll_reads'] == expected_reads
    results.append(dict(region=region, **stats)); print(region, stats, flush=True)
report = dict(passed=True, diagnostic_only=True, source_vector_cases=len(cases), source_regions=source_regions,
    case_start=a.case_start,ram_bytes=ram_bytes,fire=fire,actors=actors,irq_status=irq_status,results=results,
    kernel_sha256=sha((project / 'out/release/rom.bin').read_bytes()),
    scope='Compiled68000 source semantic helper checked against the selected natural original source vectors '
          'on each target region. No physical publication scheduler or PCM claim.')
name = 'compiled-report.json' if a.source_region == 'both' else 'compiled-' + a.source_region + '-report.json'
if partitioned:name=run_prefix+'-report.json'
(work / name).write_text(json.dumps(report, indent=2) + '\n')
