"""Shared real spell spending and source-referenced merchant transactions."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from md_campaign_navigation import enter,film

def spend(c,target,tag):
 if c.sms_view()[0xdb]==target:return
 c.equip(5,tag+'-select-earth');first=c.cap()['frames']+1;trial=c.label+'-'+tag
 c.invoke('md_spend_magic.py',['--rom',str(c.rom),'--trace',c.trace,'--trial',trial,'--target-magic',str(target)],'natural-service-route','md-'+trial,lambda r:r['passed']);film(c,'md-'+trial,first);c.equip(1,tag+'-restore-axe');assert c.sms_view()[0xdb]==target

def merchant_case(c,key):
 output=ROOT/f'analysis/md_merchant_variant_{key}.json';s=json.loads((ROOT/f'analysis/sms_merchant_variant_{key}.json').read_bytes());ref=s['trace'];sr=json.loads(evidence(ROOT/'validation'/ref/'report.json'));outside=sr['outside']
 doors=json.loads((ROOT/'analysis/doors_reference.json').read_bytes())['direct_unconditional_doors'];house=next(d['target'] for d in doors if d['room']==outside and d['target'] in (0,1,0x2f));n=enter(c,outside,house,key);first=c.cap()['frames']+1
 c.service(f'{key}-choices{n:02d}','md_merchant_cases',['--choices',json.dumps(sr['choices']),'--sms-reference',ref]);name=f'md-{c.label}-{key}-choices{n:02d}';film(c,name,first)
 r=dict(passed=True,key=key,trace=c.trace,sms_reference=ref,outside=outside,choices=sr['choices'],video_report=f'videos/md-annexes-2026-11-12/{name}/report.json',resource_fixtures=0)
 output.write_bytes((json.dumps(r,indent=2)+'\n').encode());return r
