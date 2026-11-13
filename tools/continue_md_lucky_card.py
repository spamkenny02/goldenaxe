"""Observe a genuine lucky-card round by normal neutral waits and real bets."""
import argparse,json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film
from rebase_natural_campaign import evidence

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);a=p.parse_args();output=ROOT/'analysis/md_lucky_card_campaign.json'
 if output.exists() and json.loads(output.read_bytes()).get('passed'):return
 funding=json.loads((ROOT/'analysis/md_real_funding255_campaign.json').read_bytes());assert funding['passed'];ref='natural-service-route/sms-npc-minigame-lucky-wait217-play01';sr=json.loads(evidence(ROOT/'validation'/ref/'report.json'));assert sr['passed'] and sr['lucky_card_observed'];attempts=[]
 for wait in (217,0,61,123,301):
  c=Campaign(funding['last_verified_prefix'],a.rom,f'annex-minigame-lucky-wait{wait}')
  try:
   c.verify(lambda r:r['passed']);assert c.sms_view()[0xdd]==255;n=enter(c,0x5c,0x5f,'host');first=c.cap()['frames']+1
   c.service(f'play{n:02d}','md_minigame_service',['--outside','0x5c','--variant','play','--rounds','32','--stop-on-lucky','--initial-wait',str(wait),'--sms-reference',ref]);name=f'md-{c.label}-play{n:02d}';film(c,name,first);r=json.loads((ROOT/'validation'/c.trace/'report.json').read_bytes());attempts.append(dict(wait=wait,trace=c.trace,lucky=r['lucky_card_observed'],video_report=f'videos/md-annexes-2026-11-12/{name}/report.json'))
   if r['lucky_card_observed']:
    output.write_bytes((json.dumps(dict(passed=True,trace=c.trace,sms_reference=ref,attempts=attempts,lucky_outcomes=[o for o in r['outcomes'] if o['special_card']==0x38],rng_or_currency_fixtures=0,all_rng_outcomes_covered=False,video_report=attempts[-1]['video_report']),indent=2)+'\n').encode());return
  finally:c.close()
 raise AssertionError('No lucky card in the actual retained attempts; no goal credit assigned')

if __name__=='__main__':main()
