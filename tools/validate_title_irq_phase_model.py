"""Dynamic native IRQ/audio work against original title live snapshots."""
import argparse,ctypes as c,hashlib,json,os,struct,subprocess
p=argparse.ArgumentParser();p.add_argument('--out',default='title-irq-phase-model01');a=p.parse_args()
from compression import zstd
from run_core import ROOT
from validate_native_audio_reader import MODULES
out=(ROOT/'validation'/a.out).resolve();assert out.is_relative_to(ROOT/'validation');assert not out.exists();out.mkdir()
wrapper=r"""
#include "source_irq.h"
#include "source_audio_fast.h"
static void ignore(void *context,const u8 *writes,u16 count) {(void)context;(void)writes;(void)count;}
__declspec(dllexport) u8 title_case(u8 *ram,u8 *audio,const u8 *low,const u8 *bank,u16 de,u32 raster,u16 lines,u32 *result) {
 SourceIrqInput input={0};SourceIrqOutput output;SourceClockWork work;SourceAudioReaderStatus status;
 input.raster=raster;input.lines=lines;input.reset_mask=16;input.compensation=audio[3];
 if(!source_audio_reader_stream_fast(audio,low,32768,bank,&de,&work,&status,ignore,0)) return 0;
 if(!source_irq_workspace(ram,&input,&work,&output)) return 0;
 result[0]=work.tstates;result[1]=work.fetches;result[2]=output.whole.tstates;result[3]=output.whole.fetches;
 result[4]=de;result[5]=output.palette_taken;return 1;
}
"""
(out/'wrapper.c').write_text(wrapper);gcc='D:/mingw64/bin/gcc.exe';env=dict(os.environ);env['PATH']='D:/mingw64/bin;'+env['PATH'];sdk=ROOT.parents[1]/'work/sgdk'
command=[gcc,'-O3','-Wall','-Wextra','-Werror','-shared','-I',str(sdk/'inc'),'-I',str(ROOT/'megadrive/src'),str(out/'wrapper.c')]+[str(ROOT/'megadrive/src'/(n+'.c')) for n in ['source_irq_workspace']+MODULES]+['-o',str(out/'model.dll')]
built=subprocess.run(command,capture_output=True,text=True,env=env);(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
dll=c.CDLL(str(out/'model.dll'));fn=dll.title_case;u8=c.POINTER(c.c_uint8);u32=c.POINTER(c.c_uint32);fn.argtypes=[u8,u8,u8,u8,c.c_uint16,c.c_uint32,c.c_uint16,u32];fn.restype=c.c_uint8
sms=(ROOT/'input/original.sms').read_bytes();low=(c.c_uint8*32768).from_buffer_copy(sms[:32768]);bank=(c.c_uint8*16384).from_buffer_copy(sms[0x18000:0x1c000]);results=[]
for region in ['ntsc','pal']:
 blob=zstd.decompress((ROOT/'validation'/('title-irq-snapshots-'+region+'02')/'snapshots.bin.zst').read_bytes());records=[(struct.unpack_from('<8Q',blob,n),blob[n+64:n+400],blob[n+400:n+800]) for n in range(0,len(blob),800)];cases=[];last=None
 for i,(h,ram,sound) in enumerate(records):
  if h[0]!=0x137:continue
  tail=records[i+1:];reader=next(r for r in tail if r[0][0]==0x1a2);after=next(r for r in tail if r[0][0]==0x1a5);wait=next(r for r in tail if r[0][0]==0xbb3)
  assert reader[0][1]<after[0][1]<wait[0][1]
  irq=(c.c_uint8*336).from_buffer_copy(ram);audio=(c.c_uint8*400).from_buffer_copy(reader[2]);output=(c.c_uint32*6)();raster=(h[4]*3420+h[3]-h[5])%(h[6]*3420)
  assert fn(irq,audio,low,bank,reader[0][7],raster,h[6],output),(region,i,'model rejected')
  observed_reader=(after[0][1]-reader[0][1])//15-17
  assert bytes(audio)==after[2],(region,i,'audio state')
  assert output[0]==observed_reader,(region,i,'reader work',output[0],observed_reader)
  observed_to_wait=(wait[0][1]-h[1])//15+72
  cases.append(dict(source_irq_entry_elapsed=h[1],entry_raster=raster,source_reader_tstates=observed_reader,native_reader_tstates=output[0],native_irq_tstates=output[2],source_entry_to_wait_restore_tstates=observed_to_wait,wait_restore_extra_tstates=observed_to_wait-output[2],palette_polls=output[5],audio_state_exact=True))
 results.append(dict(region=region,cases=cases))
report=dict(passed_reader_work_and_state=True,source_sha256=hashlib.sha256(sms).hexdigest(),public_rom_unchanged=True,results=results,scope='Host-compiled native semantic IRQ and audio models against original live title IRQ snapshots; not yet a playable MD phase scheduler.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
for r in results:print(r['region'],len(r['cases']),'IRQ cases; wait restore extras',sorted({x['wait_restore_extra_tstates'] for x in r['cases']}))
