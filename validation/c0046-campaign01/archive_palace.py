"""Freeze actual candidate palace milestones after their strict audits pass."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from archive_lossless_evidence import freeze,sha
root=Path(__file__).resolve().parents[2];work=Path(__file__).resolve().parent
project=work/'isolated/project'
a=argparse.ArgumentParser();a.add_argument('part',choices=['entry','giant','inner','guardian','final']);args=a.parse_args();part=args.part
rpath=root/f'analysis/cold_palace_{part}_c0046_report.json';r=json.loads(rpath.read_bytes())
assert r['passed'] and r['candidate']=='c0046' and not r['primary_state_imports'] and not r['full_game_validated']
assert r['md_sha256']==sha((project/'gaw-megadrive.bin').read_bytes())
key={'entry':'cold_palace_entered','giant':'cold_palace_giant_defeated','inner':'cold_palace_inner_mechanisms_verified','guardian':'actual_golden_axe_acquired','final':'ending_complete'}[part]
assert r[key]
paths={Path(__file__).resolve(),work/'prepare_palace_entry.py',work/'prepare_palace_final.py',rpath,project/f'tools/summarize_palace_{part}_c0046.py'}
reports=[r]
if part=='entry':
    op=root/'analysis/owned_overview_c0046_report.json';o=json.loads(op.read_bytes())
    assert o['passed'] and o['candidate']=='c0046' and o['natural_owned_overview_verified'];paths.add(op);reports.append(o)
for receipt in reports:
    assert receipt['md_sha256']==r['md_sha256']
    for name,h in receipt['evidence'].items():
        p=root/name;assert sha(p.read_bytes())==h;paths.add(p)
base=project/'validation/c0046-palace-sources'
streams={'entry':(project/'validation/c0046-after-d9-sources/palace-cold-stream',2),
         'giant':(base/'giant-cold-stream02',4),'inner':(base/'inner-cold-stream02',5),
         'guardian':(base/'guardian-cold-stream',6),'final':(base/'final-cold-stream',11)}
stream,count=streams[part];p=stream/'completed.json';s=json.loads(p.read_bytes())
assert s['passed'] and s['rom_sha256']==r['md_sha256'] and s['cold_boot_count']==1 and len(s['checkpoints'])==count
assert all(c['whole_ram_png_exact'] for c in s['checkpoints']);paths.add(p)
for receipt in reports:
    assert any(Path(c['trace']).name==Path(receipt['current_campaign_trace']).name and c['frames']==receipt['campaign_frames'] for c in s['checkpoints'])
if part=='final':assert r['campaign_from_new_game_completed'] and not r['final_boss_assistance'] and r['credits_finished_frame']>r['credits_started_frame']
freeze(root,root/f'analysis/c0046-palace-{part}',paths,r,[work])
print('Actual palace milestone archived:',part,flush=True)
