"""Stable whole-frame spans, epoch wrap and horizontal read/IRQ contracts."""
import contextlib,ctypes as c,io,json,os,re,shutil,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
from run_core import run
out=root/'validation/v319-sprite-clock-boundaries01';assert not out.exists();out.mkdir()
code=r'''#include "source_intro_sprite_clock.h"
static u8 vram[16384],regs[16];
u32 clock_boundary_contracts(void)
{
 u32 errors=0;u8 value;SourceIntroSpriteClock whole,stepped,before;SourceIntroSpriteClockBinding binding;SourceClockIrq entry;
 __builtin_memset(vram,0,sizeof(vram));__builtin_memset(regs,0,sizeof(regs));
 regs[0]=6;regs[1]=0xe0;regs[5]=regs[6]=255;
 for(u16 n=0;n<9;n++) {vram[0x3f00+n]=10;vram[0x3f80+2*n]=30;}
 vram[0x3f09]=208;
 __builtin_memset(vram+8192,255,32);
 for(u16 region=0;region<2;region++) for(u16 wrap=0;wrap<2;wrap++)
 {
  u16 lines=region?313:262;u32 epoch=wrap?0xfffffff0UL:0,period=(u32)lines*3420;
  if(!source_intro_sprite_clock_init(&whole,lines,192UL*3420,epoch)) errors|=1;
  stepped=whole;
  if(!source_intro_sprite_clock_advance(&whole,epoch+period,vram,regs)) errors|=2;
  for(u16 line=1;line<=lines;line++) if(!source_intro_sprite_clock_advance(&stepped,epoch+(u32)line*3420,vram,regs)) errors|=4;
  if(__builtin_memcmp(&whole,&stepped,sizeof(whole)) || whole.sprites.flags!=0x60 || whole.vint!=0x80) errors|=8;
  if(!source_intro_sprite_clock_read(&whole,whole.elapsed+165,11,vram,regs,&value) || value!=0xff || whole.vint || whole.sprites.flags) errors|=16;
  if(!source_intro_sprite_clock_read(&whole,whole.elapsed+165,11,vram,regs,&value) || value!=0x1f) errors|=32;
  source_intro_sprite_clock_init(&whole,lines,192UL*3420,epoch);
  if(!source_intro_sprite_clock_advance(&whole,epoch+(u32)(lines-192+11)*3420,vram,regs)) errors|=64;
  if(!source_intro_sprite_clock_read(&whole,whole.elapsed+165,11,vram,regs,&value) || value!=0xdf || whole.sprites.flags!=0x20) errors|=128;
  if(!source_intro_sprite_clock_read(&whole,whole.elapsed+1000,11,vram,regs,&value) || value!=0x3f || whole.sprites.flags) errors|=256;
  source_intro_sprite_clock_init(&whole,lines,192UL*3420,epoch);
  before=whole;binding.clock=&whole;binding.vram=vram;binding.registers=regs;
  entry.entry_elapsed=epoch+165+37UL*15;entry.entry_raster=192UL*3420+165+37UL*15;entry.entry_refresh=0;
  entry.entry_raster++;
  if(source_intro_sprite_clock_irq_status(&binding,&entry,&value) || __builtin_memcmp(&before,&whole,sizeof(whole))) errors|=512;
  entry.entry_raster--;
  if(!source_intro_sprite_clock_irq_status(&binding,&entry,&value) || value!=0x1f) errors|=1024;
  if(source_intro_sprite_clock_advance(&whole,whole.elapsed+period+1,vram,regs) || whole.error!=1) errors|=2048;
 }
 return errors;
}
'''
(out/'contracts.c').write_text(code)
env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH'];sdk=root.parents[1]/'work/sgdk'
sources=[root/'megadrive/src'/(n+'.c') for n in ('source_intro_sprite_status','source_intro_sprite_clock')]
cmd=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-Wall','-Wextra','-Werror','-I',str(sdk/'inc'),'-I',str(root/'megadrive/src'),str(out/'contracts.c'),*map(str,sources),'-o',str(out/'contracts.dll')]
built=subprocess.run(cmd,capture_output=True,text=True,env=env);(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
dll=c.CDLL(str(out/'contracts.dll'));dll.clock_boundary_contracts.restype=c.c_uint32;actual=dll.clock_boundary_contracts();assert actual==0,hex(actual)
project=out/'kernel';src=project/'src';src.mkdir(parents=True);(project/'inc').mkdir();shutil.copyfile(root/'megadrive/src/rom_header.c',src/'rom_header.c')
for source in sources:
 (src/source.name).write_text('#include "../../../../megadrive/src/'+source.name+'"\n')
 (project/'inc'/source.with_suffix('.h').name).write_text('#include "../../../../megadrive/src/'+source.with_suffix('.h').name+'"\n')
(src/'contracts.c').write_text('#include "../../contracts.c"\n')
(src/'main.c').write_text('#include <genesis.h>\nu32 clock_boundary_contracts(void);\nvolatile u32 boundary_errors;volatile u16 boundary_done;\nint main(bool hard_reset) {(void)hard_reset;VDP_setEnable(FALSE);boundary_errors=clock_boundary_contracts();boundary_done=1;while(TRUE) SYS_doVBlankProcess();return 0;}\n')
for key in ('TMP','TEMP','TMPDIR'):env[key]='.'
with (out/'build.log').open('w') as log:subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'tools/build_private_candidate.ps1'),'-Project',str(project),'-PaddingByte','255'],cwd=root,env=env,check=True,stdout=log,stderr=subprocess.STDOUT)
symbols={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in (project/'out/release/symbol.txt').read_text().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))};results=[]
for region in ('ntsc','pal'):
 stats={}
 def observe(frame,ram):
  for name,size in [('boundary_errors',4),('boundary_done',2)]:stats[name]=int.from_bytes(bytes(ram[(symbols[name]+i)^1] for i in range(size)),'big')
  stats['frame']=frame
 with contextlib.redirect_stdout(io.StringIO()):run(project/'out/release/rom.bin',2000,out/region,set(),[],skip_intro=False,ram_observer=observe,stop_when=lambda:bool(stats.get('boundary_done')),core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
 assert stats['boundary_done'] and not stats['boundary_errors'],stats
 results.append(dict(region=region,**stats))
report=dict(passed=True,host_errors=actual,results=results,rom_sha256=sha((project/'out/release/rom.bin').read_bytes()),scope='48 contract checks on host and each compiled region: whole-frame versus single-line stable advance,32-bit epoch wrap, overflow/collision/VINT/read-to-clear, early horizontal read deferral, correct/mismatched IRQ time origins and overlong-span rejection.',limits=['Synthetic contract inputs for early-read branch; not a new source-oracle observation of that branch.','No physical throughput claim: kernel setup and full-frame stable spans are diagnostic only.'])
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
