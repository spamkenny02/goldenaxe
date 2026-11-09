"""Compare canonical transactional IRQ and disposable workspace entry points."""
import contextlib,ctypes as c,io,json,os,re,shutil,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from run_core import run
from archive_lossless_evidence import sha
out=root/'validation/v320-irq-workspace02';assert not out.exists();out.mkdir();snapshot=out/'sources';snapshot.mkdir()
for name in ('source_irq.c','source_irq_workspace.c','source_irq.h','source_clock.h'):shutil.copyfile(root/'megadrive/src'/name,snapshot/name)
old=subprocess.check_output(['git','show','95935a2db8331394f3b0889b4630258f412a5f31:megadrive/src/source_irq.c'],cwd=root);(out/'canonical-before.c').write_bytes(old)
sdk=root.parents[1]/'work/sgdk';env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
preprocessed=[]
for file in (out/'canonical-before.c',snapshot/'source_irq.c'):
 code=subprocess.check_output([str(sdk/'bin/gcc.exe'),'-B'+str(sdk/'bin')+'/', '-E','-P','-DSGDK_GCC','-I',str(snapshot),'-isystem',str(sdk/'inc'),str(file)],env=env)
 preprocessed.append(re.findall(rb'[A-Za-z_][A-Za-z_0-9]*|[0-9]+|[^\s]',code))
assert preprocessed[0]==preprocessed[1],'Canonical production IRQ token stream changed'
code=r'''#include "source_irq.h"
static u8 initial[336],a[336],b[336];
static SourceIrqOutput oa,ob;
volatile u32 workspace_cases,workspace_errors,workspace_accepted,workspace_rejected;
void workspace_contracts(void)
{
 workspace_cases=workspace_errors=workspace_accepted=workspace_rejected=0;
 for(u16 region=0;region<2;region++)
 {
  u16 lines=region?313:262;
  for(u16 line=0;line<lines;line++) for(u16 phase=0;phase<2;phase++) for(u16 kind=0;kind<4;kind++) for(u16 queue=0;queue<5;queue++)
  {
   SourceIrqInput input;SourceClockWork reader;u8 x,y;
   __builtin_memset(initial,0,sizeof(initial));initial[0x2e]=kind!=0;initial[0x33]=kind==1;
   initial[0x30]=3;initial[0x2f]=255;initial[0x1c]=2;initial[0x20]=7;initial[0x22]=1;
   initial[0x34]=0;initial[0x35]=0xdd;initial[0x45]=kind==2?3:0;
   if(kind==3) {initial[0x42]=1;initial[0x43]=0x20;initial[0x44]=0x80;}
   if(queue==1 || queue==2) {initial[80]=1;initial[81]=queue==2?0x80:0;initial[86]=queue==2?0:1;initial[0x34]=7;}
   if(queue==3) {initial[80]=2;initial[81]=1;initial[82]=3;initial[0x34]=5;}
   if(queue==4) {initial[0x34]=0x80;initial[0x35]=0xc0;}
   input.lines=lines;input.raster=(u32)line*3420+(phase?3419:0);input.joy=line&63;input.compensation=phase?0:128;input.tile_count=17;input.reset_mask=queue==3?0:16;
   reader.tstates=kind*17;reader.fetches=kind*3;
   if(queue==3 && kind==1) reader.tstates=0xfffffff0UL;
   if(queue==4 && kind==0) input.lines=263;
   if(queue==4 && kind==1) input.joy=64;
   if(queue==4 && kind==3) input.tile_count=0;
   __builtin_memcpy(a,initial,sizeof(a));__builtin_memcpy(b,initial,sizeof(b));__builtin_memset(&oa,0,sizeof(oa));__builtin_memset(&ob,0,sizeof(ob));
   x=source_irq(a,&input,&reader,&oa);y=source_irq_workspace(b,&input,&reader,&ob);
   if(x!=y || __builtin_memcmp(&oa,&ob,sizeof(oa)) || (x?__builtin_memcmp(a,b,sizeof(a)):__builtin_memcmp(a,initial,sizeof(a)))) workspace_errors++;
   if(x) workspace_accepted++;else workspace_rejected++;
   workspace_cases++;
  }
 }
}
'''
(out/'contracts.c').write_text(code)
modules=['source_irq.c','source_irq_workspace.c']
cmd=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-Wall','-Wextra','-Werror','-I',str(sdk/'inc'),'-I',str(snapshot),str(out/'contracts.c'),*[str(snapshot/n) for n in modules],'-o',str(out/'workspace.dll')]
built=subprocess.run(cmd,env=env,capture_output=True,text=True);(out/'compile.log').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr
dll=c.CDLL(str(out/'workspace.dll'));dll.workspace_contracts();host={k:c.c_uint32.in_dll(dll,k).value for k in ('workspace_cases','workspace_errors','workspace_accepted','workspace_rejected')};assert host['workspace_cases']==23000 and not host['workspace_errors'] and host['workspace_accepted'] and host['workspace_rejected'],host;print('host',host,flush=True)
project=out/'kernel';src=project/'src';src.mkdir(parents=True);inc=project/'inc';inc.mkdir();shutil.copyfile(root/'megadrive/src/rom_header.c',src/'rom_header.c')
for name in modules:(src/name).write_text('#include "../../sources/'+name+'"\n')
(src/'contracts.c').write_text('#include "../../contracts.c"\n');(inc/'source_irq.h').write_text('#include "../../sources/source_irq.h"\n')
(src/'main.c').write_text('#include <genesis.h>\nvoid workspace_contracts(void);volatile u16 workspace_done;\nint main(bool hard_reset){(void)hard_reset;VDP_setEnable(FALSE);workspace_contracts();workspace_done=1;while(TRUE) SYS_doVBlankProcess();return 0;}\n')
for key in ('TMP','TEMP','TMPDIR'):env[key]='.'
with (out/'build.log').open('w') as log:subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'tools/build_private_candidate.ps1'),'-Project',str(project),'-PaddingByte','255'],cwd=root,env=env,check=True,stdout=log,stderr=subprocess.STDOUT)
symbols={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in (project/'out/release/symbol.txt').read_text().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))};results=[]
for region in ('ntsc','pal'):
 stats={}
 def observe(frame,ram):
  for name,size in [('workspace_cases',4),('workspace_errors',4),('workspace_accepted',4),('workspace_rejected',4),('workspace_done',2)]:stats[name]=int.from_bytes(bytes(ram[(symbols[name]+i)^1] for i in range(size)),'big')
  stats['frame']=frame
 with contextlib.redirect_stdout(io.StringIO()):run(project/'out/release/rom.bin',100000,out/region,set(),[],skip_intro=False,ram_observer=observe,stop_when=lambda:bool(stats.get('workspace_done')),core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
 assert stats['workspace_done'] and all(stats[k]==v for k,v in host.items()),stats
 results.append(dict(region=region,**stats));print(region,stats,flush=True)
(out/'report.json').write_text(json.dumps(dict(passed=True,canonical_preprocessed_tokens_identical=True,host=host,results=results,native_sources={n:sha((snapshot/n).read_bytes()) for n in modules},scope='All575raster lines/two phases,four IRQ modes,five queue/invalid shapes. Return/allstage-and-work output exact;all336RAM bytes exact on success;canonical RAM rollback preserved on rejection. Disposable workspace after rejection is deliberately not published or compared.'),indent=2)+'\n')
