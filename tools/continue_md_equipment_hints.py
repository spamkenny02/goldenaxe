"""Display all five retained ordinary equipment hints without taking gifts."""
import argparse,json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);a=p.parse_args();output=ROOT/'analysis/md_equipment_hints_campaign.json';old=json.loads(output.read_bytes()) if output.exists() else {};done=old.get('completed_visits',[])
 c=Campaign(old.get('last_verified_prefix','natural-service-route/md-annex-early-equipment-gillian-lightning1-learn01'),a.rom,'annex-equipment-hints');verified=c.trace
 def save():output.write_text(json.dumps(dict(status='played_replayed_filmed' if len(done)==5 else 'partial',completed_visits=done,last_verified_prefix=verified,all_five_complete=len(done)==5,separate_progression_branches=True),indent=2)+'\n')
 try:
  c.verify(lambda r:r['passed'])
  for outside in (0x27,0x50,0xb1,0x6a,0x92):
   if any(v['outside']==outside for v in done):continue
   raw=c.sms_view()
   if outside in (0xb1,0x6a,0x92) and not raw[0xf0]:
    c.close();c=Campaign('natural-service-route/md-annex-magic-fairies-fairy-ec-contact01',a.rom,'annex-equipment-hints-late');c.verify(lambda r:r['passed']);raw=c.sms_view()
   assert raw[0xe4] and not raw[0x100+outside]&2
   ref=f'natural-service-route/sms-npc-quest-hint-{outside:02x}-01';n=enter(c,outside,0x4f,f'{outside:02x}');first=c.cap()['frames']+1
   c.npc(f'{outside:02x}-hint{n:02d}',ref,quest_hint=True);name=f'md-{c.label}-{outside:02x}-hint{n:02d}';film(c,name,first);verified=c.trace;done.append(dict(outside=outside,trace=c.trace,sms_reference=ref,video_report=f'videos/md-annexes-2026-11-12/{name}/report.json'));save()
 finally:c.close()

if __name__=='__main__':main()
