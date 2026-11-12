"""Keep one real cold core paused between independently generated checkpoints.

Only already recorded buttons and hurt writes feed this core. No save states,
RAM imports, controller decisions or skipped virtual frames are used.
"""
import argparse,contextlib,io,json,os,shutil,string,subprocess,sys,time,traceback
from pathlib import Path
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from assisted_prefix import recording
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols


def atomic(path,value):
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');tmp.replace(path)


class ReplayStream:
    def __init__(self,folder,suffix='',sms=False,rom=None):
        self.folder=folder.resolve();assert self.folder.is_relative_to(ROOT/'validation')
        assert all(c in string.ascii_letters+string.digits+'-_' for c in suffix)
        self.folder.mkdir(exist_ok=False);self.suffix=suffix;self.sms=sms;self.rom=rom;self.process=None;self.number=0
        self.log=(self.folder/'worker.log').open('wb')

    def prove(self,trace):
        source=(ROOT/'validation'/trace).resolve();assert source.is_relative_to(ROOT/'validation')
        capture=json.loads((source/'capture.json').read_bytes());self.number+=1
        proof=source.with_name(source.name+f'-assisted-fixed-replay-{capture["frames"]}'+self.suffix)
        assert not proof.exists()
        atomic(self.folder/f'request-{self.number:04d}.json',dict(trace=trace))
        if self.process is None:
            self.process=subprocess.Popen([sys.executable,'-u',str(Path(__file__).resolve()),
                '--worker',str(self.folder),'--suffix='+self.suffix,*(['--sms'] if self.sms else []),*(['--rom',str(self.rom)] if self.rom else [])],cwd=ROOT,
                stdout=self.log,stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        deadline=time.monotonic()+600
        while not (proof/'replay_report.json').exists():
            if self.process.poll() is not None:
                if (proof/'replay_report.json').exists():break
                raise RuntimeError('Cold replay worker stopped; inspect '+str(self.folder/'worker.log'))
            if time.monotonic()>=deadline:
                if (proof/'replay_report.json').exists():break
                raise TimeoutError('Cold replay checkpoint timed out; inspect worker state before resuming')
            time.sleep(.05)
        result=json.loads((proof/'replay_report.json').read_bytes())
        assert result['passed'] and result['frames']==capture['frames']
        return result

    def close(self):
        if self.process is not None and self.process.poll() is None:
            atomic(self.folder/'stop.json',dict(stop=True))
            self.process.wait(timeout=60)
            assert self.process.returncode==0,'Cold replay worker failed during closure'
        self.log.close()


def worker(folder,suffix,sms=False,rom=None):
    folder=folder.resolve();assert folder.is_relative_to(ROOT/'validation')
    assert all(c in string.ascii_letters+string.digits+'-_' for c in suffix)
    rom=Path(rom) if rom else ROOT/('input/original.sms' if sms else 'gaw-megadrive.bin');digest=sha(rom.read_bytes())
    sy=None if sms else symbols(ROOT/'megadrive/out/release/symbol.txt')
    writes=FrameWrites();masks=[];previous_frame=-1;request_number=0;target=None
    captures=set();options=None;stopped=False;rows=[];guard_frames=0
    core=ROOT.parents[1]/'work/libretro/genesis_plus_gx_libretro.dll'
    core_digest=sha(core.read_bytes());driver_digest=sha(Path(__file__).read_bytes())
    out=folder/'cold-core';started=time.perf_counter();input_error=None
    def next_request():
        nonlocal request_number,target,masks,previous_frame,options,stopped
        path=folder/f'request-{request_number+1:04d}.json'
        while not path.exists():
            if (folder/'stop.json').exists():stopped=True;return
            time.sleep(.05)
        request_number+=1;request=json.loads(path.read_bytes())
        source=(ROOT/'validation'/request['trace']).resolve();assert source.is_relative_to(ROOT/'validation')
        c=json.loads((source/'capture.json').read_bytes());a,w=recording(source,c)
        assert c['rom_sha256']==digest and c['sram_input'] is None
        assert not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance']
        assert all(addr==(0x305 if sms else sy['hero_hurt']) and value in
                   ((b'\0',b'\x81') if sms else (b'\0\0',b'\0\x81'))for _,addr,value in w)
        assert c['frames']>previous_frame and w[:len(writes)]==list(writes)
        assert all(f>previous_frame for f,_,_ in w[len(writes):])
        controls=json.loads((source/'controls.json').read_bytes());presses=[tuple(row)for row in c['presses']]
        for i,row in enumerate(controls):
            stop=controls[i+1]['frame']-1 if i+1<len(controls)else c['frames']
            presses.extend((row['frame'],min(stop,c['frames']),b)for b in row['buttons']if row['frame']<=c['frames'])
        new_masks=compile_fixed_inputs(presses,c['frames'])
        assert new_masks[:previous_frame+1]==masks[:previous_frame+1],'Recorded input prefix changed'
        if options is None:options=c['core_options']
        else:assert options==c['core_options']
        writes.extend(w[len(writes):]);masks=new_masks
        target=dict(source=source,capture=c,assist=a,trace=request['trace'])
        captures.add(c['frames'])
    next_request();assert target is not None
    cached_frame=-1;cached_buttons=[]
    def inputs(frame):
        nonlocal cached_frame,cached_buttons,input_error
        if not 0<=frame<len(masks):
            input_error='Input requested past verified recorded interval';return []
        if frame!=cached_frame:
            cached_frame=frame;cached_buttons=[b for b in range(16)if masks[frame]&(1<<b)]
        return cached_buttons
    def observe(frame,raw):
        nonlocal previous_frame,guard_frames
        assert input_error is None,input_error
        hurt=raw[0x305] if sms else int.from_bytes(bytes(raw[(sy['hero_hurt']+i)^1]for i in range(2)),'big')
        if hurt>128:
            guard_frames+=1
            for i in range(16):
                at=(0x600 if sms else sy['world_actor_state'])+i*48
                kind=raw[at if sms else at^1];hp=raw[at+24 if sms else (at+24)^1]
                assert not (hp and (0x63<=kind<=0x6d or 0x78<=kind<=0x7c)),'Test guard overlaps live boss'
    def checkpoint(frame):
        nonlocal previous_frame
        if frame!=target['capture']['frames']:return
        source=target['source'];c=target['capture'];a=target['assist']
        for stem,ext in [('ram','bin'),('frame','png')]:
            name=f'{stem}_{frame:05d}.{ext}'
            assert (source/name).read_bytes()==(out/name).read_bytes(),(target['trace'],name)
        proof=source.with_name(source.name+f'-assisted-fixed-replay-{frame}'+suffix);proof.mkdir(exist_ok=False)
        for stem,ext in [('ram','bin'),('frame','png')]:
            name=f'{stem}_{frame:05d}.{ext}';shutil.copyfile(out/name,proof/name)
        result=dict(passed=True,assisted_route=True,natural_campaign_proof=False,
            rom_sha256=digest,core_sha256=core_digest,frames=frame,feedback_reads=False,
            ram_injections=True,injection_count=len(writes),last_injection_frame=writes[-1][0],
            release_write_frame=a['release_write_frame'],first_boss_combat=a['first_boss_combat'],
            boss_assistance=False,approach_only=a['first_boss_combat']is None,
            whole_ram_bytes=8192 if sms else 65536,final_png_exact=True,primary_state_imports=0,
            indexed_writes=True,cold_boot_count=1,shared_cold_stream=folder.relative_to(ROOT).as_posix(),
            shared_stream_checkpoint=request_number,new_emulated_frames=frame-max(previous_frame,0),
            guard_frames_checked=guard_frames,live_boss_guard_check=True,
            driver_sha256=driver_digest,elapsed_seconds=time.perf_counter()-started,
            evidence={name:sha((source/name).read_bytes())for name in ('capture.json','controls.json','assistance.json')},
            scope='One cold core advances recorded input between checkpoints and pauses while waiting for the next recording. No save-state import or feedback-based input.')
        atomic(proof/'replay_report.json',result)
        rows.append(dict(trace=target['trace'],frames=frame,whole_ram_png_exact=True))
        atomic(folder/'checkpoints.json',dict(rom_sha256=digest,cold_boot_count=1,checkpoints=rows))
        print('COLD STREAM CHECKPOINT',request_number,frame,target['trace'],flush=True)
        previous_frame=frame;next_request()
    with contextlib.redirect_stdout(io.StringIO()):
        run(rom,1000000,out,captures,[],skip_intro=False,core=core,core_options=options,
            input_provider=inputs,ram_writes=writes,ram_observer=observe,stop_when=lambda:stopped,post_frame_observer=checkpoint)
    assert stopped,'Cold stream reached its frame limit'
    atomic(folder/'completed.json',dict(passed=True,rom_sha256=digest,cold_boot_count=1,
        primary_state_imports=0,checkpoints=rows,emulated_frames=previous_frame))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--worker',type=Path,required=True);p.add_argument('--suffix',default='');p.add_argument('--sms',action='store_true');p.add_argument('--rom',type=Path)
    a=p.parse_args()
    try:worker(a.worker,a.suffix,a.sms,a.rom)
    except Exception:
        atomic(a.worker/'failure.json',dict(passed=False,error=traceback.format_exc()));raise
