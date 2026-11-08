"""Capture publishedV319 intro or full audited campaign with streamed AV."""
import argparse,contextlib,io,json,os,struct,subprocess,sys,time,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT.parents[1]/'work/video-tools'))
import imageio_ffmpeg
import cv2,numpy as np
from run_core import run,FrameWrites
from assisted_prefix import recording
from archive_lossless_evidence import sha

parser=argparse.ArgumentParser();parser.add_argument('part',choices=['intro','gameplay']);parser.add_argument('--out-name',required=True);parser.add_argument('--frames',type=int);parser.add_argument('--complete-intro',action='store_true');args=parser.parse_args()
out=(ROOT/'validation'/args.out_name).resolve();assert out.is_relative_to(ROOT/'validation') and not out.exists();out.mkdir()
rom=ROOT/'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin';assert sha(rom.read_bytes())=='d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e'
trace=ROOT/'validation/c0046-campaign01/isolated/project/validation/natural-dungeon-combat/md-auto-c0046-cold-palace-ending01'
cap=json.loads((trace/'capture.json').read_bytes());fps=cap['fps'];rate=round(cap['sample_rate']);presses=[];writes=[]
assert cap['frames']==403488 and cap['sram_input'] is None and cap['rom_sha256']=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
if args.part=='gameplay':
 assist,writes=recording(trace,cap);controls=json.loads((trace/'controls.json').read_bytes());end=cap['frames'];presses=list(map(tuple,cap['presses']))
 for i,row in enumerate(controls):
  stop=controls[i+1]['frame']-1 if i+1<len(controls) else end
  presses += [(row['frame'],min(stop,end),b) for b in row['buttons'] if row['frame']<=end]
else:end=14000 if args.complete_intro else 3600
if args.frames:assert 0<args.frames<=end;end=args.frames
ffmpeg=Path(imageio_ffmpeg.get_ffmpeg_exe()).resolve();silent=out/'video-silent.mp4';wav=out/'audio.wav';movie=out/('gaw-v0319-'+args.part+'.mp4')
video_log=(out/'video-encode.log').open('w');encode_progress=(out/'video-encode-progress.txt').open('w');process=None;sent=audio_bytes=0;last_frame=0;last_data=None;started=time.monotonic();formats=set();initial_geometry=None
audio_file=wave.open(str(wav),'wb');audio_file.setnchannels(2);audio_file.setsampwidth(2);audio_file.setframerate(rate)
def audio(raw):
 global audio_bytes
 assert len(raw)%4==0;audio_file.writeframesraw(raw);audio_bytes+=len(raw)
def video(frame,data,width,height,pitch,mode):
 global process,sent,last_frame,last_data,initial_geometry
 if frame==0:return
 assert frame==last_frame+1,(frame,last_frame)
 if data is None:
  assert last_data is not None;raw=last_data
 else:
  pixel_bytes=4 if mode==1 else 2
  assert pitch>=width*pixel_bytes and mode in (0,1,2)
  raw=data if pitch==width*pixel_bytes else b''.join(data[y*pitch:y*pitch+width*pixel_bytes] for y in range(height))
  last_data=raw
 assert mode==2,'This published MD core is expected to produce RGB565.'
 # VDP powers on in320-wide mode before the game selects256-wide H32.
 # Normalize the viewport geometry, without dropping any startup frames.
 if (width,height)!=(256,224):raw=cv2.resize(np.frombuffer(raw,dtype='<u2').reshape(height,width),(256,224),interpolation=cv2.INTER_NEAREST).tobytes()
 if process is None:
  initial_geometry=(256,224,mode);pixel_format='rgb565le'
  command=[str(ffmpeg),'-hide_banner','-nostdin','-filter_threads','1','-f','rawvideo','-pixel_format',pixel_format,'-video_size','256x224','-framerate',f'{fps:.12f}','-i','pipe:0','-an','-vf','scale=960:720:flags=neighbor,setsar=1','-c:v','libx264','-preset','veryfast','-threads','4','-crf','18','-g','120','-bf','2','-pix_fmt','yuv420p','-movflags','+faststart','-progress','pipe:1',str(silent)]
  (out/'encoder-command.json').write_text(json.dumps(command,indent=2)+'\n');process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=encode_progress,stderr=video_log)
 assert len(raw)==256*224*2
 process.stdin.write(raw);sent+=1;last_frame=frame;formats.add(mode)
 if frame%4096==0:
  progress=dict(part=args.part,frame=frame,total=end,video_frames=sent,audio_samples=audio_bytes//4,wall_seconds=round(time.monotonic()-started,1),state='recording')
  (out/'progress.json').write_text(json.dumps(progress,indent=2)+'\n');print(json.dumps(progress),flush=True)
captures={end}
if args.part=='intro':captures.update(n for n in (200,600,1200,1800,2400,3000) if n<end)
else:captures.update(n for n in (920,1200,10000,100000,200000,300000,389961,394924,400000) if n<end)
intro_started=False;intro_title_frame=None;intro_stop=None
def intro_observer(frame,ram):
 global intro_started,intro_title_frame,intro_stop
 running=int.from_bytes(bytes(ram[(0xd310+i)^1] for i in range(2)),'big')
 if running:intro_started=True
 if running and intro_title_frame is not None:
  intro_stop=frame;captures.add(frame)
 if intro_started and not running and intro_title_frame is None:
  intro_title_frame=frame;intro_stop=frame+900;assert intro_stop<end;captures.add(frame);captures.add(intro_stop)
if args.complete_intro:
 assert args.part=='intro' and not args.frames
 proof=json.loads((ROOT/'validation/v319-scene-live-vdp-rebuild01/report.json').read_bytes());assert proof['passed'] and proof['byte_identical_v319'] and proof['sha256']==sha(rom.read_bytes())
 symbols=(ROOT/'validation/v319-scene-live-vdp-rebuild01/project/out/release/symbol.txt').read_text();assert 'e0ffd310 b intro_running' in symbols
try:
 with contextlib.redirect_stdout(io.StringIO()):
  run(rom,end,out/'capture',captures,presses,skip_intro=False,ram_writes=FrameWrites(writes),core_options=cap['core_options'],video_observer=video,audio_observer=audio,ram_observer=intro_observer if args.complete_intro else None,stop_when=(lambda:bool(intro_stop and sent>=intro_stop)) if args.complete_intro else None)
finally:
 audio_file.close()
 if process is not None:
  process.stdin.close();exit_code=process.wait();assert exit_code==0,exit_code
 video_log.close();encode_progress.close()
if args.complete_intro:assert intro_title_frame and sent==intro_stop;end=sent
assert sent==end
actual=json.loads((out/'capture/capture.json').read_bytes());assert actual['fps']==fps and round(actual['sample_rate'])==rate
assert abs(audio_bytes/4/rate-sent/fps)<0.1,(audio_bytes/4/rate,sent/fps)
verified_final=False
if args.part=='gameplay' and end==403488:
 for stem,ext in [('ram','bin'),('frame','png')]:assert (out/f'capture/{stem}_{end:05d}.{ext}').read_bytes()==(trace/f'{stem}_{end:05d}.{ext}').read_bytes()
 verified_final=True
command=[str(ffmpeg),'-hide_banner','-nostdin','-i',str(silent),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-metadata','title=Golden Axe Warrior - Mega Drive native port V319 - Development gameplay','-metadata','comment=Development build; approach-only test protection is removed before boss combat. No health,inventory,progression or save-state imports.',str(movie)]
with (out/'mux.log').open('w') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
report=dict(passed=True,part=args.part,complete_intro=args.complete_intro,intro_title_frame=intro_title_frame,rom=str(rom),rom_sha256=sha(rom.read_bytes()),movie=str(movie),movie_bytes=movie.stat().st_size,movie_sha256=sha(movie.read_bytes()),frames=sent,fps=fps,duration_seconds=sent/fps,audio_samples=audio_bytes//4,audio_rate=rate,audio_video_duration_difference_seconds=audio_bytes/4/rate-sent/fps,geometry=list(initial_geometry),output_geometry=[960,720],video_codec='libx264-veryfast-crf18',audio_codec='aac192k',final_campaign_ram_and_picture_exact=verified_final,approach_guard_writes=len(writes) if args.part=='gameplay' else 0,boss_assistance=False,initial_sram=False,save_state_imports=0,wall_seconds=time.monotonic()-started,encoder=str(ffmpeg),encoder_version=imageio_ffmpeg.get_ffmpeg_version(),visibility='pending user choice',publication='not uploaded',limits=['Published developmentV319; newer unselected intro modules are not represented.','Recorded validation route with explicitly disclosed approach protection; not an unassisted playthrough or whole-SMS fidelity certificate.'])
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(out/'progress.json').write_text(json.dumps(dict(state='complete',frame=sent,total=end,movie=str(movie)),indent=2)+'\n');print(json.dumps(report),flush=True)
