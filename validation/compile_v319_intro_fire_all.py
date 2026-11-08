"""Partition all original fire callback vectors into2MiB native kernels; preserve each region's proof."""
import json
import subprocess
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
work=root/'validation/v319-native-intro-poll-fire-callback02'
target=work/'compiled-all-report.json';assert not target.exists()
reports=[]
for region in ('ntsc','pal'):
 cases=json.loads((work/region/'native-cases.json').read_bytes())
 covered=0
 for part,start in enumerate(range(0,len(cases),900)):
  name='kernel'+str((0 if region=='ntsc' else 10)+part+1)
  subprocess.run([sys.executable,str(root/'validation/compile_v319_intro_poll_68k.py'),
   '--work',work.name,'--kernel-name',name,'--source-region',region,
   '--case-start',str(start),'--case-count','900'],cwd=root,check=True)
  report=work/('compiled-'+region+'-'+name+'-report.json')
  data=json.loads(report.read_bytes());assert data['passed'] and data['case_start']==covered
  assert data['source_vector_cases']==min(900,len(cases)-covered)
  assert data['ram_bytes']==416 and data['fire']
  covered+=data['source_vector_cases'];reports.append(dict(path=report.relative_to(root).as_posix(),report=data))
 assert covered==len(cases)
result=dict(passed=True,distinct_source_vectors=sum(row['report']['source_vector_cases'] for row in reports),
 compiled_executions=sum(row['report']['source_vector_cases']*len(row['report']['results']) for row in reports),
 kernels=reports,scope='All natural source F09/F37 fire vectors compiled on68000 and run in both target '
 'regions; only bounded original source states, not synthetic input/actor callbacks or physical game publication.')
target.write_text(json.dumps(result,indent=2)+'\n')
print(result['distinct_source_vectors'],'fire callback vectors all passed on68000 in both target regions.',flush=True)
