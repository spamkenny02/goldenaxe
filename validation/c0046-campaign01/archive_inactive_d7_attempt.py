"""Archive inactive south01 captures, then remove verified binary duplicates."""
from pathlib import Path
import json,sys
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze
work=Path(__file__).resolve().parent
failed=work/'isolated/project/validation/natural-dungeon-combat/md-auto-c0046-d7-02-south01'
assert failed.resolve().is_relative_to((work/'isolated/project/validation').resolve())
r=json.loads((failed/'report.json').read_bytes())
assert r['failure']=='controller_stalled' and not r['deaths'] and r['last_state']['room']==0x1d6
assert all(e['type']==0x52 and not e['state'] for e in r['last_actors'])
passed=json.loads((ROOT/'analysis/d7_campaign_c0046_report.json').read_bytes())
assert passed['passed'] and passed['seventh_crystal_and_exterior_return']
paths=[Path(__file__).resolve(),ROOT/'analysis/d7_campaign_c0046_report.json']
paths.extend(p for p in failed.iterdir() if p.is_file())
freeze(ROOT,ROOT/'analysis/c0046-d7-inactive-south01',paths,dict(archive_integrity_only=True,
    rejected_attempt='south01',reason='Controller did not wake the four source52 floor ambushers',
    successful_attempt='south02',numbered_roms_preserved=True,
    scope='Only this inactive failed attempt; generated binary captures removed after complete compressed readback and hash verification. PNGs, sources and active campaign outputs retained.'),[failed],cleanup=True)
