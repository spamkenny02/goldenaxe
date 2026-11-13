"""Visit the two paid-healer prices and a passage with actual insufficient money."""
import argparse,json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);a=p.parse_args();output=ROOT/'analysis/md_poor_services_campaign.json';old=json.loads(output.read_bytes()) if output.exists() else {};done=old.get('completed_visits',[])
 c=Campaign(old.get('last_verified_prefix','natural-service-route/md-annex-minigame-5c-poor-visit01'),a.rom,'annex-poor-services');verified=c.trace
 def save():output.write_bytes((json.dumps(dict(status='played_replayed_filmed',completed_visits=done,last_verified_prefix=verified,all_three_poor_service_cases_complete=len(done)==3),indent=2)+'\n').encode())
 try:
  c.verify(lambda r:r['passed']);assert c.sms_view()[0xdd]<10
  for key,outside,kind in [('inn20-poor',0x55,'inn'),('inn40-poor',0x2e,'inn'),('passage-poor',0x6d,'passage')]:
   if any(v['key']==key for v in done):continue
   doors=json.loads((ROOT/'analysis/doors_reference.json').read_bytes())['direct_unconditional_doors'];houses=(0x9f,) if kind=='passage' else tuple(n[0] for n in json.loads((ROOT/'analysis/healer_assets.json').read_bytes())['nodes']);house=next(d['target'] for d in doors if d['room']==outside and d['target'] in houses)
   n=enter(c,outside,house,key);first=c.cap()['frames']+1;ref=json.loads((ROOT/f'analysis/sms_service_alternative_{key}.json').read_bytes())['trace']
   c.service(f'{key}-visit{n:02d}','md_service_alternatives',['--kind',kind,'--variant','poor','--sms-reference',ref]);name=f'md-{c.label}-{key}-visit{n:02d}';film(c,name,first);verified=c.trace;done.append(dict(key=key,trace=c.trace,sms_reference=ref,video_report=f'videos/md-annexes-2026-11-12/{name}/report.json'));save()
 finally:c.close()

if __name__=='__main__':main()
