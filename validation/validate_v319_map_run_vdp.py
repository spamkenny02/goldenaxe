"""Differential stable-run versus individual original OUTs,complete VDP state."""
import contextlib,ctypes as c,io,json,os,re,shutil,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
from run_core import run
out=root/'validation/v319-map-run-vdp02';assert not out.exists();out.mkdir()
code=r'''#include "source_intro_vdp.h"
static u8 memory[2][16384],data[768];
static SourceIntroVdp vdp[2];
volatile u32 run_vdp_cases,run_vdp_errors;
void map_run_contracts(void)
{
 static const u16 sizes[]={1,2,63,256};
 static const u16 clear_addresses[]={0x4003,0x5fff,0x6003};
 static const u16 map_addresses[]={0x7800,0x7880,0x7a00};
 run_vdp_cases=run_vdp_errors=0;
 for(u16 i=0;i<768;i++) data[i]=(i*37+11)&255;
 for(u16 region=0;region<2;region++) for(u16 bank=0;bank<2;bank++) for(u16 clear=0;clear<2;clear++)
 for(u16 phase=0;phase<6;phase++) for(u16 ci=0;ci<4;ci++) for(u16 ai=0;ai<3;ai++)
 {
  u16 lines=region?313:262;u32 period=(u32)lines*3420;
  u32 phases[]={0,3420+3000,190UL*3420+3400,192UL*3420+3410,period-20,193UL*3420-15};
  u32 raster=phases[phase],start=period+400,elapsed=start;u16 address=clear?clear_addresses[ai]:map_addresses[ai],count=sizes[ci];
  if(!clear && ci==3 && ai==0) count=768;
  for(u16 m=0;m<2;m++)
  {
   source_intro_vdp_init(vdp+m,memory[m],lines,raster,0);
   vdp[m].registers[0]=6;vdp[m].registers[1]=0xe0;vdp[m].registers[6]=bank?255:251;
   for(u16 n=0;n<16384;n++) memory[m][n]=(n*13+7)&255;
   for(u16 n=0;n<9;n++) {memory[m][0x3f00+n]=2;memory[m][0x3f80+n*2]=30;memory[m][0x3f81+n*2]=clear?(ai==1?255:n):(0xc0+ai*8+n);}
   memory[m][0x3f09]=208;
   vdp[m].address=clear?0x20:address&0x3fff;vdp[m].code=clear?3:1;vdp[m].low=clear?0x77:(u8)address;vdp[m].buffer=0x36;
   if(!source_intro_sprite_clock_advance(&vdp[m].clock,period,memory[m],vdp[m].registers)) run_vdp_errors++;
   {u8 ignored;if(!source_intro_vdp_checkpoint(vdp+m,period) || !source_intro_vdp_read(vdp+m,period+165,11,0xbf,&ignored)) run_vdp_errors++;}
  }
  for(u16 n=0;n<count;n++)
  {
   if(clear)
   {
    const u16 offsets[]={30,45,101};u8 values[]={(u8)address,(u8)(address>>8),255};
    for(u16 k=0;k<3;k++)
     if(!source_intro_vdp_out(vdp,elapsed+(u32)offsets[k]*15,(raster+elapsed+(u32)offsets[k]*15)%period,11,k==2?0xbe:0xbf,values[k])) run_vdp_errors++;
    elapsed+=1860;address+=4;
   }
   else
   {
    if(!source_intro_vdp_out(vdp,elapsed+240,(raster+elapsed+240)%period,16,0xbe,data[n])) run_vdp_errors++;
    elapsed+=480;address++;
   }
  }
  address=clear?clear_addresses[ai]:map_addresses[ai];
  if(!source_intro_vdp_map_run(vdp+1,start,(raster+start)%period,period,address,count,clear?0:data,clear)) run_vdp_errors++;
  {u8 *owned=vdp[1].vram;vdp[1].vram=vdp[0].vram;
   if(__builtin_memcmp(vdp,vdp+1,sizeof(vdp[0])) || __builtin_memcmp(memory[0],memory[1],16384)) run_vdp_errors++;
   vdp[1].vram=owned;}
  run_vdp_cases++;
 }
}
'''
(out/'contracts.c').write_text(code);modules=['source_intro_vdp','source_intro_sprite_clock','source_intro_sprite_status'];snapshot=out/'sources';snapshot.mkdir()
for n in [*(name+ext for name in modules for ext in ('.c','.h')),'source_video_clock_math.h','source_pattern_video.h','source_clock.h']:shutil.copyfile(root/'megadrive/src'/n,snapshot/n)
sdk=root.parents[1]/'work/sgdk';env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
cmd=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-Wall','-Wextra','-Werror','-I',str(sdk/'inc'),'-I',str(snapshot),str(out/'contracts.c')]+[str(snapshot/(n+'.c')) for n in modules]+['-o',str(out/'contracts.dll')]
built=subprocess.run(cmd,env=env,capture_output=True,text=True);(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
dll=c.CDLL(str(out/'contracts.dll'));dll.map_run_contracts();host_cases=c.c_uint32.in_dll(dll,'run_vdp_cases').value;host_errors=c.c_uint32.in_dll(dll,'run_vdp_errors').value;assert host_cases==576 and not host_errors,(host_cases,host_errors)
project=out/'kernel';src=project/'src';src.mkdir(parents=True);(project/'inc').mkdir();shutil.copyfile(root/'megadrive/src/rom_header.c',src/'rom_header.c')
for n in modules:(src/(n+'.c')).write_text('#include "../../sources/'+n+'.c"\n')
(project/'inc/source_intro_vdp.h').write_text('#include "../../sources/source_intro_vdp.h"\n');(src/'contracts.c').write_text('#include "../../contracts.c"\n')
(src/'main.c').write_text('#include <genesis.h>\nvoid map_run_contracts(void);extern volatile u32 run_vdp_cases,run_vdp_errors;volatile u32 run_cases_done,run_errors;volatile u16 run_done;\nint main(bool hard_reset) {(void)hard_reset;VDP_setEnable(FALSE);map_run_contracts();run_cases_done=run_vdp_cases;run_errors=run_vdp_errors;run_done=1;while(TRUE) SYS_doVBlankProcess();return 0;}\n')
for key in ('TMP','TEMP','TMPDIR'):env[key]='.'
with (out/'build.log').open('w') as log:subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'tools/build_private_candidate.ps1'),'-Project',str(project),'-PaddingByte','255'],cwd=root,env=env,check=True,stdout=log,stderr=subprocess.STDOUT)
symbols={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in (project/'out/release/symbol.txt').read_text().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))};results=[]
for region in ('ntsc','pal'):
 stats={}
 def observe(frame,ram):
  for name,size in [('run_cases_done',4),('run_errors',4),('run_done',2)]:stats[name]=int.from_bytes(bytes(ram[(symbols[name]+i)^1] for i in range(size)),'big')
  stats['frame']=frame
 with contextlib.redirect_stdout(io.StringIO()):run(project/'out/release/rom.bin',120000,out/region,set(),[],skip_intro=False,ram_observer=observe,stop_when=lambda:bool(stats.get('run_done')),core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
 assert stats['run_done'] and stats['run_cases_done']==576 and not stats['run_errors'],stats
 results.append(dict(region=region,**stats));print(region,stats,flush=True)
(out/'report.json').write_text(json.dumps(dict(passed=True,host_cases=host_cases,results=results,native_sources={n:sha((snapshot/(n+'.c')).read_bytes()) for n in modules},scope='576clear/transfer runs versus individual BF/BF/BE native port handling onhost and each compiled region. Full16KiBVRAM and entire logicalVDP/cache/latch/calendar state compared,only owner pointer normalized. Both frame periods,6raster edges,3address ranges,4counts,clear/transfer,active sprites with cleared status before each run and pattern indices in the written ranges.'),indent=2)+'\n')
