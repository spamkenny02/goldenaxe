"""Run every captured status-model transition on both68000 target regions."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];work=root/'validation/v319-chip-events02'
report=json.loads((work/'report.json').read_bytes());assert report['passed']
count=report['transition_vectors'];partitions=[]
for index,start in enumerate(range(0,count,3000),1):
 name='kernel'+str(index);path=work/(name+'-report.json');size=min(3000,count-start)
 if not path.exists():subprocess.run([sys.executable,str(root/'validation/compile_v319_chip_events_68k.py'),'--start',str(start),'--count',str(size),'--kernel',name],cwd=root,check=True)
 r=json.loads(path.read_bytes());assert r['passed'] and r['start']==start and r['count']==size
 partitions.append(dict(path=path.relative_to(root).as_posix(),report=r))
assert sum(p['report']['count'] for p in partitions)==count
(work/'compiled-all-report.json').write_text(json.dumps(dict(passed=True,source_transition_vectors=count,compiled_executions=count*2,partitions=partitions),indent=2)+'\n')
print('All status-model transitions passed both68000 target regions.',flush=True)
