"""Package scripts and recorded controls only; no ROM, DLL or save import."""
import argparse,hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'testkit'
p=argparse.ArgumentParser();p.add_argument('--output',default='handoff/gaw-tests-bizhawk-libretro-v321.zip');a=p.parse_args()
target=(ROOT/a.output).resolve();assert target.is_relative_to(ROOT/'handoff') and not target.exists()
files=[p for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts
       and (not p.is_relative_to(source/'logs') or p.name=='.gitkeep')]
assert all(p.suffix.lower() not in ['.sms','.bin','.dll','.state','.srm'] or
           p.relative_to(source).as_posix()=='references/sms_full_ntsc_final_ram.bin' and p.stat().st_size==8192 for p in files)
hashes={p.relative_to(source).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files:z.write(p,'gaw-test-kit/'+p.relative_to(source).as_posix())
 z.writestr('gaw-test-kit/CONTENTS_SHA256.json',json.dumps(hashes,indent=2)+'\n')
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 for name,expected in hashes.items():assert hashlib.sha256(z.read('gaw-test-kit/'+name)).hexdigest()==expected
digest=hashlib.sha256(target.read_bytes()).hexdigest();target.with_suffix('.zip.sha256').write_text(digest+'  '+target.name+'\n')
print(json.dumps(dict(archive=str(target),bytes=target.stat().st_size,sha256=digest,files=len(files),all_members_readback_sha256_verified=True)))
