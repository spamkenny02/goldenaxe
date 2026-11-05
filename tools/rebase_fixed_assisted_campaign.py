"""Cold replay across a native rebuild with relocated approach-only guard writes.

Never imports RAM/state. Rejects live boss protection and timing/resource drift.
"""
import argparse,contextlib,copy,io,json,subprocess,sys
from pathlib import Path
from run_core import ROOT,run,FrameWrites
from assisted_prefix import prefix_writes,recording,episodes
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha


def main():
 p=argparse.ArgumentParser();p.add_argument('--trace',required=True);p.add_argument('--old-symbols',required=True);p.add_argument('--trial',required=True);p.add_argument('--end-frame',type=int);p.add_argument('--source-workspace',type=Path,default=ROOT);p.add_argument('--completed-dungeon-exit',action='store_true');a=p.parse_args()
 source_root=a.source_workspace.resolve();source=(source_root/'validation'/a.trace).resolve();assert source.is_relative_to(source_root/'validation')
 cap=json.loads((source/'capture.json').read_bytes());controls=json.loads((source/'controls.json').read_bytes())
 import assisted_prefix
 previous_root=assisted_prefix.ROOT
 try:
  assisted_prefix.ROOT=source_root
  oldassist,oldwrites=recording(source,cap);prefix_writes(source,cap,True)
 finally:assisted_prefix.ROOT=previous_root
 if a.completed_dungeon_exit:
  old_report=json.loads((source/'report.json').read_bytes())
  assert not a.end_frame and old_report['full_dungeon_cleared'] and old_report['dungeon_exit_verified'] and old_report['failure'] is None and not old_report['deaths']
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');oldsy=symbols(ROOT/a.old_symbols)
 assert all(address==oldsy['hero_hurt'] for _,address,_ in oldwrites)
 writes=FrameWrites((f,sy['hero_hurt'],data) for f,_,data in oldwrites)
 out=ROOT/'validation/natural-dungeon-combat'/a.trial;assert not out.exists()
 end=a.end_frame or cap['frames'];assert 0<end<=cap['frames']
 oldassist=copy.deepcopy(oldassist);oldassist['episodes']=[e for e in episodes(oldassist,cap) if e['activation_after_frame']<end]
 oldassist['episodes'][-1]['end_frame']=end+1
 for e in oldassist['episodes']:
  for k in ['first_boss_entry','first_boss_combat','first_boss_damage']:
   if e.get(k) and e[k]['frame']>end:e[k]=None
  if e.get('release_write_frame') and e['release_write_frame']>end:e['release_write_frame']=None
 for k in ['activation_after_frame','boss_room','first_boss_entry','release_write_frame','first_boss_combat','first_boss_damage']:oldassist[k]=oldassist['episodes'][-1][k]
 writes=FrameWrites((f,sy['hero_hurt'],data) for f,_,data in oldwrites if f<=end)
 eps=episodes(oldassist,dict(frames=end));checkframes={e['first_boss_combat']['frame']:e for e in eps if e['first_boss_combat']}
 captures={end}|{f+1 for f in checkframes};presses=[(a,min(b,end),k) for a,b,k in cap['presses'] if a<=end]
 controls=[r for r in controls if r['frame']<=end]
 if a.end_frame:
  entries=json.loads((ROOT/'versions/index.json').read_bytes());entry=next(e for e in entries if e['sha256']==cap['rom_sha256']);baseline=out.with_name(out.name+'-historical-reference')
  oldpresses=list(presses)
  for i,row in enumerate(controls):
   stop=controls[i+1]['frame']-1 if i+1<len(controls) else end
   oldpresses.extend((row['frame'],min(stop,end),key) for key in row['buttons'])
  # Each cartridge must start in a fresh core process: retro_deinit does not
  # clear all inactive native RAM, so sequential ROMs contaminate stack tails.
  recipe=out.with_name(out.name+'-reference-recipe.json');recipe.parent.mkdir(parents=True,exist_ok=True)
  recipe.write_bytes((json.dumps(dict(rom=str(ROOT/'versions'/entry['rom']),frames=end,folder=str(baseline),presses=oldpresses,writes=[(f,address,data.hex()) for f,address,data in oldwrites if f<=end],options=cap['core_options']))+'\n').encode())
  code="import sys,json;sys.path.insert(0,'tools');from run_core import run,FrameWrites;from pathlib import Path;r=json.loads(Path(sys.argv[1]).read_bytes());run(Path(r['rom']),r['frames'],Path(r['folder']),{r['frames']},r['presses'],ram_writes=FrameWrites((f,a,bytes.fromhex(v)) for f,a,v in r['writes']),skip_intro=False,core_options=r['options'])"
  subprocess.run([sys.executable,'-c',code,str(recipe)],cwd=ROOT,check=True,capture_output=True)
 for i,row in enumerate(controls):
  stop=controls[i+1]['frame']-1 if i+1<len(controls) else end
  presses.extend((row['frame'],min(stop,end),key) for key in row['buttons'] if row['frame']<=end)
 observations=[];failure=None;observed=0;checked=[];last={};deaths=0;previous_game=None
 def observe(f,raw):
  nonlocal failure,observed,last,deaths,previous_game
  observed=f
  data=lambda name,n:bytes(raw[(sy[name]+i)^1] for i in range(n));w=lambda name:int.from_bytes(data(name,2),'big')
  room=w('room_id');game=w('game_state');hurt=w('hero_hurt')
  if game==20 and previous_game!=20:deaths+=1
  previous_game=game
  if game==12 and hurt>128:
   actors=data('world_actor_state',768)
   live=[actors[n] for n in range(0,768,48) if actors[n] in list(range(0x63,0x6e))+list(range(0x78,0x7d)) and actors[n+3]&2]
   if live:failure=dict(reason='guard_over_live_boss',frame=f,room=room,kinds=live)
  if f in checkframes:
   e=checkframes[f];passed=room==e['boss_room'] and game==12 and hurt==0 and w('hero_health')==e['first_boss_combat']['health']
   checked.append(dict(frame=f,room=room,hurt=hurt,passed=passed))
   if not passed:failure=dict(reason='historical_boss_checkpoint_drift',frame=f,room=room,game=game,hurt=hurt)
  if f%10000==0 or f==end or failure:
   last=dict(frame=f,room=room,game=game,hero=w('hero_state'),x=w('hero_x')>>8,y=w('hero_y')>>8,health=w('hero_health'),max_health=w('hero_max_health'),magic=w('hero_magic'),max_magic=w('hero_max_magic'),gold=w('hero_gold'),keys=w('hero_keys'),crystals=list(data('game_save_state',592)[0x1f:0x28]),dungeon=w('world_dungeon_number'),audio_error=w('sound_unhandled_command'))
   observations.append(last);print(last,flush=True)
 with contextlib.redirect_stdout(io.StringIO()):
  run(ROOT/'gaw-megadrive.bin',end,out,captures,presses,ram_writes=writes,ram_observer=observe,stop_when=lambda:failure is not None,skip_intro=False,core_options=cap['core_options'])
 report=dict(passed=False,failure=failure,frames=observed,last_state=last,checked_bosses=checked,md_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),source_trace=a.trace,source_workspace=str(source_root),natural_campaign_proof=False,ram_injections=True,boss_assistance=False,deaths=deaths)
 if not failure and observed==end:
  before=(baseline/f'ram_{end:05d}.bin').read_bytes() if a.end_frame else evidence(source/f'ram_{end:05d}.bin');after=(out/f'ram_{end:05d}.bin').read_bytes()
  fields={'game_save_state':592,'hero_items':17,**{n:2 for n in ['room_id','game_state','hero_state','hero_x','hero_y','hero_health','hero_max_health','hero_magic','hero_max_magic','hero_gold','hero_keys','hero_weapon_level','hero_selected_item','world_dungeon_number']}}
  mismatch=[]
  for name,n in fields.items():
   old=bytes(before[(oldsy[name]+i)^1] for i in range(n));new=bytes(after[(sy[name]+i)^1] for i in range(n))
   if old!=new:mismatch.append(name)
  report.update(passed=not mismatch and len(checked)==len(checkframes),failure='terminal_gameplay_drift' if mismatch else None,terminal_field_mismatches=mismatch,terminal_png_exact=(out/f'frame_{end:05d}.png').read_bytes()==((baseline/f'frame_{end:05d}.png').read_bytes() if a.end_frame else evidence(source/f'frame_{end:05d}.png')))
 if report['passed']:
  if a.completed_dungeon_exit:
   assert report['terminal_png_exact'] and not deaths and last['room']<256 and last['game']==12 and last['health']>0 and last['dungeon']==0
   report.update(full_dungeon_cleared=True,dungeon_exit_verified=True)
  assist=copy.deepcopy(oldassist);assist['historical_trace']=a.trace;assist['writes']=[dict(frame=f,address=address,data_hex=value.hex()) for f,address,value in writes]
  (out/'assistance.json').write_bytes((json.dumps(assist,indent=2)+'\n').encode());(out/'controls.json').write_bytes((json.dumps(controls,indent=2)+'\n').encode())
  recording(out,json.loads((out/'capture.json').read_bytes()))
  # Compatible completed checkpoint; canonical independent replay still required.
  report.update(room_cleared=False if oldassist['first_boss_combat'] is None else True,checkpoint_verified=True,approach_only=oldassist['first_boss_combat'] is None,rom_sha256=report['md_sha256'],assisted_route=True)
 for name,value in [('report',report),('rebase_observations',observations)]: (out/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
 print(json.dumps(report,indent=2))

if __name__=='__main__':main()
