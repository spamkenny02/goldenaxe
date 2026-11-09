"""Compare native SAT runs against exact individual OUTI ports,host and68000."""
import contextlib,ctypes as c,io,json,os,re,shutil,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from run_core import run
from archive_lossless_evidence import sha
out=root/'validation/v320-sat-runs02';assert not out.exists();out.mkdir();snapshot=out/'sources';snapshot.mkdir()
modules=['source_intro_vdp.c','source_intro_sprite_clock.c','source_intro_sprite_status.c']
for path in (root/'megadrive/src').glob('*.h'):shutil.copyfile(path,snapshot/path.name)
for name in modules:shutil.copyfile(root/'megadrive/src'/name,snapshot/name)
code=r'''#include "source_intro_vdp.h"
static SourceIntroVdp fast,slow,initial;
static u8 va[16384],vb[16384],bytes[128];
volatile u32 sat_cases,sat_errors,sat_first_failure;
static u8 equal(void)
{
 u8 *saved=fast.vram;u8 result;
 fast.vram=slow.vram;result=!__builtin_memcmp(&fast,&slow,sizeof(fast)) && !__builtin_memcmp(va+0x3f00,vb+0x3f00,256);fast.vram=saved;return result;
}
void sat_contracts(void)
{
 const u16 phases[]={0,1,239,240,3180,3419},counts[]={1,2,63,64,65,127,128};
 sat_cases=sat_errors=sat_first_failure=0;
 for(u16 n=0;n<16384;n++) va[n]=vb[n]=(n*73+19)&255;
 __builtin_memset(&initial,0,sizeof(initial));initial.registers[0]=6;initial.registers[5]=initial.registers[6]=255;initial.low=128;initial.code=1;initial.buffer=69;
 for(u16 region=0;region<2;region++)
 {
  u16 lines=region?313:262;u32 period=(u32)lines*3420;
  for(u16 line=0;line<lines;line++) for(u16 pi=0;pi<6;pi++) for(u16 ci=0;ci<7;ci++) for(u16 kind=0;kind<2;kind++)
  {
   u16 count=counts[ci],address=ci==0?0x3fff:kind?0x3f80:0x3f00;
   u32 first=(u32)line*3420+phases[pi],raster=first>=1000?first-1000:first+period-1000,epoch=ci&1?0xfffff000UL:0,last;u8 ok=1,sa=0,sb=0;
   fast=slow=initial;fast.vram=va;slow.vram=vb;fast.registers[1]=slow.registers[1]=kind?0xe0:0xa0;
   fast.address=slow.address=address;fast.instruction_elapsed=slow.instruction_elapsed=epoch;fast.instruction_raster=slow.instruction_raster=raster;
   source_intro_sprite_clock_init(&fast.clock,lines,raster,epoch);source_intro_sprite_clock_init(&slow.clock,lines,raster,epoch);
   for(u16 n=0;n<256;n++) va[0x3f00+n]=vb[0x3f00+n]=(n*17+line)&255;
   for(u16 n=0;n<12;n++) va[0x3f00+n]=vb[0x3f00+n]=(line+n-5)&255;
   va[0x3f0c]=vb[0x3f0c]=208;
   for(u16 n=0;n<128;n++) bytes[n]=(n*37+ci+kind)&255;
   if(kind)
   {
    fast.clock.sprites.count[0]=fast.clock.sprites.count[1]=3;
    fast.clock.sprites.pending_overflow=0x40;
    if(ci&1) {fast.clock.sprites.flags=0x20;fast.clock.sprites.collision_line=37;fast.clock.sprites.collision_hcounter=19;}
    for(u16 slot=0;slot<2;slot++) for(u16 n=0;n<3;n++) {fast.clock.sprites.objects[slot][n].x=n+30;fast.clock.sprites.objects[slot][n].row=7;fast.clock.sprites.objects[slot][n].attribute=255;}
    slow.clock.sprites=fast.clock.sprites;
   }
   fast.clock.vint=slow.clock.vint=pi&1?0x80:0;
   ok=source_intro_vdp_sat_run(&fast,epoch+1000,first,bytes,count);
   for(u16 n=0;n<count;n++)
   {
    u32 elapsed=1000+(u32)n*240,at=raster+elapsed;while(at>=period) at-=period;
    if(!source_intro_vdp_out(&slow,epoch+elapsed,at,16,0xbe,bytes[n])) ok=0;
   }
   if(!ok || !equal()) {sat_errors++;if(!sat_first_failure) sat_first_failure=sat_cases+1;}
   last=epoch+1000+(u32)(count-1)*240;
   ok=source_intro_vdp_checkpoint(&fast,last+165) && source_intro_vdp_checkpoint(&slow,last+165) && source_intro_vdp_read(&fast,last+330,11,0xbf,&sa) && source_intro_vdp_read(&slow,last+330,11,0xbf,&sb);
   if(!ok || sa!=sb || !equal()) {sat_errors++;if(!sat_first_failure) sat_first_failure=sat_cases+1;}
   if(pi==5 && ci==6 && kind==1 && __builtin_memcmp(va,vb,16384)) {sat_errors++;if(!sat_first_failure) sat_first_failure=sat_cases+1;}
   sat_cases++;
  }
 }
}
'''
(out/'contracts.c').write_text(code)
sdk=root.parents[1]/'work/sgdk';env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
cmd=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-Wall','-Wextra','-Werror','-I',str(sdk/'inc'),'-I',str(snapshot),str(out/'contracts.c'),*[str(snapshot/n) for n in modules],'-o',str(out/'sat.dll')]
built=subprocess.run(cmd,env=env,capture_output=True,text=True);(out/'compile.log').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr
dll=c.CDLL(str(out/'sat.dll'));dll.sat_contracts();count=c.c_uint32.in_dll(dll,'sat_cases').value;errors=c.c_uint32.in_dll(dll,'sat_errors').value;first=c.c_uint32.in_dll(dll,'sat_first_failure').value;assert count==48300 and not errors,(count,errors,first);print('host',count,'cases passed',flush=True)
project=out/'kernel';src=project/'src';src.mkdir(parents=True);inc=project/'inc';inc.mkdir();shutil.copyfile(root/'megadrive/src/rom_header.c',src/'rom_header.c')
for name in modules:(src/name).write_text('#include "../../sources/'+name+'"\n')
(src/'contracts.c').write_text('#include "../../contracts.c"\n');(inc/'source_intro_vdp.h').write_text('#include "../../sources/source_intro_vdp.h"\n')
(src/'main.c').write_text('#include <genesis.h>\nvoid sat_contracts(void);extern volatile u32 sat_cases,sat_errors,sat_first_failure;volatile u16 sat_done;\nint main(bool hard_reset){(void)hard_reset;VDP_setEnable(FALSE);sat_contracts();sat_done=1;while(TRUE) SYS_doVBlankProcess();return 0;}\n')
for key in ('TMP','TEMP','TMPDIR'):env[key]='.'
with (out/'build.log').open('w') as log:subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'tools/build_private_candidate.ps1'),'-Project',str(project),'-PaddingByte','255'],cwd=root,env=env,check=True,stdout=log,stderr=subprocess.STDOUT)
symbols={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in (project/'out/release/symbol.txt').read_text().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))};results=[]
for region in ('ntsc','pal'):
 stats={}
 def observe(frame,ram):
  for name,size in [('sat_cases',4),('sat_errors',4),('sat_first_failure',4),('sat_done',2)]:stats[name]=int.from_bytes(bytes(ram[(symbols[name]+i)^1] for i in range(size)),'big')
  stats['frame']=frame
 with contextlib.redirect_stdout(io.StringIO()):run(project/'out/release/rom.bin',350000,out/region,set(),[],skip_intro=False,ram_observer=observe,stop_when=lambda:bool(stats.get('sat_done')),core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
 assert stats['sat_done'] and stats['sat_cases']==count and not stats['sat_errors'],stats
 results.append(dict(region=region,**stats));print(region,stats,flush=True)
(out/'report.json').write_text(json.dumps(dict(passed=True,host_cases=count,results=results,native_sources={n:sha((snapshot/n).read_bytes()) for n in modules},scope='All575source lines,6first-OUT phases,7counts including1/128 and3FFFboundary,displayoff/on,cached sprites aliasing mutated SAT patterns,pendingoverflow and collision/VINT latches,32bit epochwrap. CompleteVDP/calendar/cache and256SAT bytes at every run end/following read-to-clear status match individual16T OUTIs. Full16KiBVRAM additionally compared after every source-line block; untouched non-SAT bytes remain canaries across cases.'),indent=2)+'\n')
