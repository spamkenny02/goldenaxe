"""Controlled real-door teacher interactions on original SMS and native MD."""
import argparse,contextlib,ctypes as c,io,json
from run_core import ROOT,run
from extract_world import initial_room
from extract_title import rle_planes
from validate_key_door_gameplay import maps
from validate_actor_tick import PRESSES
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--trial',required=True);p.add_argument('--expect-missing',action='store_true');p.add_argument('--case');p.add_argument('--all-instructions',action='store_true');a=p.parse_args()
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');source=(ROOT/'input/original.sms').read_bytes();_,meta,_,_,arrays,_=initial_room(source);doors=json.loads((ROOT/'analysis/doors_reference.json').read_bytes())['direct_unconditional_doors'];results=[]
 cases=[dict(name='fire-intro',town=0xe6,level=0,intro=0,oil=0,hp=24,gold=0),dict(name='fire-missing-oil',town=0xe6,level=0,intro=1,oil=0,hp=24,gold=0),dict(name='fire-learn',town=0xe6,level=0,intro=1,oil=1,hp=24,gold=0),dict(name='fire-upgrade',town=0xe6,level=1,intro=1,oil=0,hp=72,gold=0),dict(name='wind-learn',town=0xa3,level=0,intro=0,oil=0,hp=24,gold=50),dict(name='wind-poor',town=0xa3,level=0,intro=1,oil=0,hp=24,gold=49),dict(name='wind-upgrade',town=0xa3,level=1,intro=1,oil=0,hp=72,gold=100),dict(name='screen-locked',town=0x2c,level=0,intro=0,oil=0,hp=71,gold=0),dict(name='screen-learn',town=0x2c,level=0,intro=0,oil=0,hp=72,gold=0),dict(name='screen-final',town=0x2c,level=1,intro=0,oil=0,hp=72,gold=0,crystals=128),dict(name='heal-learn',town=0xaa,level=0,intro=0,oil=0,hp=24,gold=0),dict(name='heal-owned',town=0xaa,level=1,intro=0,oil=0,hp=24,gold=0)]
 cases.append(dict(name='wind-decline',town=0xa3,level=0,intro=0,oil=0,hp=24,gold=100,decline=True))
 if a.case:cases=[case for case in cases if case['name']==a.case];assert cases
 for region in ['auto','pal']:
  for case in cases:
   town=case['town'];teacher=[0xe6,0xa3,0x2c,0xaa].index(town);door=next(d for d in doors if d['room']==town and d['target']==0xbf);cells=bytearray(160);rle_planes(arrays['world_room_streams'],int.from_bytes(arrays['world_room_index'][town*2:town*2+2],'little'),cells,0,1);smsmap,mdmap=maps(cells,meta);traces={}
   for tag in ['sms','md']:
    folder=ROOT/f"validation/spell-teacher-game-{a.trial}/{region}-{case['name']}-{tag}";assert not folder.exists();writes=[];rows=[];active=[];requests=[]
    values=[0]*4;values[teacher]=case['level'];flags=[0]*3;flags[0 if teacher==0 else 1]=case['intro']
    if tag=='sms':
     writes=[(3100,0xe4,bytes(values)),(3100,0xe8,bytes([case['oil']])),(3100,0xf3,bytes(flags)),(3100,0xda,bytes([case['hp']])),(3100,0xdb,b'\x07\x18'),(3100,0xdd,bytes([case['gold']])),(3100,0xcf,bytes([case.get('crystals',0)])*9),(3120,0xb9,town.to_bytes(2,'little')),(3120,0xa4,door['script_entry'].to_bytes(2,'little')),(3120,0x1c00,bytes(cells)),(3120,0x1600,smsmap),(3120,0x600,bytes(768)),(3120,0x304,b'\1'),(3120,0x301,b'\1'),(3120,0x303,b'\3'),(3120,0x30a,b'\0'),(3120,0x310,(door['y']<<8).to_bytes(2,'little')+((door['x']-1)<<8).to_bytes(2,'little')+bytes(2)+(256).to_bytes(2,'little')),(3400,0x310,(56<<8).to_bytes(2,'little')+(136<<8).to_bytes(2,'little')+bytes(4)),(3400,0x301,b'\1'),(3400,0x303,b'\3\0\0'),(3400,0x30a,b'\0')]
    else:
     writes=[(3100,sy['hero_items']+4,bytes(values)),(3100,sy['hero_items']+8,bytes([case['oil']])),(3100,sy['game_save_state']+0x43,bytes(flags)),(3100,sy['game_save_state']+0x1f,bytes([case.get('crystals',0)])*9),(3120,sy['scratch']+0x800,bytes(cells)),(3120,sy['sms_vram']+0x3800,smsmap),(3120,sy['world_new_md'],mdmap),(3120,sy['world_actor_state'],bytes(768))]
     for f,k,v in [(3100,'hero_max_health',case['hp']),(3100,'hero_magic',7),(3100,'hero_max_magic',24),(3100,'hero_gold',case['gold']),(3120,'room_id',town),(3120,'world_graphics_class',0),(3120,'hero_y',door['y']<<8),(3120,'hero_x',(door['x']-1)<<8),(3120,'hero_dy',0),(3120,'hero_dx',256),(3120,'hero_counter',1),(3120,'hero_state',1),(3120,'hero_flags',3),(3120,'hero_direction',0),(3400,'hero_y',56<<8),(3400,'hero_x',136<<8),(3400,'hero_dy',0),(3400,'hero_dx',0),(3400,'hero_state',1),(3400,'hero_flags',3),(3400,'hero_counter',0),(3400,'hero_hurt',0),(3400,'hero_direction',0)]:writes.append((f,sy[k],v.to_bytes(2,'big')))
    stack=[];heap=[];core=None;dll=None
    if tag=='md' and a.all_instructions:
     core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_stack_libretro.dll';dll=c.CDLL(str(core));dll.gaw_stack_sp.restype=c.c_uint;dll.gaw_stack_at.restype=c.c_uint;dll.gaw_stack_reset()
    def observe(f,r):
     if dll is not None:
      sp=dll.gaw_stack_sp();dll.gaw_stack_reset()
      if f>=14 and (not stack or sp<stack[-1]['sp']):stack.append(dict(frame=f,sp=sp))
      word_at=lambda address:int.from_bytes(bytes(r[((address+i)&65535)^1] for i in range(2)),'big')
      end=word_at(sy['heapEnd']+2)
      if end and f>200:
       pos=sy['_bend'];count=0
       while pos<end and count<100:
        size=word_at(pos)&65534;assert size>=2 and pos+size<=end,(f,pos,size,end);pos+=size;count+=1
       assert pos==end and word_at(pos)==0,(f,pos,end)
       if not heap or heap[-1]!=end+2:heap.append(end+2)
     if f<3400:return
     if tag=='sms':room=int.from_bytes(r[0xb9:0xbb],'little');game=r[0x1d];fields=list(r[0xe4:0xe9])+list(r[0xf3:0xf6])+[r[0xdc],r[0xdb],r[0xdd]];phase=game==22
     else:
      data=lambda n,k:bytes(r[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big');room=word('room_id');game=word('game_state');fields=list(data('hero_items',17)[4:9])+list(data('game_save_state',592)[0x43:0x46])+[word('hero_max_magic'),word('hero_magic'),word('hero_gold')];phase=word('spell_teacher_phase') if 'spell_teacher_phase' in sy else 0
     if phase and not active:active.append(f)
     if f in [3400,3600,4400,5400,5800]:rows.append(dict(frame=f,room=room,game=game,fields=fields,active=bool(phase)))
    inputs=([(200,220,0)] if tag=='sms' else [])+PRESSES[:8]+[(3400,3450,4)]+([(3500,3520,5)] if case.get('decline') else [])+[(f,f+1,8) for f in range(3600,5600,40)]
    with contextlib.redirect_stdout(io.StringIO()):run(ROOT/('input/original.sms' if tag=='sms' else 'gaw-megadrive.bin'),5800,folder,{3600,4400,5800},inputs,core=core,ram_writes=writes,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':region})
    (folder/'observations.json').write_bytes((json.dumps(rows,indent=2)+'\n').encode());assert rows[-1]['room']==0xbf and rows[-1]['game']==12,(case,tag,rows[-1]);traces[tag]=dict(rows=rows,activation=active[0] if active else None,stack=stack,heap_boundaries=heap)
    if stack:assert heap and min(v['sp'] for v in stack)>=max(heap)
   assert traces['sms']['activation'],(case,'source teacher not reached')
   if a.expect_missing:assert not traces['md']['activation']
   else:
    assert traces['md']['activation'] and traces['sms']['rows'][-1]['fields']==traces['md']['rows'][-1]['fields'],(region,case,traces)
   results.append(dict(region=region,case=case,**traces));print(region,case['name'],'observed',flush=True)
 report=dict(passed=True,md_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),source_sha256=sha(source),cases=results,missing_service_reproduced=a.expect_missing,controlled_fixtures=True,limits=['Explicit exterior room, equipment/currency/quest and pre-dialogue hero fixtures. Actual doors, service dispatch, source/native decisions, portrait/modal entry and normal button acknowledgements execute.','Final gameplay room and policy fields are checked. Exact whole framebuffer/audio/global timing and natural acquisition are not asserted.'])
 (ROOT/f'analysis/spell_teacher_game_{a.trial}_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print('passed',len(results))
if __name__=='__main__':main()
