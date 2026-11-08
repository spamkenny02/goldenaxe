"""Own native VRAM/register/port state driven by raw original IO instructions."""
import argparse,contextlib,ctypes as c,io,json,os,shutil,struct,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
from run_core import run
p=argparse.ArgumentParser();p.add_argument('--out-name',default='v319-port-mirror01');p.add_argument('--frames',type=int,default=14000);args=p.parse_args()
out=(root/'validation'/args.out_name).resolve();assert out.is_relative_to(root/'validation') and not out.exists();out.mkdir()
bridge=r'''#include "source_intro_vdp.h"
static SourceIntroVdp model;static u8 memory[16384];
static u32 counts[10],errors[64][12],error_count,elapsed,last_raster,instruction_elapsed,initial_raster;
static u8 initialized,capture_open;
typedef struct {u32 elapsed;u8 kind,port,value,tstates;} PortEvent;
static PortEvent events[400000];static u32 event_count,event_overflow,final_hash;
void model_reset(void) {__builtin_memset(counts,0,sizeof(counts));error_count=elapsed=last_raster=instruction_elapsed=initialized=event_count=event_overflow=final_hash=0;capture_open=1;}
const u32 *model_counts(void) {return counts;}
const u32 *model_errors(void) {return &errors[0][0];}
u32 model_error_count(void) {return error_count;}
u32 model_event_count(void) {return event_count;}
u32 model_event_overflow(void) {return event_overflow;}
u32 model_final_hash(void) {return final_hash;}
u32 model_initial_raster(void) {return initial_raster;}
const u8 *model_event_data(void) {return (const u8 *)events;}
static u32 state_hash(void)
{
 u32 h=2166136261UL;
 for(u16 n=0;n<16384;n++) h=(h^memory[n])*16777619UL;
 for(u16 n=0;n<16;n++) h=(h^model.registers[n])*16777619UL;
 for(u16 n=0;n<32;n++) h=(h^model.palette[n])*16777619UL;
 h=(h^(u8)model.address)*16777619UL;h=(h^(model.address>>8))*16777619UL;
 h=(h^model.code)*16777619UL;h=(h^model.pending)*16777619UL;h=(h^model.low)*16777619UL;h=(h^model.buffer)*16777619UL;
 return h;
}
void model_event(unsigned kind,unsigned cycles,unsigned lines,unsigned observed,const u8 *regs,const u8 *vram,const u8 *cram,const u32 *ports)
{
 u32 period=lines*3420,raster=(cycles+192UL*3420)%period,delta;u8 accepted=1,actual=0,bad=0;
 if(!initialized) {initialized=1;initial_raster=raster;accepted=source_intro_vdp_init(&model,memory,lines,raster,0);last_raster=raster;}
 delta=raster>=last_raster?raster-last_raster:raster+period-last_raster;elapsed+=delta;last_raster=raster;
 if(kind==0) {counts[0]++;instruction_elapsed=elapsed;}
 else if(kind==2 || kind==1 || kind==3)
 {
  u16 duration=(elapsed-instruction_elapsed)/15;
  accepted=source_intro_vdp_checkpoint(&model,instruction_elapsed);
  if(accepted)
  {
   if(kind==2) {counts[1]++;accepted=source_intro_vdp_write(&model,elapsed,observed>>8,observed);}
   else {counts[kind==1?2:3]++;accepted=source_intro_vdp_read(&model,elapsed,duration,kind==1?0xbf:0xbe,&actual);if(actual!=observed) {counts[4]++;bad=1;}}
  }
  if(elapsed>=period*200) capture_open=0;
  if(capture_open)
  {
   if(event_count<400000) {PortEvent *e=events+event_count++;e->elapsed=elapsed;e->kind=kind==2?0:kind==1?1:2;e->port=kind==2?observed>>8:kind==1?0xbf:0xbe;e->value=kind==2?(u8)observed:actual;e->tstates=duration;final_hash=state_hash();}
   else event_overflow++;
  }
 }
 if(kind==4 || kind==1 || kind==3)
 {
  if(__builtin_memcmp(memory,vram,16384)) {counts[6]++;bad=1;}
  if(__builtin_memcmp(model.registers,regs,16)) {counts[8]++;bad=1;}
  for(u16 n=0;n<32;n++) if(model.palette[n]!=cram[n*2] || cram[n*2+1]) {counts[9]++;bad=1;break;}
  if(model.address!=ports[0] || model.code!=ports[1] || model.pending!=ports[2] || model.low!=ports[3] || model.buffer!=ports[4]) {counts[7]++;bad=1;}
 }
 if(!accepted) {counts[5]++;bad=1;}
 if(bad && error_count<64)
 {
  u32 *e=errors[error_count++];e[0]=kind;e[1]=cycles;e[2]=observed;e[3]=actual;e[4]=model.error;e[5]=model.clock.error;e[6]=model.address;e[7]=ports[0];e[8]=model.registers[0];e[9]=regs[0];e[10]=model.registers[1];e[11]=regs[1];
 }
}
'''
(out/'bridge.c').write_text(bridge)
sources=[root/'megadrive/src'/(name+'.c') for name in ('source_intro_sprite_status','source_intro_sprite_clock','source_intro_vdp')]
(out/'sources').mkdir()
for source in sources:
 for path in (source,source.with_suffix('.h')):(out/'sources'/path.name).write_bytes(path.read_bytes())
sdk=root.parents[1]/'work/sgdk';env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
cmd=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-Wall','-Wextra','-Werror','-I',str(sdk/'inc'),'-I',str(root/'megadrive/src'),str(out/'bridge.c'),*map(str,sources),'-o',str(out/'native.dll')]
built=subprocess.run(cmd,env=env,capture_output=True,text=True);(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
native=c.CDLL(str(out/'native.dll'));native.model_counts.restype=native.model_errors.restype=c.POINTER(c.c_uint32);native.model_event_data.restype=c.POINTER(c.c_uint8)
for name in ('model_error_count','model_event_count','model_event_overflow','model_final_hash','model_initial_raster'):getattr(native,name).restype=c.c_uint32
build=json.loads((root/'validation/v319-port-mirror-observer01/report.json').read_bytes());core=Path(build['core']);assert sha(core.read_bytes())==build['core_sha256']
results=[]
for region in ('ntsc','pal'):
 # Reference vdp_reset does not clear its static FIFO. Separate DLL images
 # give each region a true cold process-image state, rather than retaining
 # an unobservable previous-region data buffer until the first port write.
 region_core=core
 if region=='pal':
  region_core=core.with_name(core.stem+'_'+args.out_name.replace('-','_')+'_pal.dll');assert not region_core.exists();shutil.copyfile(core,region_core)
 dll=c.CDLL(str(region_core));dll.gaw_port_mirror_set_hook.argtypes=[c.c_void_p];dll.gaw_port_mirror_set_hook.restype=None;dll.gaw_port_mirror_set_hook(c.cast(native.model_event,c.c_void_p))
 native.model_reset();psg=bytearray()
 with contextlib.redirect_stdout(io.StringIO()):run(root/'input/original.sms',args.frames,out/region,set(),[],skip_intro=False,core=region_core,psg_observer=lambda frame,values:psg.extend(struct.pack('<8H',*values)),core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
 counts=list(native.model_counts()[:10]);errors=[list(native.model_errors()[n*12:(n+1)*12]) for n in range(native.model_error_count())]
 (out/(region+'-psg.bin')).write_bytes(psg)
 events=c.string_at(native.model_event_data(),native.model_event_count()*8);(out/(region+'-ports.bin')).write_bytes(events)
 row=dict(region=region,initial_raster=native.model_initial_raster(),cpu_checkpoints=counts[0],writes=counts[1],status_reads=counts[2],data_reads=counts[3],read_errors=counts[4],rejected=counts[5],vram_errors=counts[6],protocol_errors=counts[7],register_errors=counts[8],palette_errors=counts[9],errors=errors,psg_sha256=sha(psg),captured_port_events=native.model_event_count(),capture_overflow=native.model_event_overflow(),event_sha256=sha(events),capture_final_hash=native.model_final_hash())
 results.append(row);print(json.dumps(row),flush=True)
 dll.gaw_port_mirror_set_hook(None)
report=dict(passed=all(not any(row[k] for k in ('read_errors','rejected','vram_errors','protocol_errors','register_errors','palette_errors','capture_overflow')) for row in results),frames=args.frames,results=results,native_sources={s.name:sha(s.read_bytes()) for s in sources},core_sha256=build['core_sha256'],source_sha256=sha((root/'input/original.sms').read_bytes()),scope='Native-owned zero-initialized VRAM/register/palette/port protocol and native sprite calendar driven only by raw original OUT/IN times and bytes. Reference arrays and expected reads are compared afterward; never copied into the product model.',limits=['Original Z80 produces the raw IO here; native foreground/IRQ writers still need binding to the same port model.','No-input intro/title, SMS2 Mode4/192,no overscan. No physical MD/PCM/throughput proof.'],oracle_ram_writes=0,sram_imports=0)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');assert report['passed'],results
