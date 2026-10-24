"""Bind current first-dungeon replay and keep unsuccessful D2 outcomes explicit."""
import gzip,json
from run_core import ROOT
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols
from summarize_axe_campaign_v0274 import read as historical

def main():
 base=ROOT/'validation/natural-dungeon-combat';digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());evidence={}
 def read(p):
  name=p.relative_to(ROOT).as_posix()
  if p.exists():raw=p.read_bytes()
  else:
   archive=ROOT/'analysis/natural-campaign-v0280';m=json.loads((archive/'manifest.json').read_bytes())
   if name in m['files']:raw=(archive/name).read_bytes();assert sha(raw)==m['files'][name]
   else:
    item=m['compressed'][name];encoded=(archive/item['stored']).read_bytes();assert sha(encoded)==item['stored_sha256'];raw=gzip.decompress(encoded);assert sha(raw)==item['raw_sha256']
  evidence[name]=sha(raw);return raw
 def load(p):return json.loads(read(p))
 stages=[]
 for name in ['md-auto-v0280-axe-aim01','md-auto-v0280-d1-boss-aim01','md-auto-v0280-d1-exit-aim01']:
  folder=base/name;r=load(folder/'report.json');c=load(folder/'capture.json');load(folder/'controls.json')
  assert r['rom_sha256']==c['rom_sha256']==digest and not c['test_ram_writes'] and c['sram_input'] is None
  assert r['room_cleared'] and not r['failure'] and not r['deaths']
  stages.append(dict(trace=name,clear_frame=r['clear_frame'],final_frame=c['frames'],state=r['last_state']))
 assert stages[0]['state']['weapon']==1 and stages[1]['state']['progress']==128 and stages[2]['state']['max_health']==32
 folder=base/'md-auto-v0280-d1-exit-aim01';c=load(folder/'capture.json');replay=folder.with_name(folder.name+'-fixed-replay');proof=load(replay/'replay_report.json')
 assert proof['passed'] and proof['rom_sha256']==digest and not proof['feedback_reads'] and not proof['ram_injections']
 for stem,ext in [('ram','bin'),('frame','png')]:assert read(folder/f"{stem}_{c['frames']:05d}.{ext}")==read(replay/f"{stem}_{c['frames']:05d}.{ext}")
 ram=read(folder/f"ram_{c['frames']:05d}.bin");sy=symbols(ROOT/'megadrive/out/release/symbol.txt');data=lambda n,k:bytes(ram[(sy[n]+i)^1] for i in range(k))
 source=base/'sms-auto-v0274-axe-exit01';old_capture=historical(source/'capture.json');sc=json.loads(old_capture);source_ram=historical(source/f"ram_{sc['frames']:05d}.bin")
 assert sc['rom_sha256']==sha((ROOT/'input/original.sms').read_bytes()) and not sc['test_ram_writes'] and sc['sram_input'] is None
 assert data('game_save_state',592)[0x50:0x150]==source_ram[0x100:0x200]
 assert data('sms_vram',16384)[0x3800:0x3d00]==source_ram[0x1600:0x1b00]
 attempts=[]
 for folder in sorted(base.glob('*-auto-v0280-d2-boss-aim*')):
  r=load(folder/'report.json');c=load(folder/'capture.json');ev=load(folder/'events.json');load(folder/'controls.json');assert not c['test_ram_writes'] and c['sram_input'] is None
  assert r['rom_sha256']==c['rom_sha256']==(sha((ROOT/'input/original.sms').read_bytes()) if folder.name.startswith('sms') else digest)
  hp=[a['hp'] for v in ev if v['room']==0x144 for a in v.get('actors',[]) if a['type']==0x63]
  attempts.append(dict(trace=folder.name,failure=r['failure'],deaths=r['deaths'],final_room=r['last_state']['room'],reached_boss=bool(hp),minimum_boss_hp=min(hp) if hp else None,second_crystal=r['room_cleared'] and r['last_state']['progress']==128))
 # Preserve the exact successful pilot implementation before later experiments.
 driver=ROOT/'validation/natural-v0280-pilot-baseline'
 result=dict(passed=True,md_sha256=digest,source_sha256=sc['rom_sha256'],first_dungeon=stages,successful_driver_sha256={n:sha((driver/n).read_bytes()) for n in ['natural_dungeon_combat.py','natural_combat_aim.py']},fixed_replay_ram_bytes=65536,fixed_replay_png_exact=True,source_first_exit_flags_exact_bytes=256,source_first_exit_map_exact_bytes=1280,source_reference=dict(trace=source.relative_to(ROOT).as_posix(),frame=sc['frames'],capture_sha256=sha(old_capture),ram_sha256=sha(source_ram),archive_manifest_sha256=sha((ROOT/'analysis/natural-axe-campaign-v0274/manifest.json').read_bytes())),second_dungeon_attempts=attempts,evidence=evidence,full_game_validated=False,limits=['Current playable v0280,ordinary cold boot/controller route,axe equip/first boss/crystal/exit without deaths. Entire final RAM and image reproduced by fixed buttons without feedback.','Persistent flags and map compare with the archived,unmodified original SMS first-exit trace;new SMS pilot failures are not successful source campaign runs.','D2 attempts are controller outcomes,not proof of a port defect. No second crystal/full campaign/PAL campaign/global R/IRQ/waveform/hardware claim.'])
 (ROOT/'analysis/natural_campaign_v0280_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('v0280 first dungeon and fixed replay pass;D2 attempts:',len(attempts),'second crystals:',sum(v['second_crystal'] for v in attempts))

if __name__=='__main__':main()
