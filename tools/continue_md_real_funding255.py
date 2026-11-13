"""Earn and cap255 gold through unclaimed native gifts, without money writes."""
import argparse,json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import fund_wallet

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);a=p.parse_args();output=ROOT/'analysis/md_real_funding255_campaign.json'
 if output.exists() and json.loads(output.read_bytes()).get('passed'):return
 c=Campaign('natural-service-route/md-annex-gold-houses-shard1of2-dd-contact-return01',a.rom,'annex-real-funding255')
 try:
  c.verify(lambda r:r['passed']);before=c.sms_view()[0xdd];fund_wallet(c,255);assert c.sms_view()[0xdd]==255
  output.write_bytes((json.dumps(dict(passed=True,initial_gold=before,final_gold=255,last_verified_prefix=c.trace,currency_fixtures=0,scope='Real once-only money gifts and normal map travel;255 reached by the actual game clamp. No wallet, item, health, actor or quest write.'),indent=2)+'\n').encode())
 finally:c.close()

if __name__=='__main__':main()
