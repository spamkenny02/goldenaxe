"""Compose dated032A output with source-checked full E50 scene/IRQ vectors."""
import ctypes as c,gzip,json,os,shutil,struct,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
prior=root/'validation/v319-native-intro-poll-scene03';out=root/'validation/v319-scene-ports01';assert not out.exists();out.mkdir()
manifest=json.loads((root/'analysis/v319-pattern-dates/manifest.json').read_bytes());name='validation/v319-pattern-dates01/ntsc-dates.bin';item=manifest['compressed'][name];encoded=(root/'analysis/v319-pattern-dates'/item['stored']).read_bytes();assert sha(encoded)==item['stored_sha256'];raw=gzip.decompress(encoded);assert sha(raw)==item['raw_sha256']
records=[struct.unpack_from('<8I',raw,n) for n in range(0,len(raw),32)];header=[]
for plan in (1,2):
 events=[r for r in records if r[0]==1 and r[1]==plan];first=events[0][2]
 header.append(f'static const u32 pattern_{plan}[][2]={{'+','.join('{'+str(r[2]-first)+'UL,'+str((r[4]<<8)|r[5])+'UL}' for r in events)+'};')
(out/'pattern_expected.h').write_text('\n'.join(header)+'\n')
wrapper=(prior/'wrapper.c').read_text();anchor='static u8 scene_vram[16384];'
extra=r'''#include "pattern_expected.h"
static SourceClock *pattern_clock;
static const u32 (*pattern_expected)[2];
static u32 pattern_count,pattern_position,pattern_origin,video_last,video_total;
u32 scene_pattern_outputs(void) {return pattern_position;}
u32 scene_video_outputs(void) {return video_total;}
static u8 pattern_sink(void *user,u32 elapsed,u32 raster,u8 port,u8 value)
{
 u32 foreground=elapsed-pattern_clock->irq_tstates*15;(void)user;
 if(pattern_position>=pattern_count || elapsed<=video_last || raster!=(pattern_clock->raster+elapsed-pattern_clock->elapsed+pattern_clock->period)%pattern_clock->period) return 0;
 if(!pattern_position) pattern_origin=foreground;
 if(foreground-pattern_origin!=pattern_expected[pattern_position][0] || (((u32)port<<8)|value)!=pattern_expected[pattern_position][1]) return 0;
 pattern_position++;video_last=elapsed;video_total++;return 1;
}
'''
wrapper=wrapper.replace(anchor,anchor+'\n'+extra)
wrapper=wrapper.replace('(void)user;\n if(reveal_event_position', '(void)user;\n if(elapsed<=video_last) return 0;video_last=elapsed;video_total++;\n if(reveal_event_position')
needle='if(!source_intro_scene_load(&clock,&context,ram[1184]|((u16)ram[1185]<<8),ram[1186]|((u16)ram[1187]<<8),scene_vram,sequence_callback,&sequence_data,reveal_sink,0,&sequence)) return 0;'
replacement='''pattern_clock=&clock;pattern_position=pattern_origin=video_last=video_total=0;
 if((ram[1184]|((u16)ram[1185]<<8))==0x9d70) {pattern_expected=pattern_1;pattern_count=sizeof(pattern_1)/sizeof(pattern_1[0]);}
 else {pattern_expected=pattern_2;pattern_count=sizeof(pattern_2)/sizeof(pattern_2[0]);}
 if(!source_intro_scene_load_ports(&clock,&context,ram[1184]|((u16)ram[1185]<<8),ram[1186]|((u16)ram[1187]<<8),scene_vram,sequence_callback,&sequence_data,reveal_sink,0,pattern_sink,0,&sequence)) return 0;
 if(pattern_position!=pattern_count) return 0;'''
assert needle in wrapper;wrapper=wrapper.replace(needle,replacement);(out/'wrapper.c').write_text(wrapper)
report=json.loads((prior/'report.json').read_bytes());modules=list(report['native_sources'])
# Context needs a separate symbol: source-checked status queue lives in wrapper.
(out/'irq.c').write_text('#define source_irq_interrupt source_irq_interrupt_impl\n#include "../../megadrive/src/source_irq_context.c"\n')
sdk=root.parents[1]/'work/sgdk';env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
cmd=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I',str(sdk/'inc'),'-I',str(root/'megadrive/src'),str(out/'wrapper.c'),str(out/'irq.c')]
cmd += [str(root/'megadrive/src'/(n+'.c')) for n in modules if n!='source_irq_context']+['-o',str(out/'scene.dll')]
built=subprocess.run(cmd,env=env,capture_output=True,text=True);(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
dll=c.CDLL(str(out/'scene.dll'));fn=dll.poll_case;fn.restype=c.c_uint8;fn.argtypes=[c.POINTER(c.c_uint32),c.c_uint8,*([c.POINTER(c.c_uint8)]*4),c.POINTER(c.c_uint32)]
dll.configure_reveal_events.argtypes=[c.POINTER(c.c_uint32),c.c_uint16];dll.scene_pattern_outputs.restype=dll.scene_video_outputs.restype=c.c_uint32
rom=(root/'input/original.sms').read_bytes();low=(c.c_uint8*32768).from_buffer_copy(rom[:32768]);bank=(c.c_uint8*16384).from_buffer_copy(rom[0x18000:0x1c000]);checks=[]
for region in ('ntsc','pal'):
 (out/region).mkdir();cases=json.loads((prior/region/'native-cases.json').read_bytes());(out/region/'native-cases.json').write_bytes((prior/region/'native-cases.json').read_bytes())
 for index,row in enumerate(cases):
  ram=(c.c_uint8*len(row['input_ram']))(*row['input_ram']);audio=(c.c_uint8*400)(*row['input_audio']);phase=(c.c_uint32*len(row['phase']))(*row['phase']);events=(c.c_uint32*len(row['events']))(*row['events']);actual=(c.c_uint32*18)()
  dll.configure_reveal_events(events,len(row['events'])//2)
  assert fn(phase,row['refresh'],ram,audio,low,bank,actual),(region,index,'rejected')
  assert list(ram)==row['expected_ram'] and list(audio)==row['expected_audio'] and list(actual)==row['expected'],(region,index,'state')
  checks.append(dict(region=region,index=index,pattern_outputs=dll.scene_pattern_outputs(),all_foreground_outputs=dll.scene_video_outputs(),real_native_irqs=actual[6],state_and_io_exact=True))
report.update(passed=True,native_sources={name:sha((root/'megadrive/src'/(name+'.c')).read_bytes()) for name in modules},host_scene_ports=checks,
 scope='Composed original ten E50 scene loads with actual native audio/IRQ work and source-captured per-IRQ status inputs. Existing8452map/clear OUT dates remain source-exact; additional032A foreground dates/values independently match original execution. Full tracked RAM/audio/VRAM/clock/R states unchanged.',
 limits=['Status bytes remain original captured diagnostic inputs,not a live VDP provider; IRQ video delivery and complete coldboot are not yet composed.','Pattern dates compare foreground time excluding actual native IRQ work; existing original map/clear dates remain full elapsed checks. No physical video/PSG or throughput gate.'])
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Composed scene ports:',len(checks),'cases;',sum(r['all_foreground_outputs'] for r in checks),'outputs;',sum(r['real_native_irqs'] for r in checks),'actual native IRQs exact')
