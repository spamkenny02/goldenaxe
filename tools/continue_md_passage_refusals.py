"""Cover all six passage refusals and real paid returns, with earned money."""
import argparse,json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film,fund_wallet,entry_options
from continue_sms_plain_house_census import census_world

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);a=p.parse_args();output=ROOT/'analysis/md_passage_refusals_campaign.json';old=json.loads(output.read_bytes()) if output.exists() else {};done=old.get('completed_visits',[])
 c=Campaign(old.get('last_verified_prefix','natural-service-route/md-annex-minigame-5c-play-fund-wallet-54-gift01'),a.rom,'annex-passage-refusals');verified=c.trace
 def save():output.write_bytes((json.dumps(dict(status='played_replayed_filmed',completed_visits=done,last_verified_prefix=verified,all_six_refusals_complete=len(done)==6),indent=2)+'\n').encode())
 try:
  c.verify(lambda r:r['passed'])
  while len(done)<6:
   raw=c.sms_view();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311]);choices=[]
   for outside in json.loads((ROOT/'analysis/paid_passage_reference.json').read_bytes())['towns']:
    if any(v['outside']==outside for v in done):continue
    for d in range(4):
     world=census_world(raw,outside,0x9f,d)
     if not entry_options(raw,outside,0x9f,d,world):continue
     path,_=world.route(start)
     if path is not None:choices.append((len(path),outside));break
   assert choices,'No remaining actual passage approach';_,outside=min(choices);fund_wallet(c,20);n=enter(c,outside,0x9f,f'{outside:02x}',bell_room=0x96 if outside==0x96 else None);first=c.cap()['frames']+1
   ref=json.loads((ROOT/f'analysis/sms_service_alternative_passage-refuse-{outside:02x}.json').read_bytes())['trace']
   c.service(f'{outside:02x}-decline-pay-v3-{n:02d}','md_passage_decline_then_pay',['--outside',hex(outside),'--sms-reference',ref]);name=f'md-{c.label}-{outside:02x}-decline-pay-v3-{n:02d}';film(c,name,first);verified=c.trace;done.append(dict(outside=outside,trace=c.trace,sms_reference=ref,video_report=f'videos/md-annexes-2026-11-12/{name}/report.json'));save()
 finally:c.close()

if __name__=='__main__':main()
