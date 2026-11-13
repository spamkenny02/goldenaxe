"""Encode an interval of the independent, continuously cold-replayed MD core."""
import hashlib,json,subprocess,sys,wave
from pathlib import Path
import cv2,numpy as np
from run_core import ROOT
from write_atomic_report import write_bytes
sys.path.insert(0,str(ROOT.parents[1]/'work/video-tools'))
import imageio_ffmpeg

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

class Movie:
    def __init__(self,trace,cap,first,core_sha):
        assert 1<=first<=cap['frames']
        self.trace,self.cap,self.first,self.core_sha=trace,cap,first,core_sha
        self.folder=ROOT/'validation/md-stream-videos'/Path(trace).name
        assert not self.folder.exists();self.folder.mkdir(parents=True)
        self.rate=round(cap['sample_rate']);assert self.rate==44100
        self.wav=self.folder/'audio.wav';self.silent=self.folder/'silent.mp4';self.movie=self.folder/'recording.mp4'
        self.audio=wave.open(str(self.wav),'wb');self.audio.setparams((2,2,self.rate,0,'NONE','not compressed'))
        self.log=(self.folder/'encode.log').open('w');self.ff=imageio_ffmpeg.get_ffmpeg_exe()
        self.encoder=None;self.last=None;self.frames=0;self.audio_bytes=0
    def sound(self,frame,data):
        if frame<self.first:return
        self.audio.writeframesraw(data);self.audio_bytes+=len(data)
    def video(self,frame,data,w,h,pitch,mode):
        if not frame:return
        assert mode==2
        if data is not None:self.last=data,w,h,pitch
        if frame<self.first:return
        assert self.last is not None and frame==self.first+self.frames
        data,w,h,pitch=self.last;packed=b''.join(data[y*pitch:y*pitch+w*2] for y in range(h))
        if (w,h)!=(256,224):packed=cv2.resize(np.frombuffer(packed,dtype='<u2').reshape(h,w),(256,224),interpolation=cv2.INTER_NEAREST).tobytes()
        if self.encoder is None:
            self.encoder=subprocess.Popen([self.ff,'-hide_banner','-nostdin','-filter_threads','1','-f','rawvideo','-pixel_format','rgb565le','-video_size','256x224','-framerate',f'{self.cap["fps"]:.12f}','-i','pipe:0','-an','-vf','scale=960:720:flags=neighbor,setsar=1','-c:v','libx264','-preset','veryfast','-threads','2','-crf','18','-pix_fmt','yuv420p',str(self.silent)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=self.log)
        self.encoder.stdin.write(packed);self.frames+=1
    def finish(self,proof,writes):
        self.audio.close();assert self.encoder is not None
        self.encoder.stdin.close();assert self.encoder.wait()==0;self.log.close()
        end=self.cap['frames'];fps=self.cap['fps'];assert self.frames==end-self.first+1
        witness=json.loads(proof.read_bytes());assert witness['passed'] and witness['final_png_exact'] and witness['rom_sha256']==self.cap['rom_sha256']
        delta=self.audio_bytes/4/self.rate-self.frames/fps;assert abs(delta)<.1
        with (self.folder/'mux.log').open('w') as log:
            subprocess.run([self.ff,'-hide_banner','-nostdin','-i',str(self.silent),'-i',str(self.wav),'-map','0:v:0','-map','1:a:0','-map_chapters','-1','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-metadata',('comment=Isolated currency-assisted component; actual purchases; no inventory, health, quest or save-state imports.' if self.cap.get('currency_assisted_component_test') else 'comment=Actual independent cold replay; marked side branch, declared approach guard; no save-state imports.'),str(self.movie)],stdout=log,stderr=subprocess.STDOUT,check=True)
        with (self.folder/'decode.log').open('w') as log:
            subprocess.run([self.ff,'-hide_banner','-nostdin','-v','error','-xerror','-threads','2','-i',str(self.movie),'-map','0:v:0','-map','0:a:0','-f','null','-'],stdout=log,stderr=subprocess.STDOUT,check=True)
        reader=cv2.VideoCapture(str(self.movie));assert reader.isOpened() and round(reader.get(cv2.CAP_PROP_FRAME_COUNT))==self.frames;reader.release()
        result=dict(passed=True,currency_assisted_component_test=bool(self.cap.get('currency_assisted_component_test')),trace=self.trace,rom_sha256=self.cap['rom_sha256'],movie=self.movie.relative_to(ROOT).as_posix(),movie_sha256=sha(self.movie),frames=self.frames,first_emulated_frame=self.first,last_emulated_frame=end,fps=fps,duration_seconds=self.frames/fps,audio_video_delta_seconds=delta,full_audio_video_decoded=True,final_ram_and_pixels_exact=True,ram_writes=len(writes),boss_assistance=False,sram_imports=0,genuine_game_written_continue=False,all_npcs_complete=False,proof_sha256=sha(proof),core_sha256=self.core_sha,recorder_sha256=sha(Path(__file__)),recorded_from_independent_cold_stream=True)
        write_bytes(self.folder/'report.json',(json.dumps(result,indent=2)+'\n').encode())
        self.wav.unlink();self.silent.unlink()
