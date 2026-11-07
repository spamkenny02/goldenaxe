"""Prepare real PAL gold gift, Earth purchase and fourth-dungeon entry."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
s=(root/'validation/pal318-earth-run01/run.py').read_text().replace('pal318','palc0046').replace('PAL V318','PAL c0046')
s=s.replace('b9e1f0a0543f191e24ffd6d2740a0d717501e0fcd986f8b8953a37a1b3c416a4','9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5')
s=s.replace('h.EVIDENCE=Path(__file__).resolve().parent',"h.EVIDENCE=h.ROOT/'validation/palc0046-earth-sources'")
marker="with streamed_replays(h,V/'palc0046-earth-cold-stream01'):"
setup="""import json,shutil
prior=json.loads((h.ROOT/'analysis/palc0046_d3_report.json').read_bytes())
assert prior['passed'] and prior['candidate']=='c0046' and prior['region']=='pal' and prior['actual_third_crystal_and_exterior'] and prior['rom_sha256']==digest
h.EVIDENCE.mkdir(exist_ok=False)
names=('continue_earth_palc0046.py','continue_d8_entry_v0312.py','campaign_stream_replay.py','cold_replay_stream.py','run_core.py','assisted_boss_route.py','assisted_prefix.py','natural_dungeon_route.py','natural_house_service.py','replay_assisted_prefix.py')
index={}
for name in names:
    target=h.EVIDENCE/name;shutil.copyfile(h.ROOT/'tools'/name,target);index['tools/'+name]=sha(target.read_bytes())
(h.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\\n',encoding='utf-8')
"""
assert s.count(marker)==1;s=s.replace(marker,setup+marker)
p=project/'tools/continue_earth_palc0046.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf-8')
print('PAL Earth controller prepared with real50-piece gift and price, after the verified third crystal')
