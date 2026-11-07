"""Archive actual D9 Balloon and ninth-crystal checkpoints separately."""
import argparse,gzip,json,sys
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
out=ROOT/f'analysis/c0046-d9-{part}'
if out.exists():
    # Keep an early milestone immutable when the shared reader later advances.
    m=json.loads((out/'manifest.json').read_bytes())
    assert all(m[k]==v for k,v in r.items())
    archived={}
    for name,h in m['files'].items():
        raw=(out/name).read_bytes();assert sha(raw)==h;archived[name]=raw
    for name,item in m['compressed'].items():
        stored=(out/item['stored']).resolve();assert stored.is_relative_to(out.resolve())
        encoded=stored.read_bytes();assert sha(encoded)==item['stored_sha256']
        raw=gzip.decompress(encoded);assert len(raw)==item['raw_bytes'] and sha(raw)==item['raw_sha256'];archived[name]=raw
    assert set(archived)=={p.resolve().relative_to(ROOT).as_posix() for p in paths}
    for name,raw in archived.items():
        if name==stream.relative_to(ROOT).as_posix():
            old=json.loads(raw);assert old['rom_sha256']==s['rom_sha256'] and old['cold_boot_count']==s['cold_boot_count']
            assert old['checkpoints']==s['checkpoints'][:len(old['checkpoints'])]
        else:assert (ROOT/name).read_bytes()==raw
    print('D9 '+part+' existing immutable archive fully verified',flush=True)
else:freeze(ROOT,out,paths,r,[work])
print('D9 '+part+' archived',flush=True)
