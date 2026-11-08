"""Recheck final full-command map batching and profile the whole scene budget."""
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for name in ('scene-runs04','map-runs01'):
 subprocess.run([sys.executable,str(root/'validation/compile_v319_intro_poll_68k.py'),'--work','v319-native-intro-poll-'+name],cwd=root,check=True)
subprocess.run([sys.executable,str(root/'validation/build_v319_intro_scene_profile.py'),
 '--source-work','v319-native-intro-poll-scene-runs04','--out-name','v319-native-intro-poll-scene-throughput05'],cwd=root,check=True)
