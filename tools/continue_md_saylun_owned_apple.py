"""Bring an actually bought apple to the unclaimed Saylun giver."""
import argparse,json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);a=p.parse_args();output=ROOT/'analysis/md_saylun_owned_apple_campaign.json'
 if output.exists() and json.loads(output.read_bytes()).get('passed'):return
 c=Campaign('natural-service-route/md-annex-merchant-apple-only-choices01',a.rom,'annex-saylun-owned-apple')
 try:
  c.verify(lambda r:r['passed']);raw=c.sms_view();assert raw[0xe8] and not raw[0x1c7]&2
  n=enter(c,0xc7,0x1f,'chimney');first=c.cap()['frames']+1;ref='natural-service-route/sms-npc-saylun-owned-apple-return03'
  steps=[dict(kind='travel',room=0x1f,point=[104,24],direction=0,target_room=15),dict(kind='talk',room=15,point=[104,56],text_pc=0x905b),dict(kind='travel',room=15,point=[104,152],direction=1,target_room=0x1f),dict(kind='travel',room=0x1f,point=[136,160],direction=1,target_room=0xc7)]
  c.service(f'hint-formatter{n:02d}','md_contact_plan',['--plan',json.dumps(dict(steps=steps)),'--sms-reference',ref,'--single-ack-reference']);name=f'md-{c.label}-hint-formatter{n:02d}';film(c,name,first)
  assert c.sms_view()[0xe8] and not c.sms_view()[0x1c7]&2
  output.write_text(json.dumps(dict(passed=True,trace=c.trace,sms_reference=ref,actual_purchase_trace='natural-service-route/md-annex-merchant-apple-only-choices01',currency_fixtures=0,gift_flag_remains_unclaimed=True,sms_final_duplicate_suffix_not_reproduced=True,sms_comparison_boundary='complete_recursive_formatter_return_not_later_duplicate_suffix',video_report=f'videos/md-annexes-2026-11-12/{name}/report.json'),indent=2)+'\n')
 finally:c.close()

if __name__=='__main__':main()
