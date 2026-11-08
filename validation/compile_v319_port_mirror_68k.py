"""Replay complete cold raw-port prefixes on68000, using native-owned VRAM."""
import argparse,contextlib,io,json,os,re,shutil,struct,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
from run_core import run
p=argparse.ArgumentParser();p.add_argument('--source-region',choices=['ntsc','pal'],required=True);p.add_argument('--kernel-name');a=p.parse_args()
work=root/'validation/v319-port-mirror02';report=json.loads((work/'report.json').read_bytes());assert report['passed']
for name,digest in report['native_sources'].items():assert sha((root/'megadrive/src'/name).read_bytes())==digest
row=next(r for r in report['results'] if r['region']==a.source_region)
origin=json.loads((root/'validation/v319-port-origin01/report.json').read_bytes());assert origin['passed']
phase=next(r for r in origin['results'] if r['region']==a.source_region)
assert phase['event_sha256']==row['event_sha256'] and phase['capture_final_hash']==row['capture_final_hash']
assert phase['initial_raster']==(159 if a.source_region=='ntsc' else 132)*3420+990
raw=(work/(a.source_region+'-ports.bin')).read_bytes();assert sha(raw)==row['event_sha256'] and len(raw)==row['captured_port_events']*8
packed=bytearray(raw);last=0;reads=0
for offset in range(0,len(raw),8):
 elapsed,kind,port,value,tstates=struct.unpack_from('<IBBBB',raw,offset)
 assert last<=elapsed and tstates and tstates<256 and kind in (0,1,2);last=elapsed
 reads+=kind!=0;struct.pack_into('>I',packed,offset,elapsed)
kernel=a.kernel_name or 'kernel-'+a.source_region;assert re.fullmatch(r'kernel-(ntsc|pal)[0-9]*',kernel)
project=work/kernel;assert not project.exists();src=project/'src';src.mkdir(parents=True);(project/'inc').mkdir()
shutil.copyfile(root/'megadrive/src/rom_header.c',src/'rom_header.c')
for name in ('source_intro_sprite_status','source_intro_sprite_clock','source_intro_vdp'):
 (src/(name+'.c')).write_text('#include "../../../../megadrive/src/'+name+'.c"\n')
 (project/'inc'/(name+'.h')).write_text('#include "../../../../megadrive/src/'+name+'.h"\n')
(src/'ports-be.bin').write_bytes(packed);(src/'ports.s').write_text('.section .rodata\n.balign 2\n.global port_events\nport_events:\n.incbin "src/ports-be.bin"\n')
main=r'''#include <genesis.h>
#include "source_intro_vdp.h"
typedef struct {u32 elapsed;u8 kind,port,value,tstates;} PortEvent;
typedef char EventSizeCheck[sizeof(PortEvent)==8?1:-1];
extern const PortEvent port_events[];
static SourceIntroVdp model;static u8 memory[16384];
volatile u32 port_events_done,port_errors,port_first_failure,port_reads,port_irq_reads,port_final_hash;
volatile u32 port_expected,port_actual,port_elapsed,port_raster;
volatile u16 port_done;
static u32 state_hash(void)
{
 u32 h=2166136261UL;
 for(u16 n=0;n<16384;n++) h=(h^memory[n])*16777619UL;
 for(u16 n=0;n<16;n++) h=(h^model.registers[n])*16777619UL;
 for(u16 n=0;n<32;n++) h=(h^model.palette[n])*16777619UL;
 h=(h^(u8)model.address)*16777619UL;h=(h^(model.address>>8))*16777619UL;
 h=(h^model.code)*16777619UL;h=(h^model.pending)*16777619UL;h=(h^model.low)*16777619UL;h=(h^model.buffer)*16777619UL;
 return h;
}
int main(bool hard_reset)
{
 (void)hard_reset;VDP_setEnable(FALSE);
 if(!source_intro_vdp_init(&model,memory,SOURCE_LINES,SOURCE_RASTER,0)) port_errors|=1;
 for(u32 n=0;n<EVENT_COUNT && !port_errors;n++)
 {
  const PortEvent *entry=port_events+n;u8 value=0,accepted;
  accepted=source_intro_vdp_checkpoint(&model,entry->elapsed-(u32)entry->tstates*15);
  if(accepted)
  {
   if(entry->kind==0) accepted=source_intro_vdp_write(&model,entry->elapsed,entry->port,entry->value);
   else
   {
    if(entry->kind==1 && (port_reads&1))
    {
     SourceClockIrq irq;irq.entry_elapsed=entry->elapsed+37UL*15;
     irq.entry_raster=(model.instruction_raster+entry->elapsed-model.instruction_elapsed+37UL*15)%model.clock.period;
     irq.entry_refresh=0;accepted=source_intro_vdp_irq_status(&model,&irq,&value);port_irq_reads++;
    }
    else accepted=source_intro_vdp_read(&model,entry->elapsed,entry->tstates,entry->port,&value);
    if(value!=entry->value) {port_errors|=2;port_expected=entry->value;port_actual=value;port_elapsed=entry->elapsed;port_raster=model.clock.raster;}
    port_reads++;
   }
  }
  if(!accepted) port_errors|=1;
  if(port_errors && !port_first_failure) port_first_failure=n+1;
  port_events_done++;
 }
 port_final_hash=state_hash();if(port_final_hash!=EXPECTED_HASH) port_errors|=4;
 port_done=1;while(TRUE) SYS_doVBlankProcess();return 0;
}
'''
(src/'main.c').write_text(f'#define SOURCE_LINES {262 if a.source_region=="ntsc" else 313}\n#define SOURCE_RASTER {phase["initial_raster"]}UL\n#define EVENT_COUNT {len(raw)//8}UL\n#define EXPECTED_HASH {row["capture_final_hash"]}UL\n'+main)
env=dict(os.environ)
for key in ('TMP','TEMP','TMPDIR'):env[key]='.'
with (project/'build-command.log').open('w') as log:subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'tools/build_private_candidate.ps1'),'-Project',str(project),'-PaddingByte','255'],cwd=root,env=env,check=True,stdout=log,stderr=subprocess.STDOUT)
symbols={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in (project/'out/release/symbol.txt').read_text().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))};results=[]
for region in ('ntsc','pal'):
 stats={}
 def observe(frame,ram):
  for name in ('port_events_done','port_errors','port_first_failure','port_reads','port_irq_reads','port_final_hash','port_done','port_expected','port_actual','port_elapsed','port_raster'):
   stats[name]=int.from_bytes(bytes(ram[(symbols[name]+i)^1] for i in range(2 if name=='port_done' else 4)),'big')
  stats['frame']=frame
 with contextlib.redirect_stdout(io.StringIO()):run(project/'out/release/rom.bin',50000,work/(kernel+'-'+region),set(),[],skip_intro=False,ram_observer=observe,stop_when=lambda:bool(stats.get('port_done')),core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
 (work/(kernel+'-'+region+'-observation.json')).write_text(json.dumps(stats,indent=2)+'\n')
 assert stats['port_done']==1 and stats['port_errors']==0 and stats['port_events_done']==len(raw)//8 and stats['port_reads']==reads and stats['port_final_hash']==row['capture_final_hash'],stats
 results.append(dict(region=region,**stats));print(a.source_region,region,json.dumps(stats),flush=True)
r=dict(passed=True,source_region=a.source_region,source_events=len(raw)//8,source_reads=reads,results=results,rom_sha256=sha((project/'out/release/rom.bin').read_bytes()),scope='Complete cold first200 source-period raw IO prefix; own16KiB VRAM,registers,palette,buffered reads and command state. All original source-checked read bytes plus final full-state digest agree on68000. Alternating status reads also execute the native IRQ adapter. Diagnostic kernel frames are not game cadence.')
(work/('compiled-'+a.source_region+'-report.json')).write_text(json.dumps(r,indent=2)+'\n')
