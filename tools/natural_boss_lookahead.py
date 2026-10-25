"""Plan buttons in a separate emulator; primary game only receives normal input.

Secondary states are imported for search. A later cold fixed-input replay,
without this planner, is required before treating a route as natural evidence.
"""
import contextlib,ctypes as c,hashlib,io,json,shutil,sys
from pathlib import Path
import natural_dungeon_combat as game
from run_core import ROOT,ENV,VIDEO,AUDIO,BATCH,POLL,INPUT,Variable,Game
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha

class Secondary:
 def __init__(self,path,rom,options):
  self.dll=c.CDLL(str(path));self.buttons=();variables={};settings={k.encode():v.encode() for k,v in options.items()}
  system=str(ROOT.parents[1]/'work/libretro').encode()
  @ENV
  def environment(command,data):
   cmd=command&65535
   if cmd==3:c.cast(data,c.POINTER(c.c_bool))[0]=False;return True
   if cmd in [9,30,31]:c.cast(data,c.POINTER(c.c_char_p))[0]=system;return True
   if cmd==10:return c.cast(data,c.POINTER(c.c_uint))[0] in [0,1,2]
   if cmd==15:
    var=c.cast(data,c.POINTER(Variable)).contents
    if var.key in variables:var.value=variables[var.key];return True
    return False
   if cmd==16:
    array=c.cast(data,c.POINTER(Variable));n=0
    while array[n].key:
     value=array[n].value.split(b'; ',1)[-1].split(b'|',1)[0];variables[array[n].key]=settings.get(array[n].key,value);n+=1
    return True
   if cmd in [17,18]:c.cast(data,c.POINTER(c.c_bool))[0]=False;return True
   if cmd in [1,6,11,13,35]:return True
   if cmd==52:c.cast(data,c.POINTER(c.c_uint))[0]=0;return True
   return False
  callbacks=[environment,VIDEO(lambda *a:None),AUDIO(lambda *a:None),BATCH(lambda data,count:count),POLL(lambda:None),INPUT(lambda port,device,index,button:int(port==0 and button in self.buttons))]
  self.callbacks=callbacks
  for name,typ,cb in zip(['environment','video_refresh','audio_sample','audio_sample_batch','input_poll','input_state'],[ENV,VIDEO,AUDIO,BATCH,POLL,INPUT],callbacks):
   fn=getattr(self.dll,'retro_set_'+name);fn.argtypes=[typ];fn(cb)
  self.dll.retro_init();self.dll.retro_load_game.argtypes=[c.POINTER(Game)];self.dll.retro_load_game.restype=c.c_bool
  self.rom_buffer=c.create_string_buffer(rom.read_bytes());self.rom_path=str(rom.resolve()).encode()
  cart=Game(self.rom_path,c.cast(self.rom_buffer,c.c_void_p),len(rom.read_bytes()),None);assert self.dll.retro_load_game(c.byref(cart))
  self.dll.retro_get_memory_data.argtypes=[c.c_uint];self.dll.retro_get_memory_data.restype=c.c_void_p
  self.dll.retro_get_memory_size.argtypes=[c.c_uint];self.dll.retro_get_memory_size.restype=c.c_size_t
  self.dll.retro_serialize_size.restype=c.c_size_t;self.size=self.dll.retro_serialize_size();self.buffer=c.create_string_buffer(self.size)
  for name in ['retro_serialize','retro_unserialize']:
   fn=getattr(self.dll,name);fn.argtypes=[c.c_void_p,c.c_size_t];fn.restype=c.c_bool
  self.imports=0;self.steps=0
 def restore(self,state):
  assert len(state)==self.size;raw=c.create_string_buffer(state);assert self.dll.retro_unserialize(raw,len(state));self.imports+=1
 def snapshot(self):
  assert self.dll.retro_serialize(self.buffer,self.size);return self.buffer.raw
 def ram(self):return c.string_at(self.dll.retro_get_memory_data(2),self.dll.retro_get_memory_size(2))
 def advance(self,buttons,frames):
  self.buttons=tuple(buttons)
  for _ in range(frames):self.dll.retro_run();self.steps+=1
 def close(self):self.dll.retro_unload_game();self.dll.retro_deinit()

class Planner:
 def __init__(self,primary,secondary,sms,sy,step=8,horizon=48):
  self.primary=primary;self.secondary=secondary;self.sms=sms;self.sy=sy;self.step=step;self.horizon=horizon;self.start=0;self.schedule=[]
  primary.retro_serialize_size.restype=c.c_size_t;primary.retro_serialize.argtypes=[c.c_void_p,c.c_size_t];primary.retro_serialize.restype=c.c_bool
  self.buffer=c.create_string_buffer(secondary.size);self.state=None;self.active=False;self.frame=0;self.until=0;self.buttons=[];self.expected=None;self.expected_ram=None;self.verify_at=None;self.decisions=[];self.diagnostics=None;self.verified=0;self.full_ram_matches=0;self.stack_only=0;self.persistent_bytes=0
 def fields(self,r):
  if self.sms:
   e=r[0x600:0x630];return dict(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],health=r[0x318],x=r[0x313],y=r[0x311],kind=e[0],boss_hp=e[0x18],boss_y=e[0x11])
  data=lambda n,k:bytes(r[(self.sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big');e=data('world_actor_state',48)
  return dict(room=word('room_id'),game=word('game_state'),health=word('hero_health'),x=word('hero_x')>>8,y=word('hero_y')>>8,kind=e[0],boss_hp=e[0x18],boss_y=e[0x11])
 def observe(self,f,r):
  if self.sms:self.persistent_bytes=len(r)
  else:
   address=self.sy['heapEnd'];heap_end=int.from_bytes(bytes(r[(address+i)^1] for i in range(4)),'big')&65535
   self.persistent_bytes=heap_end+2;assert 0<self.persistent_bytes<=len(r)
  if f==self.verify_at:
   same=sha(r)==self.expected
   if not same and self.diagnostics and (self.stack_only<2 or r[:self.persistent_bytes]!=self.expected_ram[:self.persistent_bytes]):
    (self.diagnostics/f'prediction-{f}-expected.bin').write_bytes(self.expected_ram);(self.diagnostics/f'prediction-{f}-actual.bin').write_bytes(r)
   assert r[:self.persistent_bytes]==self.expected_ram[:self.persistent_bytes],('Secondary persistent RAM prediction differs',f,self.persistent_bytes)
   if same:self.full_ram_matches+=1
   else:self.stack_only+=1
   self.verified+=1;self.verify_at=None
  self.frame=f;v=self.fields(r);self.current=v;self.active=v['room']==0x144 and v['game']==12 and v['health']>0 and v['kind']==0x63 and v['boss_hp']>0
  if self.active:
   assert self.primary.retro_serialize(self.buffer,len(self.buffer));self.state=self.buffer.raw
 def score(self,r):
  v=self.fields(r)
  if not v['health']:return -1000000
  if v['room']!=0x144:return -100000
  if v['kind']!=0x63 or not v['boss_hp']:return 100000+v['health']*100
  distance=abs(v['x']-112)+max(0,abs(v['y']-v['boss_y']-8)-16)
  return v['health']*100-v['boss_hp']*15-distance*0.15
 def choose(self,f,fallback):
  if f<self.until:return list(self.schedule[f-self.start])
  if not self.active or self.state is None:return fallback
  assert self.frame==f-1,(self.frame,f)
  actions=[(),(4,),(5,),(6,),(7,),(4,8),(5,8),(6,8),(7,8),(8,)]
  candidates=[('hold-'+str(a),[a]*self.horizon) for a in actions]
  candidates += [('fresh-fire-'+str(d),[()]+[(d,8)]*(self.horizon-1)) for d in [4,5,6,7]]
  choices=[]
  for name,schedule in candidates:
   self.secondary.restore(self.state);first_ram=None
   for n,buttons in enumerate(schedule):
    self.secondary.advance(buttons,1)
    if n==self.step-1:first_ram=self.secondary.ram()
   choices.append(dict(name=name,schedule=schedule[:self.step],first_ram=first_ram,score=self.score(self.secondary.ram())))
  best=max(choices,key=lambda n:n['score']);self.schedule=best['schedule'];self.start=f;self.until=f+self.step
  self.expected_ram=best['first_ram'];self.expected=sha(self.expected_ram);self.verify_at=f+self.step-1
  self.decisions.append(dict(frame=f,action=best['name'],buttons=self.schedule,score=best['score'],primary=dict(self.current)))
  return list(self.schedule[0])

def main(core_override=None):
 official=Path(core_override) if core_override else ROOT.parents[1]/'work/libretro/genesis_plus_gx_libretro.dll';folder=ROOT/'validation/boss-lookahead-core';folder.mkdir(exist_ok=True)
 clone=folder/('planning-'+sha(official.read_bytes())[:12]+'.dll')
 if not clone.exists():shutil.copyfile(official,clone)
 assert sha(clone.read_bytes())==sha(official.read_bytes())
 original=game.run;result={};actual=[];planner=None;secondary=None
 def wrapped(*args,**kwargs):
  nonlocal planner,secondary
  rom=Path(args[0]);result['folder']=Path(args[2]);sms=rom.suffix.lower()=='.sms';sy=None if sms else symbols(ROOT/'megadrive/out/release/symbol.txt')
  primary=c.CDLL(str(official));secondary=Secondary(clone,rom,kwargs.get('core_options',{}));planner=Planner(primary,secondary,sms,sy);planner.diagnostics=result['folder']
  observer=kwargs['ram_observer'];controller=kwargs['input_provider'];cached={}
  def observe(f,r):
   observer(f,r)
   if result.get('planner_error'):raise RuntimeError(result['planner_error'])
   planner.observe(f,r)
  def choose(f):
   if cached.get('frame')==f:return cached['buttons']
   try:buttons=planner.choose(f,controller(f))
   except Exception as error:result['planner_error']=repr(error);buttons=[]
   cached.update(frame=f,buttons=buttons)
   if not actual or actual[-1]['buttons']!=buttons:actual.append(dict(frame=f,buttons=list(buttons)))
   return buttons
  kwargs['ram_observer']=observe;kwargs['input_provider']=choose;kwargs['core']=official
  return original(*args,**kwargs)
 game.run=wrapped
 try:game.main()
 finally:
  if secondary:
   secondary.close()
   if planner and result.get('folder') and result['folder'].exists():(result['folder']/'planning_partial.json').write_bytes((json.dumps(dict(verified_windows=planner.verified,decisions=planner.decisions,primary_state_imports=0,persistent_prediction_bytes=planner.persistent_bytes,full_ram_matches=planner.full_ram_matches,stack_only_difference_windows=planner.stack_only),indent=2)+'\n').encode())
 path=result['folder'];(path/'controls.json').write_bytes((json.dumps(actual,indent=2)+'\n').encode())
 report=json.loads((path/'report.json').read_bytes());report.update(secondary_snapshot_lookahead=True,planning_method="48-frame model-predictive held inputs and fresh attacks",primary_state_imports=0,secondary_state_imports=secondary.imports,secondary_frames=secondary.steps,verified_persistent_prediction_windows=planner.verified,persistent_prediction_bytes=planner.persistent_bytes,full_ram_prediction_matches=planner.full_ram_matches,stack_only_difference_windows=planner.stack_only,planning_decisions=len(planner.decisions),planner_driver_sha256=sha(Path(__file__).read_bytes()),planner_core_sha256=sha(clone.read_bytes()),cold_fixed_replay_required=True)
 (path/'report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());(path/'planning.json').write_bytes((json.dumps(planner.decisions,indent=2)+'\n').encode())
 print('Secondary lookahead:',report['planning_decisions'],'decisions;',planner.verified,'persistent-RAM prediction windows;',planner.stack_only,'reserved-stack differences;final whole-RAM cold replay still required',flush=True)

if __name__=='__main__':main()
