"""Replay one retained merchant choice list on native MD and film it."""
import argparse,json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film,fund_wallet
from rebase_natural_campaign import evidence

def main():
 p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--rom',required=True);p.add_argument('--case',required=True);p.add_argument('--fund',type=int,default=0);p.add_argument('--owned-followup',choices=['j9','kari']);a=p.parse_args()
 output=ROOT/f'analysis/md_merchant_variant_{a.case}.json'
 completed=json.loads(output.read_bytes()) if output.exists() else {}
 followup=ROOT/f'analysis/md_owned_quest_{a.owned_followup}.json' if a.owned_followup else None
 if completed.get('passed') and (followup is None or followup.exists() and json.loads(followup.read_bytes()).get('passed')):return
 source=json.loads((ROOT/f'analysis/sms_merchant_variant_{a.case}.json').read_bytes());ref=source['trace'];sr=json.loads(evidence(ROOT/'validation'/ref/'report.json'));assert sr['passed'];outside=sr['outside']
 doors=json.loads((ROOT/'analysis/doors_reference.json').read_bytes())['direct_unconditional_doors'];house=next(d['target'] for d in doors if d['room']==outside and d['target'] in (0,1,0x2f))
 label='annex-merchant-'+a.case;c=Campaign(completed.get('trace',a.prefix),a.rom,label)
 try:
  c.verify(lambda r:r['passed'])
  if not completed.get('passed'):
   if a.fund:fund_wallet(c,a.fund)
   n=enter(c,outside,house,a.case);first=c.cap()['frames']+1
   c.service(f'choices{n:02d}','md_merchant_cases',['--choices',json.dumps(sr['choices']),'--sms-reference',ref]);name=f'md-{label}-choices{n:02d}';film(c,name,first)
   output.write_text(json.dumps(dict(passed=True,key=a.case,outside=outside,initial_prefix=a.prefix,trace=c.trace,sms_reference=ref,choices=sr['choices'],video_report=f'videos/md-annexes-2026-11-12/{name}/report.json',separate_actual_branch=True),indent=2)+'\n')
  if a.owned_followup:
   outside=0x92 if a.owned_followup=='j9' else 0x55;house=0x4f if outside==0x92 else 0x1f;raw=c.sms_view();item=0xe8 if outside==0x92 else 0xe2
   assert raw[item] and raw[0xe4] and not raw[0x100+outside]&2
   ref='natural-service-route/sms-npc-owned-quest-'+('j9-owned-apple-contact01' if outside==0x92 else 'kari-owned-oil-contact01');sr=json.loads(evidence(ROOT/'validation'/ref/'report.json'));assert sr['passed']
   n=enter(c,outside,house,a.owned_followup+'-owned');first=c.cap()['frames']+1
   c.service(f'{a.owned_followup}-owned-hint{n:02d}','md_contact_plan',['--plan',json.dumps(sr['plan']),'--sms-reference',ref]);name=f'md-{label}-{a.owned_followup}-owned-hint{n:02d}';film(c,name,first)
   followup.write_bytes((json.dumps(dict(passed=True,trace=c.trace,sms_reference=ref,owned_item_really_bought=True,gift_not_awarded=True,video_report=f'videos/md-annexes-2026-11-12/{name}/report.json'),indent=2)+'\n').encode())
 finally:c.close()

if __name__=='__main__':main()
