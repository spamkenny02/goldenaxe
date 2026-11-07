"""Keep the D6 checks, adapting candidate identity and isolated-root provenance."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
project=root/'validation/c0046-campaign01/isolated/project'
text=(root/'tools/summarize_d6_progress_v0317.py').read_text()
text=text.replace('v0317','c0046').replace('version=317',"candidate='c0046'").replace('v317 D6','c0046 D6')
text=text.replace('    refs = {}','    refs = {}; origins = {}; global_root=ROOT.parents[3]')
before="        raw = evidence(ROOT / name)\n        refs[name] = sha(raw)\n        return raw"
after="        path=ROOT/name\n        if not path.exists():path=global_root/name\n        raw=evidence(path)\n        refs[name]=sha(raw); origins[name]=path.resolve().relative_to(global_root).as_posix()\n        return raw"
assert text.count(before)==1
text=text.replace(before,after)
text=text.replace("    previous_root = prior['stages'][-1]['trace']", "    previous_root = 'validation/natural-dungeon-combat/'+prior['stages'][-1]['trace'].split('/')[-1]")
marker="    (ROOT / 'analysis/d6_progress_c0046_report.json').write_bytes"
assert text.count(marker)==1
normalize="""    prefix=ROOT.relative_to(global_root).as_posix()+'/'
    for key in ('stages','earth_casts','ordinary_route_adaptations'):
        for row in result[key]:row['trace']=prefix+row['trace']
    result['acquired_key_stages']=[prefix+name for name in result['acquired_key_stages']]
    result['ready_trace']=prefix+result['ready_trace']
    result['evidence']={origins[name]:h for name,h in refs.items()}
"""
text=text.replace(marker,normalize+marker)
target=project/'tools/summarize_d6_progress_c0046.py';assert not target.exists()
target.write_text(text,encoding='utf-8')
print('D6 progress audit prepared; seventeen-stage checks retained; not executed')
