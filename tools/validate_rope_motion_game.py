"""Compare rope deployment and the first32 movement frames in real SMS/MD loops."""
import contextlib,io,json
from run_core import ROOT,run
from validate_playable_sprite_limit import symbols
from validate_actor_tick import PRESSES
from validate_key_door_gameplay import maps
from archive_lossless_evidence import sha

def main():
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');results=[]
 for region in ['auto','pal']:
  traces={}
  for tag in ['sms','md']:
   pending=[];rows=[];folder=ROOT/f'validation/rope-motion-v0288/{region}-{tag}';assert not folder.exists()
   def observe(f,b):
    if f==3100:
     if tag=='sms':meta=b[0x900:0x1100]
     else:meta=bytes(b[(sy['scratch']+i)^1] for i in range(2048))
     cells=bytearray(160);cells[0x46]=2
     for index in [0x06,0x16,0x26,0x36]:cells[index]=12
     m=maps(cells,meta)[0]+bytes(256)
     if tag=='sms':pending[:]=[(3101,0x1c00,bytes(cells)),(3101,0x1600,m),(3101,0x600,bytes(768)),(3101,0x310,bytes.fromhex('0058006800000000')),(3101,0x301,b'\1'),(3101,0x303,b'\3'),(3101,0x304,bytes(2)),(3101,0x30a,bytes(2)),(3101,0x68,b'\0'),(3101,0x98,bytes(4)),(3101,0xed,b'\1'),(3101,0xee,b'\0')]
     else:
      values=[('hero_y',0x5800),('hero_x',0x6800),('hero_dy',0),('hero_dx',0),('hero_state',1),('hero_flags',3),('hero_hurt',0),('hero_counter',0),('hero_direction',0),('hero_animation',0),('hero_pending',0),('hero_attack_speed',0)]
      pending[:]=[(3101,sy[k],v.to_bytes(2,'big')) for k,v in values]+[(3101,sy['scratch']+0x800,bytes(cells)),(3101,sy['sms_vram']+0x3800,m),(3101,sy['world_actor_state'],bytes(768)),(3101,sy['magic_rope_work'],bytes(4)),(3101,sy['hero_items']+13,b'\1')]
    if not 3101<=f<=3132:return
    if tag=='sms':
     word=lambda a:int.from_bytes(b[a:a+2],'little');state=[word(0x310),word(0x312),b[0x304],b[0x30a],b[0x30b],word(0x314),word(0x316),b[0x41]];work=b[0x98:0x9c];cells=b[0x1c00:0x1ca0];m=b[0x1600:0x1b00]
    else:
     data=lambda n,k:bytes(b[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big');state=[word(n) for n in ['hero_y','hero_x','hero_counter','hero_direction','hero_animation','hero_dy','hero_dx','hero_terrain_context']];work=data('magic_rope_work',4);cells=data('scratch',4096)[0x800:0x8a0];m=data('sms_vram',16384)[0x3800:0x3d00]
    rows.append(dict(frame=f,state=state,work=work.hex(),column=[cells[i] for i in [6,22,38,54,70]],rope_rows=[m[offset:offset+4].hex() for offset in range(24,601,64)]))
   with contextlib.redirect_stdout(io.StringIO()):run(ROOT/('input/original.sms' if tag=='sms' else 'gaw-megadrive.bin'),3132,folder,{3101,3110,3122,3132},([(200,220,0)] if tag=='sms' else [])+PRESSES[:8]+[(3101,3132,4)],ram_writes=pending,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':region})
   (folder/'observations.json').write_text(json.dumps(rows,indent=2)+'\n');traces[tag]=rows
  assert traces['sms']==traces['md'],(region,[(s,m) for s,m in zip(traces['sms'],traces['md']) if s!=m][:1])
  assert len(traces['md'])==32 and traces['md'][10]['state'][2]==11
  results.append(dict(region=region,frames=32,hero_motion_and_counter_exact=True,terrain_context_exact=True,rope_work_and_column_exact=True,ten_progressive_software_rows_exact=True,rope_step_ticks=12));print(region,'32 movement/rope frames exact',flush=True)
 report=dict(passed=True,md_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),source_sha256=sha((ROOT/'input/original.sms').read_bytes()),cases=results,controlled_fixture=True,limits=['Common map, hero, ownership and actor fixtures. Actual movement, terrain classification and rope deployment/animation execute in both game loops.','No natural campaign or complete framebuffer/audio/global timing claim.'])
 (ROOT/'analysis/rope_motion_v0288_game_report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
