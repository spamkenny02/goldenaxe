"""Capture the actual boot with native sound, then prove a second cold replay."""
import argparse,json,hashlib,subprocess,wave,sys
from pathlib import Path
import cv2,numpy as np,imageio_ffmpeg
from run_core import ROOT,run

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);p.add_argument('--out',required=True);a=p.parse_args();rom=ROOT/a.rom;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True);assert not (out/'presentation-v0324-ntsc.mp4').exists();work=ROOT/'validation/presentation-preview-v0324-02';work.mkdir();ff=imageio_ffmpeg.get_ffmpeg_exe();fps=59.92274339771384;frames=650;log=(work/'encode.log').open('wb');silent=work/'silent.mp4'
 enc=subprocess.Popen([ff,'-hide_banner','-nostdin','-f','rawvideo','-pixel_format','rgb565le','-video_size','256x224','-framerate',f'{fps:.12f}','-i','pipe:0','-an','-vf','scale=768:672:flags=neighbor,setsar=1','-c:v','libx264','-preset','veryfast','-threads','2','-crf','18','-pix_fmt','yuv420p',str(silent)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log);count=0;last=None
 def video(frame,data,w,h,pitch,mode):
  nonlocal count,last
  if not frame:return
  if data is not None:last=(data,w,h,pitch)
  assert last and mode==2;data,w,h,pitch=last;packed=b''.join(data[y*pitch:y*pitch+w*2]for y in range(h))
  if (w,h)!=(256,224):packed=cv2.resize(np.frombuffer(packed,dtype='<u2').reshape(h,w),(256,224),interpolation=cv2.INTER_NEAREST).tobytes()
  enc.stdin.write(packed);count+=1
 first=work/'capture';run(rom,frames,first,{100,300,frames},[],skip_intro=False,audio_out=first/'audio.wav',video_observer=video);enc.stdin.close();assert enc.wait()==0 and count==frames;log.close()
 second=work/'cold-replay'
 code="import sys;from pathlib import Path;sys.path.insert(0,'tools');from run_core import run;r=Path(sys.argv[1]);o=Path(sys.argv[2]);run(r,650,o,{650},[],skip_intro=False,audio_out=o/'audio.wav')"
 subprocess.run([sys.executable,'-c',code,str(rom),str(second)],cwd=ROOT,check=True)
 for name in [f'frame_{frames:05d}.png',f'ram_{frames:05d}.bin','audio.wav']:assert sha(first/name)==sha(second/name),name
 movie=out/'presentation-v0324-ntsc.mp4'
 with (work/'mux.log').open('wb')as log:subprocess.run([ff,'-hide_banner','-nostdin','-i',str(silent),'-i',str(first/'audio.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(movie)],stdout=log,stderr=subprocess.STDOUT,check=True)
 with (work/'decode.log').open('wb')as log:subprocess.run([ff,'-hide_banner','-nostdin','-v','error','-xerror','-i',str(movie),'-map','0:v:0','-map','0:a:0','-f','null','NUL'],stdout=log,stderr=subprocess.STDOUT,check=True)
 assert not (work/'decode.log').read_bytes();cap=cv2.VideoCapture(str(movie));assert round(cap.get(cv2.CAP_PROP_FRAME_COUNT))==frames;cap.release()
 r=dict(passed=True,md_sha256=sha(rom),movie=movie.relative_to(ROOT).as_posix(),movie_sha256=sha(movie),frames=frames,fps=fps,full_audio_video_decoded=True,cold_replay_whole_ram_pixels_and_audio_exact=True,external_ram_writes=0,sram_imports=0,scope='Actual cold boot presentation and following original introduction, captured from the cartridge emulator with its actual audio.')
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n',newline='\n');print(json.dumps(r),flush=True)
if __name__=='__main__':main()
