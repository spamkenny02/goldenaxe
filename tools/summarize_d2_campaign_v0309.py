"""Verify current v309 cold progression through D2 and its ordinary return."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
 digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());assert digest=='7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049'
 names=['md-auto-v0309-d2-entry02','md-auto-v0309-d2-key01','md-auto-v0309-d2-key04','md-auto-v0309-d2-key05','md-auto-v0309-d2-boss03','md-auto-v0309-d2-boss05','md-auto-v0309-d2-exit01'];stages=[];files={}
 for name in names:
  folder=ROOT/'validation/natural-dungeon-combat'/name;cap=json.loads(evidence(folder/'capture.json'));report=json.loads(evidence(folder/'report.json'));assist,writes=recording(folder,cap);cold=folder.with_name(folder.name+'-assisted-fixed-replay-'+str(cap['frames']));proof=json.loads(evidence(cold/'replay_report.json'))
  assert cap['rom_sha256']==digest and cap['sram_input'] is None and proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof.get('controlled_sram_fixture',False)
  for stem,ext in [('ram','bin'),('frame','png')]:assert evidence(folder/f'{stem}_{cap["frames"]:05d}.{ext}')==evidence(cold/f'{stem}_{cap["frames"]:05d}.{ext}')
  if name.endswith('boss03'):assert report['failure']=='frame_limit' and report['last_state']['health']==40 and not report['room_cleared']
  else:assert report['failure'] is None
  if name.endswith('boss05') or name.endswith('exit01'):
   assert max(f for f,_,_ in writes)<=assist['release_write_frame']<assist['first_boss_combat']['frame'] and assist['first_boss_combat']['hurt']==0
  stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frames=cap['frames'],state=report['last_state'],room_cleared=report['room_cleared'],whole_ram_png_exact=True,live_partial_boss_checkpoint=name.endswith('boss03')))
  paths=[folder/n for n in ['capture.json','report.json','controls.json','assistance.json']]+[cold/'replay_report.json',folder/f'ram_{cap["frames"]:05d}.bin',folder/f'frame_{cap["frames"]:05d}.png']
  for p in paths:files[p.relative_to(ROOT).as_posix()]=sha(evidence(p))
 last=stages[-1];assert last['state']['room']==0xd6 and last['state']['health']==33 and last['state']['dungeon']==0 and last['state']['max_health']==48
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');raw=evidence(ROOT/last['trace']/f'ram_{last["frames"]:05d}.bin');save=bytes(raw[(sy['game_save_state']+i)^1] for i in range(592));assert list(save[0x1f:0x28])==[128,128,0,0,0,0,0,0,0]
 for n in ['versions/v0309-7270576d/gaw-megadrive-v0309.bin','input/original.sms','megadrive/src/main.c','tools/summarize_d2_campaign_v0309.py','validation/v0309-controlled-prefix-sources/natural_dungeon_combat.py']:
  files[n]=sha(evidence(ROOT/n))
 result=dict(passed=True,md_sha256=digest,version=309,full_game_validated=False,controlled_sram_fixture=False,second_crystal_and_exterior_return=True,boss_assistance=False,health_refills_imported=0,primary_state_imports=0,sram_imports=0,stages=stages,current_campaign_trace=last['trace'],campaign_frames=last['frames'],boss_prediction_windows=461,exit_prediction_windows=14,evidence=files,limits=['Strict cold v309 proof currently covers two crystals; nine crystals remain a separate v306 proof.','Boss03 is an incomplete live fight checkpoint continued by boss05,not a standalone victory. Boss05 and exit have independent full-RAM/PNG replays.','The palace Continue fixture is a separate controlled integration test and is excluded from this campaign proof.','Optional quests,final palace,Golden Axe,last boss,ending,global RNG/audio/video fidelity and broad current stack coverage remain open.'])
 (ROOT/'analysis/d2_campaign_v0309_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('D2 v309 cold campaign and unassisted exterior return verified:',last['frames'])

if __name__=='__main__':main()
