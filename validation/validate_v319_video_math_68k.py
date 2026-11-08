"""Exhaust native DIVU line/phase results over every PAL and NTSC raster tick."""
import contextlib,io,json,os,re,shutil,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from run_core import run
from archive_lossless_evidence import sha
out=root/'validation/v319-video-math01';assert not out.exists();out.mkdir();project=out/'kernel';src=project/'src';src.mkdir(parents=True);(project/'inc').mkdir()
shutil.copyfile(root/'megadrive/src/rom_header.c',src/'rom_header.c');(project/'inc/source_video_clock_math.h').write_text('#include "../../../../megadrive/src/source_video_clock_math.h"\n')
(src/'main.c').write_text(r'''#include <genesis.h>
#include "source_video_clock_math.h"
volatile u32 video_math_cases,video_math_errors,video_math_wraps;
volatile u16 video_math_done;
int main(bool hard_reset)
{
 (void)hard_reset;VDP_setEnable(FALSE);
 for(u16 region=0;region<2;region++)
 {
  u16 lines=region?313:262;u32 period=(u32)lines*3420,raster=0;
  for(u16 line=0;line<lines;line++) for(u16 phase=0;phase<3420;phase++,raster++)
  {
   if(source_video_line(raster)!=line || source_video_phase(raster)!=phase) video_math_errors++;
   video_math_cases++;
  }
  for(u16 n=0;n<lines;n++)
  {
   u32 base=(u32)n*3420;
   u32 deltas[]={0,1,15,165,3420,period-1,period,period+1,period*2-1,period*2,0x7fffffffUL};
   for(u16 j=0;j<sizeof(deltas)/sizeof(deltas[0]);j++)
   {
    u32 delta=deltas[j],expected=((base+delta)%period);
    if(source_video_wrap(base,delta,period)!=expected) video_math_errors++;
    video_math_wraps++;
   }
  }
 }
 video_math_done=1;while(TRUE) SYS_doVBlankProcess();return 0;
}
''')
env=dict(os.environ)
for key in ('TMP','TEMP','TMPDIR'):env[key]='.'
with (out/'build.log').open('w') as log:subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'tools/build_private_candidate.ps1'),'-Project',str(project),'-PaddingByte','255'],cwd=root,env=env,check=True,stdout=log,stderr=subprocess.STDOUT)
symbols={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in (project/'out/release/symbol.txt').read_text().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))};results=[]
for region in ('ntsc','pal'):
 stats={}
 def observe(frame,ram):
  for name,size in [('video_math_cases',4),('video_math_errors',4),('video_math_wraps',4),('video_math_done',2)]:stats[name]=int.from_bytes(bytes(ram[(symbols[name]+i)^1] for i in range(size)),'big')
  stats['frame']=frame
 with contextlib.redirect_stdout(io.StringIO()):run(project/'out/release/rom.bin',20000,out/region,set(),[],skip_intro=False,ram_observer=observe,stop_when=lambda:bool(stats.get('video_math_done')),core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
 assert stats['video_math_done'] and not stats['video_math_errors'] and stats['video_math_cases']==1966500 and stats['video_math_wraps']==6325,stats
 results.append(dict(region=region,**stats));print(region,stats,flush=True)
(out/'report.json').write_text(json.dumps(dict(passed=True,results=results,header_sha256=sha((root/'megadrive/src/source_video_clock_math.h').read_bytes()),rom_sha256=sha((project/'out/release/rom.bin').read_bytes()),scope='Every valid NTSC/PAL master-raster tick uses native DIVU line/phase and compares independently incremented line/phase counters. Wrap checks include exact period edges and long stable gaps.'),indent=2)+'\n')
