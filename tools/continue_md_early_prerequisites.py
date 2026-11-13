"""Obtain the actual rope early and play both refused equipment hints."""
import argparse,json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film,fund_wallet
from rebase_natural_campaign import evidence

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);a=p.parse_args()
 for key,initial,pc in [('no-lightning','natural-service-route/md-annex-campaign-axe-before-apple01',0x8e5c),('low-health-capacity','natural-service-route/md-annex-before-apple-gillian-lightning1-learn01',0x8ed9)]:
  output=ROOT/f'analysis/md_equipment_prerequisite_{key}.json'
  if output.exists() and json.loads(output.read_bytes()).get('passed'):continue
  resume='natural-dungeon-combat/md-auto-annex-prerequisite-'+key+'-supply-exit02'
  folder=ROOT/'validation'/resume
  if (folder/'report.json').exists() and json.loads((folder/'report.json').read_bytes()).get('dungeon_exit_verified'):initial=resume
  c=Campaign(initial,a.rom,'annex-prerequisite-'+key)
  try:
   c.verify(lambda r:r.get('passed',r.get('dungeon_exit_verified',False)));raw=c.sms_view();assert raw[0xda]<56 and bool(raw[0xe4])==(key=='low-health-capacity')
   if not raw[0xed]:
    if not raw[0xde]:
     fund_wallet(c,40);n=enter(c,0xd7,0x2f,'rope-key');first=c.cap()['frames']+1
     c.service(f'rope-key-buy{n:02d}','natural_merchant_purchase',['--outside','0xd7','--kind','key','--count','1']);film(c,f'md-{c.label}-rope-key-buy{n:02d}',first);assert c.sms_view()[0xde]
    first=c.cap()['frames']+1;c.route('d3-entry03',['--door-index','3','--live-prefix-terrain','--persisted-only'])
    c.stage('rope02','0x1f8,0x1f7,0x1e7,0x1e2,0x1f2,0x1f3,0x1f4','0x1f4',['--equip-axe','--retarget-pending-boss','--collect-item','13'],planner='item',boss=0x1c3,gate='item_acquisition_passed')
    c.stage('supply-exit02','0x1f4,0x1f3,0x1f2,0x1e2,0x1e7,0x1f7,0x1f8','0x62',['--equip-axe','--exit-dungeon','--exit-before-crystal'],boss=0x1c3,gate='dungeon_exit_verified')
    film(c,f'md-{c.label}-rope-and-exit01',first)
   raw=c.sms_view();assert raw[0xed] and not raw[0xd1]&128 and raw[0xda]<56
   n=enter(c,0x50,0x4f,'a5');first=c.cap()['frames']+1
   ref='natural-service-route/'+('sms-npc-equipment-no-lightning-hint01' if key=='no-lightning' else 'sms-npc-equipment-low-capacity-hint01')
   sr=json.loads(evidence(ROOT/'validation'/ref/'report.json'))
   plan=sr.get('plan') or dict(steps=[dict(kind='silent',room=0x4f,point=[120,72]),dict(kind='talk',room=0x4f,point=[136,72],text_pc=pc),dict(kind='travel',room=0x4f,point=[136,160],direction=1,target_room=0x50)])
   c.service(f'hint{n:02d}','md_contact_plan',['--plan',json.dumps(plan),'--sms-reference',ref]);name=f'md-{c.label}-hint{n:02d}';film(c,name,first)
   output.write_text(json.dumps(dict(passed=True,key=key,trace=c.trace,initial_prefix=initial,sms_reference=ref,health_capacity=raw[0xda],lightning_level=raw[0xe4],rope_genuinely_obtained=True,video_report=f'videos/md-annexes-2026-11-12/{name}/report.json'),indent=2)+'\n')
  finally:c.close()

if __name__=='__main__':main()
