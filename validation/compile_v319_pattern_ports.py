"""Every original intro pattern OUT compared on compiled68000 at six IRQ edges."""
import contextlib,io,json,os,re,shutil,struct,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
from run_core import run
work=root/'validation/v319-pattern-ports02';report=json.loads((work/'report.json').read_bytes());assert report['passed']
assert sha((root/'megadrive/src/source_pattern_clock.c').read_bytes())==report['native_sha256']
cases=json.loads((work/'compiled-cases.json').read_bytes());parts=[]
for plan in (1,2):
 for lines in (262,313):
  name=f'kernel-{plan}-{lines}';project=work/name;target=work/(name+'-report.json')
  if target.exists():
   done=json.loads(target.read_bytes());assert done['passed'];parts.append(done);continue
  assert not project.exists();src=project/'src';src.mkdir(parents=True);(project/'inc').mkdir()
  shutil.copyfile(root/'megadrive/src/rom_header.c',src/'rom_header.c')
  for module in ('source_pattern_clock','source_clock','source_rng'):(src/(module+'.c')).write_text('#include "../../../../megadrive/src/'+module+'.c"\n')
  for header in ('source_pattern_clock','source_intro_pattern_plans_generated'):(project/'inc'/(header+'.h')).write_text('#include "../../../../megadrive/src/'+header+'.h"\n')
  selected=[c for c in cases if c['plan_id']==plan and c['lines']==lines];assert len(selected)==6
  events=bytearray();definitions=['static const u8 packed[]={'+','.join(map(str,selected[0]['stream']))+'};',
   'typedef struct {u32 raster,offset,count,state[16],hash;} PatternCase;','static const PatternCase cases[]={']
  for row in selected:
   # Independent decoded destination digest, initialized like the host.
   pixels=bytearray([0xa7])*16384;s=0
   for plane in range(4):
    dst=plane
    while row['stream'][s]:
     cmd=row['stream'][s];s+=1
     for n in range(cmd&127 or 256):pixels[dst]=row['stream'][s];dst+=4;s+=bool(cmd&128)
     if not cmd&128:s+=1
    s+=1
   h=2166136261
   for value in pixels:h=((h^value)*16777619)&0xffffffff
   offset=len(events)//10
   for e in row['events']:events.extend(struct.pack('>IIBB',*e))
   definitions.append('{'+f'{row["raster"]}UL,{offset}UL,{len(row["events"])}UL,'+'{'+','.join(str(v)+'UL' for v in row['result'])+'},'+str(h)+'UL},')
  definitions.append('};');(src/'expected.h').write_text('\n'.join(definitions)+'\n');(src/'events.bin').write_bytes(events)
  (src/'events.s').write_text('.section .rodata\n.balign 2\n.global pattern_events\npattern_events:\n.incbin "src/events.bin"\n')
  main=r'''#include <genesis.h>
#include "source_pattern_clock.h"
#include "source_intro_pattern_plans_generated.h"
#include "expected.h"
typedef struct {u32 elapsed,raster;u8 port,value;} PatternEvent;
typedef char EventSizeCheck[sizeof(PatternEvent)==10?1:-1];
extern const PatternEvent pattern_events[];
static u8 pixels[16384];static const PatternCase *current;static u32 position;
volatile u32 pattern_outputs,pattern_errors;volatile u16 pattern_cases,pattern_done;
u8 source_irq_interrupt(void *context,const SourceClockIrq *entry,SourceClockWork *work)
{(void)context;(void)entry;work->tstates=82;work->fetches=8;return 1;}
static u8 sink(void *user,u32 elapsed,u32 raster,u8 port,u8 value)
{
 const PatternEvent *e;(void)user;
 if(position>=current->count) return 0;
 e=pattern_events+current->offset+position++;pattern_outputs++;
 if(e->elapsed!=elapsed || e->raster!=raster || e->port!=port || e->value!=value) pattern_errors++;
 return 1;
}
int main(bool hard_reset)
{
 (void)hard_reset;VDP_setEnable(FALSE);
 for(u16 n=0;n<6;n++)
 {
  SourceClock clock;SourceIrqContext context={0};u8 ram[336]={0};const u8 *stream=packed;u16 end;
  u32 state[16],h=2166136261UL;
  current=cases+n;position=0;context.ram=ram;memset(pixels,0xa7,sizeof(pixels));
  source_clock_init(&clock,SOURCE_LINES,current->raster,0,1,0,0);
  if(!source_pattern_decode_ports(&clock,&context,&stream,pixels,0x4000,&end,PATTERN_PLAN,sink,0)) pattern_errors++;
  state[0]=stream-packed;state[1]=end;state[2]=ram[0x31]|((u16)ram[0x32]<<8);
  state[3]=clock.elapsed;state[4]=clock.raster;state[5]=clock.foreground_tstates;state[6]=clock.foreground_m1;
  state[7]=clock.irq_tstates;state[8]=clock.irq_m1;state[9]=clock.irq_count;state[10]=clock.refresh;
  state[11]=clock.iff;state[12]=clock.blocked;state[13]=clock.pending;state[14]=clock.first;state[15]=clock.until_vint;
  if(memcmp(state,current->state,sizeof(state)) || position!=current->count) pattern_errors++;
  for(u16 k=0;k<sizeof(pixels);k++) h=(h^pixels[k])*16777619UL;
  if(h!=current->hash) pattern_errors++;
  pattern_cases++;
 }
 pattern_done=1;while(TRUE) SYS_doVBlankProcess();return 0;
}
'''
  tag='gaw_intro_9d70_plan' if plan==1 else 'gaw_intro_a655_plan'
  (src/'main.c').write_text(f'#define SOURCE_LINES {lines}\n#define PATTERN_PLAN (&{tag})\n'+main)
  env=dict(os.environ)
  for key in ('TMP','TEMP','TMPDIR'):env[key]='.'
  with (project/'build-command.log').open('w') as log:subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'tools/build_private_candidate.ps1'),'-Project',str(project),'-PaddingByte','255'],cwd=root,env=env,check=True,stdout=log,stderr=subprocess.STDOUT)
  symbols={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in (project/'out/release/symbol.txt').read_text().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))};results=[]
  for region in ('ntsc','pal'):
   stats={}
   def observe(frame,ram):
    for field,size in [('pattern_outputs',4),('pattern_errors',4),('pattern_cases',2),('pattern_done',2)]:stats[field]=int.from_bytes(bytes(ram[(symbols[field]+i)^1] for i in range(size)),'big')
    stats['frame']=frame
   with contextlib.redirect_stdout(io.StringIO()):run(project/'out/release/rom.bin',20000,work/(name+'-'+region),set(),[],skip_intro=False,ram_observer=observe,stop_when=lambda:bool(stats.get('pattern_done')),core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
   assert stats['pattern_done'] and stats['pattern_cases']==6 and stats['pattern_errors']==0 and stats['pattern_outputs']==len(events)//10,stats
   results.append(dict(region=region,**stats));print(name,region,stats,flush=True)
  done=dict(passed=True,plan=plan,source_lines=lines,cases=6,results=results,rom_sha256=sha((project/'out/release/rom.bin').read_bytes()));target.write_text(json.dumps(done,indent=2)+'\n');parts.append(done)
summary=dict(passed=True,compiled_cases=sum(p['cases']*len(p['results']) for p in parts),compiled_outputs=sum(row['pattern_outputs'] for p in parts for row in p['results']),partitions=parts,limits=['Exact host scalar-checked OUT dates on actual68000; synthetic82T IRQ workload. No original absolute032A timestamp certificate or physical output.'])
(work/'compiled-report.json').write_text(json.dumps(summary,indent=2)+'\n')
