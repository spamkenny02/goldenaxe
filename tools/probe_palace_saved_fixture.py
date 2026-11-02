"""Controlled late-game Continue fixture derived from the verified v306 campaign.

This synthesizes a save payload; it is NOT a game-written save or a natural
campaign proof. It is solely for integration tests of the unfinished palace.
"""
import contextlib,io,json,sys
from pathlib import Path
from run_core import ROOT,run
from validate_playable_sprite_limit import symbols
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha


def main():
 trial=sys.argv[1];folder=ROOT/f'validation/palace-save-fixture-{trial}';assert not folder.exists();folder.mkdir()
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');oldsy=symbols(ROOT/'validation/v0306-d9-navigation-sources/symbol.txt')
 source=ROOT/'validation/natural-dungeon-combat/md-auto-v0306-d9-exit01/ram_270242.bin';raw=evidence(source)
 olddata=lambda n,k:bytes(raw[(oldsy[n]+i)^1] for i in range(k));old=lambda n:int.from_bytes(olddata(n,2),'big')
 save=bytearray(olddata('game_save_state',592));assert save[0x1f:0x28]==bytes([128]*9)
 save[:9]=bytes(9);name=olddata('character_name',9).split(b'\0')[0];assert 1<=len(name)<=8;save[:len(name)]=name
 def word(offset,value):save[offset:offset+2]=value.to_bytes(2,'little')
 word(9,old('room_id'));word(11,old('house_return_room'));save[13]=old('house_return_y')>>8;save[14]=old('house_return_x')>>8
 word(16,old('save_checkpoint_room'));word(18,old('house_return_room'));save[0x16]=old('hero_fire_charge')
 for offset,key in [(0x29,'hero_health'),(0x2a,'hero_max_health'),(0x2b,'hero_magic'),(0x2c,'hero_max_magic'),(0x2d,'hero_gold'),(0x2e,'hero_keys'),(0x2f,'hero_selected_item')]:save[offset]=old(key)
 save[0x30:0x41]=olddata('hero_items',17);save[0x30]=old('hero_basic_level');save[0x31]=old('hero_weapon_level');save[0x41]=old('hero_armor_level');save[0x42]=old('hero_shield_level')
 logical=bytearray([255]*8192);logical[0x30]=1;logical[0x400:0x650]=save
 physical=bytearray([255]*65536);physical[1:16384:2]=logical;sram=folder/'controlled-derived.srm';sram.write_bytes(physical)
 observations=[];first=None;saw_reset=False;captures={1900,2000,2200,2400}
 def observe(frame,ram):
  nonlocal first,saw_reset
  if frame<900:return
  data=lambda n,k:bytes(ram[(sy[n]+i)^1] for i in range(k));w=lambda n:int.from_bytes(data(n,2),'big')
  current=dict(frame=frame,game=w('game_state'),room=w('room_id'),hero=w('hero_state'),health=w('hero_health'),max_health=w('hero_max_health'),magic=w('hero_magic'),max_magic=w('hero_max_magic'),gold=w('hero_gold'),keys=w('hero_keys'),x=w('hero_x')>>8,y=w('hero_y')>>8,selected=w('hero_selected_item'),weapon=w('hero_weapon_level'),save_phase=w('save_service_phase'),crystals=list(data('game_save_state',592)[0x1f:0x28]),items=list(data('hero_items',17)))
  if not observations or any(current[n]!=observations[-1][n] for n in ['game','room','hero','save_phase','health']):observations.append(current);captures.add(frame+1)
  if current['room']==old('house_return_room') and current['hero']==0:saw_reset=True
  if saw_reset and current['game']==12 and current['room']==old('house_return_room') and current['hero']==1 and not current['save_phase'] and first is None:first=current
 inputs=[(200,220,0),(920,935,0),(1000,1005,5),(1050,1065,8),(1300,1310,8)]
 with contextlib.redirect_stdout(io.StringIO()):run(ROOT/'gaw-megadrive.bin',2400,folder/'boot',captures,inputs,sram_in=sram,ram_observer=observe,skip_intro=False)
 passed=first is not None and first['health']==old('hero_health') and first['max_health']==old('hero_max_health') and first['magic']==old('hero_magic') and first['gold']==old('hero_gold') and first['keys']==old('hero_keys') and first['crystals']==[128]*9 and first['weapon']==old('hero_weapon_level')
 report=dict(passed=passed,md_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),controlled_sram_fixture=True,game_written_save=False,natural_campaign_proof=False,source_ram=source.relative_to(ROOT).as_posix(),source_ram_sha256=sha(raw),sram_sha256=sha(physical),first_playable=first,observations=observations,scope='Synthetic source-layout Continue record assembled from actual nine-crystal v306 RAM. Controlled integration fixture only; no current-ROM whole-campaign claim.')
 (ROOT/f'analysis/palace_save_fixture_{trial}_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print('Continue controlled fixture',passed,first)
 assert passed

if __name__=='__main__':main()
