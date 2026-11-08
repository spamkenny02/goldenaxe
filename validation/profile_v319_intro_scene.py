"""Measure only the native composed helper, excluding fixture copies and final comparisons."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];work=root/'validation/v319-native-intro-poll-scene-throughput01'
p=work/'wrapper.c';old=p.read_bytes();assert b'scene_native_start' not in old
(work/'wrapper-unmeasured.c').write_bytes(old)
s=old.decode().replace('#include "source_intro_scene.h"','#include <genesis.h>\n#include "source_intro_scene.h"\nvolatile u32 scene_native_frames;static u32 scene_native_start;')
s=s.replace('if(!source_intro_scene_load(', 'scene_native_start=vtimer;\n if(!source_intro_scene_load(')
needle='if(irq_status_position!=irq_status_count) return 0;';assert needle in s
s=s.replace(needle,'scene_native_frames=vtimer-scene_native_start;\n '+needle)
p.write_bytes(s.encode())
p=work/'report.json';r=json.loads(p.read_bytes());r['measure_native_frames']=True;p.write_text(json.dumps(r,indent=2)+'\n')
subprocess.run([sys.executable,str(root/'validation/compile_v319_intro_poll_68k.py'),'--work',work.name,
 '--kernel-name','kernel2','--case-start','0','--case-count','10'],cwd=root,check=True)
