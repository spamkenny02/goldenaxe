"""Check live sprite-status delivery before real native IRQ video/audio work."""
import contextlib,ctypes as c,io,json,os,re,shutil,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha,freeze
from validate_native_source_wait import MODULES
from validate_reader_timing import MODULES as TIMED_MODULES
from run_core import run
out=root/'validation/v319-irq-status-binding01';assert not out.exists();out.mkdir()
modules=list(dict.fromkeys(MODULES+TIMED_MODULES+['source_irq_timed_context','source_irq_fast_timed_context','source_audio_fast_timed','source_audio_reader_master','source_irq_master_context','source_intro_sprite_status']))
wrapper=r'''#include "source_irq_timed_context.h"
#include "source_intro_sprite_status.h"
typedef struct {
 SourceIrqContext *core;SourceIntroSpriteStatus sprites;SourceClockIrq entry;
 u32 reads,videos,traces,writes,errors,hash;u8 fail,expected;
} Observer;
static u8 status_read(void *user,const SourceClockIrq *entry,u8 *status)
{
 Observer *p=user;p->reads++;
 if(p->videos || p->writes || p->traces || entry->entry_elapsed!=p->entry.entry_elapsed ||
    entry->entry_raster!=p->entry.entry_raster || entry->entry_refresh!=p->entry.entry_refresh) p->errors++;
 if(p->fail) return 0;
 *status=0x9f|source_intro_sprite_read(&p->sprites,193,100);
 return 1;
}
static u8 video(void *user,const SourceIrqContext *core,const SourceClockIrq *entry,u16 *tiles)
{
 Observer *p=user;(void)entry;(void)tiles;p->videos++;
 if(core->ram[0x1b]!=p->expected) p->errors++;
 return 1;
}
static void plain_sink(void *user,const u8 *values,u16 count)
{
 Observer *p=user;
 if(p->core->ram[0x1b]!=p->expected) p->errors++;
 for(u16 n=0;n<count;n++) {p->hash=(p->hash^values[n])*16777619UL;p->writes++;}
}
static void timed_sink(void *user,const u8 *values,const u32 *dates,u16 count)
{
 Observer *p=user;
 plain_sink(user,values,count);
 for(u16 n=0;n<count;n++) {p->hash=(p->hash^dates[n])*16777619UL;}
}
static void trace(void *user,const SourceClockIrq *entry,const SourceClockWork *work)
{Observer *p=user;(void)entry;(void)work;p->traces++;}
u8 binding_case(u8 adapter,u8 full,u8 flags,u8 mode,u16 lines,u32 epoch,const u8 *low,const u8 *bank,u32 *output)
{
 SourceTimedIrqContext timed={0};SourceIrqContext *core=&timed.core;SourceClockWork work;
 u8 ram[336]={0},audio[400]={0},before_ram[336],before_audio[400],accepted;
 Observer observer={0};
 observer.core=core;observer.fail=mode==2;observer.expected=0x9f|flags;observer.hash=2166136261UL;
 observer.entry.entry_raster=193UL*3420+72UL*15;observer.entry.entry_elapsed=epoch;observer.entry.entry_refresh=7;
 source_intro_sprite_status_reset(&observer.sprites);observer.sprites.flags=flags;
 ram[0x1b]=mode==0?observer.expected:0x55;ram[0x2e]=full;ram[0x33]=1;ram[0x35]=0xdd;
 ram[0x1c]=2;ram[0x30]=2;ram[0x2f]=255;audio[5]=128;audio[1]=2;audio[6]=0x81;
 core->ram=ram;core->audio=audio;core->low=low;core->bank6=bank;core->low_bytes=32768;
 core->input.lines=lines;core->input.reset_mask=16;core->input.joy=17;
 core->sink=plain_sink;core->sink_context=&observer;core->trace=trace;core->trace_context=&observer;
 core->video=video;core->video_context=&observer;
 if(mode) {core->status_read=status_read;core->status_context=&observer;}
 timed.sink=timed_sink;timed.sink_context=&observer;
 __builtin_memcpy(before_ram,ram,336);__builtin_memcpy(before_audio,audio,400);
 if(adapter==0) accepted=source_irq_interrupt(core,&observer.entry,&work);
 else if(adapter==1) accepted=source_irq_timed_interrupt(&timed,&observer.entry,&work);
 else if(adapter==2) accepted=source_irq_fast_timed_interrupt(&timed,&observer.entry,&work);
 else accepted=source_irq_master_interrupt(&timed,&observer.entry,&work);
 output[0]=accepted;output[1]=core->error;output[2]=work.tstates;output[3]=work.fetches;
 output[4]=observer.reads;output[5]=observer.videos;output[6]=observer.writes;output[7]=observer.traces;
 output[8]=ram[0x1b];output[9]=observer.errors;output[10]=observer.hash;
 output[11]=__builtin_memcmp(before_ram,ram,336)==0;output[12]=__builtin_memcmp(before_audio,audio,400)==0;
 output[13]=2166136261UL;output[14]=2166136261UL;
 for(u16 n=0;n<336;n++) output[13]=(output[13]^ram[n])*16777619UL;
 for(u16 n=0;n<400;n++) output[14]=(output[14]^audio[n])*16777619UL;
 output[15]=observer.sprites.flags;
 return 1;
}
'''
(out/'wrapper.c').write_text(wrapper)
sdk=root.parents[1]/'work/sgdk';env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
command=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-Wall','-Wextra','-Werror','-I',str(sdk/'inc'),'-I',str(root/'megadrive/src'),str(out/'wrapper.c')]
command += [str(root/'megadrive/src'/(name+'.c')) for name in modules]+['-o',str(out/'binding.dll')]
built=subprocess.run(command,capture_output=True,text=True,env=env);(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
dll=c.CDLL(str(out/'binding.dll'));fn=dll.binding_case
fn.argtypes=[c.c_uint8]*4+[c.c_uint16,c.c_uint32,c.POINTER(c.c_uint8),c.POINTER(c.c_uint8),c.POINTER(c.c_uint32)];fn.restype=c.c_uint8
image=(root/'input/original.sms').read_bytes();low=(c.c_uint8*32768).from_buffer_copy(image[:32768]);bank=(c.c_uint8*16384).from_buffer_copy(image[0x18000:0x1c000])
rows=[]
for adapter in range(4):
 for full in (0,1):
  for flags in (0,0x20,0x40,0x60):
   for lines in (262,313):
    for epoch in (1080,0xfffffff0):
     baseline=None
     for mode in range(3):
      values=(c.c_uint32*16)();assert fn(adapter,full,flags,mode,lines,epoch,low,bank,values);v=list(values)
      assert v[9]==0,v
      if mode==2:
       assert v[:8]==[0,0x804,0,0,1,0,0,0] and v[8]==0x55 and v[11:13]==[1,1],v
      else:
       assert v[0]==1 and v[1]==0 and v[2]>500 and v[3]>50 and v[4]==mode and v[5]==full and v[6]>0 and v[7]==1 and v[8]==(0x9f|flags),v
       if mode==0:baseline=v
       else:
        assert v[:4]==baseline[:4] and v[5:11]==baseline[5:11] and v[13:15]==baseline[13:15] and v[15]==0,v
      rows.append(dict(adapter=adapter,full=full,flags=flags,lines=lines,epoch=epoch,mode=mode,result=v))
(out/'host-cases.json').write_text(json.dumps(rows,indent=2)+'\n');print('Host status binding:',len(rows),'cases passed',flush=True)
# Compile the identical contracts and expected host results on the real68000.
project=out/'kernel';src=project/'src';src.mkdir(parents=True)
shutil.copyfile(root/'megadrive/src/rom_header.c',src/'rom_header.c')
for name in modules:(src/(name+'.c')).write_text('#include "../../../../megadrive/src/'+name+'.c"\n')
(src/'wrapper.c').write_text('#include "../../wrapper.c"\n')
(project/'inc').mkdir()
for name in ('source_irq_timed_context','source_intro_sprite_status'):(project/'inc'/(name+'.h')).write_text('#include "../../../../megadrive/src/'+name+'.h"\n')
array=lambda values:'{'+','.join(map(str,values))+'}'
expected=['static const u8 low[32768]='+array(image[:32768])+';','static const u8 bank[16384]='+array(image[0x18000:0x1c000])+';',
 'typedef struct {u8 adapter,full,flags,mode;u16 lines;u32 epoch,expected[16];} BindingCase;', 'static const BindingCase cases[]={']
for row in rows:expected.append('{'+','.join(str(row[n]) for n in ('adapter','full','flags','mode','lines','epoch'))+','+array(row['result'])+'},')
expected.append('};');(src/'expected.h').write_text('\n'.join(expected)+'\n')
(src/'main.c').write_text(r'''#include <genesis.h>
#include "expected.h"
u8 binding_case(u8,u8,u8,u8,u16,u32,const u8 *,const u8 *,u32 *);
volatile u16 binding_done,binding_errors,binding_cases,binding_first_failure;
int main(bool hard_reset)
{
 (void)hard_reset;VDP_setEnable(FALSE);
 for(u16 n=0;n<sizeof(cases)/sizeof(cases[0]);n++)
 {
  const BindingCase *c=cases+n;u32 output[16];
  if(!binding_case(c->adapter,c->full,c->flags,c->mode,c->lines,c->epoch,low,bank,output) ||
     memcmp(output,c->expected,sizeof(output))) {binding_errors++;if(!binding_first_failure) binding_first_failure=n+1;}
  binding_cases++;
 }
 binding_done=1;while(TRUE) SYS_doVBlankProcess();return 0;
}
''')
build_env=dict(os.environ)
for key in ('TMP','TEMP','TMPDIR'):build_env[key]='.'
with (out/'build.log').open('w') as log:subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'tools/build_private_candidate.ps1'),'-Project',str(project),'-PaddingByte','255'],cwd=root,env=build_env,stdout=log,stderr=subprocess.STDOUT,check=True)
symbols={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in (project/'out/release/symbol.txt').read_text().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
results=[]
for region in ('ntsc','pal'):
 stats={}
 def observe(frame,ram):
  for name in ('binding_done','binding_errors','binding_cases','binding_first_failure'):stats[name]=int.from_bytes(bytes(ram[(symbols[name]+i)^1] for i in range(2)),'big')
  stats['frame']=frame
 with contextlib.redirect_stdout(io.StringIO()):run(project/'out/release/rom.bin',2000,out/region,set(),[],skip_intro=False,ram_observer=observe,stop_when=lambda:bool(stats.get('binding_done')),core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
 assert stats['binding_done']==1 and stats['binding_cases']==len(rows) and stats['binding_errors']==0,stats
 results.append(dict(region=region,**stats));print(region,stats,flush=True)
report=dict(passed=True,host_cases=len(rows),compiled_executions=len(rows)*2,results=results,
 native_sources={name:sha((root/'megadrive/src'/(name+'.c')).read_bytes()) for name in modules},
 header_sha256=sha((root/'megadrive/src/source_irq_context.h').read_bytes()),kernel_sha256=sha((project/'out/release/rom.bin').read_bytes()),
 scope='Optional live sprite status delivered to compact intro IRQ context before full/video/audio work. Four adapters, full/audio-only, flags20/40, NTSC/PAL and elapsed wrap. Real semantic IRQ and audio modules; disabled-provider state/work/PSG parity and provider rejection before publication.',
 limits=['Contract integration with seeded native sprite latches, not a SourceClock-driven parse/render/VRAM producer or physical audio/video proof.','Expected compiled outputs are independently host-checked adapter contracts; original source game coverage remains the separate temporal sprite corpus.'],production_rom_changed=False)
target=root/'analysis/v319_irq_status_binding_report.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n')
paths={p for p in out.rglob('*') if p.is_file()}|{target,Path(__file__).resolve()}
paths.update(root/'megadrive/src'/(name+'.c') for name in modules)
paths.update((root/'megadrive/src').glob('*.h'))
freeze(root,root/'analysis/v319-irq-status-binding',paths,report,[project/'out',out/'ntsc',out/'pal'],cleanup=True)
