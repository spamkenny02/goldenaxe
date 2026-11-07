"""Prepare ship, main boss and seventh-crystal candidate continuation."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
project=root/'validation/c0046-campaign01/isolated/project'
for name in ('continue_d7_finish','summarize_d7_campaign'):
    text=(root/'tools'/f'{name}_v0317.py').read_text().replace('v0317','c0046')
    if name.startswith('summarize'):
        text=text.replace('version=317',"candidate='c0046'")
        text=text.replace('    hashes = {}','    hashes = {};origins={};global_root=ROOT.parents[3]')
        before="        hashes[path.relative_to(ROOT).as_posix()] = sha(raw)"
        assert text.count(before)==1
        text=text.replace(before,"        name=path.relative_to(ROOT).as_posix();hashes[name]=sha(raw);origins[name]=path.resolve().relative_to(global_root).as_posix()")
        text=text.replace("    previous = ROOT / previous_proof['stages'][-1]['trace']", "    previous=ROOT/'validation/natural-dungeon-combat'/previous_proof['stages'][-1]['trace'].split('/')[-1]")
        marker="    (ROOT / f'analysis/d7_{suffix}_c0046_report.json').write_text"
        assert text.count(marker)==1
        text=text.replace(marker,"    prefix=ROOT.relative_to(global_root).as_posix()+'/'\n    for stage in report['stages']:stage['trace']=prefix+stage['trace']\n    report['evidence']={origins[name]:h for name,h in hashes.items()}\n"+marker)
    target=project/'tools'/f'{name}_c0046.py';assert not target.exists()
    target.write_text(text,encoding='utf-8')
print('D7 ship, main boss, crystal and return controller prepared; not executed')
