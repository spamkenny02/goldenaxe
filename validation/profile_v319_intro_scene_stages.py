"""Profile the six native loader stages; source code remains unchanged."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];work=root/'validation/v319-native-intro-poll-scene-throughput01'
p=work/'wrapper.c';old=p.read_bytes();assert b'scene_profile_frames' not in old
(work/'wrapper-whole-measured.c').write_bytes(old)
s=old.decode().replace('volatile u32 scene_native_frames;', 'volatile u32 scene_native_frames,scene_profile_frames[6];')
s=s.replace('scene_native_start=vtimer;', '__builtin_memset((void *)scene_profile_frames,0,sizeof(scene_profile_frames));scene_native_start=vtimer;')
p.write_bytes(s.encode())
p=work/'report.json';r=json.loads(p.read_bytes());r['profile_stages']=True;p.write_text(json.dumps(r,indent=2)+'\n')
subprocess.run([sys.executable,str(root/'validation/compile_v319_intro_poll_68k.py'),'--work',work.name,
 '--kernel-name','kernel3','--case-start','0','--case-count','10'],cwd=root,check=True)
