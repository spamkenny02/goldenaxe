"""Prepare D7 intermediate: guard release, real boss, then resume next approach."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
s=(root/'validation/pal318-d7-midboss01/run.py').read_text().replace('pal318','palc0046').replace("default='02'","default='01'").replace('pal_d7_prep_v0318_report.json','palc0046_d7_preparation_report.json').replace("prior['md_sha256']","prior['rom_sha256']")
s=s.replace("previous = prior['stages'][-1]['trace'].removeprefix('validation/')", "previous = 'natural-dungeon-combat/'+Path(prior['current_campaign_trace']).name")
s=s.replace('out=Path(__file__).resolve().parent', "out=ROOT/'validation/palc0046-d7-midboss-sources'\n    out.mkdir(exist_ok=False)")
s=s.replace("'continue_d7_midboss_v0317.py'", "'continue_d7_midboss_palc0046.py'")
s=s.replace("stream=ReplayStream(out/'cold-stream')", "stream=ReplayStream(ROOT/'validation/palc0046-d7-midboss-cold-stream01')")
s=s.replace("common=['--pal','--assisted-prefix'", "common=['--pal','--wake-sentinels','--assisted-prefix'")
p=project/'tools/continue_d7_midboss_palc0046.py';assert not p.exists();ast.parse(s);p.write_text(s)
print('D7 intermediate controller prepared; requires successful D7 preparation audit')
