"""Native sprite calendar derives its events from CPU time, compared to SMS."""
import argparse,contextlib,ctypes as c,io,json,os,struct,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
from run_core import run
p=argparse.ArgumentParser();p.add_argument('--out-name',default='v319-sprite-clock01');p.add_argument('--frames',type=int,default=14000);p.add_argument('--capture-transitions',action='store_true');args=p.parse_args()
out=(root/'validation'/args.out_name).resolve();assert out.is_relative_to(root/'validation') and not out.exists();out.mkdir()
bridge=r'''#include "source_intro_sprite_clock.h"
static SourceIntroSpriteClock model;
static u32 counts[6],last_raster,elapsed,error_count,errors[64][10];static u8 initialized;
void model_reset(void) {__builtin_memset(counts,0,sizeof(counts));initialized=0;elapsed=error_count=last_raster=0;}
const u32 *model_counts(void) {return counts;}
const u32 *model_errors(void) {return &errors[0][0];}
u32 model_error_count(void) {return error_count;}
void model_event(unsigned kind,unsigned cycles,unsigned lines,const u8 *regs,const u8 *vram,unsigned observed)
{
 u32 period=lines*3420,raster=(cycles+192UL*3420)%period,delta;u8 accepted=1,actual=0;
 counts[kind]++;
 if(!initialized) {initialized=1;accepted=source_intro_sprite_clock_init(&model,lines,raster,0);last_raster=raster;}
 delta=raster>=last_raster?raster-last_raster:raster+period-last_raster;elapsed+=delta;last_raster=raster;
 if(kind==1 && delta!=165) counts[5]++;
 if(kind==0) accepted=source_intro_sprite_clock_advance(&model,elapsed,vram,regs);
 else accepted=source_intro_sprite_clock_read(&model,elapsed,11,vram,regs,&actual);
 if(!accepted) counts[2]++;
 if(kind==1 && (regs[0]&4)) {counts[4]++;if(actual!=observed) counts[3]++;}
 if(!accepted || (kind==1 && (regs[0]&4) && actual!=observed))
 {
  if(error_count<64) {u32 *e=errors[error_count++];e[0]=kind;e[1]=cycles;e[2]=raster;e[3]=elapsed;e[4]=observed;e[5]=actual;e[6]=model.error;e[7]=regs[0];e[8]=regs[1];e[9]=model.sprites.pending_overflow;}
 }
}
'''
if args.capture_transitions:
 extra=r'''typedef struct {
 SourceIntroSpriteClock before,after;u32 delta;
 u8 kind,tstates,result,source_valid,regs[16],sat[256];u16 addresses[8];u8 patterns[32];
 } ClockCase;
static ClockCase cases[262144];static u32 slots[524288],case_count,case_overflow;
u32 clock_case_count(void) {return case_count;}
u32 clock_case_stride(void) {return sizeof(ClockCase);}
u32 clock_state_stride(void) {return sizeof(SourceIntroSpriteClock);}
u32 clock_case_overflow(void) {return case_overflow;}
const u8 *clock_case_data(void) {return (const u8 *)cases;}
static void canonical(SourceIntroSpriteClock *state)
{
 for(u16 slot=0;slot<2;slot++) for(u16 n=state->sprites.count[slot];n<8;n++)
  __builtin_memset(state->sprites.objects[slot]+n,0,sizeof(SourceIntroCachedSprite));
 if(!(state->sprites.flags&0x20)) {state->sprites.collision_line=-1;state->sprites.collision_hcounter=0;}
}
static void record_case(ClockCase *entry)
{
 const u8 *bytes=(const u8 *)entry;u32 hash=2166136261UL,index;
 for(u16 n=0;n<sizeof(*entry);n++) hash=(hash^bytes[n])*16777619UL;
 index=hash&524287;
 while(slots[index])
 {
  if(!__builtin_memcmp(cases+slots[index]-1,entry,sizeof(*entry))) return;
  index=(index+1)&524287;
 }
 if(case_count>=262144) {case_overflow++;return;}
 cases[case_count]=*entry;slots[index]=++case_count;
}
'''
 bridge=bridge.replace('void model_reset(void)',extra+'\nvoid model_reset(void)')
 bridge=bridge.replace('u8 accepted=1,actual=0;', 'u8 accepted=1,actual=0,capture;ClockCase entry;')
 needle='if(kind==1 && delta!=165) counts[5]++;'
 replacement=r'''capture=kind==1 || elapsed-model.elapsed>=model.until_line;
 if(capture)
 {
  __builtin_memset(&entry,0,sizeof(entry));entry.before=model;entry.delta=elapsed-model.elapsed;
  entry.before.elapsed=0;canonical(&entry.before);entry.kind=kind;entry.tstates=11;
  __builtin_memcpy(entry.regs,regs,16);
  if(entry.delta>=model.until_line && (regs[0]&4))
  {
   u16 line=(model.raster/3420+1)%model.lines,mask=((u16)~0x3f80^((u16)regs[5]<<7))|0x80;
   if(entry.delta-model.until_line>=3420) counts[2]++;
   if(line==model.lines-1 || line<192) __builtin_memcpy(entry.sat,vram+(mask&0x3f00),256);
   if(line<192 && (regs[1]&0x40) && !(model.sprites.flags&0x20))
   {
    u16 slot=line&1,pattern_mask=(((u16)~0x01c0^((u16)regs[6]<<6))|0xc0)&0x1ff;
    for(u16 n=0;n<model.sprites.count[slot];n++)
    {
     SourceIntroCachedSprite *sprite=model.sprites.objects[slot]+n;
     entry.addresses[n]=(((sprite->attribute|0x100)&pattern_mask)<<5)+(sprite->row<<2);
     __builtin_memcpy(entry.patterns+n*4,vram+entry.addresses[n],4);
    }
   }
  }
 }
 if(kind==1 && delta!=165) counts[5]++;
'''
 assert needle in bridge;bridge=bridge.replace(needle,replacement)
 needle='if(!accepted) counts[2]++;'
 replacement=r'''if(capture)
 {
  entry.after=model;entry.after.elapsed=entry.delta;canonical(&entry.after);
  /* Advance-only vectors isolate one line transition: no reads/writes
   * occur in either fractional-line tail. Preserve the physical line,
   * cache/latches and all input bytes, normalize just those empty tails.
   * Read vectors retain their exact raster and instruction duration. */
  if(kind==0)
  {
   entry.before.raster=entry.before.raster/3420*3420;entry.before.until_line=3420;
   entry.after.raster=entry.after.raster/3420*3420;entry.after.until_line=3420;
   entry.delta=entry.after.elapsed=3420;
  }
  entry.source_valid=kind==1 && (regs[0]&4);entry.result=kind==1?actual:accepted;
  if(entry.source_valid && actual!=observed) counts[3]++;
  record_case(&entry);
 }
 if(!accepted) counts[2]++;
'''
 assert needle in bridge;bridge=bridge.replace(needle,replacement)
(out/'bridge.c').write_text(bridge)
sdk=root.parents[1]/'work/sgdk';env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
sources=[root/'megadrive/src'/(name+'.c') for name in ('source_intro_sprite_status','source_intro_sprite_clock')]
(out/'sources').mkdir()
for source in sources:
 for path in (source,source.with_suffix('.h')):(out/'sources'/path.name).write_bytes(path.read_bytes())
cmd=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-Wall','-Wextra','-Werror','-I',str(sdk/'inc'),'-I',str(root/'megadrive/src'),str(out/'bridge.c'),*map(str,sources),'-o',str(out/'native.dll')]
built=subprocess.run(cmd,env=env,capture_output=True,text=True);(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
native=c.CDLL(str(out/'native.dll'));native.model_counts.restype=native.model_errors.restype=c.POINTER(c.c_uint32);native.model_error_count.restype=c.c_uint32
build=json.loads((root/'validation/v319-sprite-clock-observer01/report.json').read_bytes());core=Path(build['core']);assert sha(core.read_bytes())==build['core_sha256']
dll=c.CDLL(str(core));dll.gaw_sprite_clock_set_hook.argtypes=[c.c_void_p];dll.gaw_sprite_clock_set_hook.restype=None
dll.gaw_sprite_clock_set_hook(c.cast(native.model_event,c.c_void_p));results=[]
for region in ('ntsc','pal'):
 native.model_reset();psg=bytearray()
 with contextlib.redirect_stdout(io.StringIO()):run(root/'input/original.sms',args.frames,out/region,set(),[],skip_intro=False,core=core,psg_observer=lambda frame,values:psg.extend(struct.pack('<8H',*values)),core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
 counts=list(native.model_counts()[:6]);errors=[list(native.model_errors()[n*10:(n+1)*10]) for n in range(native.model_error_count())]
 (out/(region+'-psg.bin')).write_bytes(psg)
 row=dict(region=region,cpu_checkpoints=counts[0],reads=counts[1],unsupported=counts[2],mismatch=counts[3],mode4_reads=counts[4],non_11t_reads=counts[5],errors=errors,psg_sha256=sha(psg))
 results.append(row);print(json.dumps(row),flush=True)
dll.gaw_sprite_clock_set_hook(None)
report=dict(passed=all(not(r['mismatch'] or r['unsupported'] or r['non_11t_reads']) for r in results),frames=args.frames,results=results,
 native_sources={s.name:sha(s.read_bytes()) for s in sources},core_sha256=build['core_sha256'],source_sha256=sha((root/'input/original.sms').read_bytes()),
 scope='Independent native parse/render/VINT calendar driven solely by CPU checkpoint and IN completion time. Reference live VRAM/register inputs; original full status byte compared afterward, never passed to product algorithm.',
 limits=['Reference VRAM and register inputs, not an independently port-written native mirror yet.','No overscan processing; SMS2 Mode4/192,8px unzoomed sprites, no-input intro/title only. No physical MD/PCM deadline proof.'],oracle_ram_writes=0,sram_imports=0)
if args.capture_transitions:
 for name in ('clock_case_count','clock_case_stride','clock_state_stride','clock_case_overflow'):getattr(native,name).restype=c.c_uint32
 native.clock_case_data.restype=c.POINTER(c.c_uint8)
 count=native.clock_case_count();stride=native.clock_case_stride()
 overflow=native.clock_case_overflow();report.update(capture_overflow=overflow,transition_stride=stride,state_stride=native.clock_state_stride())
 if overflow or stride!=512 or native.clock_state_stride()!=92:
  (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');raise AssertionError(report)
 raw=c.string_at(native.clock_case_data(),count*stride);(out/'transitions.bin').write_bytes(raw)
 report.update(transition_vectors=count,transition_stride=stride,transition_sha256=sha(raw),
  canonicalization='Epoch rebased to0 before and delta after; unused sprite slots and unlatched collision coordinates canonicalized. Advance-only cases normalize empty fractional-line tails to exact3420-tick one-line transitions; read cases keep exact raster. Vector copies only; live calendar state unchanged.')
 print('Clock transitions:',count,flush=True)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');assert report['passed'],results
