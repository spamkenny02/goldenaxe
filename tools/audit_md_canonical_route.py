"""Read-only milestones of the filmed canonical MD route, with exact final witness."""
import json,hashlib
from pathlib import Path
import validate_rc_campaign as base
from run_core import ROOT
from validate_playable_sprite_limit import symbols

original_run=base.run;sy=symbols(ROOT/'megadrive/out/release/symbol.txt');entries=[];events=[];bosses=[];previous=None;last_room=None;boss_previous={}

def run(*args,**kwargs):
 inherited=kwargs['ram_observer']
 def observe(frame,raw):
  global previous,last_room,boss_previous
  inherited(frame,raw)
  word=lambda n:raw[sy[n]]|raw[sy[n]+1]<<8
  data=lambda n,k,off=0:bytes(raw[(sy[n]+off+i)^1] for i in range(k))
  room=word('room_id');graphics=word('world_graphics_class');game=word('game_state')
  items=data('hero_items',17);crystals=data('game_save_state',9,0x1f)
  state=dict(room=room,graphics=graphics,game=game,dungeon=word('world_dungeon_number'),health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),max_magic=word('hero_max_magic'),gold=word('hero_gold'),keys=word('hero_keys'),basic=word('hero_basic_level'),weapon=word('hero_weapon_level'),armor=word('hero_armor_level'),shield=word('hero_shield_level'),items_hex=items.hex(),crystals_hex=crystals.hex(),room_flags=raw[(sy['game_save_state']+0x50+(room&255))^1])
  signature=tuple(state.values())
  if previous!=signature:events.append(dict(frame=frame,**state));previous=signature
  ready=game==12 and word('hero_state')==1 and not word('resume_phase') and not raw[sy['door_transition_loading']^1]
  if ready and (room,graphics)!=last_room:
   entries.append(dict(frame=frame,x=word('hero_x')>>8,y=word('hero_y')>>8,**state));last_room=room,graphics
  current={}
  if graphics==2:
   for slot in range(16):
    at=sy['world_actor_state']+slot*48;kind=raw[at^1];hp=raw[(at+24)^1]
    if 0x63<=kind<=0x6d or 0x78<=kind<=0x7c:
     key=room,slot,kind;current[key]=hp
     if boss_previous.get(key)!=hp:bosses.append(dict(frame=frame,room=room,slot=slot,kind=kind,hp=hp,hero_health=state['health'],hurt_guard=word('hero_hurt')))
  boss_previous=current
 kwargs['ram_observer']=observe
 result=original_run(*args,**kwargs)
 out=Path(args[2]);end=args[1];reference=ROOT/'validation/rc1-campaign-ntsc01'
 assert kwargs['core_options']=={'genesis_plus_gx_region_detect':'auto'}
 for stem,ext in [('ram','bin'),('frame','png')]:assert (out/f'{stem}_{end:05d}.{ext}').read_bytes()==(reference/f'{stem}_{end:05d}.{ext}').read_bytes()
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 movie=json.loads((ROOT/'videos/v0322-rc1/report.json').read_bytes());assert movie['passed'] and movie['rom_sha256']==sha(Path(args[0])) and movie['full_audio_decoded'] and movie['full_video_decoded']
 report=dict(passed=True,rom_sha256=sha(Path(args[0])),route_csv_sha256=json.loads((ROOT/'validation/rc1-campaign-ntsc01/report.json').read_bytes())['route_csv_sha256'],frames=end,final_whole_ram_and_png_match_film_campaign=True,video_report='videos/v0322-rc1/report.json',video_report_sha256=sha(ROOT/'videos/v0322-rc1/report.json'),movie_sha256=movie['sha256'],independent_cold_boot=True,state_imports=0,emulated_frames_skipped=0,entries=entries,events=events,boss_hp_events=bosses,all_npcs_complete=False,scope='Read-only native milestones of the exact fixed input campaign already filmed on V322. Fully restored playable room entries, real inventory/currency/flag changes and actual boss HP events are recorded. Presence in this ledger alone does not certify every SMS NPC dialogue variant or physical-pixel fidelity.')
 (ROOT/'analysis/md_canonical_route_milestones.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
 return result

base.run=run
if __name__=='__main__':base.main()
