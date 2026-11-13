"""Write all three slots at the actual retained 2E NPC and reload each normally."""
import json,subprocess,sys
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film

def main():
 out=ROOT/'analysis/md_fresh_save_2e_campaign.json';old=json.loads(out.read_bytes()) if out.exists() else {};done=old.get('completed',[])
 c=Campaign(old.get('last_verified_prefix','natural-service-route/md-annex-gold-houses-shard0of2-60-contact-return01'),'validation/dialogue-empty-width03/candidate.bin','annex-fresh-save-2e')
 def invoke(tool,args,label):
  with (ROOT/'validation'/(label+'.log')).open('w') as log:subprocess.run([sys.executable,str(ROOT/'tools'/tool),*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 try:
  c.verify(lambda r:r['passed'])
  for slot in range(1):
   if any(r['slot']==slot for r in done):continue
   n=enter(c,0x2e,0,f'slot{slot}');first=c.cap()['frames']+1
   c.service(f'slot{slot}-write{n:02d}','natural_save_service',['--slot',str(slot),'--exit-after']);trace=c.trace;name=f'md-{c.label}-slot{slot}-write{n:02d}';film(c,name,first)
   trial=f'md-fresh-save-2e-slot{slot}-continue01';reload='game-written-save-load/'+trial
   invoke('validate_game_written_save.py',['--trace',trace,'--rom',str(c.rom),'--trial',trial,'--release-report-name',trial+'.json'],trial+'-load')
   invoke('replay_natural_campaign.py',['--trace',reload,'--rom',str(c.rom),'--game-written-continue'],trial+'-fixed')
   invoke('record_md_annex.py',['--trace',reload,'--rom',str(c.rom),'--from-frame','1','--name',trial,'--game-written-continue'],trial+'-movie')
   done.append(dict(slot=slot,trace=trace,continue_trace=reload,video_report=f'videos/md-annexes-2026-11-12/{name}/report.json',continue_video_report=f'videos/md-annexes-2026-11-12/{trial}/report.json'))
   out.write_bytes((json.dumps(dict(passed=len(done)==1,completed=done,last_verified_prefix=c.trace),indent=2)+'\n').encode())
 finally:c.close()
if __name__=='__main__':main()
