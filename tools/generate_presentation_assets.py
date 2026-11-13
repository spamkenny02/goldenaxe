"""Convert the supplied presentation into native MD tiles/palettes and DAC audio."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--image',required=True);p.add_argument('--audio',required=True);a=p.parse_args();out=ROOT/'megadrive/presentation';out.mkdir(exist_ok=True)
 image=Path(a.image);audio=Path(a.audio)
 if image.resolve()!=(out/'original.png').resolve():shutil.copyfile(image,out/'original.png')
 if audio.resolve()!=(out/'voice.mp3').resolve():shutil.copyfile(audio,out/'voice.mp3')
 im=Image.open(image).convert('RGBA');bg=Image.new('RGBA',im.size,(0,0,0,255));bg.alpha_composite(im);im=bg.convert('RGB');im.thumbnail((244,216),Image.Resampling.LANCZOS);canvas=Image.new('RGB',(256,224));canvas.paste(im,((256-im.width)//2,(224-im.height)//2))
 rgb=np.array(canvas).astype(np.int32);q=np.clip(np.rint(rgb*7/255),0,7).astype(np.int32);ids=q[:,:,0]*64+q[:,:,1]*8+q[:,:,2];tiles=ids.reshape(28,8,32,8).transpose(0,2,1,3).reshape(896,64)
 universe=np.array([[r,g,b] for r in range(8) for g in range(8) for b in range(8)],dtype=np.int32)*255//7
 # Deterministic tile clustering, then iterated palette assignment by actual RGB error.
 hist=np.array([np.bincount(t,minlength=512) for t in tiles],dtype=np.float32);means=(hist@universe)/64;centers=means[[380,150,700,290]].copy()
 for _ in range(12):
  groups=((means[:,None,:]-centers[None,:,:])**2).sum(2).argmin(1)
  for k in range(4):
   if np.any(groups==k):centers[k]=means[groups==k].mean(0)
 palettes=[]
 for iteration in range(12):
  palettes=[];maps=[];errs=[]
  for k in range(4):
   values=tiles[groups==k].ravel();values=values[values!=0]
   if not len(values):values=tiles.ravel()[tiles.ravel()!=0]
   pixels=universe[values].astype(np.uint8);sample=Image.fromarray(pixels.reshape(1,-1,3)).quantize(colors=15,method=Image.Quantize.MEDIANCUT)
   pal=np.array(sample.getpalette()[:45]).reshape(15,3);pal=np.clip(np.rint(pal*7/255),0,7).astype(int);native=[0]
   for r,g,b in pal:
    value=int(r*64+g*8+b)
    if value and value not in native:native.append(value)
   native=(native+[0]*16)[:16];colors=universe[native];distance=((universe[:,None,:]-colors[None,:,:])**2).sum(2);mapping=distance.argmin(1);maps.append(mapping);errs.append(distance.min(1));palettes.append(native)
  new_groups=np.array([np.array(e)[tiles].sum(1) for e in errs]).argmin(0)
  if np.array_equal(new_groups,groups):break
  groups=new_groups
 encoded=bytearray();tilemap=bytearray();preview=np.zeros((896,64,3),dtype=np.uint8)
 for n,t in enumerate(tiles):
  k=int(groups[n]);mapped=maps[k][t];preview[n]=universe[np.array(palettes[k])[mapped]]
  for j in range(0,64,2):encoded.append(int(mapped[j]*16+mapped[j+1]))
  tilemap.extend(((n+1)|(k<<13)).to_bytes(2,'big'))
 colors=[]
 for pal in palettes:
  for idx in pal:
   r=idx//64;g=(idx//8)%8;b=idx%8;colors.append((r<<1)|(g<<5)|(b<<9))
 (out/'tiles.bin').write_bytes(encoded);(out/'map.bin').write_bytes(tilemap);(out/'palette.bin').write_bytes(b''.join(x.to_bytes(2,'big')for x in colors));Image.fromarray(preview.reshape(28,32,8,8,3).transpose(0,2,1,3,4).reshape(224,256,3)).save(out/'preview.png')
 audio_rows={}
 # The DAC loop has478 execution cycles plus YM bus synchronization (~25/3 cycles).
 # Both region rates are checked against actual captured audio.
 for region,cpu in [('ntsc',7670453),('pal',7600489)]:
  rate=round(cpu*3/1459);target=out/f'voice-{region}.pcm'
  result=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-nostdin','-v','error','-i',str(audio),'-ac','1','-af','lowpass=f=7000,afade=t=in:d=0.003','-ar',str(rate),'-f','f32le','pipe:1'],stdout=subprocess.PIPE,check=True)
  floating=np.frombuffer(result.stdout,dtype='<f4').astype(np.float64);peak=float(np.max(np.abs(floating)));gain=0.9/max(peak,0.0001);floating*=gain
  ramp=min(round(rate*.005),len(floating));floating[-ramp:]*=np.linspace(1,0,ramp)
  data=np.clip(np.rint(128+floating*127),0,255).astype(np.uint8).tobytes()
  target.write_bytes(data);audio_rows[region]=dict(rate=rate,samples=len(data),seconds=len(data)/rate,source_peak=peak,normalization_gain=gain)
 report=dict(source_image_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),source_audio_sha256=hashlib.sha256(audio.read_bytes()).hexdigest(),width=256,height=224,tile_count=896,palettes=4,colors_per_palette=16,audio=audio_rows,transparent_background_composited_black=True)
 (out/'assets.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
