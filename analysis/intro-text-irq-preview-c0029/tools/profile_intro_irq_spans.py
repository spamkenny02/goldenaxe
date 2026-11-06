"""Measure source intro IRQ/foreground boundaries with actual frame raster."""
import contextlib
import ctypes as c
import io
import json
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from run_core import ROOT,run

def main():
    out=ROOT/'validation/menu-raster-v0316/irq-spans01';out.mkdir(parents=True,exist_ok=False)
    core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_intro_irq_raster_libretro.dll';dll=c.CDLL(str(core));dll.gaw_timing_events.restype=c.POINTER(c.c_uint64);dll.gaw_timing_count.restype=c.c_uint
    cases=[]
    for region in ('ntsc','pal'):
        dll.gaw_timing_reset();previous=0;events=[];snapshots=bytearray();rows=[]
        def observe(frame,raw):
            nonlocal previous
            count=dll.gaw_timing_count();assert count<65536;ptr=dll.gaw_timing_events()
            for n in range(previous,count):
                pc,elapsed,irq,raster,clock,hl,de,bc=[int(ptr[n*8+i])for i in range(8)]
                events.append(dict(frame=frame,pc=pc,elapsed=elapsed,irq=irq,raster=raster,clock=clock,hl=hl,de=de,bc=bc))
            previous=count;snapshots.extend(raw[:80]+raw[0x1d00:0x1f90])
            rows.append(dict(frame=frame,clock=raw[0x2f],callback=int.from_bytes(raw[0x1cec:0x1cee],'little'),counter=raw[0x1ce2],line=raw[0x1ce0]))
        folder=out/region
        with contextlib.redirect_stdout(io.StringIO()):run(ROOT/'input/original.sms',6500,folder,set(),[],skip_intro=False,core=core,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':'pal'if region=='pal'else'auto'})
        reference=json.loads(evidence(ROOT/f'validation/menu-raster-v0316/logical-clock26/{region}-sms/observations.json'))
        assert rows[:len(reference)]==reference
        (folder/'events.json').write_text(json.dumps(events,indent=2)+'\n');(folder/'snapshots.bin').write_bytes(snapshots)
        spans=[]
        for i,event in enumerate(events):
            if event['pc']!=0x384 or event['de']!=0x7b00 or event['bc']!=768:continue
            before=next(e for e in reversed(events[:i])if e['pc']==0xbb3)
            end=next(e for e in events[i+1:]if e['pc']==0xf09)
            actor_start=next(e for e in reversed(events[:i])if e['pc']==0xf32)
            actor_end=next(e for e in events if actor_start['elapsed']<e['elapsed']<event['elapsed']and e['pc']==0xf12)
            spans.append(dict(frame=before['frame'],clock=before['clock'],next_request_frame=end['frame'],raster_return=before['raster'],raster_request=end['raster'],
                foreground_tstates=((end['elapsed']-before['elapsed'])-(end['irq']-before['irq']))//15,
                actor_tstates=((actor_end['elapsed']-actor_start['elapsed'])-(actor_end['irq']-actor_start['irq']))//15,
                requested_after_audio_only_irq=end['frame']>before['frame']))
        cases.append(dict(region=region,events=len(events),official_clock_trace_exact_frames=len(reference),text_spans=spans))
        print(region,'text spans',len(spans),'crossed frames',[(r['frame'],r['next_request_frame'])for r in spans if r['requested_after_audio_only_irq']],flush=True)
    (out/'report.json').write_text(json.dumps(dict(cases=cases,source_sha256=sha((ROOT/'input/original.sms').read_bytes()),core_sha256=sha(core.read_bytes()),ram_writes=0,scope='Physical raster and foreground source spans. Slot3 is raster, not room ID.'),indent=2)+'\n')

if __name__=='__main__':main()
