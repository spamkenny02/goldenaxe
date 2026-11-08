"""Measure live scene helper only, removing foreground expected-OUT comparisons."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--out-name',required=True);a=p.parse_args()
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
(out/'wrapper.c').write_text(s);(out/'pattern_expected.h').write_bytes((source/'pattern_expected.h').read_bytes())
report=json.loads((source/'report.json').read_bytes());report.update(measure_native_frames=True,throughput_only=True,profile_stages=False,max_kernel_frames=50000,scope='Helper-only native scene with ownedVDP status and real IRQ work: fixture copies and final comparisons excluded from measured interval,per-OUT expected-event checks disabled; all original final state/clock/status checks retained. Physical MD video/PSG excluded.')
report['native_sources']={name:hashlib.sha256((root/'megadrive/src'/(name+'.c')).read_bytes()).hexdigest() for name in report['native_sources']}
report['native_headers']={'source_video_clock_math.h':hashlib.sha256((root/'megadrive/src/source_video_clock_math.h').read_bytes()).hexdigest()} if (root/'megadrive/src/source_video_clock_math.h').exists() else {}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
for region in ('ntsc','pal'):
 (out/region).mkdir();(out/region/'native-cases.json').write_bytes((source/region/'native-cases.json').read_bytes())
subprocess.run([sys.executable,str(root/'validation/compile_v319_intro_poll_68k.py'),'--work',out.name],cwd=root,check=True)
