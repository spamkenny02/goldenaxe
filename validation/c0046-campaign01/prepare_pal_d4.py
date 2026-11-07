"""Prepare the PAL fourth dungeon after the actual Earth purchase."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
s=(root/'validation/pal318-d4-run01/run.py').read_text().replace('pal318','palc0046').replace('PAL V318','PAL c0046')
s=s.replace('b9e1f0a0543f191e24ffd6d2740a0d717501e0fcd986f8b8953a37a1b3c416a4','9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5')
s=s.replace('h.EVIDENCE=Path(__file__).resolve().parent',"h.EVIDENCE=h.ROOT/'validation/palc0046-d4-sources'")
s=s.replace("COMMON=['--pal','--assisted-prefix'","COMMON=['--pal','--wake-sentinels','--assisted-prefix'")
s=s.replace("'--target-room','0x10','--exit-dungeon'","'--target-room','0x10','--exit-dungeon','--defer-puzzles-rooms','0x1b0'")
marker="with streamed_replays(h,V/'palc0046-d4-cold-stream01'):"
setup="""import json,shutil
prior=json.loads((h.ROOT/'analysis/palc0046_earth_report.json').read_bytes())
assert prior['passed'] and prior['candidate']=='c0046' and prior['region']=='pal' and prior['fourth_dungeon_entered'] and prior['rom_sha256']==ROM
h.EVIDENCE.mkdir(exist_ok=False)
names=('continue_d4_palc0046.py','continue_d8_entry_v0312.py','campaign_stream_replay.py','cold_replay_stream.py','run_core.py','assisted_boss_route.py','assisted_prefix.py','natural_dungeon_combat.py','natural_earth_passage.py','natural_item_acquisition.py','close_assisted_approach.py','unassisted_fast_prediction.py','unassisted_dungeon_continuation.py','prediction_video_skip.py','natural_combat_beam.py','natural_boss_evasive_planner.py','replay_assisted_prefix.py')
index={}
for name in names:
    target=h.EVIDENCE/name;shutil.copyfile(h.ROOT/'tools'/name,target);index['tools/'+name]=sha(target.read_bytes())
(h.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\\n',encoding='utf-8')
"""
assert s.count(marker)==1;s=s.replace(marker,setup+marker)
p=project/'tools/continue_d4_palc0046.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf-8')
print('PAL D4 controller prepared, real Earth receipt required; existing1B0 puzzle deferred during exit')
