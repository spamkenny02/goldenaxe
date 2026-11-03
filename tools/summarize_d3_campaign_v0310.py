"""Verify strict boot-to-D3 progression, ordinary boss combat and exterior return."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording, prefix_writes
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

CASES=[
 ('natural-dungeon-route/md-v0310-d3-entry01','entry'),
 ('natural-dungeon-combat/md-auto-v0310-d3-rope01','rope'),
 ('natural-dungeon-combat/md-auto-v0310-d3-switch01','switch'),
 ('natural-dungeon-combat/md-auto-v0310-d3-key01','key'),
 ('natural-dungeon-combat/md-auto-v0310-d3-approach01','approach'),
 ('natural-dungeon-combat/md-auto-v0310-d3-release01','release'),
 ('natural-dungeon-combat/md-auto-v0310-d3-boss01','boss'),
 ('natural-dungeon-combat/md-auto-v0310-d3-exit01','exit'),
]


def main():
 digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())
 assert digest=='32fe75a653d7152f7cbf873a32f2ffef14234ea190885ae8a8235f2ccd10e071'
 prior=json.loads((ROOT/'analysis/d2_campaign_v0310_report.json').read_bytes())
 assert prior['passed'] and prior['md_sha256']==digest and prior['second_crystal_and_exterior_return']
 oil=json.loads((ROOT/'analysis/oil_service_v0310_report.json').read_bytes());assert oil['passed'] and oil['md_sha256']==digest
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');stages=[];files={};reports={};assists={};previous=[];boss_writes=None
 for relative,kind in CASES:
  folder=ROOT/'validation'/relative
  cap=json.loads(evidence(folder/'capture.json'))
  report_path=folder/('route_report.json' if kind=='entry' else 'report.json')
  r=json.loads(evidence(report_path));a,writes=recording(folder,cap)
  assert cap['rom_sha256']==r['rom_sha256']==digest and cap['sram_input'] is None
  assert a['primary_state_imports']==0 and not a['boss_assistance'] and not a['health_refills']
  assert not r.get('controlled_sram_fixture',False) and not r.get('primary_state_imports',0)
  assert r['failure'] is None and not r.get('deaths',0)
  assert prefix_writes(folder,cap,True)==writes
  assert all(address==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,address,value in writes)
  assert writes[:len(previous)]==previous;previous=writes
  proof_folder=folder.with_name(folder.name+'-assisted-fixed-replay-'+str(cap['frames']))
  proof=json.loads(evidence(proof_folder/'replay_report.json'))
  assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact']
  assert not proof.get('controlled_sram_fixture',False)
  for stem,ext in [('ram','bin'),('frame','png')]:
   file=f'{stem}_{cap["frames"]:05d}.{ext}'
   assert evidence(folder/file)==evidence(proof_folder/file)
  raw=evidence(folder/f'ram_{cap["frames"]:05d}.bin')
  data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
  word=lambda n:int.from_bytes(data(n,2),'big')
  save=data('game_save_state',592);items=data('hero_items',17)
  assert save[0x1f:0x21]==bytes([128,128]) and items[8]==1
  assert word('hero_weapon_level')==word('hero_selected_item')==1
  assert word('sound_unhandled_command')==0
  if kind!='entry':assert items[13]==1
  if kind=='entry':assert r['reached_entrance'] and r['directional_probe_succeeded'] and not r['normal_continues']
  if kind=='rope':assert r['item_acquisition_passed'] and r['item_acquisition_first']['owned']==0
  if kind=='switch':assert r['contact_route_passed'] and r['contact_opened']['active_enemies'] and r['last_state']['room_flags']&0x24==0x24
  if kind=='key':assert r['new_key_verified'] and word('hero_keys')==1
  if kind=='release':assert word('hero_hurt')==0 and word('room_id')==0x1d3
  if kind in ('boss','exit'):
   assert r['unassisted_extension'] and r['new_assistance_writes']==0
   assert max(f for f,_,_ in writes)==r['guard_release_frame']==58421
   assert save[0x1f:0x28]==bytes([128]*3+[0]*6) and word('hero_max_health')==56
   if boss_writes is None:boss_writes=writes
   else:assert writes==boss_writes
   sms=data('sms_vram',16384)
   physical=folder/f'vram_{cap["frames"]:05d}.bin';registers=folder/f'vdp_regs_{cap["frames"]:05d}.bin'
   vram=evidence(physical);regs=evidence(registers);base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
   for n in range(128):
    at=base+((n//32+22)*width+n%32)*2
    assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
   original=(ROOT/'input/original.sms').read_bytes()
   for n in range(3):
    tile,off=original[0x1edc+n*2:0x1ede+n*2]
    assert sms[0x3d00+off:0x3d02+off]==bytes([tile,0x59])
   for p in [physical,registers]:files[p.relative_to(ROOT).as_posix()]=sha(evidence(p))
  stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),kind=kind,frames=cap['frames'],
                     room=word('room_id'),health=word('hero_health'),max_health=word('hero_max_health'),
                     crystals=sum(x==128 for x in save[0x1f:0x28]),rope_owned=bool(items[13]),oil_owned=True,
                     primary_state_imports=0,whole_ram_png_exact=True))
  reports[kind],assists[kind]=r,a
  for p in [folder/'capture.json',report_path,folder/'controls.json',folder/'assistance.json',
            folder/f'ram_{cap["frames"]:05d}.bin',folder/f'frame_{cap["frames"]:05d}.png',proof_folder/'replay_report.json']:
   files[p.relative_to(ROOT).as_posix()]=sha(evidence(p))
 boss=reports['boss'];out=reports['exit'];first=boss['first_intermediate_combat']
 assert first['frame']>58421 and first['health']==39 and first['hurt']==0
 assert any(e['kind']==0x69 and e['hp']==32 for e in first['actors'])
 assert boss['full_ram_prediction_matches']==boss['verified_persistent_prediction_windows'] and boss['full_ram_prediction_matches']>0 and boss['stack_only_difference_windows']==0
 assert boss['unassisted_controller_sha256']==sha(evidence(ROOT/'tools/unassisted_dungeon_continuation.py'))
 assert out['unassisted_controller_sha256']==sha(evidence(ROOT/'tools/unassisted_dungeon_continuation.py'))
 assert out['full_ram_prediction_matches']==out['verified_persistent_prediction_windows'] and out['full_ram_prediction_matches']>0 and out['stack_only_difference_windows']==0
 assert out['full_dungeon_cleared'] and out['dungeon_exit_verified'] and stages[-1]['room']==0x62
 final=assists['exit'];assert final['first_boss_combat']['frame']==first['frame']
 assert final['first_boss_entry']['frame']<first['frame'] and final['release_write_frame']<final['first_boss_entry']['frame']
 for n in ['analysis/d2_campaign_v0310_report.json','tools/summarize_d3_campaign_v0310.py',
           'tools/unassisted_dungeon_continuation.py',
           'tools/unassisted_dungeon_continuation.py','megadrive/src/main.c','input/original.sms']:
  files[n]=sha(evidence(ROOT/n))
 result=dict(passed=True,version=310,md_sha256=digest,production_rom_unchanged=True,
             cold_boot_from_new_game=True,assisted_approaches=True,boss_assistance=False,
             controlled_sram_fixture=False,primary_state_imports=0,sram_imports=0,
             three_crystals_and_exterior_return=True,guard_release_frame=58421,
             first_boss_combat=first,boss_prediction_windows=boss['full_ram_prediction_matches'],exit_prediction_windows=out['full_ram_prediction_matches'],hud_words_per_checkpoint=128,owned_crystal_markers=3,stages=stages,
             current_campaign_trace=stages[-1]['trace'],campaign_frames=stages[-1]['frames'],
             full_game_validated=False,evidence=files,
             limits=['Authorized approach hurt guards only; not an entirely unassisted campaign.',
                     'Oil is acquired by a real C7 gift before the D3 route; no resource or progression writes are added.',
                     'The actual boss is type69; type65 satellite tests remain separate. This is one NTSC path,not all alternatives.',
                     'No SRAM or state from the separate controlled palace ending enters this cold campaign.',
                     'Current cold D4 onward,optional content,global fidelity and broad current stack/hardware coverage remain unverified.'])
 (ROOT/'analysis/d3_campaign_v0310_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'))
 print('Strict v310 third crystal and ordinary exterior return verified:',stages[-1]['frames'])


if __name__=='__main__':main()
