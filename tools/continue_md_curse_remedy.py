"""Enter the palace, receive real corrosion, defeat the curser and use actual oil."""
import argparse,json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import film

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);a=p.parse_args();output=ROOT/'analysis/md_curse_remedy_campaign.json'
 if output.exists() and json.loads(output.read_bytes()).get('passed'):return
 c=Campaign('natural-service-route/md-annex-late-equipment-equipment-55-return01',a.rom,'annex-curse-remedy')
 try:
  c.verify(lambda r:r['passed']);assert c.sms_view()[0xe2] and not c.sms_view()[0xbf]
  c.route('palace-entry03',['--door-index','10'],tool='natural_palace_world_route.py')
  c.stage('switch16d01','0x18d,0x17d,0x16d','0x16d',['--equip-basic','--contact-room','0x16d','--contact-destination','0x16d','--mechanism-during-combat'],planner='contact',gate='contact_route_passed')
  c.stage('curser-entry02','0x16d,0x17d,0x18d,0x18e','0x18e',['--equip-basic','--reach-room','--allow-live-arrival','--rush-rooms','0x18e','--arrival-x','128','--arrival-y','128'],gate='target_room_reached')
  first=c.cap()['frames']+1;trial=c.label+'-contact-and-cure03';name='md-auto-'+trial
  c.invoke('md_curse_remedy.py',['--rom',str(c.rom),'--trace',c.trace,'--trial',trial],'natural-dungeon-combat',name,lambda r:r['curse_remedy_passed'])
  film(c,name,first);r=json.loads((ROOT/'validation'/c.trace/'report.json').read_bytes())
  output.write_bytes((json.dumps(dict(passed=True,trace=c.trace,sms_reference='natural-dungeon-combat/sms-auto-sms-npc-palace-extended-curse-remedy01',first_curse=r['first_curse'],first_cure=r['first_cure'],resource_or_actor_writes=r['resource_or_actor_writes'],video_report=f'videos/md-annexes-2026-11-12/{name}/report.json'),indent=2)+'\n').encode())
 finally:c.close()

if __name__=='__main__':main()
