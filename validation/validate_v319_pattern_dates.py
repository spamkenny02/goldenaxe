"""Native032A foreground OUT dates against independently executed SMS ROM."""
import contextlib,ctypes as c,gzip,io,json,os,struct,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
from run_core import run
out=root/'validation/v319-pattern-dates01';assert not out.exists();out.mkdir()
prior=root/'validation/v319-pattern-ports02'
# Rebuild the previously audited test helper without rerunning archived tests.
sdk=root.parents[1]/'work/sgdk';env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
cmd=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-but-set-variable','-I',str(sdk/'inc'),'-I',str(root/'megadrive/src'),str(prior/'wrapper.c'),str(prior/'scalar.c')]
cmd += [str(root/'megadrive/src'/(n+'.c')) for n in ('source_pattern_clock','source_clock','source_rng')]+['-o',str(out/'native.dll')]
built=subprocess.run(cmd,env=env,capture_output=True,text=True);(out/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
native=c.CDLL(str(out/'native.dll'));native.port_event_count.restype=c.c_uint32;native.port_event_data.restype=c.POINTER(c.c_uint32)
fn=native.pattern_case;fn.restype=c.c_uint8;fn.argtypes=[c.POINTER(c.c_uint8),c.c_uint16,c.c_uint16,c.c_uint32,c.c_uint8,c.c_uint8,c.POINTER(c.c_uint8),c.POINTER(c.c_uint32)]
build=json.loads((root/'validation/v319-pattern-dates-observer01/report.json').read_bytes());core=Path(build['core']);assert sha(core.read_bytes())==build['core_sha256']
dll=c.CDLL(str(core));dll.gaw_pattern_dates.restype=c.POINTER(c.c_uint32);dll.gaw_pattern_date_count.restype=dll.gaw_pattern_date_overflow.restype=c.c_uint32
rom=(root/'input/original.sms').read_bytes();results=[];manifest=json.loads((root/'analysis/v319-pattern-ports/manifest.json').read_bytes())
for region in ('ntsc','pal'):
 dll.gaw_pattern_date_reset();psg=bytearray()
 with contextlib.redirect_stdout(io.StringIO()):run(root/'input/original.sms',14000,out/region,set(),[],skip_intro=False,core=core,psg_observer=lambda frame,values:psg.extend(struct.pack('<8H',*values)),core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
 assert dll.gaw_pattern_date_overflow()==0
 raw=c.string_at(dll.gaw_pattern_dates(),dll.gaw_pattern_date_count()*32);(out/(region+'-dates.bin')).write_bytes(raw);(out/(region+'-psg.bin')).write_bytes(psg)
 rows=[struct.unpack_from('<8I',raw,off) for off in range(0,len(raw),32)];checks=[]
 for plan,header,end in [(1,0x9d70,0xa598),(2,0xa655,0xae6f)]:
  subset=[row for row in rows if row[1]==plan];assert subset and subset[0][0]==0 and subset[-1][0]==2,(region,plan,len(subset))
  assert subset[0][6:8]==(header+4,0x4000),subset[0]
  stream=rom[0x18000+header+4-0x8000:0x18000+end-0x8000];packed=(c.c_uint8*len(stream)).from_buffer_copy(stream);pixels=(c.c_uint8*16384)();result=(c.c_uint32*16)()
  assert fn(packed,0x4000,262 if region=='ntsc' else 313,0,1,plan,pixels,result)
  dates=[struct.unpack_from('<6I',c.string_at(native.port_event_data(),native.port_event_count()*24),n*24) for n in range(native.port_event_count())]
  original=[(row[2],row[4],row[5]) for row in subset if row[0]==1];predicted=[(row[4],row[2],row[3]) for row in dates]
  assert original==predicted,(region,plan,next(((n,a,b) for n,(a,b) in enumerate(zip(original,predicted)) if a!=b),None),len(original),len(predicted))
  assert subset[-1][2]==result[5]*15 and subset[-1][6]==end and subset[-1][7]==result[1],(subset[-1],list(result))
  checks.append(dict(plan=plan,header=header,outputs=len(original),foreground_master=subset[-1][2],actual_elapsed_master=subset[-1][3],actual_irq_master=subset[-1][3]-subset[-1][2],foreground_dates_and_values_exact=True,source_end_and_destination_exact=True))
 item=manifest['compressed'][f'validation/v319-pattern-ports02/compiled-cases.json'];encoded=(root/'analysis/v319-pattern-ports'/item['stored']).read_bytes();assert sha(encoded)==item['stored_sha256']
 # Independent old source PSG capture, not the native-only port fixture.
 prior_psg=json.loads((root/'analysis/v319-psg-write-spacing/manifest.json').read_bytes());item=prior_psg['compressed'][f'validation/v319-psg-writes01/{region}-sms/exposed-psg-states.bin'];encoded=(root/'analysis/v319-psg-write-spacing'/item['stored']).read_bytes();assert sha(encoded)==item['stored_sha256'] and sha(gzip.decompress(encoded))==item['raw_sha256'] and gzip.decompress(encoded)==psg
 results.append(dict(region=region,checks=checks,raw_sha256=sha(raw),psg_exact_frames=14000));print(json.dumps(results[-1]),flush=True)
report=dict(passed=True,results=results,source_sha256=sha(rom),core_sha256=build['core_sha256'],native_sha256=sha((root/'megadrive/src/source_pattern_clock.c').read_bytes()),scope='Actual original032A foreground OUT completion timestamps,port/value order,final foreground duration and HL/DE return state. Actual IRQ master time separated using original instruction execution accounting; native event foreground dates subtract only its separately counted synthetic IRQ work.',limits=['Foreground dates exact, not original absolute wall-clock publication from native full IRQ composition. Native wrapper still uses synthetic82T IRQ callback; real IRQ work remains to compose.','No physical video/audio or throughput certificate.'],oracle_ram_writes=0,sram_imports=0)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
