"""Return to the inn already paid in the actual native tour and pay again."""
import json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film

def main():
 c=Campaign('natural-service-route/md-annex-inn-55-pay01','validation/dialogue-empty-width03/candidate.bin','annex-inn-repeat')
 try:
  c.verify(lambda r:r['passed']);n=enter(c,0x55,1,'55-return');first=c.cap()['frames']+1
  c.service(f'55-rest{n:02d}','md_paid_healer',['--outside','0x55']);name=f'md-{c.label}-55-rest{n:02d}';film(c,name,first)
  (ROOT/'analysis/md_inn_repeat_campaign.json').write_bytes((json.dumps(dict(passed=True,trace=c.trace,sms_reference='natural-service-route/sms-npc-inn-repeat-rest01',earlier_actual_rest='natural-service-route/md-annex-inn-55-pay01',video_report=f'videos/md-annexes-2026-11-12/{name}/report.json'),indent=2)+'\n').encode())
 finally:c.close()
if __name__=='__main__':main()
