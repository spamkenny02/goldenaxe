"""Read source drop tables to explain failed water-only funding and select coin-capable foes."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];rom=(root/'input/original.sms').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(rom)=='852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9'
e=rom[0x3226d:0x322ae];choices=rom[0x322ae:0x3234e];exceptions=dict(zip(e[1:1+e[0]],e[1+e[0]:]));rows=[]
for room in (0x19,0x1a,0x29,0x2a,0x2b):
 kinds=sorted(set(v for v in rom[0x3234e+room*8:0x3234e+room*8+8] if v>=0x20));actors=[]
 for kind in kinds:
  category=exceptions.get(kind,0);counts={}
  for roll in range(256):
   n=((roll&0xe0)>>4)|(category<<4)
   if (roll&31)<choices[n]:counts[choices[n+1]]=counts.get(choices[n+1],0)+1
  actors.append(dict(kind=kind,drop_category=category,accepted_roll_counts=counts,coin_roll_values=sum(counts.get(t,0) for t in (8,9))))
 rows.append(dict(room=room,actors=actors))
assert all(a['coin_roll_values']==0 for row in rows[:4] for a in row['actors'])
assert any(a['kind']==0x21 and a['coin_roll_values']>0 for a in rows[-1]['actors'])
r=dict(passed=True,source_sha256=sha(rom),source_drop_exceptions_offset=0x3226d,source_drop_choices_offset=0x322ae,source_room_types_offset=0x3234e,rooms=rows,scope='Exhaustive enumeration of all256 supplied random bytes against original source drop category/threshold tables. The water-only19/1A/29/2A foes cannot drop coins;21 in2B can. Counts are accepted byte values, not an empirical probability or a claim that a particular gameplay route succeeds.')
p=root/'analysis/palc0046_d9_drop_planning_report.json';p.write_text(json.dumps(r,indent=2)+'\n');print('Source drop-table planning verified; enemy21 has',next(a['coin_roll_values'] for a in rows[-1]['actors'] if a['kind']==0x21),'coin-producing byte values out of256')
