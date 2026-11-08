"""Compile final scene and strided-copy proofs, then profile current exact ROM plans."""
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for name in ('scene-runs03','place-runs01'):
 subprocess.run([sys.executable,str(root/'validation/compile_v319_intro_poll_68k.py'),'--work','v319-native-intro-poll-'+name],cwd=root,check=True)
subprocess.run([sys.executable,str(root/'validation/build_v319_intro_scene_profile.py'),
 '--source-work','v319-native-intro-poll-scene-runs03','--out-name','v319-native-intro-poll-scene-throughput04'],cwd=root,check=True)
