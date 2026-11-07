"""Prepare the PAL oil-to-Fire exchange, real Long Sword gift and D5 entry."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
s=(root/'validation/pal318-fire-sword-run01/run.py').read_text().replace('pal318','palc0046').replace('PAL V318','PAL c0046')
s=s.replace('b9e1f0a0543f191e24ffd6d2740a0d717501e0fcd986f8b8953a37a1b3c416a4','9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5')
s=s.replace('helper.EVIDENCE=Path(__file__).resolve().parent',"helper.EVIDENCE=ROOT/'validation/palc0046-fire-sword-sources'")
s=s.replace('pal_d4_v0318_report.json','palc0046_d4_report.json').replace("prior['fourth_crystal_and_exit']","prior['actual_fourth_crystal_and_exterior']").replace("prior['md_sha256']","prior['rom_sha256']")
s=s.replace('md-pal-palc0046-d4-exit02','md-pal-palc0046-d4-exit01')
s=s.replace("    index={}","    helper.EVIDENCE.mkdir(exist_ok=False)\n    index={}")
s=s.replace("('continue_fire_sword_v0317.py'", "('continue_fire_sword_palc0046.py','run_core.py'")
p=project/'tools/continue_fire_sword_palc0046.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf-8')
print('PAL Fire and Long Sword controller prepared with verified fourth-crystal receipt')
