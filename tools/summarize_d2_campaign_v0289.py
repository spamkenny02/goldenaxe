"""Historical v289 D2 campaign proof, independent of newer root aliases."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence

def main():
 refs={}
 def read(n):
  raw=evidence(ROOT/n);refs[n]=sha(raw);return raw
 def load(n):return json.loads(read(n))
 digest=sha(read('versions/v0289-1abcdb47/gaw-megadrive-v0289.bin'));stages=[]
 for name in ['key01','boss01','boss02','exit02']:
  base='validation/natural-dungeon-combat/md-auto-v0289-d2-'+name;r=load(base+'/report.json');c=load(base+'/capture.json');a=load(base+'/assistance.json');proof=load(base+f"-assisted-fixed-replay-{c['frames']}/replay_report.json")
  assert r['rom_sha256']==c['rom_sha256']==proof['rom_sha256']==digest and proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not r['deaths'] and c['sram_input'] is None and not a['health_refills']
  assert not a['boss_assistance'] and r['failure'] in [None,'frame_limit']
  if name!='key01':assert a['writes'][-1]['frame']==a['release_write_frame']<a['first_boss_combat']['frame'] and a['first_boss_combat']['hurt']==0 and a['first_boss_damage'] is None
  if name.startswith('boss'):assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows'] and r['primary_state_imports']==0
  if name=='exit02':assert a['new_assistance_writes']==0 and r['full_dungeon_cleared'] and r['last_state']['completed_dungeon_progress']==128 and r['last_state']['room']==0xd6 and r['last_state']['health']==r['last_state']['max_health']==48
  stages.append(dict(trace=base,frames=c['frames'],last_state=r['last_state'],failure=r['failure'],first_boss_combat=a['first_boss_combat'],release_frame=a['release_write_frame'],boss_damage=a['first_boss_damage'],whole_ram_png_cold_replay=True))
 result=dict(passed=True,md_sha256=digest,version=289,native_d2_stages=stages,full_game_validated=False,evidence=refs,limits=['Approach is explicitly assisted by logged hurt-counter writes, released before the boss. No boss/exit help, health refill or imported primary state.','Boss01 stopped alive at its diagnostic budget; boss02 continued and won. Exit01 reached the exterior but omitted inherited assistance metadata, so clean exit02 is authoritative.','This proves the recorded v289 second dungeon in NTSC, not later dungeons, PAL campaign, source encounters or global timing.'])
 (ROOT/'analysis/d2_campaign_v0289_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('v289 D2 proof',stages[-1]['frames'])
if __name__=='__main__':main()
