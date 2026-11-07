from pathlib import Path
import ast
root=Path(__file__).resolve().parents[2]
p=root/'validation/c0046-campaign01'
s=(root/'validation/pal318-d5-run01/run.py').read_text().replace('pal318','palc0046').replace('PAL V318','PAL c0046').replace('b9e1f0a0543f191e24ffd6d2740a0d717501e0fcd986f8b8953a37a1b3c416a4','9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5')
s=s.replace('helper.EVIDENCE=Path(__file__).resolve().parent',"helper.EVIDENCE=ROOT/'validation/palc0046-d5-sources'").replace("COMMON=['--pal','--assisted-prefix'","COMMON=['--pal','--wake-sentinels','--assisted-prefix'")
s=s.replace("stream=ReplayStream(helper.EVIDENCE/'cold-stream')","stream=ReplayStream(ROOT/'validation/palc0046-d5-cold-stream01')")
setup="""    import json,shutil
    receipt=report(ROOT/'analysis','palc0046_fire_sword_report.json')
    assert receipt['passed'] and receipt['fifth_dungeon_entered'] and receipt['rom_sha256']==ROM
    helper.EVIDENCE.mkdir(exist_ok=False)
    names=('continue_d5_palc0046.py','run_core.py','continue_d8_entry_v0312.py','cold_replay_stream.py','assisted_boss_route.py','assisted_prefix.py','natural_dungeon_combat.py','natural_earth_passage.py','natural_item_acquisition.py','natural_house_service.py','natural_merchant_purchase.py','close_assisted_approach.py','unassisted_satellite_arrival.py','unassisted_fast_prediction.py','unassisted_dungeon_continuation.py','prediction_video_skip.py','natural_combat_beam.py','natural_boss_evasive_planner.py','replay_assisted_prefix.py')
    index={}
    for name in names:
        target=helper.EVIDENCE/name;shutil.copyfile(ROOT/'tools'/name,target);index['tools/'+name]=sha(target.read_bytes())
    (helper.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\\n')
"""
s=s.replace("    current='md-pal-palc0046-d5-entry01'",setup+"    current='md-pal-palc0046-d5-entry01'")
# Preserve the initial frozen controller; fresh controllers avoid162's return portal.
s=s.replace("['--contact-room','0x162','--contact-destination','0x172','--mechanism-during-combat']", "['--contact-room','0x162','--contact-destination','0x172','--mechanism-during-combat','--avoid-portal-rooms','0x162']")
target=p/'isolated/project/tools/continue_d5_palc0046.py';assert not target.exists();ast.parse(s);target.write_text(s)
print('PAL D5 controller prepared')
