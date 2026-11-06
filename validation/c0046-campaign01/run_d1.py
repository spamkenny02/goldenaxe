"""Regenerate the first-dungeon inputs on c0046, retaining cold replay gates."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

work=Path(__file__).resolve().parent
project=work/'isolated/project'
parser=argparse.ArgumentParser();parser.add_argument('region',choices=['auto','pal'])
region=parser.parse_args().region
region_args=['--pal'] if region=='pal' else []
log=work/(region+'-commands.jsonl')
family='natural-dungeon-combat'
common=['--assisted-prefix','--max-deaths','0','--collision-aim',
        '--settle-attacks','--doorway-ranges','--ignore-inactive-actors']

def run(tool,args):
    path=project/'tools'/tool
    with log.open('a') as f:
        f.write(json.dumps(dict(tool=tool,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),arguments=args))+'\n')
    print('START',tool,*args,flush=True)
    subprocess.run([sys.executable,'-u',str(path),*args],cwd=project,check=True)

def replay(name,predicate):
    path=project/'validation'/family/name
    report=json.loads((path/'report.json').read_bytes())
    assert report['failure'] is None and not report['deaths'] and predicate(report)
    run('replay_assisted_prefix.py',['--trace',family+'/'+name])
    c=json.loads((path/'capture.json').read_bytes())
    proof=json.loads((path.with_name(path.name+f"-assisted-fixed-replay-{c['frames']}")/'replay_report.json').read_bytes())
    assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact']
    return name

current=replay('md-'+region+'-c46-d1-key01',lambda r:r['new_key_verified'])
run('assisted_boss_route.py',region_args+['--boss-room','0x175','--planner','ordinary',
    *common,'--continuation',current,'--rooms',
    '0x1e5,0x1e4,0x1d4,0x1c4,0x1b4,0x1b5,0x1a5,0x1a4,0x194,0x193,0x194,0x184,0x185',
    '--target-room','0x185','--retry-isolated-foes','--wake-sentinels',
    '--frames','26000','--trial','c46-d1-ready01'])
current=replay('md-'+region+'-c46-d1-ready01',lambda r:r['room_cleared'])
run('close_assisted_approach.py',['--trace',family+'/'+current,'--before-room','0x175',
    '--trial','c46-'+region+'-d1-release01'])
current=replay('md-auto-c46-'+region+'-d1-release01',lambda r:r['last_state']['hurt']==0)
run('unassisted_fast_prediction.py',region_args+common+['--planner','evasive','--planning-step','16',
    '--entry-boss-kind','0x68','--continuation',current,'--rooms','0x185,0x175',
    '--target-room','0x175','--collect-gem','--frames','46000','--trial','c46-d1-boss01'])
current=replay('md-'+region+'-c46-d1-boss01',lambda r:r['room_cleared'] and not r['new_assistance_writes'])
run('unassisted_dungeon_continuation.py',region_args+common+['--planner','ordinary',
    '--continuation',current,'--rooms',
    '0x175,0x185,0x184,0x194,0x1a4,0x1a5,0x1b5,0x1b4,0x1c4,0x1d4,0x1e4',
    '--target-room','0xb9','--exit-dungeon','--frames','60000','--trial','c46-d1-exit01'])
current=replay('md-'+region+'-c46-d1-exit01',lambda r:r['dungeon_exit_verified'] and not r['new_assistance_writes'])
print('C0046 FIRST CRYSTAL AND EXTERIOR VERIFIED',region,current,flush=True)
