"""Adapt the existing source64 boss controller and audit to the isolated ROM."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
project=root/'validation/c0046-campaign01/isolated/project'
for name in ('finish_d6','summarize_d6_campaign'):
    text=(root/'tools'/f'{name}_v0317.py').read_text()
    text=text.replace('v0317','c0046').replace('V317','C0046').replace('v317:','c0046:')
    if name.startswith('summarize'):
        old='7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294'
        assert old in text
        text=text.replace(old,'9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5')
        text=text.replace('version=317',"candidate='c0046'")
        text=text.replace("previous = ROOT/prior['ready_trace']", "previous = ROOT/'validation/natural-dungeon-combat'/prior['ready_trace'].split('/')[-1]")
        text=text.replace(' refs = {}',' refs = {}; origins={}; global_root=ROOT.parents[3]')
        before="  raw = evidence(p); refs[p.relative_to(ROOT).as_posix()] = sha(raw); return raw"
        after="  raw=evidence(p); name=p.relative_to(ROOT).as_posix(); refs[name]=sha(raw); origins[name]=p.resolve().relative_to(global_root).as_posix(); return raw"
        assert text.count(before)==1
        text=text.replace(before,after)
        marker=" (ROOT/'analysis/d6_campaign_c0046_report.json').write_bytes"
        assert text.count(marker)==1
        text=text.replace(marker," prefix=ROOT.relative_to(global_root).as_posix()+'/'\n for stage in result['stages']:stage['trace']=prefix+stage['trace']\n result['evidence']={origins[name]:h for name,h in refs.items()}\n"+marker)
    target=project/'tools'/f'{name}_c0046.py';assert not target.exists()
    target.write_text(text,encoding='utf-8')
print('D6 boss, exterior return and source-stat audit prepared; not executed')
