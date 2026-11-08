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
for header in profile_report.get('extra_headers',[]):
    assert re.fullmatch(r'source_[a-z_]+\.h',header)
    (inc/header).write_text('#include "../../../../megadrive/src/'+header+'"\n')
profile_stages=profile_report.get('profile_stages',False)
measure_native=profile_report.get('measure_native_frames',False)
scene=profile_report.get('scene',False)
map_mode=profile_report.get('map')
transfer=profile_report.get('transfer',False)
sequence=profile_report.get('sequence',False)
reveal=profile_report.get('reveal',False)
fire=profile_report.get('fire',False);actors=profile_report.get('actors');irq_status=profile_report.get('irq_status',False)
if fire or sequence: (inc/'source_intro_fire.h').write_text('#include "../../../../megadrive/src/source_intro_fire.h"\n')
if scene:(inc/'source_intro_scene.h').write_text('#include "../../../../megadrive/src/source_intro_scene.h"\n')
if map_mode:(inc/'source_intro_map.h').write_text('#include "../../../../megadrive/src/source_intro_map.h"\n')
if transfer:(inc/'source_intro_video.h').write_text('#include "../../../../megadrive/src/source_intro_video.h"\n')
if reveal:(inc/'source_intro_reveal.h').write_text('#include "../../../../megadrive/src/source_intro_reveal.h"\n')
if actors:(inc/'source_intro_actors.h').write_text('#include "../../../../megadrive/src/source_intro_actors.h"\n')
for module in (['source_intro_scene','source_pattern_clock'] if scene else [])+(['source_intro_map'] if map_mode else [])+(['source_intro_video'] if transfer else [])+(['source_intro_actors','source_intro_fire'] if sequence else ['source_intro_fire'] if fire else [])+(['source_intro_reveal' if reveal else 'source_intro_actors'] if actors else [])+['source_intro_wait', 'source_wait_restore', *MODULES]+profile_report.get('extra_modules',[]):
    prefix='#define source_irq_interrupt source_irq_interrupt_impl\n' if irq_status and module=='source_irq_context' else ''
    if profile_stages and module=='source_intro_scene':
        prefix='#include <genesis.h>\n#include "../../../../megadrive/src/source_intro_scene.h"\nextern volatile u32 scene_profile_frames[6];\n'
        for index,name in [(0,'source_intro_map_prepare'),(1,'source_pattern_decode'),(1,'source_pattern_decode_planned'),(1,'source_pattern_decode_runs'),(2,'source_intro_plane_clear'),(3,'source_intro_map_decode'),(4,'source_intro_map_place'),(5,'source_intro_map_transfer')]:
            prefix+=f'#define {name}(...) ({{u32 began=vtimer;u8 accepted={name}(__VA_ARGS__);scene_profile_frames[{index}]+=vtimer-began;accepted;}})\n'
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
         'typedef struct {u32 phase[12];u8 refresh,ram[RAM_BYTES],audio[400],after_ram[RAM_BYTES],after_audio[400];u32 expected[18];'+(f"u32 events[{max(1,max(len(c['events']) for c in cases))}];" if reveal else '')+'} PollCase;',
         'static const PollCase cases[]={']
for case in cases:
    lines.append('{' + ','.join([array(case['phase']), str(case['refresh']), array(case['input_ram']),
        array(case['input_audio']), array(case['expected_ram']), array(case['expected_audio']), array(case['expected'])]+([array(case['events'])] if reveal else [])) + '},')
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
if reveal:
    main=(src/'main.c').read_text().replace('int main(bool hard_reset)',
        'void configure_reveal_events(const u32 *,u16);\nint main(bool hard_reset)')
    main=main.replace('if(!poll_case(entry->phase',
        "configure_reveal_events(entry->events,(u16)entry->expected[12]);\n  if(!poll_case(entry->phase")
    (src/'main.c').write_text(main)
if measure_native:
    main=(src/'main.c').read_text().replace('int main(bool hard_reset)',
        'extern volatile u32 scene_native_frames;\nvolatile u32 intro_scene_elapsed[sizeof(cases)/sizeof(cases[0])];\nint main(bool hard_reset)')
    main=main.replace('intro_poll_cases++;','intro_scene_elapsed[n]=scene_native_frames;\n  intro_poll_cases++;')
    (src/'main.c').write_text(main)
if profile_stages:
    main=(src/'main.c').read_text().replace('extern volatile u32 scene_native_frames;',
        'extern volatile u32 scene_native_frames,scene_profile_frames[6];\nvolatile u32 intro_scene_stage_elapsed[sizeof(cases)/sizeof(cases[0])][6];')
    main=main.replace('intro_scene_elapsed[n]=scene_native_frames;',
        'intro_scene_elapsed[n]=scene_native_frames;\n  for(i=0;i<6;i++) intro_scene_stage_elapsed[n][i]=scene_profile_frames[i];')
    (src/'main.c').write_text(main)
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
        if measure_native and stats['intro_poll_done']:
            base=sy['intro_scene_elapsed']
            stats['native_call_frames']=[int.from_bytes(bytes(raw[(base+n*4+i)^1] for i in range(4)),'big') for n in range(len(cases))]
            if profile_stages:
                base=sy['intro_scene_stage_elapsed']
                stats['native_stage_frames']=[[int.from_bytes(bytes(raw[(base+n*24+j*4+i)^1] for i in range(4)),'big') for j in range(6)] for n in range(len(cases))]
    with contextlib.redirect_stdout(io.StringIO()):
        run(project / 'out/release/rom.bin', profile_report.get('max_kernel_frames',5000), work / (run_prefix + '-' + region), set(), [], skip_intro=False,
            ram_observer=observe, stop_when=lambda: bool(stats.get('intro_poll_done')),
            core_options={'genesis_plus_gx_region_detect': 'pal' if region == 'pal' else 'auto'})
    assert stats['intro_poll_done'] == 1 and stats['intro_poll_errors'] == 0, stats
    assert stats['intro_poll_cases'] == len(cases) and stats['intro_poll_reads'] == expected_reads
    results.append(dict(region=region, **stats)); print(region, stats, flush=True)
report = dict(passed=True, diagnostic_only=True, source_vector_cases=len(cases), source_regions=source_regions,
    case_start=a.case_start,ram_bytes=ram_bytes,fire=fire,actors=actors,reveal=reveal,sequence=sequence,transfer=transfer,map=map_mode,scene=scene,measure_native_frames=measure_native,profile_stages=profile_stages,irq_status=irq_status,results=results,
    kernel_sha256=sha((project / 'out/release/rom.bin').read_bytes()),
    scope='Compiled68000 source semantic helper checked against the selected natural original source vectors '
          'on each target region. No physical publication scheduler or PCM claim.')
name = 'compiled-report.json' if a.source_region == 'both' else 'compiled-' + a.source_region + '-report.json'
if partitioned:name=run_prefix+'-report.json'
(work / name).write_text(json.dumps(report, indent=2) + '\n')
