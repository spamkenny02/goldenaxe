"""Audit eighth crystal, unguarded exterior return and all-instruction stack."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

def main():
 refs={}
 def read(name):
  raw=evidence(ROOT/name);refs[name]=sha(raw);return raw
 def load(name):return json.loads(read(name))
 prior=load('analysis/d8_thief_v0306_report.json');assert prior['passed'] and prior['thief_key_acquired'] and not prior['eighth_boss_entered']
 digest=sha(read('versions/v0306-3a12380b/gaw-megadrive-v0306.bin'));assert digest==prior['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');read('megadrive/out/release/symbol.txt');index=load('validation/v0306-d8-thief-sources/source_index.json')
 for name,h in index.items():assert sha(read('validation/v0306-d8-thief-sources/'+name.split('/')[-1]))==h and sha((ROOT/name).read_bytes())==h
 original=read('input/original.sms');assert original[0x3234e+0x196*8]==0x6b and original[0x320ea+(0x6b-0x20)*4:0x320ee+(0x6b-0x20)*4]==bytes([80,16,2,64])
 selection=load('analysis/d8_campaign_v0306_selection.json');assert selection['stages'][-1]['kind']=='exit'
 previous=prior['ready_trace'];pc=load(previous+'/capture.json');pa,pw=recording(ROOT/previous,pc);stages=[];release=None;combat=None;damage=None;fixed=None;predictions=0;crystal=False
 for number,spec in enumerate(selection['stages']):
  kind=spec['kind'];root='validation/natural-dungeon-combat/'+spec['name'];c=load(root+'/capture.json');r=load(root+'/report.json');f=c['frames'];proof=root+f'-assisted-fixed-replay-{f}';p=load(proof+'/replay_report.json')
  assert c['rom_sha256']==r['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
  assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
  assert r['recorded_new_game_prefix']==previous.split('/')[-1] and r['prefix_end']==pc['frames'] and f>pc['frames']
  assert not r['deaths'] and not r['rom_modifications'] and not r['sram_checkpoint_injection']
  assert r['failure'] is None or kind=='partial' and r['failure']=='frame_limit'
  for name,h in p['evidence'].items():assert sha(read(root+'/'+name))==h
  for stem,ext in [('ram','bin'),('frame','png')]:assert read(root+f'/{stem}_{f:05d}.{ext}')==read(proof+f'/{stem}_{f:05d}.{ext}')
  raw=read(root+f'/ram_{f:05d}.bin');png=read(root+f'/frame_{f:05d}.png');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big');save=data('game_save_state',592)
  a,w=recording(ROOT/root,c);read(root+'/assistance.json');assert len(a['episodes'])==10 and a['episodes'][:-1]==pa['episodes'][:-1] and a['boss_room']==0x196
  assert not a['boss_assistance'] and not a['health_refills'] and not a['primary_state_imports'] and all(addr==sy['hero_hurt'] for _,addr,_ in w)
  if release is None:
   release=a['release_write_frame'];combat=a['first_boss_combat'];assert release<combat['frame'] and combat['hurt']==0
   assert w[:len(pw)]==pw and w[-1]==(release,sy['hero_hurt'],b'\x00\x00');fixed=w
  else:assert w==fixed and a['release_write_frame']==release and a['first_boss_combat']==combat
  assert all(frame<=release for frame,_,_ in w) and word('game_state')==12 and word('hero_health')>0
  items=data('hero_items',17);assert items[15]==items[16]==1 and save[0x1f:0x26]==bytes([128]*7) and save[0x27]==0
  if 'full_ram_prediction_matches' in r:
   assert r['primary_state_imports']==0 and r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows'] and r['stack_only_difference_windows']==0;predictions+=r['full_ram_prediction_matches']
  if number==0:
   plan=load(root+'/planning.json');assert plan[0]['primary']['kind']==0x6b and plan[0]['primary']['boss_hp']==80
  if kind in ['partial','crystal']:
   assert r['equip_basic_requested'] and word('hero_selected_item')==0 and word('hero_basic_level')==2 and word('hero_attack')==6
   if a['first_boss_damage'] is not None and damage is None:damage=a['first_boss_damage']
  if kind=='partial':
   assert word('hero_max_health')==88 and save[0x26] in [0,1]
   actors=data('world_actor_state',768)
   if actors[0]==0x6b:assert 0<actors[24]<80 and save[0x26]==0
   else:assert actors[0] in [7,15] and save[0x26]==1 and not any(actors[i*48]==0x6b and actors[i*48+24] for i in range(8))
  else:
   assert save[0x1f:0x28]==bytes([128]*8+[0]) and word('hero_max_health')==96
   if kind=='crystal':assert r['room_cleared'] and r['collect_gem_requested'] and word('hero_health')==96 and word('hero_magic')==word('hero_max_magic') and not word('item_reward_active');crystal=True
   elif kind=='exit':assert crystal and r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and word('room_id')==0x29 and word('world_dungeon_number')==0 and a['unassisted_extension'] and a['new_assistance_writes']==0
  stages.append(dict(trace=root,kind=kind,frames=f,room=word('room_id'),health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),keys=word('hero_keys'),gold=word('hero_gold'),prediction_windows=r.get('full_ram_prediction_matches',0),whole_ram_png_exact=True,partial_combat_only=kind=='partial'))
  previous,pc,pa,pw=root,c,a,w
 sms=data('sms_vram',16384);v=read(previous+f'/vram_{pc["frames"]:05d}.bin');regs=read(previous+f'/vdp_regs_{pc["frames"]:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
 for n in range(128):
  at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(v[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
 for n in range(8):
  tile,offset=original[0x1edc+n*2:0x1ede+n*2];assert sms[0x3d00+offset:0x3d02+offset]==bytes([tile,0x59])
 stack_root='validation/stack-v0306-d8-all';stack=load(stack_root+'/stack_report.json');assert stack['md_sha256']==digest and stack['frames']==pc['frames'] and stack['all_instructions'] and stack['logged_assistance_replayed'] and not stack['invalid_heap_examples']
 margin=stack['minimum_instruction_sp']-max(row['end']+2 for row in stack['heap_changes']);assert margin>0
 assert read(stack_root+f'/ram_{pc["frames"]:05d}.bin')==raw and read(stack_root+f'/frame_{pc["frames"]:05d}.png')==png
 read('tools/summarize_d8_campaign_v0306.py')
 result=dict(passed=True,version=306,md_sha256=digest,production_rom_unchanged=True,stages=stages,current_campaign_trace=previous,campaign_frames=pc['frames'],eighth_crystal_and_exterior_exit=True,main_boss_assistance=False,guard_release_frame=release,first_boss_combat=combat,first_boss_damage=damage,guard_release_lead_frames=combat['frame']-release,full_ram_prediction_windows=predictions,observed_instruction_stack_margin_bytes=margin,final_hud_words_exact=128,source_crystal_markers_exact=8,source_boss_stats='50100240',thief_key_owned=True,full_game_validated=False,evidence=refs,limits=['The approach guard is released before main196/6B and never resumes during combat,crystal collection or exit. Intermediate7A was separately verified without assistance. No resources,actors,progression or SRAM state are imported.','A partial checkpoint is not crystal collection. Only the crystal checkpoint proves eight markers128 and the real health/MP refill.','Cold RAM/PNG equality and stack integrity do not prove whole-source RNG,audiovisual fidelity,ninth dungeon,ending,saves or hardware behavior.'])
 (ROOT/'analysis/d8_campaign_v0306_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('D8 crystal and exterior return verified; stack margin',margin)
if __name__=='__main__':main()
