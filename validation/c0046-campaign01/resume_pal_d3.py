"""Recover the PAL D3 controller after its Python scope error, retaining three cold proofs."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
s=(project/'tools/continue_d3_palc0046.py').read_text()
s=s.replace("h.EVIDENCE=h.ROOT/'validation/palc0046-d3-sources'", "h.EVIDENCE=h.ROOT/'validation/palc0046-d3-resumed-sources01'")
start=s.index('def campaign():');stop=s.index("    combat('rope01'",start)
s=s[:start]+"def campaign():\n    global current\n    current='md-pal-palc0046-d3-entry01'\n    h.assert_canonical(h.ROUTE,current)\n"+s[stop:]
s=s.replace("names=('continue_d3_palc0046.py'", "names=('continue_d3_palc0046_resume01.py','continue_d3_palc0046.py'")
s=s.replace("h.ROOT/'validation/palc0046-d3-cold-stream'", "h.ROOT/'validation/palc0046-d3-cold-stream02'")
needle='    h.EVIDENCE.mkdir(exist_ok=False)'
s=s.replace(needle,"""    old=json.loads((h.ROOT/'validation/palc0046-d3-cold-stream/completed.json').read_bytes())
    assert old['passed'] and old['rom_sha256']==ROM and old['cold_boot_count']==1 and len(old['checkpoints'])==3
    assert all(c['whole_ram_png_exact'] for c in old['checkpoints']) and old['checkpoints'][-1]['trace']=='natural-dungeon-route/md-pal-palc0046-d3-entry01'
"""+needle)
p=project/'tools/continue_d3_palc0046_resume01.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf-8')
print('PAL D3 recovery prepared, prior three independent cold proofs required; old controller retained')
