"""Measure live scene helper only, removing foreground expected-OUT comparisons."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--out-name',required=True);p.add_argument('--runs',action='store_true');p.add_argument('--stages',action='store_true');p.add_argument('--scene-runs',action='store_true');a=p.parse_args()
source=root/'validation/v319-scene-live-vdp02';out=(root/'validation'/a.out_name).resolve();assert out.is_relative_to(root/'validation') and not out.exists();out.mkdir()
s=(source/'wrapper.c').read_text()
begin=s.index('static u8 pattern_sink(');end=s.index('\n}',begin)+2
s=s[:begin]+'''static u8 pattern_sink(void *user,u32 elapsed,u32 raster,u8 port,u8 value)
{(void)user;pattern_position++;video_total++;return source_intro_scene_vdp_pattern(&live_video,elapsed,raster,port,value);}
'''+s[end:]
begin=s.index('static u8 reveal_sink(');end=s.index('\n}',begin)+2
s=s[:begin]+'''static u8 reveal_sink(void *user,u32 elapsed,u32 raster,u8 port,u8 value)
{(void)user;reveal_event_position++;video_total++;return source_intro_scene_vdp_map(&live_video,elapsed,raster,port,value);}
'''+s[end:]
s=s.replace('#include "source_intro_scene.h"','#include <genesis.h>\n#include "source_intro_scene.h"\nvolatile u32 scene_native_frames;static u32 scene_started;')
needle='if(!source_intro_scene_load_ports(';assert s.count(needle)==1;s=s.replace(needle,'scene_started=vtimer;\n '+needle)
needle='if(pattern_position!=pattern_count) return 0;';assert s.count(needle)==1;s=s.replace(needle,'scene_native_frames=vtimer-scene_started;\n '+needle)
if a.runs:
 anchor='static u32 pattern_count,pattern_position,pattern_origin,video_last,video_total;'
 s=s.replace(anchor,anchor+'''\nstatic u8 pattern_run(void *user,const SourcePatternVideoRun *run)
{(void)user;pattern_position+=(u32)run->count*3;video_total+=(u32)run->count*3;return source_intro_vdp_pattern_run(&live_video,run);}
''')
 s=s.replace('source_intro_scene_load_ports(', 'source_intro_scene_load_runs(').replace('pattern_sink,0,&sequence)', 'pattern_sink,0,pattern_run,&sequence)')
s=s.replace('if(irq_status_position!=irq_status_count) return 0;', 'if(irq_status_position!=irq_status_count || live_status_differences) return 0;')
if a.scene_runs:
 assert a.runs
 anchor='static u8 reveal_sink('
 s=s.replace(anchor,'''static u8 map_run(void *user,const SourceIntroVideoRun *run)
{(void)user;u32 outputs=(u32)run->count*(run->kind==SOURCE_INTRO_VIDEO_CLEAR?3:1);reveal_event_position+=outputs;video_total+=outputs;return source_intro_scene_vdp_run(&live_video,run);}
'''+anchor)
 s=s.replace('source_intro_scene_load_runs(', 'source_intro_scene_load_video_runs(').replace('pattern_run,&sequence)', 'pattern_run,map_run,&sequence)')
if a.stages:
 s=s.replace('volatile u32 scene_native_frames;', 'volatile u32 scene_native_frames,scene_profile_frames[6];')
 s=s.replace('scene_started=vtimer;', '__builtin_memset((void *)scene_profile_frames,0,sizeof(scene_profile_frames));scene_started=vtimer;')
(out/'wrapper.c').write_text(s);(out/'pattern_expected.h').write_bytes((source/'pattern_expected.h').read_bytes())
report=json.loads((source/'report.json').read_bytes());report.update(measure_native_frames=True,throughput_only=True,profile_stages=a.stages,max_kernel_frames=50000,scope='Helper-only native scene with ownedVDP status and real IRQ work: fixture copies and final comparisons excluded from measured interval,per-OUT expected-event checks disabled; all original final state/clock/status checks retained. Physical MD video/PSG excluded.')
report['native_sources']={name:hashlib.sha256((root/'megadrive/src'/(name+'.c')).read_bytes()).hexdigest() for name in report['native_sources']}
report['native_sources']['source_irq_workspace']=hashlib.sha256((root/'megadrive/src/source_irq_workspace.c').read_bytes()).hexdigest()
if 'source_irq_workspace' not in report['extra_modules']:report['extra_modules'].append('source_irq_workspace')
report['native_headers']={'source_video_clock_math.h':hashlib.sha256((root/'megadrive/src/source_video_clock_math.h').read_bytes()).hexdigest()} if (root/'megadrive/src/source_video_clock_math.h').exists() else {}
report['pattern_runs']=a.runs
report['scene_video_runs']=a.scene_runs
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
for region in ('ntsc','pal'):
 (out/region).mkdir();(out/region/'native-cases.json').write_bytes((source/region/'native-cases.json').read_bytes())
subprocess.run([sys.executable,str(root/'validation/compile_v319_intro_poll_68k.py'),'--work',out.name],cwd=root,check=True)
