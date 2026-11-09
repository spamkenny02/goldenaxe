"""Cold boot pixel/timing capture,originalSMS versus publishedV320,no inputs."""
import argparse,hashlib,json,contextlib,io,re
from pathlib import Path
from compression import zstd
import numpy as np
from run_core import ROOT,run
p=argparse.ArgumentParser();p.add_argument('--system',choices=['sms','md'],required=True);p.add_argument('--region',choices=['ntsc','pal'],required=True);p.add_argument('--out',required=True);p.add_argument('--frames',type=int,default=7600);p.add_argument('--rom',type=Path);p.add_argument('--symbols',type=Path);options=p.parse_args()
out=(ROOT/'validation'/options.out).resolve();assert out.is_relative_to(ROOT/'validation') and not out.exists();out.mkdir()
md=options.system=='md';rom=options.rom or ROOT/('versions/v0320-9e5b0abe/gaw-megadrive-v0320.bin' if md else 'input/original.sms');expected='9e5b0abed80678ce864a0bb796c17e97047d1d34e5227a5275bf9336129ceaff' if md else '852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9'
if options.rom:
 assert md and options.symbols,'Candidate MD captures require their own symbol file'
 expected=hashlib.sha256(rom.read_bytes()).hexdigest()
assert hashlib.sha256(rom.read_bytes()).hexdigest()==expected
symbols={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in (options.symbols or ROOT/'megadrive/out/release/symbol.txt').read_text().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
levels5=np.array([0,12,21,29] if md else [0,10,21,31]);levels6=np.array([0,25,42,59] if md else [0,21,42,63]);lut5=np.abs(np.arange(32)[:,None]-levels5).argmin(axis=1).astype(np.uint8);lut6=np.abs(np.arange(64)[:,None]-levels6).argmin(axis=1).astype(np.uint8)
rows=[];pictures=set();latest={};geometry=set();channels=[set(),set(),set()];last=None
with zstd.ZstdFile(out/'pictures.zst','wb',level=3) as images:
 def video(frame,data,w,h,pitch,mode):
  global last
  if data is None:
   assert last is not None;latest.update(last);return
  assert mode==2,(frame,mode);geometry.add((w,h,pitch));im=np.frombuffer(data,dtype='<u2').reshape(h,pitch//2)[:,:w]
  if md and h==224 and w==256:im=im[16:208]
  elif h!=192 or w!=256:
   assert not np.count_nonzero(im),(frame,w,h);im=np.zeros((192,256),dtype=np.uint16)
  r=(im>>11)&31;g=(im>>5)&63;b=im&31
  for values,dest in zip((r,g,b),channels):dest.update(map(int,np.unique(values)))
  unknown=int(np.count_nonzero(~np.isin(r,levels5)|~np.isin(g,levels6)|~np.isin(b,levels5)))
  pixels=(lut5[r]|lut6[g]<<2|lut5[b]<<4).tobytes();digest=hashlib.sha256(pixels).digest();name=digest.hex()
  if name not in pictures:pictures.add(name);images.write(digest);images.write(pixels)
  latest.clear();latest.update(hash=name,unknown_color_pixels=unknown,nonblack_pixels=int(np.count_nonzero(im)));last=dict(latest)
 def observe(frame,raw):
  if md:
   d=np.frombuffer(raw,dtype=np.uint16).byteswap().tobytes();word=lambda k:int.from_bytes(d[symbols[k]:symbols[k]+2],'big')
   line=word('intro_line');scene=word('intro_scene');counter=word('intro_counter');clock=word('intro_logic_clock')&255;running=bool(word('intro_running'))
  else:
   line=raw[0x1ce0];callback=int.from_bytes(raw[0x1cec:0x1cee],'little');scene={0xf37:1,0x1055:2,0x104a:3}.get(callback,0);counter=raw[0x1ce2];clock=raw[0x2f];running=bool(1<=line<=65 and not raw[0x1ce1])
  rows.append(dict(frame=frame,line=line,scene=scene,counter=counter,clock=clock,running=running,**latest))
 with contextlib.redirect_stdout(io.StringIO()):run(rom,options.frames,out/'capture',set(),[],skip_intro=False,ram_observer=observe,video_observer=video,core_options={'genesis_plus_gx_region_detect':'pal' if options.region=='pal' else 'auto'})
(out/'frames.json.zst').write_bytes(zstd.compress(json.dumps(rows,separators=(',',':')).encode(),level=3))
cap=json.loads((out/'capture/capture.json').read_bytes());report=dict(system=options.system,region=options.region,rom_sha256=expected,frames=len(rows),fps=cap['fps'],unique_pictures=len(pictures),noncanonical_color_frames=sum(bool(r['unknown_color_pixels']) for r in rows),max_noncanonical_pixels=max(r['unknown_color_pixels'] for r in rows),channel_levels=[sorted(x) for x in channels],geometry=sorted(geometry),pixel_format='OriginalRGB565 mapped through exact expected SMS2bit/MD3bit palette levels to6bit color indices;MD16pixel top/bottom border removed.',no_buttons=True,no_ram_writes=True,picture_record_bytes=49184,scope='Actual rendered cold-boot pictures and per-frame post-render metadata. Metadata may lead/lag visible publication;matching by logical line alone does not prove absolute phase timing.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
