"""Buy native64-point refills, saturation and full refusals after real spell casts."""
import argparse,json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_financial_preparation import spend,merchant_case

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);p.add_argument('--case',choices=['magic64','magic-clamp'],required=True);a=p.parse_args();out=ROOT/f'analysis/md_merchant_variant_{a.case}.json'
 if out.exists() and json.loads(out.read_bytes()).get('passed'):return
 c=Campaign('natural-service-route/md-annex-gold-houses-shard1of2-dd-contact-return01',a.rom,'annex-'+a.case)
 try:
  c.verify(lambda r:r['passed']);assert c.sms_view()[0xdd]>=70 and c.sms_view()[0xdc]==128
  spend(c,48 if a.case=='magic64' else 96,'actual-mp-spending02' if a.case=='magic64' else 'actual-mp-spending01');merchant_case(c,a.case)
 finally:c.close()

if __name__=='__main__':main()
