"""Portable reader for the actual recorded regression routes (Windows GX core)."""
import argparse,csv,hashlib,json,sys
from PIL import Image
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'runtime'))
from run_core import run,FrameWrites

p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--route',choices=list(json.loads((BASE/'manifest.json').read_text())['routes']),required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--core',type=Path,default=BASE/'runtime/genesis_plus_gx_libretro.dll');p.add_argument('--frames',type=int);p.add_argument('--without-assistance',action='store_true');a=p.parse_args()
manifest=json.loads((BASE/'manifest.json').read_text());route=manifest['routes'][a.route];digest=hashlib.sha256(a.rom.read_bytes()).hexdigest();known={v['sha256'] for k,v in manifest['roms'].items() if (k=='sms')==(route['system']=='sms')};assert digest in known,'ROM hash not included in this kit; do not reuse native RAM addresses on another build'
assert a.core.is_file(),'Supply --core path/to/genesis_plus_gx_libretro.dll'
assert not a.out.exists(),'Choose a new output directory';end=a.frames or route['frames'];assert 0<end<=route['frames'];csvpath=BASE/'routes'/route['csv'];assert hashlib.sha256(csvpath.read_bytes()).hexdigest()==route['csv_sha256'];presses=[];writes=FrameWrites()
with csvpath.open(newline='') as stream:
 for row in csv.DictReader(stream):
  first,last,mask,guard=(int(row[k]) for k in ['start','end','mask','guard']);last=min(last,end)
  if first>last:continue
  presses.extend((first,last,key) for key in range(16) if mask&(1<<key))
  if guard!=-1 and not a.without_assistance:
   address,width=(0x305,1) if route['system']=='sms' else (0x2b1a,2)
   writes.extend((f,address,guard.to_bytes(width,'big')) for f in range(first,last+1))
last={};ending_seen=False;final_ram=None;guard_frames_checked=0
def observe(frame,raw):
 global ending_seen,final_ram,guard_frames_checked
 if route['system']=='md':
  def word(n):return raw[n]|(raw[n+1]<<8)
  crystals=sum(bool(raw[(0x28be+0x1f+n)^1]&128) for n in range(9))
  last.update(game=word(0x74c),room=word(0x28b4),health=word(0x2b16),crystals=crystals,audio_error=word(0x2d12));ending_seen|=last['game']==14
 else:
  last.update(game=raw[0x1d],room=int.from_bytes(raw[0xb9:0xbb],'little'),health=raw[0x318],
              crystals=sum(bool(b&128) for b in raw[0xcf:0xd8]),audio_error=None)
  ending_seen|=last['game']==14
  if route.get('full_campaign') and raw[0x305]>128:
   guard_frames_checked+=1
   assert not any(raw[0x618+n*48] and (0x63<=raw[0x600+n*48]<=0x6d or 0x78<=raw[0x600+n*48]<=0x7c) for n in range(16)), 'Approach guard overlaps a live boss'
 if frame==end:final_ram=bytes(raw)
 if frame%10000==0:print('frame',frame,'/',end,last,flush=True)
run(a.rom,end,a.out,{end},presses,core=a.core,skip_intro=False,ram_writes=writes,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':'pal' if route['region']=='pal' else 'auto'})
complete=end==route['frames'];passed=None
if complete and route['system']=='md' and not a.without_assistance:
 passed=ending_seen and last['audio_error']==0 and all(last[k]==v for k,v in route['expected_final'].items())
if complete and route.get('full_campaign') and route['system']=='sms' and not a.without_assistance:
 passed=ending_seen and all(last[k]==v for k,v in route['expected_final'].items())
 passed=passed and hashlib.sha256(final_ram).hexdigest()==route['expected_final_ram_sha256']
 pixels=Image.open(a.out/f'frame_{end:05d}.png').convert('RGB').tobytes()
 passed=passed and hashlib.sha256(pixels).hexdigest()==route['expected_final_pixels_sha256']
report=dict(route=a.route,rom_sha256=digest,core_sha256=hashlib.sha256(a.core.read_bytes()).hexdigest(),frames=end,full_route_executed=complete,ending_seen=ending_seen,expected_final_passed=passed,final=last,approach_writes=len(writes),boss_assistance=False,sram_imports=0,feedback_input_reads=False,guard_frames_checked=guard_frames_checked,scope='Recorded libretro route replay. Full SMS NTSC campaign and SMS intro-only routes are distinct. Reaching the ending does not certify every NPC/quest, PAL, paired graphics/audio or hardware fidelity.')
(a.out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if passed is False:raise SystemExit(1)
