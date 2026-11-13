"""Buy the intermediate shield, prove ownership, then play real low-money magic cases."""
import argparse,json,itertools
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film,entry_options
from md_financial_preparation import spend,merchant_case
from continue_sms_plain_house_census import census_world

def gift(c,amount,tag):
 raw=c.sms_view();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311]);choices=[]
 for outside,gain in json.loads((ROOT/'analysis/house_gold_reference.json').read_bytes())['records']:
  if gain!=amount or raw[0x100+outside]&2:continue
  for direction in range(4):
   world=census_world(raw,outside,0x3f,direction)
   if not entry_options(raw,outside,0x3f,direction,world):continue
   path,_=world.route(start)
   if path is not None:choices.append((len(path),outside));break
 assert choices,('No genuine gift of the required value remains',amount)
 _,outside=min(choices);n=enter(c,outside,0x3f,tag);first=c.cap()['frames']+1
 c.service(f'{tag}-gift{n:02d}','natural_house_service',['--outside',hex(outside),'--kind','gold','--gold-gain',str(amount)]);film(c,f'md-{c.label}-{tag}-gift{n:02d}',first)

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);a=p.parse_args();output=ROOT/'analysis/md_knight_and_low_magic_campaign.json';old=json.loads(output.read_bytes()) if output.exists() else {};steps=old.get('completed_steps',[])
 funding=json.loads((ROOT/'analysis/md_real_funding255_campaign.json').read_bytes());assert funding['passed']
 c=Campaign(old.get('last_verified_prefix',funding['last_verified_prefix']),a.rom,'annex-knight-low-magic')
 def save(key):
  steps.append(key);output.write_bytes((json.dumps(dict(status='played_replayed_filmed',completed_steps=steps,last_verified_prefix=c.trace,all_five_complete='magic32-poor' in steps),indent=2)+'\n').encode())
 try:
  c.verify(lambda r:r['passed'])
  if 'shield-buy' not in steps:
   raw=c.sms_view();assert raw[0xf2]<2 and raw[0xdd]==255
   doors=json.loads((ROOT/'analysis/doors_reference.json').read_bytes())['direct_unconditional_doors'];house=next(d['target'] for d in doors if d['room']==0xf9 and d['target'] in (0,1,0x2f));n=enter(c,0xf9,house,'shield-buy');first=c.cap()['frames']+1
   c.service(f'shield-buy{n:02d}','natural_merchant_purchase',['--outside','0xf9','--kind','shield','--count','1']);name=f'md-{c.label}-shield-buy{n:02d}';film(c,name,first);assert c.sms_view()[0xf2]==2 and c.sms_view()[0xdd]==5
   (ROOT/'analysis/md_knight_shield_campaign.json').write_bytes((json.dumps(dict(passed=True,trace=c.trace,sms_reference='natural-service-route/sms-npc-knight-shield-f9-buy01',shield_before=1,shield_after=2,gold_before=255,gold_after=5,video_report=f'videos/md-annexes-2026-11-12/{name}/report.json'),indent=2)+'\n').encode());save('shield-buy')
  if 'shield-owned' not in steps:merchant_case(c,'shield-owned');save('shield-owned')
  if 'magic-poor' not in steps:spend(c,min(120,c.sms_view()[0xdb]),'one-real-cast01');merchant_case(c,'magic-poor');save('magic-poor')
  if 'budget65' not in steps:
   assert c.sms_view()[0xdd]==5
   raw=c.sms_view();available=[(outside,gain) for outside,gain in json.loads((ROOT/'analysis/house_gold_reference.json').read_bytes())['records'] if 0<gain<100 and not raw[0x100+outside]&2];chosen=None
   for count in range(1,7):
    chosen=next((rows for rows in itertools.combinations(available,count) if 60<=5+sum(v for _,v in rows)<100),None)
    if chosen:break
   assert chosen,'No remaining real gifts produce the required low-money range'
   for number,(_,amount) in enumerate(chosen,1):gift(c,amount,f'real-budget-gift-{number:02d}')
   if c.sms_view()[0xdd]>=80:
    assert c.sms_view()[0xdb]<128
    n=enter(c,0x7b,0x2f,'budget-real-magic16');first=c.cap()['frames']+1
    c.service(f'budget-real-magic16-buy{n:02d}','natural_merchant_purchase',['--outside','0x7b','--kind','magic','--count','1']);film(c,f'md-{c.label}-budget-real-magic16-buy{n:02d}',first)
   assert 60<=c.sms_view()[0xdd]<80;save('budget65')
  if 'magic32-poor' not in steps:spend(c,32,'actual-mp-to32');merchant_case(c,'magic32-poor');save('magic32-poor')
 finally:c.close()

if __name__=='__main__':main()
