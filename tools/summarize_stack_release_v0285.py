"""Bind the playable stack/VDP corrections to scoped cold-run evidence."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols
from validate_playable_map_conversion import symbols as full_symbols
from extract_title import rle_planes,map_decode


def main():
 digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());refs={}
 def raw(name):
  b=evidence(ROOT/name);refs[name]=sha(b);return b
 def load(name,current=False):
  r=json.loads(raw(name))
  if current:assert r.get('md_sha256',r.get('rom_sha256'))==digest,name
  return r
 old=load('validation/stack-v0280-all/stack_report.json')
 stack=load('validation/stack-v0285-natural-all02/stack_report.json',True)
 assert stack['all_instructions'] and stack['read_only'] and not stack['invalid_heap_examples']
 minimum=min(v['sp'] for v in stack['instruction_minima']);boundary=max(v['end'] for v in stack['heap_changes'])+2
 assert minimum>boundary and all(v['valid'] for v in stack['heap_changes'])
 before=min(v['sp'] for v in old['instruction_minima']);assert before<0xf184 and old['invalid_heap_examples']
 rows=stack['gameplay_milestones'];assert not any(r['game_state']==20 or r['game_state']==12 and not r['hero_health'] or r['sound_unhandled_command'] for r in rows)
 axe=next(r for r in rows if r['hero_weapon_level']==1)
 crystal=next(r for r in rows if r['first_crystal']==128)
 reward=next(r for r in rows if r['hero_max_health']==40 and r['hero_health']==40)
 end=rows[-1];assert end['room_id']==0xc9 and end['first_crystal']==128 and end['world_dungeon_number']==0
 trace='validation/natural-dungeon-route/md-v0285-fairy-rebase01'
 capture=load(trace+'/capture.json');rebase=load(trace+'/rebase_report.json',True);replay=load(trace+'-fixed-replay/replay_report.json',True)
 assert rebase['passed'] and replay['passed'] and not capture['test_ram_writes'] and capture['sram_input'] is None
 frame=capture['frames'];ram=raw(trace+f'/ram_{frame:05d}.bin')
 for stem,ext in [('ram','bin'),('frame','png')]:
  b=raw(trace+f'/{stem}_{frame:05d}.{ext}')
  assert b==raw(trace+f'-fixed-replay/{stem}_{frame:05d}.{ext}')
  assert b==raw('validation/stack-v0285-natural-all02'+f'/{stem}_{frame:05d}.{ext}'),'Observer changed execution'
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');data=lambda n,k:bytes(ram[(sy[n]+i)^1] for i in range(k))
 source='validation/natural-service-route/sms-v0280-fairy-c9-01';sc=load(source+'/capture.json');sr=raw(source+f"/ram_{sc['frames']:05d}.bin")
 flags_equal=data('game_save_state',592)[0x50:0x150]==sr[0x100:0x200];map_equal=data('sms_vram',16384)[0x3800:0x3d00]==sr[0x1600:0x1b00]
 assert flags_equal and map_equal
 audio=load('validation/audio_stream_equivalence_report.json',True)
 assert audio['source_vector_cases']==25644 and audio['caller_workspace_cases']==28644 and audio['caller_workspace_guard_bytes']==32 and audio['all_400_bytes_work_DE_PSG_status_exact'] and audio['production_fast_audio_wired']
 menu=load('validation/menu_transition_report.json',True);assert len(menu['cases'])==6
 video=load('analysis/dialogue_vblank_v0285_report.json',True);assert video['passed'] and all(not r['differing_frames'] for r in video['cases'])
 negative=load('analysis/dialogue_vblank_v0284_report.json');assert not negative['passed']
 titles=[load('validation/title_cadence'+suffix+'_report.json',True) for suffix in ['', '-pal']]
 assert all(r['relative_timing_exact'] and len(r['pixel_checks'])==20 for r in titles)
 # Check the immutable ROM's actual RLE output extents against the workspace.
 fs=full_symbols(ROOT/'megadrive/out/release/symbol.txt');rom=(ROOT/'gaw-megadrive.bin').read_bytes();bank=rom[fs['title_bank7']:fs['title_bank7']+16384]
 p,_=rle_planes(bank,16,bytearray(16384),0,4);extents={}
 for name in ['title','animation']:p,_,b=map_decode(bank,p);extents[name]=len(b)-1
 for label in ['world','world_house','world_dungeon']:
  p,_=rle_planes(rom,fs[label+'_background_rle'],bytearray(16384),0,4);_,n=rle_planes(rom,p,bytearray(4096),0,2);extents[label]=n
 assert max(extents.values())<0x900
 report=dict(passed=True,md_sha256=digest,version=285,bytes=len(rom),baseline_minimum_sp=before,current_minimum_sp=minimum,stack_boundary=boundary,observed_stack_margin_bytes=minimum-boundary,all_instruction_cold_frames=frame,heap_chain_valid_throughout=True,observer_matches_official_core_whole_ram_and_png=True,milestones=dict(axe=axe,first_crystal=crystal,fairy_reward=reward,final=end),deaths=0,fixed_replay_ram_bytes=65536,fixed_replay_png_exact=True,sms_fairy_flags_exact_bytes=256,sms_fairy_map_exact_bytes=1280,source_rle_scratch_extents=extents,dialogue_window_frame_mismatches=0,menu_cases=6,title_pixel_checks=40,audio_source_vectors=25644,audio_workspace_cases=28644,evidence=refs,full_game_validated=False,limits=['Stack minimum covers this NTSC cold route through first dungeon and life fairy, starting at frame14. It is not a worst-case proof for all campaign branches or hardware.','PAL/NTSC title, inventory and dialogue checks are scoped separately. The v0284 initial-dialogue tear is retained as a negative reference.','Fast streaming channels intentionally do not promise failed-channel rollback; public transactional capture still restores state/DE. Host audio equivalence and actual playable progression are not analogue waveform parity.','D2 bridge/key success belongs to the retained v0280 traces. No second crystal, complete campaign, global R/IRQ phase, whole-game physical cadence or hardware completion claim.'])
 (ROOT/'analysis/stack_release_v0285_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print({k:v for k,v in report.items() if k not in ['evidence','milestones','limits']})


if __name__=='__main__':main()
