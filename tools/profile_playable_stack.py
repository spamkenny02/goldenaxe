"""Read-only stack observations and allocator-chain checks during cold input replay.

Configured PC samples bound observed depth, not every-instruction depth. Never
write a canary into game memory: allocator headers are checked in place.
"""
import argparse, contextlib, ctypes as c, io, json, re, subprocess
from run_core import ROOT, run
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import prefix_writes


def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--trace',required=True);p.add_argument('--frames',type=int);p.add_argument('--build-dir');p.add_argument('--all-instructions',action='store_true');p.add_argument('--logged-assistance',action='store_true',help='Replay only verified,logged approach assistance');a=p.parse_args()
 folder=ROOT/'validation'/a.tag;assert not folder.exists();folder.mkdir(parents=True)
 build=ROOT/a.build_dir if a.build_dir else ROOT/'megadrive/out/release';rom=build/'rom.bin'
 for name in ['rom.bin','rom.out','symbol.txt']:(folder/name).write_bytes((build/name).read_bytes())
 sy={m[2]:int(m[1],16) for line in (build/'symbol.txt').read_text().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
 ram_sy={name.split('.lto_priv.')[0]:address for name,address in sy.items()}
 watched={sy[n]:n for n in ['memset','memcpy'] if n in sy}
 for name,pc in sy.items():
  if not name.startswith(('source_audio_reader_stream','prepare_world_sms_sprite_overflow','world_vint')):continue
  dump=subprocess.check_output([str(ROOT.parents[1]/'work/sgdk/bin/objdump.exe'),'-d','--disassemble='+name,str(build/'rom.out')],text=True)
  (folder/(name+'.asm')).write_bytes(dump.encode())
  instructions=[int(m[1],16) for line in dump.splitlines() if (m:=re.match(r'\s*([0-9a-fA-F]+):\s+[0-9a-fA-F]',line))]
  for offset in [0,2,4]:
   if len(instructions)>offset:watched[instructions[offset]]=name+':instruction'+str(offset)
 assert len(watched)<=32
 core=ROOT.parents[1]/('work/genesis-plus-gx/genesis_plus_gx_stack_libretro.dll' if a.all_instructions else 'work/genesis-plus-gx/genesis_plus_gx_clock_libretro.dll');dll=c.CDLL(str(core))
 if a.all_instructions:
  dll.gaw_stack_sp.restype=c.c_uint;dll.gaw_stack_at.restype=c.c_uint;dll.gaw_stack_reset()
 dll.gaw_md_config.argtypes=[c.c_uint,c.POINTER(c.c_uint)];dll.gaw_md_event_count.restype=c.c_uint;dll.gaw_md_event_data.restype=c.POINTER(c.c_uint)
 pcs=(c.c_uint*len(watched))(*watched);dll.gaw_md_config(len(watched),pcs)
 source=ROOT/'validation'/a.trace;capture=json.loads(evidence(source/'capture.json'));controls=json.loads(evidence(source/'controls.json'));end=a.frames or capture['frames'];writes=prefix_writes(source,capture,a.logged_assistance)
 if writes:assert sha(rom.read_bytes())==capture['rom_sha256'],'Logged assistance uses build-specific RAM addresses and requires the exact recorded ROM'
 presses=[(x,min(y,end),b) for x,y,b in capture['presses'] if x<=end]
 for i,row in enumerate(controls):
  stop=min(end,controls[i+1]['frame']-1 if i+1<len(controls) else end)
  presses.extend((row['frame'],stop,b) for b in row['buttons'] if row['frame']<=end)
 minima={};heap_changes=[];previous_heap=None;observed=0;error=[];instruction_minima=[];milestones=[];last_game=None
 def observe(f,r):
  nonlocal previous_heap,observed,last_game
  count=dll.gaw_md_event_count();assert count<8192
  data=dll.gaw_md_event_data()
  for n in range(count):
   pc,cycles,sp=[int(data[n*3+j]) for j in range(3)];sp&=65535;observed+=1
   label=watched[pc]
   if label not in minima or sp<minima[label]['sp']:minima[label]=dict(frame=f,sp=sp,pc=pc,cycles=cycles)
  dll.gaw_md_config(len(watched),pcs)
  if a.all_instructions:
   sp=dll.gaw_stack_sp()
   if f>=14 and (not instruction_minima or sp<instruction_minima[-1]['sp']):instruction_minima.append(dict(frame=f,sp=sp,pc=dll.gaw_stack_at()))
   dll.gaw_stack_reset()
  word=lambda addr:int.from_bytes(bytes(r[((addr+i)&65535)^1] for i in range(2)),'big')
  names=['room_id','game_state','hero_weapon_level','hero_selected_item','hero_max_health','hero_health','world_dungeon_number','sound_unhandled_command']
  game={name:word(ram_sy[name]) for name in names};game['first_crystal']=r[((ram_sy['game_save_state']+0x1f)&65535)^1]
  key=tuple(game.values())
  if f>=200 and key!=last_game:milestones.append(dict(frame=f,**game));last_game=key
  heapend=word(sy['heapEnd']+2)
  if not heapend:return
  pos=sy['_bend']&65535;chain=[];valid=True
  while pos<=heapend and len(chain)<100:
   header=word(pos);chain.append([pos,header])
   if not header:valid=pos==heapend;break
   size=header&65534
   if size<2 or pos+size>heapend:valid=False;break
   pos+=size
  else:valid=False
  signature=(heapend,valid,tuple(map(tuple,chain)))
  if signature!=previous_heap:
   heap_changes.append(dict(frame=f,end=heapend,valid=valid,chain=chain));previous_heap=signature
  if f>200 and not valid and len(error)<8:error.append(dict(frame=f,end=heapend,chain=chain))
 with contextlib.redirect_stdout(io.StringIO()):run(rom,end,folder,{end},presses,skip_intro=False,core=core,ram_writes=writes,ram_observer=observe,core_options=capture['core_options'])
 sampled_minimum=min(v['sp'] for v in minima.values())
 instruction_minimum=min((v['sp'] for v in instruction_minima),default=None)
 minimum=min(sampled_minimum,instruction_minimum) if instruction_minimum is not None else sampled_minimum
 result=dict(md_sha256=sha(rom.read_bytes()),rom_sha256=sha(rom.read_bytes()),core_sha256=sha(core.read_bytes()),trace=a.trace,frames=end,observed_entries=observed,minimum_sp=minimum,minimum_sampled_sp=sampled_minimum,minimum_instruction_sp=instruction_minimum,minima=minima,all_instructions=a.all_instructions,instruction_minima=instruction_minima,heap_changes=heap_changes,invalid_heap_examples=error,gameplay_milestones=milestones,read_only=True,ram_injections=bool(writes),logged_assistance_replayed=bool(writes),limits=['Selected entries bound depth only; when all_instructions is true the additional observer records SP before each normal m68k_run instruction, starting at frame14 after hardware initialization. Scope is this recorded route, not every campaign path. Heap validity uses the SGDK block chain, not arbitrary free-byte equality. All inputs replay from cold boot.'])
 (folder/'stack_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps({k:v for k,v in result.items() if k!='heap_changes'},indent=2))


if __name__=='__main__':main()
