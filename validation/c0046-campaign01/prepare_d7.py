"""Adapt D7 ordinary funding to the candidate's actual 38-coin D6 return."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
project=root/'validation/c0046-campaign01/isolated/project'
text=(root/'tools/continue_d7_funded_v0317.py').read_text().replace('v0317','c0046')
before="prefix = prior['stages'][-1]['trace'].removeprefix('validation/')"
assert text.count(before)==1
text=text.replace(before,"prefix = 'natural-dungeon-combat/'+prior['stages'][-1]['trace'].split('/')[-1]")
before="    endpoint = end['trace'] + f'/ram_{end[\"frames\"]:05d}.bin'"
after="    endpoint_key = end['trace'] + f'/ram_{end[\"frames\"]:05d}.bin'\n    endpoint = 'validation/natural-dungeon-combat/'+prefix+f'/ram_{end[\"frames\"]:05d}.bin'"
assert text.count(before)==1
text=text.replace(before,after).replace("prior['evidence'][endpoint]","prior['evidence'][endpoint_key]")
# B5 gives10 and A5 charges40; the original50 floor excluded valid30..49 balances.
assert text.count("assert 50<=end['gold']<60")==1
text=text.replace("assert 50<=end['gold']<60","assert 30<=end['gold']<60")
target=project/'tools/continue_d7_funded_c0046.py';assert not target.exists()
target.write_text(text,encoding='utf-8')

text=(root/'tools/summarize_d7_prep_v0317.py').read_text().replace('v0317','c0046').replace('version=317',"candidate='c0046'").replace('v317 D7','c0046 D7')
text=text.replace('    refs = {}','    refs = {}; origins={}; global_root=ROOT.parents[3]')
before="        raw = evidence(ROOT/path)\n        refs[path] = sha(raw)\n        return raw"
after="        raw=evidence(ROOT/path)\n        refs[path]=sha(raw); origins[path]=(ROOT/path).resolve().relative_to(global_root).as_posix()\n        return raw"
assert text.count(before)==1
text=text.replace(before,after)
text=text.replace("    previous = prior['stages'][-1]['trace']", "    previous = 'validation/natural-dungeon-combat/'+prior['stages'][-1]['trace'].split('/')[-1]")
before="        expected[2:2]=[('natural-dungeon-route/md-c0046-d7-02-healer-route','route',None),('natural-service-route/md-c0046-d7-02-heal','heal',None)]"
after="        at=next(i for i,row in enumerate(expected) if row[1]=='entry')\n"+before.replace('expected[2:2]','expected[at:at]')
assert text.count(before)==1
text=text.replace(before,after).replace('len(points) in (7,9)','len(points) in (7,9,11)')
text=text.replace('    key_price=None','    key_price=None;key_shop=None')
before="            assert r['unit_price']==key_price and r['first_state']['gold']-r['last_state']['gold']==key_price"
assert text.count(before)==1
text=text.replace(before,before+"\n            key_shop=r['outside']")
text=text.replace('keys_bought=1,key_price=key_price','keys_bought=1,key_price=key_price,key_shop_outside=key_shop')
text=text.replace('The selected route uses the real B5 gift and open94 shop. No A5 shop entry or historical failed controller trial is claimed by this current recording.',
    'The B5 gift is used when needed. The shop and its source-derived key price are recorded; no currency, item or health fixture is used.')
marker="    (ROOT/'analysis/d7_prep_c0046_report.json').write_text"
assert text.count(marker)==1
text=text.replace(marker,"    prefix=ROOT.relative_to(global_root).as_posix()+'/'\n    for stage in result['stages']:stage['trace']=prefix+stage['trace']\n    result['evidence']={origins[name]:h for name,h in refs.items()}\n"+marker)
target=project/'tools/summarize_d7_prep_c0046.py';assert not target.exists()
target.write_text(text,encoding='utf-8')
print('D7 funding controller and audit prepared; real B5 gift and source-priced shop')
