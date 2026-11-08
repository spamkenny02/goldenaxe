"""Feed dated native032A OUTs into the independently owned logical VDP."""
import ctypes as c,json,os,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
prior=root/'validation/v319-pattern-ports02';out=root/'validation/v319-pattern-vdp-binding01';assert not out.exists();out.mkdir()
body=(prior/'wrapper.c').read_text()
body=body.replace('#include "source_pattern_clock.h"','#include "source_pattern_clock.h"\n#include "source_intro_vdp.h"\nstatic SourceIntroVdp video;static u8 video_memory[16384],bind_video;')
body=body.replace('row=events[event_count++];', '''if(bind_video)
 {
  if(!source_intro_vdp_checkpoint(&video,elapsed-165) ||
     (video.instruction_raster+165)%video.clock.period!=raster ||
     !source_intro_vdp_write(&video,elapsed,port,value)) return 0;
 }
 row=events[event_count++];''')
body=body.replace('context.ram=ram;event_count=0;active=&clock;', '''context.ram=ram;event_count=0;active=&clock;bind_video=mode==3;
 if(bind_video) {if(!source_intro_vdp_init(&video,video_memory,lines,raster,0)) return 0;__builtin_memset(video_memory,0xa7,16384);}''')
body=body.replace('else if(mode==1)','else if(mode==1 || mode==3)')
body=body.replace('result[0]=source-stream;', 'if(bind_video && __builtin_memcmp(video_memory,pixels,16384)) return 0;\n result[0]=source-stream;')
(out/'wrapper.c').write_text(body)
sdk=root.parents[1]/'work/sgdk';env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
modules=['source_pattern_clock','source_clock','source_rng','source_intro_vdp','source_intro_sprite_clock','source_intro_sprite_status']
cmd=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-but-set-variable','-I',str(sdk/'inc'),'-I',str(root/'megadrive/src'),str(out/'wrapper.c'),str(prior/'scalar.c')]
cmd += [str(root/'megadrive/src'/(name+'.c')) for name in modules]+['-o',str(out/'binding.dll')]
built=subprocess.run(cmd,capture_output=True,text=True,env=env);(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
dll=c.CDLL(str(out/'binding.dll'));dll.port_event_count.restype=c.c_uint32;dll.port_event_data.restype=c.POINTER(c.c_uint32)
fn=dll.pattern_case;fn.restype=c.c_uint8;fn.argtypes=[c.POINTER(c.c_uint8),c.c_uint16,c.c_uint16,c.c_uint32,c.c_uint8,c.c_uint8,c.POINTER(c.c_uint8),c.POINTER(c.c_uint32)]
rows=json.loads((prior/'compiled-cases.json').read_bytes());checks=[]
for row in rows:
 stream=(c.c_uint8*len(row['stream']))(*row['stream']);pixels=(c.c_uint8*16384)();result=(c.c_uint32*16)()
 assert fn(stream,row['address'],row['lines'],row['raster'],3,row['plan_id'],pixels,result),row['index']
 assert list(result)==row['result'] and sha(bytes(pixels))==row['pixels_sha256']
 raw=c.string_at(dll.port_event_data(),dll.port_event_count()*24);assert sha(raw)==row['events_sha256']
 checks.append(dict(index=row['index'],lines=row['lines'],raster=row['raster'],outputs=dll.port_event_count(),state_exact=True,full_vram_exact=True))
report=dict(passed=True,cases=len(checks),outputs=sum(row['outputs'] for row in checks),checks=checks,
 native_sources={name:sha((root/'megadrive/src'/(name+'.c')).read_bytes()) for name in modules},
 scope='Native032A dated output sink checkpoints the owned SourceIntroVdp before each11T OUT then writes at completion. Full16KiB video memory agrees with decoder mirror, all source-clock state and OUT events agree with prior instruction-only comparison.',
 limits=['Host integration with synthetic82T IRQ callback and initialized synthetic video history, not the complete boot/scene/IRQ renderer.','This composition has not yet been compiled/profiled with physical MD video/audio output.'])
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Native pattern -> owned VDP:',len(checks),'cases,',report['outputs'],'outputs exact')
