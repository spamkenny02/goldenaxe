"""Original/native room49 bridge in actual gameplay loops, controlled start."""
import argparse,contextlib,io,json
from run_core import ROOT,run
from natural_dungeon_route import World
from extract_title import rle_planes
from validate_key_door_gameplay import maps
from validate_playable_sprite_limit import symbols
from validate_actor_tick import PRESSES
from archive_lossless_evidence import sha

CASES=[(0,0),(1,0),(127,0),(128,0),(255,0xa4),(128,0xa5)]

def main():
 p=argparse.ArgumentParser();p.add_argument('--trial',required=True);p.add_argument('--rom');p.add_argument('--symbols');p.add_argument('--expect-missing',action='store_true');a=p.parse_args()
 rom=ROOT/a.rom if a.rom else ROOT/'gaw-megadrive.bin';sy=symbols(ROOT/a.symbols if a.symbols else ROOT/'megadrive/out/release/symbol.txt');world=World();ptr=int.from_bytes(world.arrays['world_room_index'][0x92:0x94],'little');initial=bytearray(160);rle_planes(world.arrays['world_room_streams'],ptr,initial,0,1);results=[]
 for region in ['auto','pal']:
  traces={}
  for tag in ['sms','md']:
   folder=ROOT/f'validation/crystal-bridge-game-{a.trial}/{region}-{tag}';assert not folder.exists();pending=[];rows=[];captures=set();end=3101+400*(len(CASES)-1)+300
   def observe(f,r):
    for i,(gem,flags) in enumerate(CASES):
     start=3101+400*i
     if f==start-1:
      cells=bytearray(initial)
      if flags&1:cells[0x4a]=0x0a;cells[0x5a]=0x6b
      tilemap=maps(cells,world.meta)[0]+bytes(256)
      if tag=='sms':
       pending[:]=[(start,0xb9,b'\x49\0'),(start,0xa4,b'\x4a\xaf'),(start,0x40,b'\0'),(start,0x149,bytes([flags])),(start,0xd3,bytes([gem])),(start,0x6e,b'\x4a\x4a\x14'),(start,0x1c00,bytes(cells)),(start,0x1600,tilemap),(start,0x600,bytes(768)),(start,0xa2,b'\x80'),(start,0x301,b'\1'),(start,0x303,b'\3\0\0'),(start,0x310,b'\0\x58\0\xa8'+bytes(4))]
      else:
       values=dict(room_id=0x49,world_graphics_class=0,game_state=12,hero_state=1,hero_x=168<<8,hero_y=88<<8,hero_counter=0,hero_dx=0,hero_dy=0,hero_flags=3,world_actor_count=128)
       pending[:]=[(start,sy[n],v.to_bytes(2,'big')) for n,v in values.items()]+[(start,sy['game_save_state']+0x99,bytes([flags])),(start,sy['game_save_state']+0x23,bytes([gem])),(start,sy['room_metadata'],b'\x4a\x4a\x14'),(start,sy['scratch']+0x800,bytes(cells)),(start,sy['sms_vram']+0x3800,tilemap),(start,sy['world_actor_state'],bytes(768))]
     if f==start+250:
      if tag=='sms':value=dict(flag=r[0x149],gem=r[0xd3],room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],x=r[0x313],y=r[0x311],cells=bytes(r[0x1c00:0x1ca0]).hex(),map=bytes(r[0x1600:0x1b00]).hex())
      else:
       data=lambda n,k:bytes(r[(sy[n]+j)^1] for j in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
       value=dict(flag=data('game_save_state',592)[0x99],gem=data('game_save_state',592)[0x23],room=word('room_id'),game=word('game_state'),x=word('hero_x')>>8,y=word('hero_y')>>8,cells=data('scratch',4096)[0x800:0x8a0].hex(),map=data('sms_vram',16384)[0x3800:0x3d00].hex())
      rows.append(dict(case=i,frame=f,**value));captures.add(f+1)
   with contextlib.redirect_stdout(io.StringIO()):run(ROOT/'input/original.sms' if tag=='sms' else rom,end,folder,captures,([(200,220,0)] if tag=='sms' else [])+PRESSES[:8],ram_writes=pending,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':region})
   assert len(rows)==len(CASES);(folder/'observations.json').write_text(json.dumps(rows,indent=2)+'\n');traces[tag]=rows
  for i,((gem,flags),s,m) in enumerate(zip(CASES,traces['sms'],traces['md'])):
   expected=bytearray(initial)
   if flags&1 or gem&128:expected[0x4a]=0x0a;expected[0x5a]=0x6b
   assert bytes.fromhex(s['cells'])==expected and s['flag']==(flags|1 if gem&128 else flags)
   fields=['flag','gem','room','game','x','y','cells','map'];exact=all(s[k]==m[k] for k in fields)
   missing=bool(a.expect_missing and gem&128 and not flags&1)
   assert exact!=missing,(region,i,[(k,s[k],m[k]) for k in fields if s[k]!=m[k]])
   results.append(dict(region=region,case=i,gem=gem,initial_flag=flags,fields_exact=exact,missing_reproduced=missing))
 report=dict(passed=True,md_sha256=sha(rom.read_bytes()),source_sha256=sha(world.rom),controlled_fixture=True,cases=len(results),baseline_missing=a.expect_missing,results=results,limits=['Room49,metadata,crystal,flags,position and empty actors are explicit controlled fixtures. Original ROM and production native gameplay execute the script/redraw.','All160 cells,1280 software map bytes,flags,crystal,room,game state and integer position are compared after settling. Actual VDP pixels,audio waveforms,physical redraw timing and natural campaign are separate requirements.'])
 (ROOT/f'analysis/crystal_bridge_game_{a.trial}_report.json').write_text(json.dumps(report,indent=2)+'\n');print('Bridge game:',len(results),'PAL/NTSC cases; missing baseline:',a.expect_missing)

if __name__=='__main__':main()
