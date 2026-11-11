"""Record an authenticated SMS input route, with its actual audio and coverage scope.

No game-state imports. Input/approach protection comes exclusively from the
hashed route. A finished campaign must never be presented as an NPC 100% run.
"""
import argparse, contextlib, csv, hashlib, io, json, subprocess, sys, time, wave
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from run_core import ROOT, FrameWrites, run
from assisted_prefix import prefix_writes

sys.path.insert(0, str(ROOT.parents[1] / 'work/video-tools'))
import imageio_ffmpeg


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--route',default='sms_full_ntsc')
    parser.add_argument('--trace',help='Alternatively record an independently replayed validation trace')
    parser.add_argument('--from-frame',type=int,default=1,help='Video excerpt starts here; the emulator still replays every earlier frame from boot')
    parser.add_argument('--out',required=True)
    parser.add_argument('--frames',type=int,help='Short encoder probe only; not a completed run')
    parser.add_argument('--require-100',action='store_true')
    args=parser.parse_args()
    trace_presses=None;trace_writes=None
    if args.trace:
        source=(ROOT/'validation'/args.trace).resolve();assert source.is_relative_to((ROOT/'validation').resolve())
        capture=json.loads((source/'capture.json').read_bytes());assert capture['sram_input'] is None
        stop=capture['frames'];proof=source.with_name(source.name+f'-assisted-fixed-replay-{stop}')
        witness=json.loads((proof/'replay_report.json').read_bytes());assert witness['passed'] and not witness['primary_state_imports']
        evidence={n:digest(source/n) for n in ('capture.json','controls.json','assistance.json')}
        assert evidence==witness['evidence']
        trace_writes=prefix_writes(source,capture,True);assert all(a==0x305 and d in (b'\0',b'\x81') for _,a,d in trace_writes)
        trace_presses=list(map(tuple,capture['presses']));controls=json.loads((source/'controls.json').read_bytes())
        for i,row in enumerate(controls):
            last=controls[i+1]['frame']-1 if i+1<len(controls) else stop
            trace_presses.extend((row['frame'],min(last,stop),k) for k in row['buttons'] if row['frame']<=stop)
        raw=(proof/f'ram_{stop:05d}.bin').read_bytes();assert len(raw)==8192
        route=dict(system='sms',region='ntsc',frames=stop,full_campaign=False,all_npcs_complete=False,
            approach_writes=len(trace_writes),core_options=capture['core_options'],
            historical_recording_rom_sha256=capture['rom_sha256'],validated_core_sha256=witness['core_sha256'],
            expected_final=dict(game=raw[0x1d],room=int.from_bytes(raw[0xb9:0xbb],'little'),health=raw[0x318],crystals=sum(bool(b&128) for b in raw[0xcf:0xd8])),
            expected_final_ram_sha256=hashlib.sha256(raw).hexdigest(),
            expected_final_pixels_sha256=hashlib.sha256(Image.open(proof/f'frame_{stop:05d}.png').convert('RGB').tobytes()).hexdigest())
        route_hash=hashlib.sha256(json.dumps(evidence,sort_keys=True).encode()).hexdigest()
    else:
        route=json.loads((ROOT/'testkit/manifest.json').read_bytes())['routes'][args.route]
        csvpath=ROOT/'testkit/routes'/route['csv'];route_hash=digest(csvpath);assert route_hash==route['csv_sha256']
    assert route['system']=='sms' and route['region']=='ntsc'
    if args.require_100:
        assert route['all_npcs_complete'] and route.get('all_side_quests_complete'), 'NPC/quest coverage is still incomplete'
    out=(ROOT/'validation'/args.out).resolve()
    assert out.is_relative_to((ROOT/'validation').resolve()) and not out.exists()
    rom=ROOT/'input/original.sms';core=ROOT.parents[1]/'work/libretro/genesis_plus_gx_libretro.dll'
    assert digest(rom)==route['historical_recording_rom_sha256']
    assert digest(core)==route['validated_core_sha256']
    end=args.frames or route['frames'];assert 0<end<=route['frames']
    first=args.from_frame;assert 1<=first<=end
    complete=end==route['frames'];presses=[];writes=FrameWrites()
    if args.trace:
        presses=trace_presses;writes=FrameWrites([w for w in trace_writes if w[0]<=end])
    else:
      with csvpath.open(newline='') as stream:
        for row in csv.DictReader(stream):
            row_first,last,mask,guard=(int(row[k]) for k in ['start','end','mask','guard'])
            if row_first>end:continue
            last=min(last,end)
            presses.extend((row_first,last,k) for k in range(16) if mask&(1<<k))
            if guard!=-1:
                assert guard in (0,0x81)
                writes.extend((f,0x305,bytes([guard])) for f in range(row_first,last+1))
    out.mkdir();fps=59.92274340431231;rate=44100;ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    silent=out/'video-silent.mp4';wav=out/'audio.wav';movie=out/'sms-gameplay.mp4'
    video_log=(out/'encode.log').open('w');process=None;sent=0;last=None;audio_bytes=0;state={};ending=False;observed=0;native=None
    start=time.monotonic();audio_file=wave.open(str(wav),'wb');audio_file.setparams((2,2,rate,0,'NONE','not compressed'))
    def audio(data):
        nonlocal audio_bytes
        if observed+1<first:return
        assert len(data)%4==0
        audio_file.writeframesraw(data);audio_bytes+=len(data)
    def video(frame,data,width,height,pitch,mode):
        nonlocal process,sent,last,native
        if frame==0:return
        assert mode==2
        if data is not None:native=(data,width,height,pitch)
        if frame<first:return
        assert frame==first+sent and native is not None
        data,width,height,pitch=native
        packed=data if pitch==width*2 else b''.join(data[y*pitch:y*pitch+width*2] for y in range(height))
        last=packed if (width,height)==(256,192) else cv2.resize(np.frombuffer(packed,dtype='<u2').reshape(height,width),(256,192),interpolation=cv2.INTER_NEAREST).tobytes()
        assert last is not None
        if process is None:
            command=[ffmpeg,'-hide_banner','-nostdin','-filter_threads','1','-f','rawvideo','-pixel_format','rgb565le',
                '-video_size','256x192','-framerate',f'{fps:.12f}','-i','pipe:0','-an','-vf','scale=768:576:flags=neighbor,setsar=1',
                '-c:v','libx264','-preset','veryfast','-threads','2','-crf','18','-pix_fmt','yuv420p',str(silent)]
            (out/'encoder-command.json').write_text(json.dumps(command,indent=2)+'\n')
            process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=video_log)
        process.stdin.write(last);sent+=1
        if frame%8192==0:
            p=dict(frame=frame,total=end,wall_seconds=round(time.monotonic()-start,1),state='recording',all_npcs_complete=route['all_npcs_complete'])
            (out/'progress.json').write_text(json.dumps(p,indent=2)+'\n');print(json.dumps(p),flush=True)
    def observe(frame,raw):
        nonlocal ending,observed
        observed=frame
        state.update(game=raw[0x1d],room=int.from_bytes(raw[0xb9:0xbb],'little'),health=raw[0x318],crystals=sum(bool(b&128) for b in raw[0xcf:0xd8]))
        ending|=state['game']==14
        if raw[0x305]>128:
            assert not any((0x63<=raw[i]<=0x6d or 0x78<=raw[i]<=0x7c) and raw[i+24]>0 for i in range(0x600,0x900,48)), (frame,'approach protection overlaps a living boss')
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            run(rom,end,out/'capture',{end},presses,core=core,skip_intro=False,ram_writes=writes,
                video_observer=video,audio_observer=audio,ram_observer=observe,core_options=route['core_options'])
    finally:
        audio_file.close()
        if process:
            process.stdin.close();assert process.wait()==0
        video_log.close()
    assert sent==end-first+1
    av_delta=audio_bytes/4/rate-sent/fps;assert abs(av_delta)<.1
    if complete:
        assert state==route['expected_final']
        if route.get('full_campaign'):assert ending
        assert len(writes)==route['approach_writes']
        assert digest(out/f'capture/ram_{end:05d}.bin')==route['expected_final_ram_sha256']
        pixels=Image.open(out/f'capture/frame_{end:05d}.png').convert('RGB').tobytes()
        assert hashlib.sha256(pixels).hexdigest()==route['expected_final_pixels_sha256']
    scope='All NPCs and side quests' if args.require_100 else ('Recorded NPC route excerpt; global NPC and side-quest coverage incomplete' if args.trace else 'Campaign recording; NPC and side-quest coverage incomplete')
    command=[ffmpeg,'-hide_banner','-nostdin','-i',str(silent),'-i',str(wav),'-map','0:v:0','-map','1:a:0',
        '-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-metadata','title=Golden Axe Warrior - Master System',
        '-metadata','comment='+scope+'. Recorded approach-only protection, removed before bosses. No save imports.',str(movie)]
    with (out/'mux.log').open('w') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    cap=cv2.VideoCapture(str(movie));assert cap.isOpened()
    assert int(cap.get(cv2.CAP_PROP_FRAME_COUNT))==sent
    assert (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))==(768,576)
    cap.release()
    report=dict(passed=True,movie=str(movie),movie_sha256=digest(movie),movie_bytes=movie.stat().st_size,
        route=args.trace or args.route,route_sha256=route_hash,rom_sha256=digest(rom),core_sha256=digest(core),frames=sent,fps=fps,
        first_emulated_video_frame=first,emulated_frames_from_boot=end,recorder_sha256=digest(Path(__file__)),
        duration_seconds=sent/fps,audio_samples=audio_bytes//4,audio_rate=rate,audio_video_delta_seconds=av_delta,
        full_campaign_replayed=bool(complete and route.get('full_campaign')),all_npcs_complete=bool(complete and route['all_npcs_complete']),
        all_side_quests_complete=bool(complete and route.get('all_side_quests_complete',False)),
        scope=scope,ending_seen=ending,final=state,approach_guard_writes=len(writes),boss_assistance=False,
        save_imports=0,final_ram_and_pixels_exact=complete,wall_seconds=time.monotonic()-start)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)


if __name__=='__main__':main()
