"""Prepare the remaining native candidate palace campaign without weakening its audits."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[2]
project=root/'validation/c0046-campaign01/isolated/project'
for part in ('inner','guardian','final'):
    for kind in ('continue','summarize'):
        name=f'{kind}_palace_{part}'
        text=(root/'tools'/f'{name}_v0317.py').read_text()
        text=text.replace('v0317','c0046').replace('v317','c0046').replace('V317','c0046')
        if kind=='continue':
            text=text.replace("receipt['current_campaign_trace'].removeprefix('validation/')", "('natural-dungeon-combat/'+receipt['current_campaign_trace'].split('/')[-1])")
        else:
            text=text.replace('version=317',"candidate='c0046'")
            text=text.replace(' refs={}', ' refs={};origins={};global_root=ROOT.parents[3]')
            before="  raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw"
            after="  raw=evidence(p);n=p.relative_to(ROOT).as_posix();refs[n]=sha(raw);origins[n]=p.resolve().relative_to(global_root).as_posix();return raw"
            assert text.count(before)==1;text=text.replace(before,after)
            text=text.replace("previous=ROOT/prior['current_campaign_trace']", "previous=ROOT/'validation/natural-dungeon-combat'/prior['current_campaign_trace'].split('/')[-1]")
            marker=" (ROOT/'analysis/";assert text.count(marker)==1
            normalize=" prefix=ROOT.relative_to(global_root).as_posix()+'/'\n result['current_campaign_trace']=prefix+result['current_campaign_trace']\n for stage in result['stages']:stage['trace']=prefix+stage['trace']\n result['evidence']={origins[n]:h for n,h in refs.items()}\n"
            text=text.replace(marker,normalize+marker)
        ast.parse(text)
        target=project/'tools'/f'{name}_c0046.py';assert not target.exists();target.write_text(text,encoding='utf-8')
print('Six remaining palace scripts prepared, not executed; preceding campaign audits required')
