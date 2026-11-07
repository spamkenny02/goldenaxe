"""Recover verified PAL D5 warp endpoint after a controller-only return-portal detour."""
import ast,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
old=project/'validation/palc0046-d5-cold-stream01/completed.json';r=json.loads(old.read_bytes())
assert r['passed'] and len(r['checkpoints'])==12 and r['checkpoints'][-1]['trace']=='natural-dungeon-combat/md-pal-palc0046-d5-warp01'
failed=project/'validation/natural-dungeon-combat/md-pal-palc0046-d5-contact01/report.json';f=json.loads(failed.read_bytes())
assert f['failure']=='frame_limit' and not f['contact_route_passed'] and f['contact_opened'] and f['last_state']['room']==0x153 and not f['contact_state_writes']
s=(project/'tools/continue_d5_palc0046.py').read_text().replace('palc0046-d5-sources','palc0046-d5-resumed-sources01').replace('palc0046-d5-cold-stream01','palc0046-d5-cold-stream02').replace('continue_d5_palc0046.py','continue_d5_palc0046_resume01.py')
s=s.replace("current='md-pal-palc0046-d5-entry01';family=ROUTE", "current='md-pal-palc0046-d5-warp01';family=COMBAT")
a=s.index("        step('key01'");b=s.index("        step('contact01'",a);s=s[:a]+s[b:]
s=s.replace("step('contact01'", "step('contact02'").replace("['--contact-room','0x162','--contact-destination','0x172','--mechanism-during-combat']", "['--contact-room','0x162','--contact-destination','0x172','--mechanism-during-combat','--avoid-portal-rooms','0x162']")
p=project/'tools/continue_d5_palc0046_resume01.py';assert not p.exists();ast.parse(s);p.write_text(s)
print('D5 resume prepared from verified warp; return portal avoided by ordinary walking; old failed trial preserved')
