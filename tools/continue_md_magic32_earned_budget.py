"""Reuse an already proved real60-gold branch, then cast and buy normally."""
import json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_financial_preparation import spend,merchant_case

def main():
 source='natural-service-route/md-annex-gold-houses-shard0of2-60-contact-return01'
 c=Campaign(source,'validation/dialogue-empty-width03/candidate.bin','annex-magic32-earned-budget')
 try:
  c.verify(lambda r:r['passed']);v=c.sms_view();assert v[0xdd]==60 and v[0xe5]==2 and v[0xdb]>=32
  spend(c,32,'actual-mp-to32');merchant_case(c,'magic32-poor')
  out=ROOT/'analysis/md_knight_and_low_magic_campaign.json';j=json.loads(out.read_bytes());j.update(all_four_financial_cases_complete=True,all_financial_cases_complete=True,completed_case_keys=['shield-buy','shield-owned','magic-poor','magic32-poor'],separate_magic32_branch=dict(initial_prefix=source,actual_initial_gold=60,trace=c.trace,no_currency_fixtures=True),status='all_selected_shield_and_low_money_magic_cases_played_replayed_filmed');out.write_bytes((json.dumps(j,indent=2)+'\n').encode())
 finally:c.close()
if __name__=='__main__':main()
