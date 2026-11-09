"""Restore a compacted local validation input on demand (Python3.14+)."""
import argparse,hashlib,json,os,subprocess,tempfile,zipfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parent.resolve();CACHE=ROOT/'analysis/local-validation-cache'
p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--path',help='Exact repository-relative path,or outputs-relative gaw-md... path');g.add_argument('--prefix',help='Restore all inputs below a directory');options=p.parse_args()
wanted=(options.path or options.prefix).replace('\\','/').rstrip('/')
if not wanted.startswith(('gaw-md/','gaw-md-upward-ntsc01/')):wanted='gaw-md/'+wanted
assert '..' not in Path(wanted).parts and not Path(wanted).is_absolute()
catalog=json.loads((CACHE/'catalog.json').read_bytes()) if (CACHE/'catalog.json').exists() else {'packs':[]};restored=existing=discarded=0;found=False
for part in catalog['packs']:
 index=CACHE/part['index'];assert hashlib.sha256(index.read_bytes()).hexdigest()==part['index_sha256']
 with index.open(encoding='utf-8') as rows:
  for line in rows:
   row=json.loads(line);name=row['path']
   if name!=wanted and not (options.prefix and name.startswith(wanted+'/')):continue
   found=True
   if row['kind']=='regenerable':discarded+=1;continue
   target=(BASE/name).resolve();assert target.is_relative_to(BASE)
   if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()==row['sha256'],'Refusing to overwrite a changed file: '+str(target)
    existing+=1;continue
   target.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix='.restore-',dir=target.parent);temporary=Path(tmp);sha=hashlib.sha256();size=0;process=None;archive=None
   try:
    if row['kind']=='git':
     process=subprocess.Popen(['git','cat-file','blob',row['blob']],cwd=ROOT,stdout=subprocess.PIPE);source=process.stdout
    else:archive=zipfile.ZipFile(CACHE/row['pack']);source=archive.open(row['member'])
    with os.fdopen(fd,'wb') as out,source:
     while data:=source.read(1024*1024):out.write(data);sha.update(data);size+=len(data)
    if process:assert process.wait()==0
    assert sha.hexdigest()==row['sha256'] and size==row['bytes'],'Restored content hash mismatch'
    os.replace(temporary,target);os.utime(target,ns=(row['mtime_ns'],row['mtime_ns']));restored+=1
   finally:
    if archive:archive.close()
    if temporary.exists():temporary.unlink()
if not found and options.path and wanted.startswith('gaw-md/'):
 relative=wanted[len('gaw-md/'):]
 entry=subprocess.check_output(['git','ls-files','--stage','--',relative],cwd=ROOT).decode().strip()
 if entry:
  oid=entry.split()[1];data=subprocess.check_output(['git','cat-file','blob',oid],cwd=ROOT)
  assert hashlib.sha1(('blob '+str(len(data))+'\0').encode()+data).hexdigest()==oid
  target=(BASE/wanted).resolve();assert target.is_relative_to(BASE)
  if target.exists():assert target.read_bytes()==data;existing+=1
  else:
   target.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix='.restore-',dir=target.parent)
   with os.fdopen(fd,'wb') as out:out.write(data)
   os.replace(tmp,target);restored+=1
  found=True
assert found,'No compacted or Git-tracked input matches this path'
print(json.dumps(dict(restored=restored,already_present=existing,regenerable_outputs_not_restored=discarded)))
