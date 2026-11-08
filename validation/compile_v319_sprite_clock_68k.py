"""Run calendar boundary/read vectors and its IRQ adapter on compiled68000."""
import argparse,contextlib,io,json,os,re,shutil,struct,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
from run_core import run
p=argparse.ArgumentParser();p.add_argument('--start',type=int,required=True);p.add_argument('--count',type=int,required=True);p.add_argument('--kernel',required=True);a=p.parse_args()
assert 0<=a.start and 0<a.count<=3000 and re.fullmatch(r'kernel[0-9]+',a.kernel)
work=root/'validation/v319-sprite-clock03';report=json.loads((work/'report.json').read_bytes());assert report['passed']
for name,digest in report['native_sources'].items():assert sha((root/'megadrive/src'/name).read_bytes())==digest
raw=(work/'transitions.bin').read_bytes();assert sha(raw)==report['transition_sha256'] and a.start+a.count<=report['transition_vectors']
packed=bytearray(raw[a.start*512:(a.start+a.count)*512])
for base in range(0,len(packed),512):
 for state in (0,92):
  for off in [*range(0,64,4),68,88]:struct.pack_into('>H',packed,base+state+off,struct.unpack_from('<H',packed,base+state+off)[0])
  for off in (72,76,80,84):struct.pack_into('>I',packed,base+state+off,struct.unpack_from('<I',packed,base+state+off)[0])
 struct.pack_into('>I',packed,base+184,struct.unpack_from('<I',packed,base+184)[0])
 for off in range(464,480,2):struct.pack_into('>H',packed,base+off,struct.unpack_from('<H',packed,base+off)[0])
project=work/a.kernel;assert not project.exists();src=project/'src';src.mkdir(parents=True);(project/'inc').mkdir()
shutil.copyfile(root/'megadrive/src/rom_header.c',src/'rom_header.c')
for name in ('source_intro_sprite_status','source_intro_sprite_clock'):
 (src/(name+'.c')).write_text('#include "../../../../megadrive/src/'+name+'.c"\n')
 (project/'inc'/(name+'.h')).write_text('#include "../../../../megadrive/src/'+name+'.h"\n')
(src/'transitions-be.bin').write_bytes(packed)
(src/'cases.s').write_text('.section .rodata\n.balign 2\n.global clock_cases\nclock_cases:\n.incbin "src/transitions-be.bin"\n')
main=r'''#include <genesis.h>
#include "source_intro_sprite_clock.h"
typedef struct {
 SourceIntroSpriteClock before,after;u32 delta;
 u8 kind,tstates,result,source_valid,regs[16],sat[256];u16 addresses[8];u8 patterns[32];
} ClockCase;
typedef char ClockSizeCheck[sizeof(SourceIntroSpriteClock)==92?1:-1];
typedef char CaseSizeCheck[sizeof(ClockCase)==512?1:-1];
extern const ClockCase clock_cases[];
static u8 vram[16384];
volatile u16 clock_done,clock_errors,clock_first_failure,clock_cases_done,clock_irq_checks;
static void canonical(SourceIntroSpriteClock *state)
{
 for(u16 slot=0;slot<2;slot++) for(u16 n=state->sprites.count[slot];n<8;n++) memset(state->sprites.objects[slot]+n,0,sizeof(SourceIntroCachedSprite));
 if(!(state->sprites.flags&0x20)) {state->sprites.collision_line=-1;state->sprites.collision_hcounter=0;}
}
int main(bool hard_reset)
{
 (void)hard_reset;VDP_setEnable(FALSE);
 for(u16 n=0;n<CASE_COUNT;n++)
 {
  const ClockCase *entry=clock_cases+n;SourceIntroSpriteClock model=entry->before;u8 result=0,accepted;
  memset(vram,0,sizeof(vram));
  if(entry->delta>=model.until_line && (entry->regs[0]&4))
  {
   u16 line=(model.raster/3420+1)%model.lines,mask=((u16)~0x3f80^((u16)entry->regs[5]<<7))|0x80;
   if(line==model.lines-1 || line<192) memcpy(vram+(mask&0x3f00),entry->sat,256);
   if(line<192 && (entry->regs[1]&0x40) && !(model.sprites.flags&0x20))
    for(u16 k=0;k<model.sprites.count[line&1];k++) memcpy(vram+entry->addresses[k],entry->patterns+k*4,4);
  }
  if(entry->kind==0) {accepted=source_intro_sprite_clock_advance(&model,entry->delta,vram,entry->regs);result=accepted;}
  else accepted=source_intro_sprite_clock_read(&model,entry->delta,entry->tstates,vram,entry->regs,&result);
  canonical(&model);
  if(!accepted || result!=entry->result || memcmp(&model,&entry->after,sizeof(model))) clock_errors++;
  if(entry->kind==1)
  {
   SourceClockIrq irq;SourceIntroSpriteClockBinding binding;
   model=entry->before;binding.clock=&model;binding.vram=vram;binding.registers=entry->regs;
   irq.entry_elapsed=entry->delta+37UL*15;irq.entry_raster=(model.raster+irq.entry_elapsed)%model.period;irq.entry_refresh=0;
   accepted=source_intro_sprite_clock_irq_status(&binding,&irq,&result);canonical(&model);
   if(!accepted || result!=entry->result || memcmp(&model,&entry->after,sizeof(model))) clock_errors++;
   clock_irq_checks++;
  }
  if(clock_errors && !clock_first_failure) clock_first_failure=n+1;
  clock_cases_done++;
 }
 clock_done=1;while(TRUE) SYS_doVBlankProcess();return 0;
}
'''
(src/'main.c').write_text('#define CASE_COUNT '+str(a.count)+'\n'+main)
env=dict(os.environ)
for key in ('TMPDIR','TMP','TEMP'):env[key]='.'
with (project/'build-command.log').open('w') as log:subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'tools/build_private_candidate.ps1'),'-Project',str(project),'-PaddingByte','255'],cwd=root,env=env,check=True,stdout=log,stderr=subprocess.STDOUT)
symbols={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in (project/'out/release/symbol.txt').read_text().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
results=[]
for region in ('ntsc','pal'):
 stats={}
 def observe(frame,ram):
  for name in ('clock_done','clock_errors','clock_first_failure','clock_cases_done','clock_irq_checks'):stats[name]=int.from_bytes(bytes(ram[(symbols[name]+i)^1] for i in range(2)),'big')
  stats['frame']=frame
 with contextlib.redirect_stdout(io.StringIO()):run(project/'out/release/rom.bin',5000,work/(a.kernel+'-'+region),set(),[],skip_intro=False,ram_observer=observe,stop_when=lambda:bool(stats.get('clock_done')),core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
 assert stats['clock_done']==1 and stats['clock_cases_done']==a.count and stats['clock_errors']==0,stats
 results.append(dict(region=region,**stats))
r=dict(passed=True,start=a.start,count=a.count,results=results,rom_sha256=sha((project/'out/release/rom.bin').read_bytes()),scope='Normalized advance-only line transitions and exact original read phases, full cache/latch/calendar output on68000. Each read also checks the native IRQ provider with0137 minus37T sampling. Expected read bytes were source-checked by the host corpus.')
(work/(a.kernel+'-report.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(kernel=a.kernel,start=a.start,count=a.count,results=results)),flush=True)
