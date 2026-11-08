"""Replay all captured native status transitions on the actual compiled68000 code."""
import argparse,contextlib,io,json,os,re,shutil,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
from run_core import run
p=argparse.ArgumentParser();p.add_argument('--start',type=int,required=True);p.add_argument('--count',type=int,required=True);p.add_argument('--kernel',required=True);a=p.parse_args()
assert a.start>=0 and 0<a.count<=3000 and re.fullmatch('kernel[0-9]+',a.kernel)
work=root/'validation/v319-chip-events02';report=json.loads((work/'report.json').read_bytes());assert report['passed']
raw=(work/'native-transitions.bin').read_bytes();assert sha(raw)==report['transition_sha256'] and report['transition_stride']==472
selected=bytearray(raw[a.start*472:(a.start+a.count)*472]);assert len(selected)==a.count*472
swap=[*range(0,64,4),68,*range(72,136,4),140,144,*range(424,440,2)]
for start in range(0,len(selected),472):
 for offset in swap:selected[start+offset],selected[start+offset+1]=selected[start+offset+1],selected[start+offset]
project=work/a.kernel;assert not project.exists();src=project/'src';src.mkdir(parents=True);inc=project/'inc';inc.mkdir()
shutil.copyfile(root/'megadrive/src/rom_header.c',src/'rom_header.c')
(inc/'source_intro_sprite_status.h').write_text('#include "../../../../megadrive/src/source_intro_sprite_status.h"\n')
(src/'source_intro_sprite_status.c').write_text('#include "../../../../megadrive/src/source_intro_sprite_status.c"\n')
(src/'transitions-be.bin').write_bytes(selected)
(src/'cases.s').write_text('.section .rodata\n.balign 2\n.global chip_cases\nchip_cases:\n.incbin "src/transitions-be.bin"\n')
main=r'''#include <genesis.h>
#include "source_intro_sprite_status.h"
typedef struct {
 SourceIntroSpriteStatus before,after;s16 line;
 u8 kind,hcounter,result,pattern_count,source_flags,source_valid;
 u8 regs[16],sat[256];u16 addresses[8];u8 patterns[32];
} ChipCase;
typedef char StateSizeCheck[sizeof(SourceIntroSpriteStatus)==72?1:-1];
typedef char CaseSizeCheck[sizeof(ChipCase)==472?1:-1];
extern const ChipCase chip_cases[];
static u8 vram[16384];
volatile u32 chip_cases_done,chip_case_errors;
volatile u16 chip_done,chip_first_failure;
static void canonical(SourceIntroSpriteStatus *state)
{
 for(u16 slot=0;slot<2;slot++) for(u16 n=state->count[slot];n<8;n++) memset(state->objects[slot]+n,0,sizeof(SourceIntroCachedSprite));
 if(!(state->flags&0x20)) {state->collision_line=-1;state->collision_hcounter=0;}
}
int main(bool hard_reset)
{
 (void)hard_reset;VDP_setEnable(FALSE);
 for(u16 n=0;n<CASE_COUNT;n++)
 {
  const ChipCase *entry=chip_cases+n;SourceIntroSpriteStatus model=entry->before;u8 result=0;
  memset(vram,0,sizeof(vram));
  if(entry->kind==0)
  {
   u16 mask=((u16)~0x3f80^((u16)entry->regs[5]<<7))|0x80;
   memcpy(vram+(mask&0x3f00),entry->sat,256);
   result=source_intro_sprite_parse(&model,entry->line,vram,entry->regs);
  }
  else if(entry->kind==1)
  {
   for(u16 k=0;k<entry->pattern_count;k++) memcpy(vram+entry->addresses[k],entry->patterns+k*4,4);
   result=source_intro_sprite_render(&model,entry->line,vram,entry->regs);
  }
  else if(entry->kind==2) result=source_intro_sprite_read(&model,entry->line,entry->hcounter);
  else chip_case_errors++;
  canonical(&model);
  if(result!=entry->result || memcmp(&model,&entry->after,sizeof(model)) ||
     (entry->source_valid && result!=entry->source_flags)) chip_case_errors++;
  if(chip_case_errors && !chip_first_failure) chip_first_failure=n+1;
  chip_cases_done++;
 }
 chip_done=1;while(TRUE) SYS_doVBlankProcess();return 0;
}
'''
(src/'main.c').write_text('#define CASE_COUNT '+str(a.count)+'\n'+main)
env=dict(os.environ)
for key in ('TMPDIR','TMP','TEMP'):env[key]='.'
subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'tools/build_private_candidate.ps1'),'-Project',str(project),'-PaddingByte','255'],cwd=root,env=env,check=True,stdout=subprocess.DEVNULL)
sy={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in (project/'out/release/symbol.txt').read_text().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
results=[]
for region in ('ntsc','pal'):
 stats={}
 def observe(frame,ram):
  for name,size in [('chip_cases_done',4),('chip_case_errors',4),('chip_done',2),('chip_first_failure',2)]:stats[name]=int.from_bytes(bytes(ram[(sy[name]+i)^1] for i in range(size)),'big')
  stats['frame']=frame
 with contextlib.redirect_stdout(io.StringIO()):
  run(project/'out/release/rom.bin',5000,work/(a.kernel+'-'+region),set(),[],skip_intro=False,ram_observer=observe,stop_when=lambda:bool(stats.get('chip_done')),core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
 assert stats['chip_done']==1 and stats['chip_cases_done']==a.count and stats['chip_case_errors']==0,stats
 results.append(dict(region=region,**stats))
r=dict(passed=True,start=a.start,count=a.count,results=results,rom_sha256=sha((project/'out/release/rom.bin').read_bytes()),scope='All requested native parse/render/read state transitions, input sparse VRAM,flags and observable cached state compared on compiled68000. Direct original expected read flags checked where captured.')
(work/(a.kernel+'-report.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(kernel=a.kernel,start=a.start,count=a.count,results=results)),flush=True)
