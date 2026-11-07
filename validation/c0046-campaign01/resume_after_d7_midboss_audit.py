"""Resume after a completed D7 intermediate audit; never replay the primary combat."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
r=json.loads((root/'analysis/palc0046_d7_midboss_report.json').read_bytes())
assert r['passed'] and r['intermediate_defeated'] and not r['intermediate_assistance'] and r['rom_sha256']=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
assert not (root/'validation/c0047-pal-d7-midboss01').exists()
assert not (project/'validation/palc0046-d7-finish-sources').exists()
subprocess.run([sys.executable,'validation/replay_c0047_pal.py','--report','analysis/palc0046_d7_midboss_report.json','--milestone','d7-midboss'],cwd=root,check=True)
subprocess.run([sys.executable,'-u','tools/continue_d7_finish_palc0046.py'],cwd=project,check=True)
