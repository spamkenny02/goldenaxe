import sys,contextlib,io,json,re,hashlib,argparse
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools').resolve()))
from actor_reference import ROOT
from run_core import run
from validate_actor_tick import PRESSES
from validate_key_door_gameplay import initial_room,rle_planes,maps
p=argparse.ArgumentParser();p.add_argument('--rom',required=True);p.add_argument('--symbols',required=True);p.add_argument('--region',required=True);p.add_argument('--out',required=True);p.add_argument('--capture-extra',default='');options=p.parse_args()
rom=Path(options.rom);symbol_file=Path(options.symbols);out=Path(options.out);assert not out.exists()

def main():
 source=(ROOT/'input/original.sms').read_bytes();_,ext,_,_,arrays,_=initial_room(source)
 outside=bytearray(160);offset=int.from_bytes(arrays['world_room_index'][32:34],'little');rle_planes(arrays['world_room_streams'],offset,outside,0,1);osms,_=maps(outside,ext)
 door=next(x for x in json.loads((ROOT/'analysis/doors_reference.json').read_text())['direct_unconditional_dungeon_doors'] if x['room']==16)
 writes=[(3120,0xb9,b'\x10\0'),(3120,0xa4,door['script_entry'].to_bytes(2,'little')),(3120,0x1c00,bytes(outside)),(3120,0x1600,osms),(3120,0x600,bytes(768)),(3120,0x310,((door['y']+8)<<8).to_bytes(2,'little')+(door['x']<<8).to_bytes(2,'little')),
 (3400,0xb9,(0x14b).to_bytes(2,'little')),(3400,0xa4,b'\x61\xb7'),(3400,0x14c,b'\x10'),(3400,0x6e,b'\xff\xff\0'),(3400,0x600,bytes(768)),(3400,0xa2,b'\0'),(3400,0x301,b'\0'),(3400,0x303,b'\x03\0'),(3400,0x30a,b'\x03'),(3400,0x310,(80<<8).to_bytes(2,'little')+(241<<8).to_bytes(2,'little')+bytes(4)),(3400,0x1600,bytes(1280)),(3400,0x305,b'\xff'),(3400,0x318,b'\x18')]
 boss=bytearray(768);boss[0]=7;boss[3]=0x40;boss[0x11]=72;boss[0x13]=128
 terminal=True
 if terminal:boss[1]=4;writes.append((3700,0x301,b'\x0c'))
 writes += [(3700,0x37,b'\x0a'),(3700,0x600,boss),(3700,0x305,b'\0'),(3700,0x318,b'\x18'),(3700,0x310,(112<<8).to_bytes(2,'little')+(168<<8).to_bytes(2,'little')+bytes(4))]
 sy={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for l in (symbol_file).read_text().splitlines() if(m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',l))}
 converted=[]
 for f,a,b in writes:
  if a in [0xa4]:continue
  if a in [0x600,0x1600,0x1c00,0x6e,0x14c]:
   address={0x600:sy['world_actor_state'],0x1600:sy['sms_vram']+0x3800,0x1c00:sy['scratch']+0x800,0x6e:sy['room_metadata'],0x14c:sy['game_save_state']+0x9c}[a];converted.append((f,address,b));continue
  if a==0x310:
   for n,k in enumerate(['hero_y','hero_x','hero_dy','hero_dx']):
    if n*2<len(b):converted.append((f,sy[k],int.from_bytes(b[n*2:n*2+2],'little').to_bytes(2,'big')))
   continue
  if a==0x303:
   for n,k in enumerate(['hero_flags','hero_counter']):converted.append((f,sy[k],bytes([0,b[n]])))
   continue
  k={0xb9:'room_id',0xa2:'world_actor_count',0x301:'hero_state',0x30a:'hero_direction',0x305:'hero_hurt',0x318:'hero_health',0x37:'world_dungeon_number'}[a]
  converted.append((f,sy[k],int.from_bytes(b,'little').to_bytes(2,'big')))
 converted.append((3120,sy['world_graphics_class'],bytes(2)));writes=sorted(converted,key=lambda x:x[0])


 state={};rows={};latest={};borders=[];started=None;done=None;returned=None
 def video(frame,data,width,height,pitch,mode):
  if data is None or height!=224 or width!=256:return
  assert width==256 and height==224 and mode==2,(width,height,mode)
  im=np.frombuffer(data,dtype='<u2').reshape(height,pitch//2)[:,:width]
  latest.update(hash=hashlib.sha256(im[16:208].tobytes()).hexdigest(),bottom_nonblack=int(np.count_nonzero(im[208:])),top_nonblack=int(np.count_nonzero(im[:16])))
 def observe(f,raw):
  nonlocal started,done,returned
  data=lambda k,n:bytes(raw[(sy[k]+i)^1] for i in range(n))
  word=lambda k:int.from_bytes(data(k,2),'big')
  credit=data('ending_credits',9);active=word('game_state')==14 and word('ending_hero_descriptor')==0x84e1 and int.from_bytes(credit[6:8],'big')>0
  if active:
   if started is None:started=f
   key=credit.hex();rows.setdefault(key,dict(frame=f,**latest))
   borders.append(latest['bottom_nonblack'])
   if credit[1] and done is None:done=f
  if done and word('game_state')==0 and returned is None:returned=f
 with contextlib.redirect_stdout(io.StringIO()):run(rom,13000,out,({6000,8000,10000,12000,12900}|{int(x) for x in options.capture_extra.split(',') if x}),PRESSES+[(3125,3129,4),(3400,3403,7),(12800,12802,8)],ram_writes=writes,ram_observer=observe,video_observer=video,core_options={'genesis_plus_gx_region_detect':options.region})
 assert started and done and returned,(started,done,returned)
 report=dict(md_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),region=options.region,started=started,done=done,returned=returned,states=rows,bottom_nonblack_frames=sum(x>0 for x in borders),max_bottom_nonblack=max(borders),scope='Controlled terminal boss checkpoint followed by production ending and full credits; no credit-state/VRAM import. Compare full192-line picture for every credit arithmetic state,not only five samples.')
 (out/'report.json').write_text(json.dumps(report,indent=2));print(options.region,len(rows),'states',report['bottom_nonblack_frames'],'border frames',flush=True)

main()
