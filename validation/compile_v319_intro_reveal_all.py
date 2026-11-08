"""Compile every source reveal vector in bounded2MiB kernels; do not sample."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];work=root/'validation/v319-native-intro-poll-reveal05'
count=sum(len(json.loads((work/r/'native-cases.json').read_bytes())) for r in ('ntsc','pal'))
assert count==112
reports=[]
for index,start in enumerate(range(0,count,24),1):
 subprocess.run([sys.executable,str(root/'validation/compile_v319_intro_poll_68k.py'),'--work',work.name,
  '--case-start',str(start),'--case-count',str(min(24,count-start)),'--kernel-name','kernel'+str(index)],cwd=root,check=True)
 name=work/('compiled-both-kernel'+str(index)+'-report.json');r=json.loads(name.read_bytes())
 assert r['passed'] and r['case_start']==start and r['source_vector_cases']==min(24,count-start)
 reports.append(dict(path=name.relative_to(root).as_posix(),report=r))
assert sum(x['report']['source_vector_cases'] for x in reports)==count
(work/'compiled-all-report.json').write_text(json.dumps(dict(passed=True,source_entry_vectors=count,
 compiled_executions=count*2,partitions=reports,scope='Every source reveal vector on each target region, all OUT events compared.'),indent=2)+'\n')
print('All112 source reveal vectors passed on both68000 target regions.',flush=True)
