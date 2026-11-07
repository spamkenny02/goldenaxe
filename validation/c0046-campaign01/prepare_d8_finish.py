"""Prepare candidate D8 thief-key route, main boss and exterior return."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
project=root/'validation/c0046-campaign01/isolated/project'
for name in ('continue_d8_finish','summarize_d8_approach','summarize_d8_campaign'):
    text=(root/'tools'/f'{name}_v0317.py').read_text().replace('v0317','c0046').replace('v317:','c0046:')
    if name.startswith('summarize'):
        text=text.replace('version=317',"candidate='c0046'")
        text=text.replace("versions/c0046-7694654e/gaw-megadrive-c0046.bin",'gaw-megadrive.bin')
        text=text.replace('7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294','9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5')
        text=text.replace("previous=prior['stages'][-1]['trace']", "previous='validation/natural-dungeon-combat/'+prior['stages'][-1]['trace'].split('/')[-1]")
        text=text.replace("previous = ROOT/prior['ready_trace']", "previous = ROOT/'validation/natural-dungeon-combat'/prior['ready_trace'].split('/')[-1]")
        text=text.replace(' refs={}',' refs={};origins={};global_root=ROOT.parents[3]')
        text=text.replace(' refs = {}',' refs = {};origins={};global_root=ROOT.parents[3]')
        if name.endswith('approach'):
            old='  raw=evidence(ROOT/name);refs[name]=sha(raw);return raw'
            new="  raw=evidence(ROOT/name);refs[name]=sha(raw);origins[name]=(ROOT/name).resolve().relative_to(global_root).as_posix();return raw"
        else:
            old='  raw = evidence(p); refs[p.relative_to(ROOT).as_posix()] = sha(raw); return raw'
            new="  raw=evidence(p);name=p.relative_to(ROOT).as_posix();refs[name]=sha(raw);origins[name]=p.resolve().relative_to(global_root).as_posix();return raw"
        assert text.count(old)==1;text=text.replace(old,new)
        suffix='approach' if name.endswith('approach') else 'campaign'
        marker=f" (ROOT/'analysis/d8_{suffix}_c0046_report.json').write_bytes"
        assert text.count(marker)==1
        normalize=" prefix=ROOT.relative_to(global_root).as_posix()+'/'\n for stage in result['stages']:stage['trace']=prefix+stage['trace']\n"
        for key in (['ready_trace','current_campaign_trace'] if suffix=='approach' else ['current_campaign_trace']):
            normalize+=f" result['{key}']=prefix+result['{key}']\n"
        normalize+=" result['evidence']={origins[name]:h for name,h in refs.items()}\n"
        text=text.replace(marker,normalize+marker)
    target=project/'tools'/f'{name}_c0046.py';assert not target.exists()
    target.write_text(text,encoding='utf-8')
print('D8 approach, thief key, main boss and return scripts prepared; not executed')
