"""Compile every recorded calendar case exactly once, resuming done partitions."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];work=root/'validation/v319-sprite-clock03'
r=json.loads((work/'report.json').read_bytes());assert r['passed'];total=r['transition_vectors'];parts=[]
for index,start in enumerate(range(0,total,3000),1):
 count=min(3000,total-start);name='kernel'+str(index);path=work/(name+'-report.json')
 if not path.exists():subprocess.run([sys.executable,str(root/'validation/compile_v319_sprite_clock_68k.py'),'--start',str(start),'--count',str(count),'--kernel',name],cwd=root,check=True)
 part=json.loads(path.read_bytes());assert part['passed'] and part['start']==start and part['count']==count
 parts.append(dict(path=path.relative_to(root).as_posix(),report=part))
assert sum(p['report']['count'] for p in parts)==total
report=dict(passed=True,source_transition_vectors=total,compiled_executions=total*2,irq_provider_checks=sum(row['clock_irq_checks'] for p in parts for row in p['report']['results']),partitions=parts)
(work/'compiled-all-report.json').write_text(json.dumps(report,indent=2)+'\n');print('All',total,'clock vectors passed compiled NTSC/PAL.',flush=True)
