"""Archive Bell world passage and D9 entry, optionally its first guardian."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
args=argparse.ArgumentParser();args.add_argument('--midboss',action='store_true');a=args.parse_args()
work=Path(__file__).resolve().parent;project=work/'isolated/project'
part='midboss' if a.midboss else 'entry';report=ROOT/f'analysis/d9_{part}_c0046_report.json'
r=json.loads(report.read_bytes());assert r['passed'] and r['candidate']=='c0046' and r['eight_crystals_preserved']
assert not r['full_game_validated']
if a.midboss:assert r['first_intermediate_defeated'] and not r['intermediate_assistance'] and len(r['stages'])==5
else:assert r['paid_south_return'] and r['cb_gravestone_opened_with_owned_bell'] and len(r['stages'])==1
paths={Path(__file__).resolve(),work/'prepare_d9_entry.py',report,project/f'tools/summarize_d9_{part}_c0046.py'}
for name,h in r['evidence'].items():
    p=ROOT/name;assert sha(p.read_bytes())==h;paths.add(p)
base=project/'validation/c0046-d9-sources04';snap=base/'entry-tools';index=snap/'source_index.json';paths.add(index)
for name,h in json.loads(index.read_bytes()).items():
    p=snap/name;assert sha(p.read_bytes())==h;paths.add(p)
stream=base/'cold-stream'/('completed.json' if a.midboss else 'checkpoints.json');s=json.loads(stream.read_bytes())
assert s['rom_sha256']==r['md_sha256'] and s['cold_boot_count']==1
assert len(s['checkpoints'])>=(6 if a.midboss else 1)
if a.midboss:assert s['passed'] and len(s['checkpoints'])==6
assert all(p['whole_ram_png_exact'] for p in s['checkpoints']);paths.add(stream)
freeze(ROOT,ROOT/f'analysis/c0046-d9-{part}',paths,r,[work])
print('D9 '+part+' archived; no ninth-crystal claim',flush=True)
