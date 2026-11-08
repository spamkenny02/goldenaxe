"""Composed native scene foreground and real IRQ ports into an owned VDP."""
import argparse,ctypes as c,json,os,shutil,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
parser=argparse.ArgumentParser();parser.add_argument('--drive-status',action='store_true');parser.add_argument('--out-name',default='v319-scene-live-vdp01');args=parser.parse_args()
prior=root/'validation/v319-scene-ports01';out=(root/'validation'/args.out_name).resolve();assert out.is_relative_to(root/'validation') and not out.exists();out.mkdir()
shutil.copyfile(prior/'pattern_expected.h',out/'pattern_expected.h')
body=(prior/'wrapper.c').read_text();anchor='static u8 scene_vram[16384];'
body=body.replace(anchor,anchor+'''\n#include "source_intro_scene_vdp.h"
static SourceIntroVdp live_video;static u8 live_memory[16384];
static u32 live_status_differences,live_status_reads,live_irq_packets;
u32 scene_live_status_differences(void) {return live_status_differences;}
u32 scene_live_status_reads(void) {return live_status_reads;}
u32 scene_live_irq_packets(void) {return live_irq_packets;}
static u8 live_irq(void *user,const SourceIrqContext *context,const SourceClockIrq *entry,u16 *count)
{live_irq_packets++;return source_intro_scene_vdp_irq(user,context,entry,count);}
''')
body=body.replace('irq->ram[0x1b]=irq_status_values[irq_status_position++];','''{u8 status;if(!source_intro_vdp_irq_status(&live_video,entry,&status)) return 0;
 live_status_reads++;if(status!=irq_status_values[irq_status_position]) live_status_differences++;}
 irq->ram[0x1b]=irq_status_values[irq_status_position++];''')
body=body.replace('pattern_position++;video_last=elapsed;video_total++;return 1;', '''if(!source_intro_scene_vdp_pattern(&live_video,elapsed,raster,port,value)) return 0;
 pattern_position++;video_last=elapsed;video_total++;return 1;''')
body=body.replace('reveal_event_position++;return 1;', '''if(!source_intro_scene_vdp_map(&live_video,elapsed,raster,port,value)) return 0;
 reveal_event_position++;return 1;''')
anchor='context.full_ram=actor_full_ram;context.ram=ram;'
assert anchor in body
body=body.replace(anchor,'''if(!source_intro_vdp_init(&live_video,live_memory,phase[3],clock.raster,0)) return 0;
 __builtin_memcpy(live_memory,scene_vram,16384);
 for(u16 n=0;n<11;n++) live_video.registers[n]=ram[0x10+n];
 for(u16 n=0;n<32;n++) live_video.palette[n]=ram[336+n];
 for(u16 n=0;n<64;n++) live_memory[0x3f00+n]=ram[144+n];
 for(u16 n=0;n<128;n++) live_memory[0x3f80+n]=ram[208+n];
 live_status_differences=live_status_reads=live_irq_packets=0;
 context.video=live_irq;context.video_context=&live_video;
 '''+anchor)
body=body.replace('if(irq_status_position!=irq_status_count) return 0;', '''if(irq_status_position!=irq_status_count) return 0;
 if(__builtin_memcmp(live_memory,scene_vram,9216) || __builtin_memcmp(live_memory+0x3800,scene_vram+0x3800,768)) return 0;''')
if args.drive_status:
 begin=body.index('u8 source_irq_interrupt(void *opaque,');end=body.index('\nstatic u32 reveal_origin',begin)
 body=body[:begin]+'''u8 source_irq_interrupt(void *opaque,const SourceClockIrq *entry,SourceClockWork *work)
{
 SourceIrqContext *irq=opaque;u8 accepted;
 if(irq_status_position>=irq_status_count) return 0;
 accepted=source_irq_interrupt_impl(opaque,entry,work);
 /* Original values are compared AFTER canonical work, never assigned. */
 live_status_reads++;
 if(irq->ram[0x1b]!=irq_status_values[irq_status_position++]) live_status_differences++;
 return accepted;
}
'''+body[end:]
 body=body.replace('context.video=live_irq;context.video_context=&live_video;', 'context.video=live_irq;context.video_context=&live_video;context.status_read=source_intro_vdp_irq_status;context.status_context=&live_video;')
(out/'wrapper.c').write_text(body)
report=json.loads((prior/'report.json').read_bytes());modules=list(report['native_sources'])+['source_intro_vdp','source_intro_scene_vdp','source_intro_sprite_clock','source_intro_sprite_status']
(out/'irq.c').write_text('#define source_irq_interrupt source_irq_interrupt_impl\n#include "../../megadrive/src/source_irq_context.c"\n')
sdk=root.parents[1]/'work/sgdk';env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
cmd=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I',str(sdk/'inc'),'-I',str(root/'megadrive/src'),str(out/'wrapper.c'),str(out/'irq.c')]
cmd += [str(root/'megadrive/src'/(n+'.c')) for n in modules if n!='source_irq_context']+['-o',str(out/'scene.dll')]
built=subprocess.run(cmd,env=env,capture_output=True,text=True);(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
dll=c.CDLL(str(out/'scene.dll'));fn=dll.poll_case;fn.restype=c.c_uint8;fn.argtypes=[c.POINTER(c.c_uint32),c.c_uint8,*([c.POINTER(c.c_uint8)]*4),c.POINTER(c.c_uint32)]
dll.configure_reveal_events.argtypes=[c.POINTER(c.c_uint32),c.c_uint16]
for name in ('scene_live_status_differences','scene_live_status_reads','scene_live_irq_packets'):getattr(dll,name).restype=c.c_uint32
rom=(root/'input/original.sms').read_bytes();low=(c.c_uint8*32768).from_buffer_copy(rom[:32768]);bank=(c.c_uint8*16384).from_buffer_copy(rom[0x18000:0x1c000]);checks=[]
for region in ('ntsc','pal'):
 (out/region).mkdir();cases=json.loads((prior/region/'native-cases.json').read_bytes());(out/region/'native-cases.json').write_bytes((prior/region/'native-cases.json').read_bytes())
 for index,row in enumerate(cases):
  ram=(c.c_uint8*len(row['input_ram']))(*row['input_ram']);audio=(c.c_uint8*400)(*row['input_audio']);phase=(c.c_uint32*len(row['phase']))(*row['phase']);events=(c.c_uint32*len(row['events']))(*row['events']);actual=(c.c_uint32*18)()
  dll.configure_reveal_events(events,len(row['events'])//2)
  accepted=fn(phase,row['refresh'],ram,audio,low,bank,actual)
  check=dict(region=region,index=index,accepted=bool(accepted),live_status_reads=dll.scene_live_status_reads(),live_status_differences=dll.scene_live_status_differences(),live_irq_packets=dll.scene_live_irq_packets());checks.append(check);print(json.dumps(check),flush=True)
  if accepted:assert list(ram)==row['expected_ram'] and list(audio)==row['expected_audio'] and list(actual)==row['expected'],(region,index,'state')
report.update(passed=all(row['accepted'] and not row['live_status_differences'] for row in checks),native_sources={name:sha((root/'megadrive/src'/(name+'.c')).read_bytes()) for name in modules},live_checks=checks,live_status_drives_canonical_irq=args.drive_status,
 scope='Foreground scene patterns/clear/map and real native IRQ register/SAT/palette OUTs drive separate ownedVDP; tracked final VRAM and all canonical scene RAM/audio/clock states compared. Live status independently sampled and compared, while captured expected status still drives canonical IRQ state.',
 limits=['Initial scene snapshot does not reconstruct complete pre-scene video cache/latch history. Live status mismatches are reported,never patched into model or hidden.','Source IRQ observer does not yet independently capture new IRQ port dates. No physical MD/audio/throughput proof.'])
report.update(extra_modules=['source_intro_vdp','source_intro_scene_vdp','source_intro_sprite_clock','source_intro_sprite_status'],extra_headers=['source_intro_scene_vdp.h'],max_kernel_frames=50000)
if args.drive_status:report['scope']='Owned nativeVDP status drives the canonical real native IRQ work. Original status bytes compared only after work. Native scene foreground and IRQ register/SAT/palette ports feed separate owned memory; full tracked final VRAM/RAM/audio/clock/R state remains original-exact.'
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');assert report['passed'],checks
