"""Expand emitted run descriptors and compare every previously audited OUT."""
import ctypes as c,gzip,json,os,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
prior=root/'validation/v319-pattern-ports02';out=root/'validation/v319-pattern-run-dates01';assert not out.exists();out.mkdir()
body=(prior/'wrapper.c').read_text();needle='u8 pattern_case('
expand=r'''static u32 run_count;
u32 pattern_run_count(void) {return run_count;}
static u8 expand(void *user,const SourcePatternVideoRun *run)
{
 u32 elapsed=run->elapsed,raster=run->raster;u16 address=run->address;run_count++;
 for(u16 n=0;n<run->count;n++)
 {
  const u16 offsets[]={30,45,77};u8 values[]={(u8)address,(u8)(address>>8),run->bytes[run->literal?n:0]};
  for(u16 k=0;k<3;k++) if(!sink(user,elapsed+(u32)offsets[k]*15,(raster+(u32)offsets[k]*15)%run->period,k==2?0xbe:0xbf,values[k])) return 0;
  u16 cost=(run->literal?135:134)-((address&255)>=252)-(run->terminal && n+1==run->count?5:0);
  elapsed+=(u32)cost*15;raster=(raster+(u32)cost*15)%run->period;address+=4;
 }
 return 1;
}
'''
body=body.replace(needle,expand+needle).replace('event_count=0;active=&clock;', 'event_count=0;run_count=0;active=&clock;')
body=body.replace('source_pattern_decode_ports(&clock,&context,&source,pixels,address,&end,plan,sink,0)', 'source_pattern_decode_runs(&clock,&context,&source,pixels,address,&end,plan,sink,expand,0)')
(out/'wrapper.c').write_text(body)
sdk=root.parents[1]/'work/sgdk';env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
cmd=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-but-set-variable','-I',str(sdk/'inc'),'-I',str(root/'megadrive/src'),str(out/'wrapper.c'),str(prior/'scalar.c')]+[str(root/'megadrive/src'/(n+'.c')) for n in ('source_pattern_clock','source_clock','source_rng')]+['-o',str(out/'dates.dll')]
built=subprocess.run(cmd,env=env,capture_output=True,text=True);(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
dll=c.CDLL(str(out/'dates.dll'));dll.port_event_count.restype=dll.pattern_run_count.restype=c.c_uint32;dll.port_event_data.restype=c.POINTER(c.c_uint32)
fn=dll.pattern_case;fn.restype=c.c_uint8;fn.argtypes=[c.POINTER(c.c_uint8),c.c_uint16,c.c_uint16,c.c_uint32,c.c_uint8,c.c_uint8,c.POINTER(c.c_uint8),c.POINTER(c.c_uint32)]
m=json.loads((root/'analysis/v319-pattern-ports/manifest.json').read_bytes());item=m['compressed']['validation/v319-pattern-ports02/compiled-cases.json'];encoded=(root/'analysis/v319-pattern-ports'/item['stored']).read_bytes();assert sha(encoded)==item['stored_sha256'];raw=gzip.decompress(encoded);assert sha(raw)==item['raw_sha256'];cases=json.loads(raw);checks=[]
for row in cases:
 packed=(c.c_uint8*len(row['stream']))(*row['stream']);pixels=(c.c_uint8*16384)();actual=(c.c_uint32*16)()
 assert fn(packed,row['address'],row['lines'],row['raster'],1,row['plan_id'],pixels,actual)
 assert list(actual)==row['result'] and sha(bytes(pixels))==row['pixels_sha256']
 events=c.string_at(dll.port_event_data(),dll.port_event_count()*24);assert sha(events)==row['events_sha256'] and dll.pattern_run_count()>0
 checks.append(dict(plan=row['plan_id'],lines=row['lines'],raster=row['raster'],outputs=dll.port_event_count(),runs=dll.pattern_run_count()))
(out/'report.json').write_text(json.dumps(dict(passed=True,cases=len(checks),outputs=sum(r['outputs'] for r in checks),runs=sum(r['runs'] for r in checks),checks=checks,native_source_sha256=sha((root/'megadrive/src/source_pattern_clock.c').read_bytes()),scope='Expanded every emitted stable-run BF/BF/BE date,value and raster matches immutable pre-run individual-output hashes,plus all final native decoder/clock states for24intro asset/IRQ-edge cases.'),indent=2)+'\n');print('Exact run dates:',len(checks),'cases,',sum(r['outputs'] for r in checks),'outputs')
