"""Keep only the latest numbered ROM locally;old bytes remain tracked in Git."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];VERSIONS=(ROOT/'versions').resolve()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');args=p.parse_args()
entries=json.loads((VERSIONS/'index.json').read_bytes());latest=max(e['version'] for e in entries);rows=[]
for entry in entries:
 if entry['version']==latest:continue
 target=(VERSIONS/entry['rom']).resolve();assert target.is_relative_to(VERSIONS)
 if not target.exists():continue
 raw=target.read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256'],'Refusing to remove a changed historical ROM'
 rel=target.relative_to(ROOT).as_posix();tracked=subprocess.check_output(['git','ls-files','--stage','--',rel],cwd=ROOT).decode().strip()
 if not tracked:continue
 oid=tracked.split()[1];saved=subprocess.check_output(['git','cat-file','blob',oid],cwd=ROOT);assert saved==raw,'Historical ROM must be safely stored in Git'
 rows.append((target,rel,len(raw)))
if args.apply and rows:
 subprocess.run(['git','update-index','--skip-worktree','-z','--stdin'],cwd=ROOT,input=b'\0'.join(rel.encode() for _,rel,_ in rows)+b'\0',check=True)
 for target,rel,size in rows:target.unlink()
print(json.dumps(dict(applied=args.apply,latest=latest,files=len(rows),bytes=sum(size for _,_,size in rows),history_kept_in_git=True)))
