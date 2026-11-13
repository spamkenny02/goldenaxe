"""Record genuine native minigame branches from independent real prefixes."""
import argparse,json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film,fund_wallet,refill_magic

def main():
 p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--rom',required=True);p.add_argument('--outside',type=lambda x:int(x,0),required=True);p.add_argument('--variant',choices=['play','refuse','poor'],default='play');p.add_argument('--rounds',type=int,default=2);p.add_argument('--minimum-funds',type=int,default=110);p.add_argument('--attach-stream');p.add_argument('--worker-pid',type=int);a=p.parse_args();assert bool(a.attach_stream)==bool(a.worker_pid)
 label=f'annex-minigame-{a.outside:02x}-{a.variant}';report=ROOT/f'analysis/md_minigame_{a.outside:02x}_{a.variant}_campaign.json'
 if report.exists() and json.loads(report.read_bytes()).get('passed'):return
 c=Campaign(a.prefix,a.rom,label,attach=(a.attach_stream,a.worker_pid) if a.attach_stream else None)
 try:
  c.verify(lambda r:r.get('passed',r.get('reached_entrance',False)))
  if c.family=='natural-dungeon-route':
   route=json.loads((ROOT/'validation'/c.trace/'route_report.json').read_bytes())
   assert route['house_target']==0x3f
   outside=route['house_outside'];gain=next(g for town,g in json.loads((ROOT/'analysis/house_gold_reference.json').read_bytes())['records'] if town==outside);assert 0<gain<128
   first=c.cap()['frames']+1;tag=f'fund-wallet-{outside:02x}-gift01';c.service(tag,'natural_house_service',['--outside',hex(outside),'--kind','gold','--gold-gain',str(gain)]);film(c,f'md-{label}-{tag}',first)
  if a.variant=='play':fund_wallet(c,a.minimum_funds)
  if c.sms_view()[0xdb]<8:refill_magic(c)
  n=enter(c,a.outside,0x5f,'host');first=c.cap()['frames']+1
  ref=f'natural-service-route/sms-npc-minigame-{a.outside:02x}-{a.variant}-visit01'
  c.service(f'visit{n:02d}','md_minigame_service',['--outside',hex(a.outside),'--variant',a.variant,'--rounds',str(a.rounds),'--sms-reference',ref])
  name=f'md-{label}-visit{n:02d}';film(c,name,first)
  result=dict(passed=True,initial_prefix=a.prefix,last_verified_prefix=c.trace,outside=a.outside,variant=a.variant,rounds=a.rounds,video_report=f'videos/md-annexes-2026-11-12/{name}/report.json',separate_actual_branch=True,all_rng_outcomes_covered=False)
  report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
 finally:c.close()

if __name__=='__main__':main()
