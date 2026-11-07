"""Prepare the sixth-dungeon controller and expose its actual native sources."""
from pathlib import Path
import hashlib,json,os

root=Path(__file__).resolve().parents[2]
project=root/'validation/c0046-campaign01/isolated/project'
actual=root/'validation/v318-hero-three-plane02/src'
base=root/'megadrive/src'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a={p.name:sha(p) for p in actual.iterdir() if p.is_file()}
b={p.name:sha(p) for p in base.iterdir() if p.is_file()}
assert a.keys()==b.keys() and [n for n in a if a[n]!=b[n]]==['main.c']
dest=project/'megadrive/src';assert not dest.exists()
dest.mkdir()
for p in actual.iterdir():
    assert p.is_file()
    os.link(p,dest/p.name)
assert {p.name:sha(p) for p in dest.iterdir()}==a
(project.parents[1]/'native_sources_setup.json').write_text(json.dumps(dict(
    actual_source=actual.relative_to(root).as_posix(),sources=a,hard_links_read_only=True,
    warning='Do not edit these source links; they expose the already built c0046 source tree for read-only campaign provenance.'),indent=2)+'\n')
name='continue_d6'
text=(root/'tools'/f'{name}_v0317.py').read_text().replace('v0317','c0046').replace('V317','C0046')
path=project/'tools'/f'{name}_c0046.py';assert not path.exists()
path.write_text(text,encoding='utf-8')
print('D6 controller prepared; actual candidate sources linked read-only; not executed')
