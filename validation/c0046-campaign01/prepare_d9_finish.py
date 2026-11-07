"""Prepare the candidate D9 giant, real Balloon, main boss and return."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
project=root/'validation/c0046-campaign01/isolated/project'
for name in ('continue_d9_finish','summarize_d9_balloon','summarize_d9_campaign'):
    text=(root/'tools'/f'{name}_v0317.py').read_text().replace('v0317','c0046').replace('v317:','c0046:')
    text=text.replace('c0046-d9-sources03','c0046-d9-sources04')
    if name.startswith('summarize'):
        text=text.replace('version=317',"candidate='c0046'")
        text=text.replace('7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294','9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5')
        text=text.replace("previous=ROOT/prior['current_campaign_trace']", "previous=ROOT/'validation/natural-dungeon-combat'/prior['current_campaign_trace'].split('/')[-1]")
        text=text.replace("previous = ROOT/prior['current_campaign_trace']", "previous = ROOT/'validation/natural-dungeon-combat'/prior['current_campaign_trace'].split('/')[-1]")
        text=text.replace(' refs={}',' refs={};origins={};global_root=ROOT.parents[3]')
        text=text.replace(' refs = {}',' refs = {};origins={};global_root=ROOT.parents[3]')
        if name.endswith('balloon'):
            before='  raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw'
            after="  raw=evidence(p);n=p.relative_to(ROOT).as_posix();refs[n]=sha(raw);origins[n]=p.resolve().relative_to(global_root).as_posix();return raw"
            part='balloon'
        else:
            before='  raw = evidence(p); refs[p.relative_to(ROOT).as_posix()] = sha(raw); return raw'
            after="  raw=evidence(p);n=p.relative_to(ROOT).as_posix();refs[n]=sha(raw);origins[n]=p.resolve().relative_to(global_root).as_posix();return raw"
            part='campaign'
        assert text.count(before)==1;text=text.replace(before,after)
        marker=f" (ROOT/'analysis/d9_{part}_c0046_report.json').write_bytes"
        assert text.count(marker)==1
        normalize=" prefix=ROOT.relative_to(global_root).as_posix()+'/'\n for stage in result['stages']:stage['trace']=prefix+stage['trace']\n"
        if part=='balloon':normalize+=" result['current_campaign_trace']=prefix+result['current_campaign_trace']\n"
        normalize+=" result['evidence']={origins[n]:h for n,h in refs.items()}\n"
        text=text.replace(marker,normalize+marker)
    target=project/'tools'/f'{name}_c0046.py';assert not target.exists();target.write_text(text)
print('D9 second guardian, Balloon and ninth-crystal continuation prepared; not executed')
