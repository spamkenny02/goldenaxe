"""Complete the prepared palace branch only after its first giant audit passes."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
r=json.loads((root/'analysis/cold_palace_giant_c0046_report.json').read_bytes())
assert r['passed'] and r['candidate']=='c0046' and r['cold_palace_giant_defeated']
assert r['md_sha256']=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
commands=[(root,'validation/c0046-campaign01/archive_palace.py',['entry']),
          (root,'validation/c0046-campaign01/archive_palace.py',['giant'])]
for part in ('inner','guardian','final'):
    commands.extend([(project,f'tools/continue_palace_{part}_c0046.py',[]),
                     (project,f'tools/summarize_palace_{part}_c0046.py',[]),
                     (root,'validation/c0046-campaign01/archive_palace.py',[part])])
commands.extend([(root,'validation/replay_c0047_palace.py',['final']),
                 (project,'tools/continue_after_d9_c0046.py',['save'])])
for cwd,tool,args in commands:
    print('PALACE FINISH START',tool,*args,flush=True)
    subprocess.run([sys.executable,'-u',tool,*args],cwd=cwd,check=True)
    print('PALACE FINISH PASSED',tool,flush=True)
print('Native candidate reached ending and actual save/Continue; full source fidelity and PAL campaign remain open',flush=True)
