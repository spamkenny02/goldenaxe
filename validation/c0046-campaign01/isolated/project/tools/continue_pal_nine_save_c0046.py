"""Write and reload an ordinary nine-crystal PAL save from the verified campaign."""
import json
import sys
from pathlib import Path

sys.path.insert(0,'tools')
import continue_d8_entry_palc0046 as helper
from continue_d8_entry_palc0046 import COMBAT, ROUTE, SERVICE, assert_canonical, budget, replay, run
from archive_lossless_evidence import sha
from cold_replay_stream import ReplayStream
from run_core import ROOT

work=ROOT/'validation/palc0046-pal-nine-save-sources'
helper.EVIDENCE=work
source='md-pal-palc0046-d9-exit01'
receipt=json.loads((ROOT/'analysis/palc0046_d9_report.json').read_bytes())
assert receipt['passed'] and receipt['ninth_crystal_and_exterior_return']
assert receipt['rom_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
assert Path(receipt['current_campaign_trace']).name==source
assert_canonical(COMBAT,source)

route='palc0046-nine-crystals-save-route01'
save='palc0046-nine-crystals-save01'
work.mkdir(exist_ok=False)
helper.STREAM=ReplayStream(work/'cold-stream')
try:
    run('natural_dungeon_route.py',['--pal','--prefix-combat',source,'--assisted-prefix',
        '--house-outside','0xfa','--house-target','0x6f','--trial',route,
        '--frames',budget(COMBAT,source,6000),'--axe-terrain','--required-chop',
        '0xfa:0x5d','--live-prefix-terrain','--live-room-replan'])
    replay(ROUTE,'md-pal-'+route,lambda r:r['reached_entrance'])
finally:
    helper.STREAM.close()
run('natural_save_service.py',['--prefix','md-pal-'+route,'--assisted-prefix','--trial',save])
run('validate_game_written_save.py',['--trace',SERVICE+'/md-'+save,'--trial','palc0046-nine-crystals01',
    '--release-report-name','game_written_save_pal_c0046_nine_crystals_report.json'])
print('PAL GAME-WRITTEN NINE-CRYSTAL SAVE AND CONTINUE VERIFIED',flush=True)
