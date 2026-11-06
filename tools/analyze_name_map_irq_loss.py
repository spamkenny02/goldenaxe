"""Check an instruction-derived name-map IRQ-loss prediction against real SMS runs."""
import argparse
import contextlib
import ctypes as c
import io
import json
import os
import subprocess
from pathlib import Path

from archive_lossless_evidence import sha
from run_core import ROOT, run
from validate_native_audio_reader import MODULES, Output as AudioOutput
from validate_native_audio_prefix import Work
from validate_native_source_irq import Input, Output as IrqOutput


def main():
    p=argparse.ArgumentParser();p.add_argument('--trial',default='02');a=p.parse_args()
    out=ROOT/'validation/menu-audio-v0316'/('name-map-model'+a.trial);out.mkdir(parents=True,exist_ok=False)
    env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
    command=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-I',str(ROOT.parents[1]/'work/sgdk/inc'),'-I',str(ROOT/'megadrive/src')]
    command += [str(ROOT/'megadrive/src'/(name+'.c'))for name in MODULES+['source_irq']]
    command += ['-o',str(out/'model.dll')]
    built=subprocess.run(command,capture_output=True,text=True,env=env);(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
    dll=c.CDLL(str(out/'model.dll'));reader=dll.source_audio_reader;irq=dll.source_irq
    reader.argtypes=[c.POINTER(c.c_uint8),c.POINTER(c.c_uint8),c.c_uint16,c.POINTER(c.c_uint8),c.POINTER(c.c_uint16),c.POINTER(Work),c.POINTER(AudioOutput)]
    irq.argtypes=[c.POINTER(c.c_uint8),c.POINTER(Input),c.POINTER(Work),c.POINTER(IrqOutput)]
    rom=(ROOT/'input/original.sms').read_bytes();low=(c.c_uint8*32768).from_buffer_copy(rom[:32768]);bank=(c.c_uint8*16384).from_buffer_copy(rom[0x18000:0x1c000])
    cases=[]
    for pal in (False,True):
      for cursor,typed in [(0,f)for f in range(1160,1241)]+[(n,f)for n in (1,11,12,23,24,35,36,39)for f in (1160,1183,1200)]:
        region='pal'if pal else'ntsc';snapshots={}
        def observe(frame,raw):
            if typed-1<=frame<=typed+2:snapshots[frame]=bytes(raw)
        folder=out/(region+'-'+str(cursor)+'-'+str(typed))
        moves=[(1110+2*i,1110+2*i,5)for i in range(cursor//12)]
        moves += [(1110+2*(cursor//12+i),1110+2*(cursor//12+i),7)for i in range(cursor%12)]
        with contextlib.redirect_stdout(io.StringIO()):run(ROOT/'input/original.sms',typed+2,folder,{typed-1,typed,typed+1,typed+2},
            [(200,220,0),(920,935,0),(1050,1065,0)]+moves+[(typed,typed+2,8)],skip_intro=False,ram_observer=observe,
            core_options={'genesis_plus_gx_region_detect':'pal'if pal else'auto'})
        before=snapshots[typed-1];at=snapshots[typed];after=snapshots[typed+1]
        assert before[0xa0]==cursor,(region,typed,cursor,before[0xa0])
        audio=(c.c_uint8*400).from_buffer_copy(before[0x1e00:0x1f90]);de=c.c_uint16(0);work=Work();audio_out=AudioOutput()
        assert reader(audio,low,32768,bank,c.byref(de),c.byref(work),c.byref(audio_out)) and not audio_out.error
        # Foreground typing has queued96 after the IRQ; exclude that one byte.
        mismatch=[i for i,(a,b)in enumerate(zip(bytes(audio),at[0x1e00:0x1f90]))if i!=8 and a!=b]
        assert not mismatch,(region,typed,'reader reconstruction',mismatch)
        actual_loss=at[0x1e01]==after[0x1e01]
        outcomes=[];whole=[]
        for alignment in range(28):
            state=bytearray(before[:0x50]+before[0x1d00:0x1e00]);state[0x2e]=1
            state=(c.c_uint8*336).from_buffer_copy(state);output=IrqOutput()
            entry=Input(193*3420+(72+alignment)*15,313 if pal else 262,0,0x20,16,0 if pal else 128)
            assert irq(state,c.byref(entry),c.byref(work),c.byref(output)),(region,typed,'IRQ reconstruction')
            template=bytearray(336);template[0x2e]=1;template[0x35]=0xdd
            template=(c.c_uint8*336).from_buffer_copy(template);generic=IrqOutput()
            assert irq(template,c.byref(entry),c.byref(work),c.byref(generic))
            assert generic.whole.tstates==output.whole.tstates,(region,cursor,typed,'template IRQ')
            # Frontend frame begins one scanline before source VINT. The
            # BB3->0914 foreground path measured for typing A is2034T.
            total=228+alignment+output.whole.tstates+2034+44842
            outcomes.append(total>=(71364 if pal else 59736));whole.append(output.whole.tstates)
        cases.append(dict(region=region,cursor=cursor,typed_frame=typed,audio_work=work.tstates,
                          actual_loss=actual_loss,predictions=sorted(set(outcomes)),irq_work_min_max=[min(whole),max(whole)]))
    result=dict(cases=cases,source_sha256=sha(rom),ram_writes=0,sram_imports=0,
                correct_unambiguous_cases=sum(r['predictions']==[r['actual_loss']]for r in cases),
                driver_sha256=sha(Path(__file__).read_bytes()),scope='Natural first glyph input at dense timings and representative letters, plus generic empty-queue IRQ template equivalence. Not a full input/IRQ scheduler proof.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Unambiguous correct IRQ-loss predictions:',result['correct_unambiguous_cases'],'/',len(cases),flush=True)
    print([r for r in cases if r['predictions']!=[r['actual_loss']]],flush=True)


if __name__=='__main__':main()
