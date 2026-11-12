"""Film one independently replayed MD branch, with real game audio and provenance."""
import argparse,contextlib,hashlib,io,json,subprocess,sys,wave
from pathlib import Path
import cv2,numpy as np
from run_core import ROOT,run,FrameWrites
from assisted_prefix import prefix_writes
from validate_playable_sprite_limit import symbols
from write_atomic_report import write_bytes
sys.path.insert(0,str(ROOT.parents[1]/'work/video-tools'))
import imageio_ffmpeg
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--trace',required=True);p.add_argument('--rom',required=True);p.add_argument('--from-frame',type=int,required=True);p.add_argument('--name',required=True);p.add_argument('--game-written-continue',action='store_true');a=p.parse_args()
    source=(ROOT/'validation'/a.trace).resolve();assert source.is_relative_to(ROOT/'validation')
    cap=json.loads((source/'capture.json').read_bytes());end=cap['frames'];rom=(ROOT/a.rom).resolve();assert sha(rom)==cap['rom_sha256']
    core=ROOT.parents[1]/'work/libretro/genesis_plus_gx_libretro.dll';core_sha=sha(core)
    assert core_sha=='d17f2392115b3cd54258a1fa6c4195ddadc19b0805ebcca400db5162b1793516'
    initial=None
    if a.game_written_continue:
        from genuine_continue_source import verified_sram
        initial=verified_sram(source,cap)
    else:assert cap['sram_input'] is None
    assert 1<=a.from_frame<=end
    assisted=bool(cap['test_ram_writes']);proof=source.with_name(source.name+(f'-assisted-fixed-replay-{end}' if assisted else '-fixed-replay'))
    witness=json.loads((proof/'replay_report.json').read_bytes());assert witness['passed'] and witness['rom_sha256']==cap['rom_sha256'] and witness['final_png_exact']
    assert witness['evidence']=={n:sha(source/n) for n in (['capture.json','controls.json','assistance.json'] if assisted else ['capture.json','controls.json'])}
    writes=[] if initial is not None else prefix_writes(source,cap,assisted);controls=json.loads((source/'controls.json').read_bytes());presses=list(map(tuple,cap['presses']))
    for i,row in enumerate(controls):
        stop=controls[i+1]['frame']-1 if i+1<len(controls) else end
        presses.extend((row['frame'],min(stop,end),k) for k in row['buttons'])
    out=(ROOT/'videos/md-annexes-2026-11-12'/a.name).resolve();assert out.is_relative_to(ROOT/'videos/md-annexes-2026-11-12') and not out.exists();out.mkdir(parents=True)
    temp=ROOT/'validation/md-annex-videos'/a.name;assert not temp.exists();temp.mkdir(parents=True)
    fps=cap['fps'];rate=round(cap['sample_rate']);assert rate==44100
    ff=imageio_ffmpeg.get_ffmpeg_exe();sy=symbols(ROOT/'megadrive/out/release/symbol.txt');last=None;observed=0;sent=0;audio_bytes=0;encoder=None
    wav=temp/'audio.wav';silent=temp/'silent.mp4';movie=out/(a.name+'.mp4');log=(temp/'encode.log').open('w')
    audio_file=wave.open(str(wav),'wb');audio_file.setparams((2,2,rate,0,'NONE','not compressed'))
    def audio(data):
        nonlocal audio_bytes
        if observed+1<a.from_frame:return
        audio_file.writeframesraw(data);audio_bytes+=len(data)
    def video(frame,data,w,h,pitch,mode):
        nonlocal last,sent,encoder
        if not frame:return
        assert mode==2
        if data is not None:last=(data,w,h,pitch)
        if frame<a.from_frame:return
        assert last is not None and frame==a.from_frame+sent
        data,w,h,pitch=last;packed=b''.join(data[y*pitch:y*pitch+w*2] for y in range(h))
        if (w,h)!=(256,224):packed=cv2.resize(np.frombuffer(packed,dtype='<u2').reshape(h,w),(256,224),interpolation=cv2.INTER_NEAREST).tobytes()
        if encoder is None:
            encoder=subprocess.Popen([ff,'-hide_banner','-nostdin','-filter_threads','1','-f','rawvideo','-pixel_format','rgb565le','-video_size','256x224','-framerate',f'{fps:.12f}','-i','pipe:0','-an','-vf','scale=960:720:flags=neighbor,setsar=1','-c:v','libx264','-preset','veryfast','-threads','2','-crf','18','-pix_fmt','yuv420p',str(silent)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log)
        encoder.stdin.write(packed);sent+=1
    def observe(frame,raw):
        nonlocal observed
        observed=frame;word=lambda n:raw[sy[n]]|(raw[sy[n]+1]<<8)
        assert word('sound_unhandled_command')==0
        if word('hero_hurt')>128:
            for n in range(16):
                at=sy['world_actor_state']+48*n;kind=raw[at^1];hp=raw[(at+24)^1]
                assert not hp or not (0x63<=kind<=0x6d or 0x78<=kind<=0x7c),('guard overlaps live boss',frame)
    try:
        with contextlib.redirect_stdout(io.StringIO()):run(rom,end,temp/'capture',{end},presses,core=core,skip_intro=False,ram_writes=FrameWrites(writes),video_observer=video,audio_observer=audio,ram_observer=observe,sram_in=initial,core_options=cap['core_options'])
    finally:
        audio_file.close()
        if encoder:encoder.stdin.close();assert encoder.wait()==0
        log.close()
    assert sent==end-a.from_frame+1
    for stem,ext in [('ram','bin'),('frame','png')]:assert (temp/f'capture/{stem}_{end:05d}.{ext}').read_bytes()==(source/f'{stem}_{end:05d}.{ext}').read_bytes(),stem
    delta=audio_bytes/4/rate-sent/fps;assert abs(delta)<.1
    with (temp/'mux.log').open('w') as f:subprocess.run([ff,'-hide_banner','-nostdin','-i',str(silent),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-map_chapters','-1','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-metadata','comment=Separate genuine game-written Continue branch, real audio, no synthetic SRAM or RAM edits.' if initial else 'comment=Separate MD branch, real recorded controls and audio. Approach protection disclosed; no save or quest imports. Not an all-NPC certificate.',str(movie)],stdout=f,stderr=subprocess.STDOUT,check=True)
    with (temp/'decode.log').open('w') as f:subprocess.run([ff,'-hide_banner','-nostdin','-v','error','-xerror','-threads','2','-i',str(movie),'-map','0:v:0','-map','0:a:0','-f','null','-'],stdout=f,stderr=subprocess.STDOUT,check=True)
    reader=cv2.VideoCapture(str(movie));assert reader.isOpened() and round(reader.get(cv2.CAP_PROP_FRAME_COUNT))==sent;reader.release()
    result=dict(passed=True,trace=a.trace,rom_sha256=cap['rom_sha256'],movie=movie.relative_to(ROOT).as_posix(),movie_sha256=sha(movie),frames=sent,first_emulated_frame=a.from_frame,last_emulated_frame=end,fps=fps,duration_seconds=sent/fps,audio_video_delta_seconds=delta,full_audio_video_decoded=True,final_ram_and_pixels_exact=True,ram_writes=len(writes),boss_assistance=False,sram_imports=int(initial is not None),genuine_game_written_continue=initial is not None,all_npcs_complete=False,proof_sha256=sha(proof/'replay_report.json'))
    result.update(core_sha256=core_sha,recorder_sha256=sha(Path(__file__)))
    write_bytes(out/'report.json',(json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result),flush=True)
    # Only this successful encode's known intermediates; preserve all traces.
    for file in (wav,silent):assert file.resolve().is_relative_to(temp.resolve());file.unlink()
if __name__=='__main__':main()
