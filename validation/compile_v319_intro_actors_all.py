"""Compile every natural intro actor callback vector in bounded2MiB kernels, both target regions."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--scene',choices=['second','third'],required=True)
p.add_argument('--resume',action='store_true');a=p.parse_args()
work=root/'validation'/('v319-native-intro-poll-actors-second01' if a.scene=='second' else 'v319-native-intro-poll-actors-third03')
target=work/'compiled-all-report.json';assert not target.exists()
reports=[]
for region in ('ntsc','pal'):
 cases=json.loads((work/region/'native-cases.json').read_bytes());covered=0
 for part,start in enumerate(range(0,len(cases),500)):
  name='kernel'+str((0 if region=='ntsc' else 20)+part+1)
  report=work/('compiled-'+region+'-'+name+'-report.json')
  if not(a.resume and report.is_file()):
   subprocess.run([sys.executable,str(root/'validation/compile_v319_intro_poll_68k.py'),
    '--work',work.name,'--kernel-name',name,'--source-region',region,'--case-start',str(start),'--case-count','500'],cwd=root,check=True)
  data=json.loads(report.read_bytes())
  assert data['passed'] and data['case_start']==covered and data['actors']==a.scene
  assert data['source_vector_cases']==min(500,len(cases)-covered)
  assert data['ram_bytes']==(1184 if a.scene=='second' else 1193)
  covered+=data['source_vector_cases'];reports.append(dict(path=report.relative_to(root).as_posix(),report=data))
 assert covered==len(cases)
target.write_text(json.dumps(dict(passed=True,scene=a.scene,
 distinct_source_vectors=sum(x['report']['source_vector_cases'] for x in reports),
 compiled_executions=sum(x['report']['source_vector_cases']*len(x['report']['results']) for x in reports),
 kernels=reports,scope='All natural callback vectors, compiled68000 on both target regions. Third-scene '
 'IRQ adapter receives the actual independently captured source VDP status byte at each IRQ entry. '
 'This is a semantic input binding in the diagnostic, not production hardware scheduling.'),indent=2)+'\n')
print(a.scene,'all source vectors passed compiled68000 in both regions.',flush=True)
