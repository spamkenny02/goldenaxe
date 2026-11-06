"""Reconstruct source text first-half scheduling from native IRQ/audio costs."""
import ctypes as c
import json
import os
import subprocess
from collections import Counter
from run_core import ROOT
from archive_lossless_evidence import sha
from validate_native_audio_reader import MODULES,Output as AudioOutput
from validate_native_audio_prefix import Work
from validate_native_source_irq import Input,Output as IrqOutput

def main():
    base=ROOT/'validation/menu-raster-v0316/irq-spans01';out=ROOT/'validation/menu-raster-v0316/text-irq-model01';out.mkdir(exist_ok=False)
    env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
    args=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-I',str(ROOT.parents[1]/'work/sgdk/inc'),'-I',str(ROOT/'megadrive/src')]+[str(ROOT/'megadrive/src'/(name+'.c'))for name in MODULES+['source_irq']]+['-o',str(out/'model.dll')]
    built=subprocess.run(args,env=env,capture_output=True,text=True);(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
    dll=c.CDLL(str(out/'model.dll'));reader=dll.source_audio_reader;irq=dll.source_irq
    reader.argtypes=[c.POINTER(c.c_uint8),c.POINTER(c.c_uint8),c.c_uint16,c.POINTER(c.c_uint8),c.POINTER(c.c_uint16),c.POINTER(Work),c.POINTER(AudioOutput)];irq.argtypes=[c.POINTER(c.c_uint8),c.POINTER(Input),c.POINTER(Work),c.POINTER(IrqOutput)]
    rom=(ROOT/'input/original.sms').read_bytes();low=(c.c_uint8*32768).from_buffer_copy(rom[:32768]);bank=(c.c_uint8*16384).from_buffer_copy(rom[0x18000:0x1c000]);lengths=[len(line)for line in rom[0x1b9ce:rom.index(0,0x1b9ce)].split(b'\xff')];cases=[]
    measured=json.loads((base/'report.json').read_bytes())
    for region in ('ntsc','pal'):
        events=json.loads((base/region/'events.json').read_bytes());snap=(base/region/'snapshots.bin').read_bytes();spans=next(r['text_spans']for r in measured['cases']if r['region']==region)
        for index,span in enumerate(spans[::2]):
            frame=span['frame'];before=snap[(frame-2)*736:(frame-1)*736];after=snap[(frame-1)*736:frame*736]
            state=(c.c_uint8*400).from_buffer_copy(before[336:]);de=c.c_uint16(0);work=Work();output=AudioOutput();assert reader(state,low,32768,bank,c.byref(de),c.byref(work),c.byref(output))and not output.error
            assert bytes(state)==after[336:],(region,frame,'audio reader')
            entry=next(e for e in reversed(events)if e['frame']==frame and e['pc']==0x137 and e['clock']==(span['clock']-1)&255)
            ret=next(e for e in events if e['frame']==frame and e['pc']==0xbb3 and e['clock']==span['clock'])
            irqs=(c.c_uint8*336).from_buffer_copy(before[:336]);irqs[0x2e]=1;result=IrqOutput();lines=313 if region=='pal'else 262
            inp=Input((entry['raster']+192*3420)%(lines*3420),lines,0,0,16,0 if region=='pal'else 128);assert irq(irqs,c.byref(inp),c.byref(work),c.byref(result))
            measured_irq=(ret['irq']-entry['irq'])//15+72
            # BB3 follows IRQ return and a short C02E polling tail.
            predicted_return=entry['raster']//15+result.whole.tstates-72
            predicted_request=predicted_return+span['foreground_tstates']+187
            prediction=predicted_request>=lines*228+228
            next_return=next(e for e in events if e['elapsed']>ret['elapsed']and e['pc']==0xbb3)
            actual=next_return['frame']>frame+1
            cases.append(dict(region=region,line=index+1,frame=frame,glyphs=lengths[index],audio_work=work.tstates,modeled_irq=result.whole.tstates,measured_irq=measured_irq,
                return_tail_tstates=ret['raster']//15-predicted_return,foreground=span['foreground_tstates'],actor_work=span['actor_tstates'],constant_foreground=span['foreground_tstates']-span['actor_tstates']-92*lengths[index],predicted_loss=prediction,actual_loss=actual))
        rows=[r for r in cases if r['region']==region];print(region,'constants',Counter(r['constant_foreground']for r in rows),'IRQ errors',Counter(r['modeled_irq']-r['measured_irq']for r in rows),'return tail',Counter(r['return_tail_tstates']for r in rows),'mispredictions',[(r['frame'],r['predicted_loss'],r['actual_loss'])for r in rows if r['predicted_loss']!=r['actual_loss']],flush=True)
    (out/'report.json').write_text(json.dumps(dict(cases=cases,source_sha256=sha(rom),scope='Predictions currently use measured actor foreground cost. No production integration or general actor cost claim.'),indent=2)+'\n')

if __name__=='__main__':main()
