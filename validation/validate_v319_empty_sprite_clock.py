"""Compare empty-list calendar skip to immutable prior line-by-line code."""
import contextlib,ctypes as c,io,json,os,re,shutil,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from run_core import run
from archive_lossless_evidence import sha
out=root/'validation/v319-empty-sprite-clock02';assert not out.exists();out.mkdir();snapshot=out/'sources';snapshot.mkdir()
for name in ('source_intro_sprite_clock.c','source_intro_sprite_clock.h','source_intro_sprite_status.c','source_intro_sprite_status.h','source_clock.h','source_video_clock_math.h'):shutil.copyfile(root/'megadrive/src'/name,snapshot/name)
old=subprocess.check_output(['git','show','HEAD:megadrive/src/source_intro_sprite_clock.c'],cwd=root);(out/'reference-before.c').write_bytes(old)
prefix=''.join('#define '+name+' '+name+'_reference\n' for name in ('source_intro_sprite_clock_init','source_intro_sprite_clock_advance','source_intro_sprite_clock_read','source_intro_sprite_clock_irq_status'))
(out/'reference.c').write_text(prefix+old.decode())
code=r'''#include "source_intro_sprite_clock.h"
u8 source_intro_sprite_clock_advance_reference(SourceIntroSpriteClock*,u32,const u8*,const u8*);
static SourceIntroSpriteClock fast,reference;
static u8 vram[16384],regs[16];
volatile u32 empty_cases,empty_errors;
void empty_contracts(void)
{
 empty_cases=empty_errors=0;
 for(u16 region=0;region<2;region++)
 {
  u16 lines=region?313:262;u32 period=(u32)lines*3420;
  for(u16 line=0;line<lines;line++) for(u16 phase_index=0;phase_index<3;phase_index++)
  for(u16 kind=0;kind<10;kind++) for(u16 di=0;di<5;di++) for(u16 wrap=0;wrap<2;wrap++)
  {
   u16 phase=phase_index==0?0:phase_index==1?1:3419;u32 raster=(u32)line*3420+phase,epoch=wrap?0xfffffff0UL:0;
   u32 deltas[]={0,1,3420-phase-1,3420-phase,period};u8 a,b;
   vram[0x3f01]=0;__builtin_memset(regs,0,sizeof(regs));
   regs[0]=6;regs[1]=kind==0?0xa0:0xe0;regs[5]=regs[6]=255;vram[0x3f00]=208;
   source_intro_sprite_clock_init(&fast,lines,raster,epoch);
   for(u16 slot=0;slot<2;slot++) for(u16 n=0;n<8;n++) {fast.sprites.objects[slot][n].x=n*3-5;fast.sprites.objects[slot][n].row=n&7;fast.sprites.objects[slot][n].attribute=n;}
   if(kind==2) fast.sprites.pending_overflow=0x40;
   if(kind==3) fast.sprites.count[0]=1;
   if(kind==4) fast.sprites.count[1]=1;
   if(kind==5) {fast.sprites.flags=0x20;fast.sprites.collision_line=100;fast.sprites.collision_hcounter=40;}
   if(kind==6) fast.sprites.flags=0x40;
   if(kind==7) {regs[0]=2;fast.sprites.count[0]=3;fast.sprites.pending_overflow=0x40;}
   if(kind==8) regs[1]|=1;
   if(kind==9) {vram[0x3f00]=7;vram[0x3f01]=208;}
   reference=fast;
   a=source_intro_sprite_clock_advance(&fast,epoch+deltas[di],vram,regs);
   b=source_intro_sprite_clock_advance_reference(&reference,epoch+deltas[di],vram,regs);
   if(a!=b || __builtin_memcmp(&fast,&reference,sizeof(fast))) empty_errors++;
   empty_cases++;
  }
 }
}
'''
(out/'contracts.c').write_text(code)
sdk=root.parents[1]/'work/sgdk';env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
cmd=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-Wall','-Wextra','-Werror','-I',str(sdk/'inc'),'-I',str(snapshot),str(out/'contracts.c'),str(out/'reference.c'),str(snapshot/'source_intro_sprite_clock.c'),str(snapshot/'source_intro_sprite_status.c'),'-o',str(out/'empty.dll')]
built=subprocess.run(cmd,env=env,capture_output=True,text=True);(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
dll=c.CDLL(str(out/'empty.dll'));dll.empty_contracts();count=c.c_uint32.in_dll(dll,'empty_cases').value;errors=c.c_uint32.in_dll(dll,'empty_errors').value;assert count==172500 and not errors,(count,errors)
project=out/'kernel';src=project/'src';src.mkdir(parents=True);(project/'inc').mkdir();shutil.copyfile(root/'megadrive/src/rom_header.c',src/'rom_header.c')
for name in ('source_intro_sprite_clock.c','source_intro_sprite_status.c'):(src/name).write_text('#include "../../sources/'+name+'"\n')
(src/'contracts.c').write_text('#include "../../contracts.c"\n');(src/'reference.c').write_text('#include "../../reference.c"\n');(project/'inc/source_intro_sprite_clock.h').write_text('#include "../../sources/source_intro_sprite_clock.h"\n')
(project/'inc/source_video_clock_math.h').write_text('#include "../../sources/source_video_clock_math.h"\n')
(src/'main.c').write_text('#include <genesis.h>\nvoid empty_contracts(void);extern volatile u32 empty_cases,empty_errors;volatile u16 empty_done;\nint main(bool hard_reset){(void)hard_reset;VDP_setEnable(FALSE);empty_contracts();empty_done=1;while(TRUE) SYS_doVBlankProcess();return 0;}\n')
for key in ('TMP','TEMP','TMPDIR'):env[key]='.'
with (out/'build.log').open('w') as log:subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'tools/build_private_candidate.ps1'),'-Project',str(project),'-PaddingByte','255'],cwd=root,env=env,check=True,stdout=log,stderr=subprocess.STDOUT)
symbols={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in (project/'out/release/symbol.txt').read_text().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))};results=[]
for region in ('ntsc','pal'):
 stats={}
 def observe(frame,ram):
  for name,size in [('empty_cases',4),('empty_errors',4),('empty_done',2)]:stats[name]=int.from_bytes(bytes(ram[(symbols[name]+i)^1] for i in range(size)),'big')
  stats['frame']=frame
 with contextlib.redirect_stdout(io.StringIO()):run(project/'out/release/rom.bin',150000,out/region,set(),[],skip_intro=False,ram_observer=observe,stop_when=lambda:bool(stats.get('empty_done')),core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
 assert stats['empty_done'] and stats['empty_cases']==count and not stats['empty_errors'],stats
 results.append(dict(region=region,**stats));print(region,stats,flush=True)
(out/'report.json').write_text(json.dumps(dict(passed=True,host_cases=count,results=results,reference_sha256=sha(old),native_source_sha256=sha((snapshot/'source_intro_sprite_clock.c').read_bytes()),scope='All575PAL/NTSC lines,3intraline phases,10cache/flag/mode/SAT states,5delta edges and32bit epoch wrap. Complete calendar/caches/latches compared against frozen prior line-by-line implementation; unsupported-mode return/partial state included.'),indent=2)+'\n')
