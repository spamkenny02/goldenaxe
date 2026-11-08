"""Replay actual parse/render/read events into the native temporal status model."""
import argparse,contextlib,ctypes as c,gzip,io,json,os,struct,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
from run_core import run
parser=argparse.ArgumentParser();parser.add_argument('--out-name',default='v319-chip-events02');parser.add_argument('--capture-transitions',action='store_true');args=parser.parse_args()
out=(root/'validation'/args.out_name).resolve();assert out.is_relative_to(root/'validation') and not out.exists();out.mkdir()
bridge=r'''#include "source_intro_sprite_status.h"
static SourceIntroSpriteStatus model;
static u32 counts[8],errors[128][8],error_count;
static u8 last_read;
void chip_model_reset(void)
{source_intro_sprite_status_reset(&model);__builtin_memset(counts,0,sizeof(counts));error_count=0;last_read=0;}
const u32 *chip_model_counts(void) {return counts;}
const u32 *chip_model_errors(void) {return &errors[0][0];}
u32 chip_model_error_count(void) {return error_count;}
void chip_model_event(unsigned kind,int line,unsigned hc,const u8 *regs,const u8 *vram,unsigned observed)
{
 u8 accepted=1,actual=0;counts[kind]++;
 if(kind==0) accepted=source_intro_sprite_parse(&model,line,vram,regs);
 else if(kind==1) accepted=source_intro_sprite_render(&model,line,vram,regs);
 else if(kind==2) {last_read=source_intro_sprite_read(&model,line,hc);actual=last_read;}
 else if(kind==3) actual=last_read;
 if(!accepted) counts[6]++;
 if(kind>=2 && (regs[0]&4) && actual!=(observed&0x60))
 {
  counts[kind+2]++;
  if(error_count<128) {u32 *e=errors[error_count++];e[0]=kind;e[1]=line;e[2]=hc;e[3]=observed;e[4]=actual;e[5]=model.flags;e[6]=model.pending_overflow;e[7]=model.collision_line;}
 }
}
'''
if args.capture_transitions:
 extra=r'''typedef struct {
 SourceIntroSpriteStatus before,after; s16 line;
 u8 kind,hcounter,result,pattern_count,source_flags,source_valid;
 u8 regs[16],sat[256];u16 addresses[8];u8 patterns[32];
 } ChipCase;
static ChipCase cases[262144];static u32 slots[524288],case_count,case_overflow;
static void canonical(SourceIntroSpriteStatus *state)
{
 for(u16 slot=0;slot<2;slot++) for(u16 n=state->count[slot];n<8;n++) __builtin_memset(state->objects[slot]+n,0,sizeof(SourceIntroCachedSprite));
 if(!(state->flags&0x20)) {state->collision_line=-1;state->collision_hcounter=0;}
}
static void record_case(const ChipCase *entry)
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
u32 chip_case_count(void) {return case_count;}
u32 chip_case_stride(void) {return sizeof(ChipCase);}
u32 chip_model_stride(void) {return sizeof(SourceIntroSpriteStatus);}
u32 chip_case_overflow(void) {return case_overflow;}
const u8 *chip_case_data(void) {return (const u8 *)cases;}
'''
 bridge=bridge.replace('void chip_model_reset(void)',extra+'\nvoid chip_model_reset(void)')
 needle='u8 accepted=1,actual=0;counts[kind]++;'
 capture=r'''u8 accepted=1,actual=0;ChipCase entry;counts[kind]++;
 if(kind<3)
 {
  __builtin_memset(&entry,0,sizeof(entry));entry.before=model;canonical(&entry.before);
  entry.kind=kind;entry.line=line;entry.hcounter=hc;__builtin_memcpy(entry.regs,regs,16);
  if(kind==0)
  {
   u16 mask=((u16)~0x3f80^((u16)regs[5]<<7))|0x80;
   __builtin_memcpy(entry.sat,vram+(mask&0x3f00),256);
  }
  if(kind==1 && (regs[1]&0x40) && !(model.flags&0x20))
  {
   u16 slot=line&1,mask=(((u16)~0x01c0^((u16)regs[6]<<6))|0xc0)&0x1ff;
   entry.pattern_count=model.count[slot];
   for(u16 n=0;n<entry.pattern_count;n++)
   {
    SourceIntroCachedSprite *sprite=model.objects[slot]+n;
    u16 address=(((sprite->attribute|0x100)&mask)<<5)+(sprite->row<<2);
    entry.addresses[n]=address;__builtin_memcpy(entry.patterns+n*4,vram+address,4);
   }
  }
 }
'''
 assert needle in bridge;bridge=bridge.replace(needle,capture)
 needle='if(!accepted) counts[6]++;'
 replacement=r'''if(kind<3)
 {
  entry.after=model;canonical(&entry.after);entry.result=kind==2?actual:accepted;
  entry.source_valid=kind==2 && (regs[0]&4);entry.source_flags=entry.source_valid?(observed&0x60):0;
  record_case(&entry);
 }
 if(!accepted) counts[6]++;
'''
 bridge=bridge.replace(needle,replacement)
(out/'bridge.c').write_text(bridge)
sdk=root.parents[1]/'work/sgdk';env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
source=root/'megadrive/src/source_intro_sprite_status.c'
built=subprocess.run(['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-Wall','-Wextra','-Werror','-I',str(sdk/'inc'),'-I',str(source.parent),str(out/'bridge.c'),str(source),'-o',str(out/'native.dll')],capture_output=True,text=True,env=env)
(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
native=c.CDLL(str(out/'native.dll'));native.chip_model_reset.restype=None
native.chip_model_counts.restype=native.chip_model_errors.restype=c.POINTER(c.c_uint32);native.chip_model_error_count.restype=c.c_uint32
build=json.loads((root/'validation/v319-chip-events-observer01/report.json').read_bytes());core=Path(build['core']);assert sha(core.read_bytes())==build['core_sha256']
dll=c.CDLL(str(core));dll.gaw_vdp_set_hook.argtypes=[c.c_void_p];dll.gaw_vdp_set_hook.restype=None
dll.gaw_vdp_set_hook(c.cast(native.chip_model_event,c.c_void_p))
manifest=json.loads((root/'analysis/v319-psg-write-spacing/manifest.json').read_bytes());results=[]
for region in ('ntsc','pal'):
 native.chip_model_reset();psg=bytearray()
 with contextlib.redirect_stdout(io.StringIO()):
  run(root/'input/original.sms',14000,out/region,set(),[],skip_intro=False,core=core,
   psg_observer=lambda frame,values:psg.extend(struct.pack('<8H',*values)),core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
 counts=list(native.chip_model_counts()[:8]);errors=[list(native.chip_model_errors()[n*8:(n+1)*8]) for n in range(native.chip_model_error_count())]
 item=manifest['compressed'][f'validation/v319-psg-writes01/{region}-sms/exposed-psg-states.bin'];encoded=(root/'analysis/v319-psg-write-spacing'/item['stored']).read_bytes();assert sha(encoded)==item['stored_sha256'];prior=gzip.decompress(encoded);assert sha(prior)==item['raw_sha256'] and prior==psg
 (out/region/'psg-states.bin').write_bytes(psg)
 row=dict(region=region,parse_events=counts[0],render_events=counts[1],read_events=counts[2],irq_samples=counts[3],read_errors=counts[4],irq_errors=counts[5],unsupported=counts[6],errors=errors,psg_exact_frames=14000)
 results.append(row);print(json.dumps(row),flush=True)
dll.gaw_vdp_set_hook(None)
r=dict(passed=all(not(row['read_errors'] or row['irq_errors'] or row['unsupported']) for row in results),results=results,
 native_source_sha256=sha(source.read_bytes()),core_sha256=sha(core.read_bytes()),source_sha256=sha((root/'input/original.sms').read_bytes()),
 scope='Native temporal parser/cache,render collision order and status latches driven by actual reference parse/render/read events. No expected status is passed into the native algorithm; only the bridge compares its outputs.',
 limits=['Reference live VRAM/register/timing events, not a production callback bound to the MD renderer yet.','Mode4/192/SMS2 unzoomed8-pixel sprites only; no hardware/PCM certificate.'],oracle_ram_writes=0,sram_imports=0)
if args.capture_transitions:
 for name in ('chip_case_count','chip_case_stride','chip_model_stride','chip_case_overflow'):getattr(native,name).restype=c.c_uint32
 native.chip_case_data.restype=c.POINTER(c.c_uint8)
 count=native.chip_case_count();stride=native.chip_case_stride()
 assert native.chip_case_overflow()==0 and stride==472 and native.chip_model_stride()==72
 raw=c.string_at(native.chip_case_data(),count*stride);(out/'native-transitions.bin').write_bytes(raw)
 r['transition_vectors']=count;r['transition_stride']=stride;r['transition_sha256']=sha(raw)
 r['transition_canonicalization']='Only unused cached sprite slots and collision coordinates when no collision is latched are canonicalized in vector snapshots; live model state is not modified.'
 print(json.dumps(dict(transition_vectors=count,stride=stride)),flush=True)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
