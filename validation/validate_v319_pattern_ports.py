"""Compare batched032A ports to instruction-only execution and real SMS bytes."""
import ctypes as c,gzip,json,os,struct,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
from validate_native_patterns import vectors
out=root/'validation/v319-pattern-ports02';assert not out.exists();out.mkdir()
source=root/'megadrive/src/source_pattern_clock.c'
body=source.read_text()
for name in ('source_pattern_decode_planned','source_pattern_decode_ports','source_pattern_decode','source_graphics_prefix_class0_planned','source_graphics_prefix_class0','source_graphics_prefix_changed'):
 # Longest names first; replace call tokens only.
 body=body.replace(name+'(',name+'_scalar(')
body=body.replace('source_clock_block(', 'never_block(').replace('source_clock_repeat(', 'never_repeat(')
body=body.replace('if(planned_window(clock,plan->planes+plane,&command_index,&src,&write,&cursor,video)) continue;','if(0) continue;')
body=body.replace('else if(command_window(clock,&src,&write,&cursor,video)) continue;','else if(0) continue;')
body=body.replace('#include "source_pattern_clock.h"','#include "source_pattern_clock.h"\nstatic u8 never_block(SourceClock *c,u16 t,u16 m) {(void)c;(void)t;(void)m;return 0;}\nstatic u16 never_repeat(SourceClock *c,u16 t,u8 m,u16 n) {(void)c;(void)t;(void)m;(void)n;return 0;}')
(out/'scalar.c').write_text(body)
wrapper=r'''#include "source_pattern_clock.h"
#include "source_intro_pattern_plans_generated.h"
u8 source_pattern_decode_ports_scalar(SourceClock*,SourceIrqContext*,const u8**,u8*,u16,u16*,const SourcePatternPlan*,SourcePatternPortSink,void*);
static u32 events[200000][6],event_count;static SourceClock *active;
const u32 *port_event_data(void) {return &events[0][0];}
u32 port_event_count(void) {return event_count;}
u8 source_irq_interrupt(void *context,const SourceClockIrq *entry,SourceClockWork *work)
{(void)context;(void)entry;work->tstates=82;work->fetches=8;return 1;}
static u8 sink(void *user,u32 elapsed,u32 raster,u8 port,u8 value)
{
 u32 *row;(void)user;
 if(event_count>=200000) return 0;
 row=events[event_count++];row[0]=elapsed;row[1]=raster;row[2]=port;row[3]=value;
 row[4]=elapsed-active->irq_tstates*15;row[5]=active->irq_count;return 1;
}
u8 pattern_case(const u8 *stream,u16 address,u16 lines,u32 raster,u8 mode,u8 plan_id,u8 *pixels,u32 *result)
{
 SourceClock clock;SourceIrqContext context={0};u8 ram[336]={0};u16 end;const u8 *source=stream;
 const SourcePatternPlan *plan=plan_id==1?&gaw_intro_9d70_plan:plan_id==2?&gaw_intro_a655_plan:0;
 context.ram=ram;event_count=0;active=&clock;
 if(!source_clock_init(&clock,lines,raster,0,1,0,0)) return 0;
 __builtin_memset(pixels,0xa7,16384);
 if(mode==0)
 {if(!source_pattern_decode_planned(&clock,&context,&source,pixels,address,&end,plan)) return 0;}
 else if(mode==1)
 {if(!source_pattern_decode_ports(&clock,&context,&source,pixels,address,&end,plan,sink,0)) return 0;}
 else if(!source_pattern_decode_ports_scalar(&clock,&context,&source,pixels,address,&end,plan,sink,0)) return 0;
 result[0]=source-stream;result[1]=end;result[2]=ram[0x31]|((u16)ram[0x32]<<8);
 result[3]=clock.elapsed;result[4]=clock.raster;result[5]=clock.foreground_tstates;result[6]=clock.foreground_m1;
 result[7]=clock.irq_tstates;result[8]=clock.irq_m1;result[9]=clock.irq_count;result[10]=clock.refresh;
 result[11]=clock.iff;result[12]=clock.blocked;result[13]=clock.pending;result[14]=clock.first;result[15]=clock.until_vint;
 return 1;
}
'''
(out/'wrapper.c').write_text(wrapper)
sdk=root.parents[1]/'work/sgdk';env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
command=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-but-set-variable','-I',str(sdk/'inc'),'-I',str(source.parent),str(out/'wrapper.c'),str(out/'scalar.c'),str(source),str(source.parent/'source_clock.c'),str(source.parent/'source_rng.c'),'-o',str(out/'ports.dll')]
built=subprocess.run(command,capture_output=True,text=True,env=env);(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
dll=c.CDLL(str(out/'ports.dll'));dll.port_event_count.restype=c.c_uint32;dll.port_event_data.restype=c.POINTER(c.c_uint32)
fn=dll.pattern_case;fn.restype=c.c_uint8;fn.argtypes=[c.POINTER(c.c_uint8),c.c_uint16,c.c_uint16,c.c_uint32,c.c_uint8,c.c_uint8,c.POINTER(c.c_uint8),c.POINTER(c.c_uint32)]
rom=(root/'input/original.sms').read_bytes();cases=list(vectors());real=[]
for header,end in [(0x9d70,0xa598),(0xa655,0xae6f)]:
 stream=rom[0x18000+header+4-0x8000:0x18000+end-0x8000];real.append((stream,0x4000))
cases+=real;rows=[];digest=bytearray();compiled_cases=[]
def invoke(stream,address,lines,raster,mode,plan_id):
 packed=(c.c_uint8*len(stream)).from_buffer_copy(stream);pixels=(c.c_uint8*16384)();result=(c.c_uint32*16)()
 assert fn(packed,address,lines,raster,mode,plan_id,pixels,result),(len(stream),address,lines,raster,mode)
 events=c.string_at(dll.port_event_data(),dll.port_event_count()*24)
 return list(result),bytes(pixels),events
for index,(stream,address) in enumerate(cases):
 for lines in (262,313):
  # Stress one of six line/IRQ edges for every stream, all edges for assets.
  phases=[0,193*3420-1,193*3420-1000,lines*3420-1,193*3420,193*3420+1]
  for raster in (phases if index>=len(cases)-2 else [phases[index%len(phases)]]):
   plan_id=index-(len(cases)-2)+1 if index>=len(cases)-2 else 0
   baseline=invoke(stream,address,lines,raster,0,plan_id)
   actual=invoke(stream,address,lines,raster,1,plan_id);scalar=invoke(stream,address,lines,raster,2,plan_id)
   assert actual==scalar,('dated/scalar',index,lines,raster)
   assert baseline[:2]==actual[:2],('legacy',index,lines,raster)
   # Every OUT is an11T immediate instruction; raster and timestamps must
   # agree with the source epoch and retain monotonic ordering across IRQs.
   events=[struct.unpack_from('<6I',actual[2],off) for off in range(0,len(actual[2]),24)]
   assert all(e[1]==(raster+e[0])%(lines*3420) for e in events)
   assert all(a[0]<b[0] for a,b in zip(events,events[1:]))
   digest.extend(actual[2]);row=dict(index=index,address=address,lines=lines,raster=raster,plan_id=plan_id,events=len(events),result=actual[0],pixels_sha256=sha(actual[1]),events_sha256=sha(actual[2]));rows.append(row)
   if index>=len(cases)-2:compiled_cases.append(dict(row,stream=list(stream),events=[list(e[:4]) for e in events]))
print('Host exact port/state comparisons:',len(rows),flush=True)
# Independent original rawIO bytes for the first actual intro032A stream.
manifest=json.loads((root/'analysis/v319-port-mirror/manifest.json').read_bytes());matches=[]
for region in ('ntsc','pal'):
 item=manifest['compressed'][f'validation/v319-port-mirror02/{region}-ports.bin'];encoded=(root/'analysis/v319-port-mirror'/item['stored']).read_bytes();assert sha(encoded)==item['stored_sha256'];raw=gzip.decompress(encoded);assert sha(raw)==item['raw_sha256']
 writes=[struct.unpack_from('<IBBBB',raw,n) for n in range(0,len(raw),8) if raw[n+4]==0]
 values=bytes(v for row in writes for v in row[2:4])
 actual=invoke(real[0][0],0x4000,262,0,1,1);events=[struct.unpack_from('<6I',actual[2],off) for off in range(0,len(actual[2]),24)]
 wanted=bytes(v for e in events for v in e[2:4]);offset=values.find(wanted);assert offset>=0 and offset%2==0
 matches.append(dict(region=region,source_write_index=offset//2,events=len(events),original_bytes_exact=True))
report=dict(passed=True,host_cases=len(rows),modes_per_case=3,compiled_asset_cases=len(compiled_cases),source_matches=matches,event_digest=sha(digest),source_sha256=sha(rom),native_sha256=sha(source.read_bytes()),limits=['Instruction-only scalar variant shares semantic032A logic but disables every batching path. Independent original corpus currently checks port/value order for first intro asset, not original032A absolute output dates.','Synthetic82T/8M1 IRQ callback exercises native scheduling boundaries; no real IRQ audio/video publication in this test.','No physical MD timing/PCM or activated ROM claim.'])
(out/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'compiled-cases.json').write_text(json.dumps(compiled_cases,separators=(',',':'))+'\n');(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
