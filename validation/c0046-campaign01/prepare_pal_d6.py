"""Prepare PAL D6; execution requires the completed audited D5 return."""
from pathlib import Path
import ast
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
s=(root/'validation/pal318-d6-run01/run.py').read_text().replace('pal318','palc0046').replace('PAL V318','PAL c0046').replace('b9e1f0a0543f191e24ffd6d2740a0d717501e0fcd986f8b8953a37a1b3c416a4','9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5')
s=s.replace('helper.EVIDENCE=Path(__file__).resolve().parent',"helper.EVIDENCE=ROOT/'validation/palc0046-d6-sources02'")
s=s.replace("ROOT/'validation/palc0046-d5-run01/cold-stream/completed.json'","ROOT/'validation/palc0046-d5-cold-stream02/completed.json'")
s=s.replace("    prior = ROOT/", "    receipt=report(ROOT/'analysis','palc0046_d5_report.json')\n    assert receipt['passed'] and receipt['actual_fifth_crystal_and_exterior'] and receipt['rom_sha256']==ROM\n    helper.EVIDENCE.mkdir(exist_ok=False)\n    prior = ROOT/",1)
s=s.replace("'continue_d6_v0317.py'","'continue_d6_palc0046.py','close_assisted_approach.py','unassisted_stance_prediction.py','unassisted_arrival_prediction.py','unassisted_fast_prediction.py','unassisted_dungeon_continuation.py','prediction_video_skip.py','natural_combat_beam.py','natural_boss_evasive_planner.py'")
marker="    index = {'tools/'+name: sha((ROOT/'tools'/name).read_bytes()) for name in source_paths}"
setup="""    for name in source_paths:
        target=helper.EVIDENCE/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'tools'/name,target)
"""
assert marker in s;s=s.replace(marker,setup+marker)
s=s.replace("stream=ReplayStream(helper.EVIDENCE/'cold-stream')","stream=ReplayStream(ROOT/'validation/palc0046-d6-cold-stream01')")
s=s.replace("args=[*args, '--pal']","args=[*args, '--pal','--wake-sentinels']").replace("common = ['--pal','--assisted-prefix'","common = ['--pal','--wake-sentinels','--assisted-prefix'")
s=s.replace("'--target-room','0x8b','--exit-dungeon'","'--target-room','0x8b','--exit-dungeon','--defer-puzzles-rooms','0x187'")
target=project/'tools/continue_d6_palc0046.py';assert not target.exists();ast.parse(s);target.write_text(s)
print('PAL D6 prepared; requires audited D5 receipt before any emulation')
