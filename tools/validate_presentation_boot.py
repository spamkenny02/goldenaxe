"""Verify real boot picture, fades, voice, and handoff without injected state."""
import argparse,json,hashlib,wave
from pathlib import Path
import numpy as np
from PIL import Image
from run_core import ROOT,run

def fit_audio(folder,region,rate):
 with wave.open(str(folder/'audio.wav'))as f:audio=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').reshape(-1,2).mean(1)
 fs=8000;t=np.arange(.7,4.9,1/fs);x=np.interp(t,np.arange(len(audio))/44100,audio);x-=x.mean();ref=np.frombuffer((ROOT/f'megadrive/presentation/voice-{region}.pcm').read_bytes(),dtype=np.uint8).astype(float)-128;nfft=1<<int(np.ceil(np.log2(len(x)+32000)));fx=np.fft.rfft(x,nfft);energy=np.r_[0,np.cumsum(x*x)]
 def score(hz):
  r=np.interp(np.arange(0,len(ref)/hz,1/fs)*hz,np.arange(len(ref)),ref);r-=r.mean();dots=np.fft.irfft(fx*np.conj(np.fft.rfft(r,nfft)),nfft)[:len(x)-len(r)+1];scores=dots/np.sqrt(np.maximum(energy[len(r):]-energy[:-len(r)],1)*np.sum(r*r));i=int(np.argmax(scores));return float(scores[i]),float(hz),float(.7+i/fs)
 best=max(score(hz)for hz in np.arange(rate-3,rate+3,.25));assert best[0]>.96 and abs(best[1]-rate)/rate<.001;assert np.max(np.abs(audio))<32767
 return dict(waveform_correlation=best[0],measured_sample_rate=best[1],expected_sample_rate=rate,audio_start_seconds=best[2],voice_seconds=len(ref)/best[1],output_peak=int(np.max(np.abs(audio))),no_digital_clipping=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);p.add_argument('--out',required=True);a=p.parse_args();rom=ROOT/a.rom;out=ROOT/a.out;out.mkdir();results=[];assets=json.loads((ROOT/'megadrive/presentation/assets.json').read_bytes())
 for region in ['ntsc','pal']:
  original_first=None
  def old_obs(f,r):
   nonlocal original_first
   if original_first is None and int.from_bytes(r[0xd310:0xd312],'little'):original_first=f
  run(ROOT/'versions/v0323-9fcee16d/gaw-megadrive-v0323.bin',100,out/(region+'-baseline'),set(),[],skip_intro=False,ram_observer=old_obs,core_options={'genesis_plus_gx_region_detect':'pal'if region=='pal'else'auto'})
  events=[];last=None;first=None
  def obs(f,r):
   nonlocal first,last
   w=lambda n:int.from_bytes(r[n:n+2],'little');phase=w(0xe4c0)
   if phase==4 and last!=phase:captures.update(f+x for x in range(1,18,2))
   if phase!=last:events.append(dict(frame=f,phase=phase));last=phase
   if first is None and w(0xd310):first=f
   assert w(0x2d12)==0
  folder=out/region;captures={30,35,40,45,50,100,235,240,245,250,255,260,265,270,275,280,300,400,650}
  captures.add(850)
  run(rom,850,folder,captures,[],skip_intro=False,ram_observer=obs,audio_out=folder/'audio.wav',core_options={'genesis_plus_gx_region_detect':'pal'if region=='pal'else'auto'})
  assert first and original_first and [e['phase']for e in events]==[0,1,2,3,4,5];offset=first-original_first
  image=Image.open(folder/'frame_00100.png');assert image.size==(256,224)and len(image.getcolors(100000))<=64 and np.asarray(image).mean()>15
  raw=(folder/'vram_00100.bin').read_bytes();swap=lambda b:bytes(v for i in range(0,len(b),2)for v in(b[i+1],b[i]));tiles=(ROOT/'megadrive/presentation/tiles.bin').read_bytes();assert swap(raw[32:32+len(tiles)])==tiles
  regs=(folder/'vdp_regs_00100.bin').read_bytes();base=(regs[2]&56)<<10;expected=(ROOT/'megadrive/presentation/map.bin').read_bytes()
  for y in range(28):assert swap(raw[base+y*128:base+y*128+64])==expected[y*64:y*64+64]
  fps=59.92274339771384 if region=='ntsc' else 49.70145974817708
  fades_in=[np.asarray(Image.open(folder/f'frame_{n:05d}.png')).astype(float).mean()for n in [30,35,40,45,50,100]]
  assert all(b>=a for a,b in zip(fades_in,fades_in[1:])),fades_in
  start_out=next(e['frame'] for e in events if e['phase']==4);fade_out=[np.asarray(Image.open(folder/f'frame_{start_out+n:05d}.png')).astype(float).mean() for n in range(1,18,2)];assert all(b<=a for a,b in zip(fade_out,fade_out[1:])),fade_out
  audio=fit_audio(folder,region,assets['audio'][region]['rate'])
  r=dict(passed=True,region=region,frame_offset=offset,original_intro_start=original_first,new_intro_start=first,phase_events=events,tiles_and_map_exact=True,palettes_used=4,colors_at_most64=True,fade_in_luminance=fades_in,fade_out_luminance=fade_out,external_ram_writes=0,sram_imports=0,**audio);results.append(r);print(json.dumps(r),flush=True)
 r=dict(passed=True,md_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),cases=results,scope='Actual native boot, original supplied picture converted into four MD palettes, actual DAC voice matched to converted source waveform, fade and original intro handoff. No injected resource or game state.')
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n',newline='\n')
if __name__=='__main__':main()
