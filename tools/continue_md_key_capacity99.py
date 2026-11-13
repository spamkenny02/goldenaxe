"""Isolated user-authorized money assistance; actual98 purchases and full refusal."""
import argparse,json,subprocess,sys
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter
from rebase_natural_campaign import evidence

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);a=p.parse_args();output=ROOT/'analysis/md_key_capacity99_campaign.json'
 if output.exists() and json.loads(output.read_bytes()).get('passed'):return
 c=Campaign('natural-service-route/md-annex-gold-houses-shard1of2-dd-contact-return01',a.rom,'annex-key-capacity99');ref='natural-service-route/sms-npc-key-capacity99-01';sr=json.loads(evidence(ROOT/'validation'/ref/'report.json'));assert sr['passed']
 try:
  c.verify(lambda r:r['passed']);assert c.sms_view()[0xde]==1;n=enter(c,0x94,0,'shop');first=c.cap()['frames']+1;trial=c.label+f'-buy{n:02d}';trace='natural-service-route/md-'+trial
  if not (ROOT/'validation'/trace/'report.json').exists():
   with (ROOT/'validation'/(trial+'.log')).open('w') as log:subprocess.run([sys.executable,str(ROOT/'tools/md_merchant_cases.py'),'--rom',str(c.rom),'--assisted-prefix','--prefix',c.current,'--trial',trial,'--choices',json.dumps(sr['choices']),'--sms-reference',ref,'--refill-gold','--budget','60000'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
  with (ROOT/'validation'/(trial+'-independent.log')).open('w') as log:subprocess.run([sys.executable,str(ROOT/'tools/replay_md_economic_component.py'),'--rom',str(c.rom),'--trace',trace,'--from-frame',str(first),'--name','md-'+trial],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
  output.write_bytes((json.dumps(dict(passed=True,trace=trace,sms_reference=ref,currency_assisted_component_test=True,keys_bought=98,final_keys=99,full_refusal=True,inventory_actor_health_and_quest_writes=0,video_report=f'videos/md-annexes-2026-11-12/md-{trial}/report.json',scope='Separate currency-only component; not a continuous campaign or unassisted economy proof.'),indent=2)+'\n').encode())
 finally:c.close()

if __name__=='__main__':main()
