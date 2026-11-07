"""Prepare owned Balloon and palace entry/giant controllers; run only after D9 audit."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[2]
project=root/'validation/c0046-campaign01/isolated/project'
names=('continue_after_d9','summarize_owned_overview','summarize_palace_entry',
       'continue_palace_giant','summarize_palace_giant')
for name in names:
    text=(root/'tools'/f'{name}_v0317.py').read_text().replace('v0317','c0046').replace('v317','c0046')
    text=text.replace('7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294','9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5')
    if name.startswith('summarize'):
        text=text.replace('version=317',"candidate='c0046'")
        text=text.replace(' refs={}', ' refs={};origins={};global_root=ROOT.parents[3]')
        before="  raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw"
        after="  raw=evidence(p);n=p.relative_to(ROOT).as_posix();refs[n]=sha(raw);origins[n]=p.resolve().relative_to(global_root).as_posix();return raw"
        assert text.count(before)==1;text=text.replace(before,after)
        # Reports are shared through analysis, with canonical global-root paths.
        text=text.replace("previous=ROOT/prior['current_campaign_trace']", "previous=ROOT/'validation'/Path(prior['current_campaign_trace']).parent.name/Path(prior['current_campaign_trace']).name")
        text=text.replace('import json','import json\nfrom pathlib import Path',1)
        if name=='summarize_owned_overview':
            text=text.replace("prior['current_campaign_trace'].removeprefix('validation/')", "('natural-dungeon-combat/'+Path(prior['current_campaign_trace']).name)")
        marker=" (ROOT/'analysis/"
        assert text.count(marker)==1
        normalize=" prefix=ROOT.relative_to(global_root).as_posix()+'/'\n result['current_campaign_trace']=prefix+result['current_campaign_trace']\n result['evidence']={origins[n]:h for n,h in refs.items()}\n"
        if name=='summarize_palace_giant':normalize+=" for stage in result['stages']:stage['trace']=prefix+stage['trace']\n"
        text=text.replace(marker,normalize+marker)
    ast.parse(text)
    target=project/'tools'/f'{name}_c0046.py';assert not target.exists();target.write_text(text,encoding='utf-8')
print('Palace entry and giant scripts prepared; not executed; D9 audit required')
