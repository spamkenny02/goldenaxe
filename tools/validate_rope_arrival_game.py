"""Cross actual exterior cliffs in the SMS and native gameplay loops.

One explicit starting fixture supplies the room, rope, position and clear actors.
Thereafter ordinary vertical input invokes deployment and room preparation.
"""
import argparse,contextlib,io,json
from run_core import ROOT,run
from natural_dungeon_route import World
from extract_title import rle_planes
from validate_key_door_gameplay import maps
from validate_playable_sprite_limit import symbols
from validate_actor_tick import PRESSES
from archive_lossless_evidence import sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--trial',required=True);p.add_argument('--rom');p.add_argument('--symbols');p.add_argument('--expect-missing',action='store_true');a=p.parse_args()
 rom=ROOT/a.rom if a.rom else ROOT/'gaw-megadrive.bin';sy=symbols(ROOT/a.symbols if a.symbols else ROOT/'megadrive/out/release/symbol.txt');world=World();results=[]
 for region in ['auto','pal']:
  for direction,room,y,target in [(0,0xb2,40,0xa2),(1,0xa2,144,0xb2)]:
   traces={}
   for tag in ['sms','md']:
    folder=ROOT/f'validation/rope-arrival-game-{a.trial}/{region}-{direction}-{tag}';assert not folder.exists();pending=[];rows=[];arrival=[];captures={3100,3450}
    def data(r,name,n):return bytes(r[(sy[name]+i)^1] for i in range(n))
    def observe(f,r):
     if f==3100:
      cells=bytearray(160);pointer=int.from_bytes(world.arrays['world_room_index'][room*2:room*2+2],'little');rle_planes(world.arrays['world_room_streams'],pointer,cells,0,1);m=maps(cells,world.meta)[0]+bytes(256)
      if tag=='sms':
       pending[:]=[(3101,0xb9,room.to_bytes(2,'little')),(3101,0x40,b'\0'),(3101,0x41,b'\0'),(3101,0x1c00,bytes(cells)),(3101,0x1600,m),(3101,0x600,bytes(768)),(3101,0x310,bytes([0,y,0,120,0,0,0,0])),(3101,0x301,b'\1'),(3101,0x303,b'\3\0\0'),(3101,0x30a,bytes([direction,0])),(3101,0x68,b'\0'),(3101,0x98,bytes(4)),(3101,0xed,b'\1'),(3101,0xee,b'\0')]
      else:
       values=dict(room_id=room,world_graphics_class=0,hero_terrain_context=0,hero_x=120<<8,hero_y=y<<8,hero_dx=0,hero_dy=0,hero_state=1,hero_flags=3,hero_hurt=0,hero_counter=0,hero_direction=direction,hero_animation=0,hero_pending=0,hero_attack_speed=0)
       pending[:]=[(3101,sy[k],v.to_bytes(2,'big')) for k,v in values.items()]+[(3101,sy['scratch']+0x800,bytes(cells)),(3101,sy['sms_vram']+0x3800,m),(3101,sy['world_actor_state'],bytes(768)),(3101,sy['magic_rope_work'],bytes(4)),(3101,sy['hero_items']+13,b'\1')]
     if f<3101:return
     if tag=='sms':
      state=dict(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],x=r[0x313],y=r[0x311],terrain=r[0x41]);cells=bytes(r[0x1c00:0x1ca0]);m=bytes(r[0x1600:0x1b00])
     else:
      word=lambda name:int.from_bytes(data(r,name,2),'big');state=dict(room=word('room_id'),game=word('game_state'),x=word('hero_x')>>8,y=word('hero_y')>>8,terrain=word('hero_terrain_context'));cells=data(r,'scratch',4096)[0x800:0x8a0];m=data(r,'sms_vram',16384)[0x3800:0x3d00]
     rows.append(dict(frame=f,**state,cells=cells.hex(),map=m.hex()))
     if state['room']==target and state['game']==12 and not arrival:
      arrival.append(rows[-1]);captures.add(f+1)
    with contextlib.redirect_stdout(io.StringIO()):run(ROOT/'input/original.sms' if tag=='sms' else rom,3450,folder,captures,([(200,220,0)] if tag=='sms' else [])+PRESSES[:8]+[(3101,3450,4+direction)],ram_writes=pending,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':region})
    (folder/'observations.json').write_text(json.dumps(rows,indent=2)+'\n');assert arrival,(region,direction,tag,'did not arrive');traces[tag]=dict(arrival=arrival[0],last=rows[-1])
   s=traces['sms']['arrival'];m=traces['md']['arrival'];exact=all(s[k]==m[k] for k in ['cells','map','x','y','terrain'])
   assert exact!=(a.expect_missing),(region,direction,'arrival mismatch',[(k,s[k],m[k]) for k in ['x','y','terrain'] if s[k]!=m[k]],[(i,x,y) for i,(x,y) in enumerate(zip(bytes.fromhex(s['cells']),bytes.fromhex(m['cells']))) if x!=y])
   results.append(dict(region=region,direction=direction,source_arrival_frame=s['frame'],native_arrival_frame=m['frame'],arrival_fields_exact=exact,source_final=traces['sms']['last'],native_final=traces['md']['last']))
   print(region,direction,'arrival exact:',exact,flush=True)
 report=dict(passed=True,md_sha256=sha(rom.read_bytes()),source_sha256=sha(world.rom),missing_arrival_reproduced=a.expect_missing,results=results,controlled_fixture=True,limits=['Common real exterior cells, rope ownership and starting hero fixture; ordinary input deploys rope and crosses the screen.','Arrival cells, software map, integer coordinates and terrain are compared; complete framebuffer, actors, audio and natural campaign require separate evidence.'])
 (ROOT/f'analysis/rope_arrival_game_{a.trial}_report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
