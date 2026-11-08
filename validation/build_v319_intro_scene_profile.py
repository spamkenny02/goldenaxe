"""Build a reproducible final-state-checked native loader CPU profile, no OUT oracle."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--source-work',required=True);p.add_argument('--out-name',required=True);a=p.parse_args()
source=(root/'validation'/a.source_work).resolve();out=(root/'validation'/a.out_name).resolve()
report=json.loads((source/'report.json').read_bytes())
for name,digest in report['native_sources'].items():assert hashlib.sha256((root/'megadrive/src'/(name+'.c')).read_bytes()).hexdigest()==digest
for name,digest in report.get('native_assets',{}).items():assert hashlib.sha256((root/'megadrive/src'/name).read_bytes()).hexdigest()==digest
assert source.is_relative_to(root/'validation') and out.is_relative_to(root/'validation') and not out.exists();out.mkdir()
s=(source/'wrapper.c').read_text();needle='scene_vram,sequence_callback,&sequence_data,reveal_sink,0,&sequence)';assert needle in s
s=s.replace(needle,'scene_vram,sequence_callback,&sequence_data,0,0,&sequence)')
s=s.replace('#include "source_intro_scene.h"','#include <genesis.h>\n#include "source_intro_scene.h"\nvolatile u32 scene_native_frames,scene_profile_frames[6];static u32 scene_native_start;')
s=s.replace('if(!source_intro_scene_load(', '__builtin_memset((void *)scene_profile_frames,0,sizeof(scene_profile_frames));scene_native_start=vtimer;\n if(!source_intro_scene_load(')
s=s.replace('if(irq_status_position!=irq_status_count) return 0;', 'scene_native_frames=vtimer-scene_native_start;\n if(irq_status_position!=irq_status_count) return 0;')
(out/'wrapper.c').write_bytes(s.encode())
r=json.loads((source/'report.json').read_bytes());r.update(throughput_only=True,measure_native_frames=True,profile_stages=True,
 source_data_reused_from=source.relative_to(root).as_posix(),scope='Native helper and six stage frame deltas, excluding fixture copies/final comparisons. OUT oracle disabled; every final RAM/VRAM/clock state still checked. No physical video or PSG publication.')
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
for region in ('ntsc','pal'):
 (out/region).mkdir();cases=json.loads((source/region/'native-cases.json').read_bytes())
 for case in cases:case['events']=[];case['expected'][12]=0
 (out/region/'native-cases.json').write_text(json.dumps(cases,separators=(',',':'))+'\n')
subprocess.run([sys.executable,str(root/'validation/compile_v319_intro_poll_68k.py'),'--work',out.name],cwd=root,check=True)
