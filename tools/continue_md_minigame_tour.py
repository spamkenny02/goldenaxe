"""Play all remaining real MD gambling hosts in one extendable branch."""
import argparse,json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film,fund_wallet,refill_magic

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);a=p.parse_args();output=ROOT/'analysis/md_minigame_hosts_campaign.json';old=json.loads(output.read_bytes()) if output.exists() else {};done=old.get('completed_visits',[])
 if not done:
  initial=json.loads((ROOT/'analysis/md_minigame_5c_play_campaign.json').read_bytes());assert initial['passed'];done=[initial]
 c=Campaign(old.get('last_verified_prefix',done[-1]['last_verified_prefix']),a.rom,'annex-minigame-hosts');verified=c.trace
 def save():output.write_bytes((json.dumps(dict(status='played_replayed_filmed',completed_visits=done,last_verified_prefix=verified,all_four_hosts_and_refusal_complete=len(done)==5,all_rng_outcomes_covered=False),indent=2)+'\n').encode())
 try:
  c.verify(lambda r:r['passed']);save()
  for outside,variant in [(0x13,'play'),(0xa7,'play'),(0xde,'play'),(0x5c,'refuse')]:
   if any(v['outside']==outside and v['variant']==variant for v in done):continue
   if variant=='play':fund_wallet(c,110)
   if c.sms_view()[0xdb]<8:refill_magic(c)
   tag=f'{outside:02x}-{variant}';n=enter(c,outside,0x5f,tag);first=c.cap()['frames']+1;ref=f'natural-service-route/sms-npc-minigame-{outside:02x}-{variant}-visit01'
   c.service(f'{tag}-visit{n:02d}','md_minigame_service',['--outside',hex(outside),'--variant',variant,'--rounds','2','--sms-reference',ref]);name=f'md-{c.label}-{tag}-visit{n:02d}';film(c,name,first);verified=c.trace
   done.append(dict(passed=True,outside=outside,variant=variant,last_verified_prefix=c.trace,sms_reference=ref,video_report=f'videos/md-annexes-2026-11-12/{name}/report.json'));save()
 finally:c.close()

if __name__=='__main__':main()
