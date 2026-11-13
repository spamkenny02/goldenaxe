"""Replay one retained merchant choice list on native MD and film it."""
import argparse,json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film,fund_wallet
from rebase_natural_campaign import evidence

def main():
 p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--rom',required=True);p.add_argument('--case',required=True);p.add_argument('--fund',type=int,default=0);a=p.parse_args()
 output=ROOT/f'analysis/md_merchant_variant_{a.case}.json'
 if output.exists() and json.loads(output.read_bytes()).get('passed'):return
 source=json.loads((ROOT/f'analysis/sms_merchant_variant_{a.case}.json').read_bytes());ref=source['trace'];sr=json.loads(evidence(ROOT/'validation'/ref/'report.json'));assert sr['passed'];outside=sr['outside']
 doors=json.loads((ROOT/'analysis/doors_reference.json').read_bytes())['direct_unconditional_doors'];house=next(d['target'] for d in doors if d['room']==outside and d['target'] in (0,1,0x2f))
 label='annex-merchant-'+a.case;c=Campaign(a.prefix,a.rom,label)
 try:
  c.verify(lambda r:r['passed'])
  if a.fund:fund_wallet(c,a.fund)
  n=enter(c,outside,house,a.case);first=c.cap()['frames']+1
  c.service(f'choices{n:02d}','md_merchant_cases',['--choices',json.dumps(sr['choices']),'--sms-reference',ref]);name=f'md-{label}-choices{n:02d}';film(c,name,first)
  output.write_text(json.dumps(dict(passed=True,key=a.case,outside=outside,initial_prefix=a.prefix,trace=c.trace,sms_reference=ref,choices=sr['choices'],video_report=f'videos/md-annexes-2026-11-12/{name}/report.json',separate_actual_branch=True),indent=2)+'\n')
 finally:c.close()

if __name__=='__main__':main()
