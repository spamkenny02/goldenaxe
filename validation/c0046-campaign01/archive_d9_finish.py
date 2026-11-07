"""Archive actual D9 Balloon and ninth-crystal checkpoints separately."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
p=argparse.ArgumentParser();p.add_argument('--balloon-only',action='store_true');args=p.parse_args()
work=Path(__file__).resolve().parent;project=work/'isolated/project'
part='balloon' if args.balloon_only else 'campaign'
report=ROOT/f'analysis/d9_{part}_c0046_report.json';r=json.loads(report.read_bytes())
assert r['passed'] and r['candidate']=='c0046' and not r['full_game_validated']
if args.balloon_only:assert r['balloon_acquired'] and r['optional_giant_defeated'] and len(r['stages'])==8
else:assert r['ninth_crystal_and_exterior_return'] and len(r['stages'])==4
paths={Path(__file__).resolve(),work/'prepare_d9_finish.py',report,project/f'tools/summarize_d9_{part}_c0046.py'}
for name,h in r['evidence'].items():
    p=ROOT/name;assert sha(p.read_bytes())==h;paths.add(p)
base=project/'validation/c0046-d9-sources04';snap=base/'finish-tools';index=snap/'source_index.json';paths.add(index)
for name,h in json.loads(index.read_bytes()).items():
    p=snap/Path(name).name;assert sha(p.read_bytes())==h;paths.add(p)
stream=base/'finish-cold-stream'/('checkpoints.json' if args.balloon_only else 'completed.json');s=json.loads(stream.read_bytes())
assert s['rom_sha256']==r['md_sha256'] and s['cold_boot_count']==1
if args.balloon_only:assert len(s['checkpoints'])>=8
else:assert s['passed'] and len(s['checkpoints'])==12
assert all(p['whole_ram_png_exact'] for p in s['checkpoints']);paths.add(stream)
freeze(ROOT,ROOT/f'analysis/c0046-d9-{part}',paths,r,[work])
print('D9 '+part+' archived',flush=True)
