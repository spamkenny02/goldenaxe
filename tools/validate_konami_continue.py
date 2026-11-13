"""Load a realV322 SRAM normally, with options off and with title-menu cheats on."""
import argparse,json,hashlib
from run_core import ROOT,run
from validate_konami_menu import inputs
from validate_playable_sprite_limit import symbols
from natural_dungeon_combat import walk

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',default='validation/konami04/candidate.bin');p.add_argument('--label',default='konami04');p.add_argument('--offset-ntsc',type=int,default=0);p.add_argument('--offset-pal',type=int,default=0);a=p.parse_args();rom=ROOT/a.rom;source=ROOT/'testkit/fixtures/continue';sr=json.loads((source/'report.json').read_bytes());sram=source/'game-written.srm';assert sr['passed'] and sr['game_written_save'] and hashlib.sha256(sram.read_bytes()).hexdigest()==sr['sram_sha256'];payload=(source/'serialized-payload.bin').read_bytes();sy=symbols(ROOT/'megadrive/out/release/symbol.txt');results=[]
 fields={'hero_health':0x29,'hero_max_health':0x2a,'hero_magic':0x2b,'hero_max_magic':0x2c,'hero_gold':0x2d,'hero_keys':0x2e,'hero_selected_item':0x2f,'hero_basic_level':0x30,'hero_weapon_level':0x31,'hero_armor_level':0x41,'hero_shield_level':0x42};target=int.from_bytes(payload[0x12:0x14],'little')
 for region in ['ntsc','pal']:
  offset=a.offset_pal if region=='pal' else a.offset_ntsc
  for enabled in [False,True]:
   state={};ready=None;moved=None;point=None;direction=None;observed=0;captures=set()
   def observe(f,r):
    nonlocal ready,moved,point,observed
    observed=f;w=lambda n:int.from_bytes(r[sy[n]:sy[n]+2],'little');data=lambda n,k:bytes(r[(sy[n]+i)^1]for i in range(k));state.update(game=w('game_state'),room=w('room_id'),hero=w('hero_state'),counter=w('hero_counter'),x=w('hero_x')>>8,y=w('hero_y')>>8,health=w('hero_health'),gold=w('hero_gold'),tilemap=data('sms_vram',16384)[0x3800:0x3e00]);assert w('sound_unhandled_command')==0
    if ready is None and state['game']==12 and state['room']==target and state['hero']==1:
     if enabled and (state['health']!=w('hero_max_health') or state['gold']!=255):return
     for name,offset in fields.items():
      expected=payload[0x2a] if enabled and name=='hero_health' else 255 if enabled and name=='hero_gold' else payload[offset];assert w(name)==expected,(region,enabled,name,w(name),expected)
     assert data('hero_items',17)==payload[0x30:0x41] and data('game_save_state',592)[0x1f:0x28]==payload[0x1f:0x28]
     assert bool(r[0xe4b0])==bool(r[0xe4b1])==enabled;ready=f;point=(state['x'],state['y']);captures.add(f+1)
    if ready and moved is None and state['room']==target and state['hero']==1 and (state['x'],state['y'])!=point:moved=f;captures.add(f+100)
   def choose(f):
    nonlocal direction
    if ready is None:return []
    if moved or state['game']!=12:return []
    if state['counter']:return [4+direction] if direction is not None else []
    if direction is None:
     for d,(dx,dy)in enumerate([(0,-8),(0,8),(-8,0),(8,0)]):
      q=(point[0]+dx,point[1]+dy);route=walk(state['tilemap'],point,lambda p:p==q)
      if route and len(route)==1:direction=route[0];break
    return [4+direction] if direction is not None else []
   presses=[p for p in inputs('both') if p[0]<=1203]+[(1350,1360,8),(1600,1610,8)] if enabled else [(200,220,0),(920,935,0),(1050,1065,8),(1300,1310,8)]
   presses=[(f+offset,t+offset,b) for f,t,b in presses]
   folder=ROOT/f'validation/{a.label}-continue-{region}-{int(enabled)}';run(rom,5000+offset,folder,captures,presses,skip_intro=False,sram_in=sram,ram_observer=observe,input_provider=choose,stop_when=lambda:moved is not None and observed>=moved+100,core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'});assert ready and moved
   results.append(dict(passed=True,region=region,cheats_enabled=enabled,normal_continue_ready_frame=ready,normal_movement_frame=moved,stats_items_crystals_checked=True,external_ram_writes=0,sram_imports=1,source_sram_sha256=sr['sram_sha256']));print('CONTINUE PASSED',region,enabled,flush=True)
 (ROOT/('analysis/'+('konami_continue_v0323_report.json' if a.label=='konami04' else a.label+'-continue-report.json'))).write_bytes((json.dumps(dict(passed=True,md_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),cases=results),indent=2)+'\n').encode())
if __name__=='__main__':main()
