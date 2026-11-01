"""Verify each controlled palace-gate displacement against the source ROM run."""
import argparse,json
from run_core import ROOT
from archive_lossless_evidence import sha


def main():
 p=argparse.ArgumentParser();p.add_argument('--trial',required=True);p.add_argument('--report',required=True);a=p.parse_args()
 report=json.loads((ROOT/f'analysis/palace_gate_{a.trial}_probe.json').read_bytes());assert report['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 checks=[]
 for complete in [False,True]:
  rows={tag:json.loads((ROOT/f'validation/palace-gate-{a.trial}-{tag}-{int(complete)}/observations.json').read_bytes()) for tag in ['sms','md']}
  for tag,r in rows.items():
   if complete:
    event=next(x['frame'] for x in r if x['seen']);opened=next(x['frame'] for x in r if x['cells']=='30' and x['room']==139)
    assert opened-event==289 and r[-1]['flags']&1
    wave=[(x['frame']-event,x['scroll']) for x in r if x['frame']>event]
    other=rows['sms'];start=next(x['frame'] for x in other if x['seen'])
    assert wave==[(x['frame']-start,x['scroll']) for x in other if x['frame']>start]
    for amplitude in range(8,-1,-1):assert any(t==1+(8-amplitude)*32 and min(v,256-v)==amplitude for t,v in wave)
    checks.append(dict(platform=tag,complete=True,event_frame=event,opened_frame=opened,delay=289,displacement_changes_exact=True,nine_amplitudes_32_frames=True))
   else:
    assert all(not x['seen'] and not x['flags'] and not x['scroll'] for x in r) and r[-1]['cells']=='35'
    checks.append(dict(platform=tag,complete=False,remained_closed=True))
 rom=(ROOT/'gaw-megadrive.bin').read_bytes();assert len(rom)==2097152 and rom==(ROOT/'gaw-title-megadrive.bin').read_bytes()
 assert sum(int.from_bytes(rom[n:n+2],'big') for n in range(512,len(rom),2))&65535==int.from_bytes(rom[398:400],'big')
 report.update(passed=True,checks=checks,scope='Controlled fixtures, not a natural campaign proof. Every displacement change and opening delay match SMS; no global audiovisual or hardware claim.',source_addresses=['6911-698A','193D','0240','0227','5E8B'],quake_effect_source_queue='DE06')
 (ROOT/a.report).write_bytes((json.dumps(report,indent=2)+'\n').encode());print('Palace gate checks passed:',a.trial)

if __name__=='__main__':main()
