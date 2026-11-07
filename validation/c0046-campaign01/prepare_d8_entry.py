"""Prepare the paid route and source-stat D8 intermediate for the candidate."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
project=root/'validation/c0046-campaign01/isolated/project'
for name in ('continue_d8_entry','summarize_d8_midboss'):
    text=(root/'tools'/f'{name}_v0317.py').read_text().replace('v0317','c0046').replace('v317','c0046')
    if name.startswith('summarize'):
        text=text.replace('version=317',"candidate='c0046'")
        text=text.replace("folder=p/prior['stages'][-1]['trace']", "folder=p/'validation/natural-dungeon-combat'/prior['stages'][-1]['trace'].split('/')[-1]")
        marker="(p/'analysis/d8_midboss_c0046_report.json').write_bytes"
        assert text.count(marker)==1
        text=text.replace(marker,"prefix=p.relative_to(p.parents[3]).as_posix()+'/'\nfor stage in report['stages']:stage['trace']=prefix+stage['trace']\nreport['evidence']={(name if name.startswith('analysis/') else prefix+name):h for name,h in refs.items()}\n"+marker)
    target=project/'tools'/f'{name}_c0046.py';assert not target.exists()
    target.write_text(text,encoding='utf-8')
print('D8 paid passage, optional real healing and source-stat intermediate prepared; not executed')
