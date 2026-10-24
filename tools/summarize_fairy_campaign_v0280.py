"""Bind naturally obtained life capacity on SMS/MD and the subsequent D2 trials."""
import gzip,json
from run_core import ROOT
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols

def main():
 evidence={};archive=ROOT/'analysis/fairy-campaign-v0280'
 def read(p):
  name=p.relative_to(ROOT).as_posix()
  if p.exists():raw=p.read_bytes()
  else:
   m=json.loads((archive/'manifest.json').read_bytes())
   if name in m['files']:raw=(archive/name).read_bytes();assert sha(raw)==m['files'][name]
   else:
    item=m['compressed'][name];encoded=(archive/item['stored']).read_bytes();assert sha(encoded)==item['stored_sha256'];raw=gzip.decompress(encoded);assert sha(raw)==item['raw_sha256']
  evidence[name]=sha(raw);return raw
 def load(p):return json.loads(read(p))
 digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());original=sha((ROOT/'input/original.sms').read_bytes());sy=symbols(ROOT/'megadrive/out/release/symbol.txt');systems=[];endpoints=[]
 for tag in ['sms','md']:
  folder=ROOT/'validation/natural-service-route'/(tag+'-v0280-fairy-c9-01');r=load(folder/'report.json');c=load(folder/'capture.json');load(folder/'controls.json')
  assert r['passed'] and r['rom_sha256']==c['rom_sha256']==(original if tag=='sms' else digest) and not c['test_ram_writes'] and c['sram_input'] is None
  assert r['initial_state']['max_health']==32 and r['initial_state']['outside_flags']&2==0
  final=r['last_state'];assert final['health']==final['max_health']==40 and final['outside_flags']&2 and final['room']==0xc9 and final['first_crystal']==128
  replay=folder.with_name(folder.name+'-fixed-replay');proof=load(replay/'replay_report.json');assert proof['passed'] and not proof['feedback_reads'] and not proof['ram_injections']
  for stem,ext in [('ram','bin'),('frame','png')]:assert read(folder/f"{stem}_{c['frames']:05d}.{ext}")==read(replay/f"{stem}_{c['frames']:05d}.{ext}")
  ram=read(folder/f"ram_{c['frames']:05d}.bin")
  if tag=='sms':endpoints.append((ram[0x100:0x200],ram[0x1600:0x1b00]))
  else:
   data=lambda n,k:bytes(ram[(sy[n]+i)^1] for i in range(k));endpoints.append((data('game_save_state',592)[0x50:0x150],data('sms_vram',16384)[0x3800:0x3d00]))
  route=ROOT/'validation/natural-dungeon-route'/(tag+'-v0280-d2-after-fairy01');rr=load(route/'route_report.json');rc=load(route/'capture.json');load(route/'controls.json')
  assert rr['reached_entrance'] and not rr['failure'] and rr['last_state']['room']==0x171 and not rr['normal_continues'] and not rc['test_ram_writes'] and rc['sram_input'] is None
  systems.append(dict(system=tag,service_complete_frame=r['complete_frame'],service_final_state=final,whole_ram_fixed_replay_bytes=proof['whole_ram_bytes'],fixed_png_exact=True,second_entrance_frame=rc['frames'],second_entrance_health=rr['last_state']['health'],second_entrance_deaths=rr['normal_continues']))
 assert endpoints[0]==endpoints[1]
 trials=[]
 for p in sorted((ROOT/'validation/natural-dungeon-combat').glob('*-auto-v0280-d2-fairy-*')):
  r=load(p/'report.json');c=load(p/'capture.json');rows=load(p/'events.json');load(p/'controls.json');assert not c['test_ram_writes'] and c['sram_input'] is None and r['rom_sha256']==c['rom_sha256']
  hp=[a['hp'] for v in rows if v['room']==0x144 for a in v.get('actors',[]) if a['type']==0x63]
  trials.append(dict(trace=p.name,failure=r['failure'],deaths=r['deaths'],reached_boss=bool(hp),minimum_boss_hp=min(hp) if hp else None,final_room=r['last_state']['room'],second_crystal=r['room_cleared'] and r['last_state']['progress']==128,last_state=r['last_state']))
 out=dict(passed=True,md_sha256=digest,source_sha256=original,game_code_changed=False,systems=systems,source_flags_exact_bytes=256,source_map_exact_bytes=1280,second_dungeon_trials=trials,evidence=evidence,full_game_validated=False,limits=['Ordinary cold boot/buttons,first C9 life-fairy dialogue,one-time persistent flag,32-to40 capacity/full healing and normal exit on both machines. Each final RAM/image is reproduced by cold fixed inputs without feedback.','Source/native final persistent flags and outside map match. This does not prove absolute timing,all intermediate pixels,audio waveform or every fairy.','Subsequent D2 controller outcomes are reported explicitly;failed trials do not prove a game defect or a completed second crystal. Full campaign/PAL/global R/IRQ/hardware remain open.'])
 (ROOT/'analysis/fairy_campaign_v0280_report.json').write_bytes((json.dumps(out,indent=2)+'\n').encode());print('C9 life capacity and fixed replay pass on SMS/MD;D2 crystal successes:',sum(v['second_crystal'] for v in trials))

if __name__=='__main__':main()
