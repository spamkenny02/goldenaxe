"""Compile all source intro skip vectors, preserving completed partitions."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];work=root/'validation/v319-native-intro-poll-skip03'
count=sum(len(json.loads((work/r/'native-cases.json').read_bytes())) for r in ('ntsc','pal'))
assert count==88
reports=[]
for index,start in enumerate(range(0,count,4),1):
 name=work/('compiled-both-kernel'+str(index)+'-report.json')
 if not name.exists():
  subprocess.run([sys.executable,str(root/'validation/compile_v319_intro_poll_68k.py'),'--work',work.name,
   '--case-start',str(start),'--case-count',str(min(4,count-start)),'--kernel-name','kernel'+str(index)],cwd=root,check=True)
 r=json.loads(name.read_bytes())
 assert r['passed'] and r['sequence'] and r['ram_bytes']==1321 and r['case_start']==start and r['source_vector_cases']==min(4,count-start)
 assert all(row['intro_poll_errors']==0 for row in r['results'])
 reports.append(dict(path=name.relative_to(root).as_posix(),report=r))
assert sum(x['report']['source_vector_cases'] for x in reports)==count
(work/'compiled-all-report.json').write_text(json.dumps(dict(passed=True,source_entry_vectors=count,
 compiled_executions=count*2,partitions=reports,scope='All deduplicated original E79 entries, normal controller skips and full prefixes, both target regions.'),indent=2)+'\n')
print('All88 source intro skip vectors passed both68000 target regions.',flush=True)
