"""Compare all terrain/boots movement rows through both unchanged gameplay loops.

Only the software map, equipment and initial hero/actor fixture are controlled.
Terrain classification and normal directional input select the actual tables.
"""
import argparse,contextlib,io,json
from run_core import ROOT,run
from validate_playable_sprite_limit import symbols
from validate_actor_tick import PRESSES
from archive_lossless_evidence import sha

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--trial',default='02');args=parser.parse_args()
 rom=(ROOT/'input/original.sms').read_bytes();groups=[]
 for n in range(5):
  p=0x2544+n*4;address=int.from_bytes(rom[p:p+2],'little');groups.append((rom[p+3],rom[address:address+rom[p+2]]))
 def context(tile):return next((kind for kind,values in groups if tile in values),0)
 tiles={kind:next(tile for tile in range(256) if context(tile)==kind) for kind in range(6)}
 cases=[(boots,terrain,direction) for boots in [0,1] for terrain in range(6) for direction in range(4)];sy=symbols(ROOT/'megadrive/out/release/symbol.txt');results=[]
 for region in ['auto','pal']:
  traces={}
  for tag in ['sms','md']:
   pending=[];samples={};folder=ROOT/f'validation/terrain-walk-v0288-{args.trial}/{region}-{tag}';assert not folder.exists()
   def prepare(index,frame):
    boots,terrain,direction=cases[index];tilemap=bytes([tiles[terrain],0])*768
    if tag=='sms':
     pending[:]=[(frame,0x1600,tilemap),(frame,0x600,bytes(768)),(frame,0x310,bytes.fromhex('0060008000000000')),(frame,0x318,b'\x18'),(frame,0xda,b'\x18'),(frame,0x301,b'\1'),(frame,0x303,b'\3'),(frame,0x304,b'\0\0'),(frame,0x30a,bytes([direction,0])),(frame,0x68,b'\0'),(frame,0xee,bytes([boots])),(frame,0xdf,b'\0')]
    else:
     values=[('hero_health',24),('hero_max_health',24),('hero_y',0x6000),('hero_x',0x8000),('hero_dy',0),('hero_dx',0),('hero_state',1),('hero_flags',3),('hero_hurt',0),('hero_counter',0),('hero_direction',direction),('hero_animation',0),('hero_pending',0),('hero_attack_speed',boots),('hero_selected_item',0)]
     pending[:]=[(frame,sy[k],v.to_bytes(2,'big')) for k,v in values]+[(frame,sy['sms_vram']+0x3800,tilemap),(frame,sy['world_actor_state'],bytes(768)),(frame,sy['hero_items']+14,bytes([boots]))]
   def observe(f,b):
    if f<3101:return
    index,offset=divmod(f-3101,32)
    if index>=len(cases):return
    if tag=='sms':
     word=lambda a:int.from_bytes(b[a:a+2],'little');row=[word(0x310),word(0x312),b[0x30a],b[0x30b],b[0x304],word(0x314),word(0x316),b[0x41]]
    else:
     word=lambda n:int.from_bytes(bytes(b[(sy[n]+i)^1] for i in range(2)),'big');row=[word(n) for n in ['hero_y','hero_x','hero_direction','hero_animation','hero_counter','hero_dy','hero_dx','hero_terrain_context']]
    samples[index,offset]=row
    if offset==31 and index+1<len(cases):prepare(index+1,f+1)
   def controller(f):
    if f<3101:return []
    index=(f-3101)//32
    return [4+cases[index][2]] if index<len(cases) else []
   prepare(0,3101);end=3100+len(cases)*32
   with contextlib.redirect_stdout(io.StringIO()):run(ROOT/('input/original.sms' if tag=='sms' else 'gaw-megadrive.bin'),end,folder,{3101,end},([(200,220,0)] if tag=='sms' else [])+PRESSES[:8],ram_writes=pending,ram_observer=observe,input_provider=controller,core_options={'genesis_plus_gx_region_detect':region})
   assert len(samples)==len(cases)*32
   (folder/'observations.json').write_text(json.dumps([dict(case=i,offset=j,values=v) for (i,j),v in samples.items()],indent=2)+'\n');traces[tag]=samples
  differences=[dict(case=i,setup=cases[i],offset=j,sms=traces['sms'][i,j],md=traces['md'][i,j]) for i,j in traces['sms'] if traces['sms'][i,j]!=traces['md'][i,j]]
  results.append(dict(region=region,cases=len(cases),frames=len(cases)*32,differences=differences));print(region,len(differences),'differences',differences[:2],flush=True)
 report=dict(passed=all(not r['differences'] for r in results),md_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),source_sha256=sha(rom),tiles=tiles,cases=cases,results=results,controlled_fixture=True,limits=['Constant software-map terrain, boots ownership/speed and hero/actor fixtures are injected before each case. Actual terrain detection, table choice, movement integration, animation counter and ordinary directional input execute in both game loops.','HP is reset per case; accumulation of environment damage across cases is excluded from this movement-table check. No hazard-damage parity, natural campaign, full graphics/audio, transition or global clock claim.'])
 (ROOT/'analysis/terrain_walk_v0288_game_report.json').write_text(json.dumps(report,indent=2)+'\n');assert report['passed']
if __name__=='__main__':main()
