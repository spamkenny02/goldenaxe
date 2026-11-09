"""Original B95->BB3 title waits versus native dynamic clock/IRQ/audio."""
import argparse,ctypes as c,hashlib,json,os,struct,subprocess
p=argparse.ArgumentParser();p.add_argument('--out',default='title-wait-phase-model03');p.add_argument('--with-title-hint',action='store_true');a=p.parse_args()
from compression import zstd
from run_core import ROOT
from validate_native_audio_reader import MODULES
out=(ROOT/'validation'/a.out).resolve();assert out.is_relative_to(ROOT/'validation');assert not out.exists();out.mkdir()
wrapper=r"""
#include "source_wait.h"
__declspec(dllexport) u8 title_wait_case(u8 *ram,u8 *audio,const u8 *low,const u8 *bank,u32 raster,u16 lines,u32 *result) {
 SourceClock clock;SourceIrqContext ctx={0};SourceWaitOutput output;
 if(!source_clock_init(&clock,lines,raster,0,1,0,0)) return 0;
 ctx.ram=ram;ctx.audio=audio;ctx.low=low;ctx.bank6=bank;ctx.low_bytes=32768;
 ctx.audio_de=4;ctx.input.lines=lines;ctx.input.reset_mask=16;
 if(!source_wait(&clock,&ctx,&output)) return 0;
 result[0]=clock.elapsed;result[1]=clock.raster;result[2]=clock.irq_tstates;result[3]=clock.irq_count;result[4]=output.taken;result[5]=ctx.last_entry.entry_raster;result[6]=ctx.last_irq.whole.tstates;
#ifdef TITLE_HINT_MODEL
 if(!source_title_logo_first_byte(&clock,&result[7])) result[7]=0xffffffffUL;
#endif
 return 1;
}
"""
if a.with_title_hint:wrapper='#define TITLE_HINT_MODEL 1\n'+wrapper.replace('#include "source_wait.h"','#include "source_title_wait.h"').replace('source_wait(&clock','source_title_wait(&clock')
(out/'wrapper.c').write_text(wrapper);gcc='D:/mingw64/bin/gcc.exe';env=dict(os.environ);env['PATH']='D:/mingw64/bin;'+env['PATH'];sdk=ROOT.parents[1]/'work/sgdk'
modules=(['source_title_wait'] if a.with_title_hint else [])+['source_wait','source_clock','source_rng','source_irq_context','source_irq','source_irq_workspace']+MODULES
command=[gcc,'-O3','-Wall','-Wextra','-Werror','-shared','-I',str(sdk/'inc'),'-I',str(ROOT/'megadrive/src'),str(out/'wrapper.c')]+[str(ROOT/'megadrive/src'/(n+'.c')) for n in modules]+['-o',str(out/'model.dll')]
built=subprocess.run(command,capture_output=True,text=True,env=env);(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
dll=c.CDLL(str(out/'model.dll'));fn=dll.title_wait_case;u8=c.POINTER(c.c_uint8);fn.argtypes=[u8,u8,u8,u8,c.c_uint32,c.c_uint16,c.POINTER(c.c_uint32)];fn.restype=c.c_uint8
sms=(ROOT/'input/original.sms').read_bytes();low=(c.c_uint8*32768).from_buffer_copy(sms[:32768]);bank=(c.c_uint8*16384).from_buffer_copy(sms[0x18000:0x1c000]);results=[]
for region in ['ntsc','pal']:
 blob=zstd.decompress((ROOT/'validation'/('title-irq-snapshots-'+region+'03')/'snapshots.bin.zst').read_bytes());records=[(struct.unpack_from('<8Q',blob,n),blob[n+64:n+400],blob[n+400:n+800]) for n in range(0,len(blob),800)];cases=[]
 for i,(h,ram,sound) in enumerate(records):
  if h[0]!=0xb95:continue
  end=next((r for r in records[i+1:] if r[0][0]==0xbb3),None)
  if end is None:continue
  assert not ram[0x42] and not ram[80] and ram[0x34:0x36]==bytes.fromhex('00dd')
  irq=(c.c_uint8*336).from_buffer_copy(ram);audio=(c.c_uint8*400).from_buffer_copy(sound);output=(c.c_uint32*8)();raster=(h[4]*3420+h[3]-h[5])%(h[6]*3420)
  assert fn(irq,audio,low,bank,raster,h[6],output),(region,i,'model rejected')
  expected_elapsed=end[0][1]-h[1];expected_raster=(end[0][4]*3420+end[0][3]-end[0][5])%(h[6]*3420)
  exact=output[0]==expected_elapsed and output[1]==expected_raster
  audio_exact=bytes(audio)==end[2];ram_exact=bytes(irq)==end[1]
  first=next((r for r in records[i+1:] if r[0][0] in [0xb95,0x38e]),None)
  first_exact=None
  if a.with_title_hint and first is not None and first[0][0]==0x38e:
   first_raster=(first[0][4]*3420+first[0][3]-first[0][5])%(h[6]*3420)
   first_exact=output[7]==first_raster
   assert first_exact,(region,i,'first logo OUTI',output[7],first_raster)
  cases.append(dict(entry_elapsed=h[1],entry_raster=raster,wait_master_ticks=output[0],exit_raster=output[1],irq_tstates=output[2],irq_count=output[3],polls=output[4],audio_state_exact=audio_exact,irq_ram_exact=ram_exact,deadline_exact=exact,expected_wait_master_ticks=expected_elapsed,wait_master_delta=int(output[0])-expected_elapsed,expected_exit_raster=expected_raster,native_irq_entry_raster=output[5],first_logo_outi_raster=output[7] if first_exact is not None else None,first_logo_outi_exact=first_exact))
 results.append(dict(region=region,cases=cases))
passed=all(x['deadline_exact'] and x['audio_state_exact'] and x['irq_ram_exact'] for r in results for x in r['cases'])
report=dict(passed=passed,title_hint_included=a.with_title_hint,public_rom_unchanged=True,source_sha256=hashlib.sha256(sms).hexdigest(),results=results,scope='Host-native B95->BB3 scheduler timing and full IRQ/audio state against original live snapshots. Empty video queue and no pending tile request; reader DE=4 verified in source snapshots. Initial refresh is0: no refresh-register equivalence claim. Does not yet drive physical MD video deadlines.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
for r in results:print(r['region'],len(r['cases']),'waits, exact deadlines',sum(x['deadline_exact'] for x in r['cases']),'deltas',sorted({x['wait_master_delta'] for x in r['cases']}))
if not passed:raise SystemExit(1)
