"""Compare a native static-frame sprite flag evaluator to original live IRQ snapshots."""
import contextlib,ctypes as c,gzip,io,json,os,struct,subprocess,sys
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
from run_core import run
out=root/'validation/v319-chip-status02';assert not out.exists();out.mkdir()
source=root/'megadrive/src/source_intro_sprite_status.c';sdk=root.parents[1]/'work/sgdk'
env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
compiled=subprocess.run(['C:/msys64/ucrt64/bin/gcc.exe','-O3','-shared','-Wall','-Wextra','-Werror','-I',str(sdk/'inc'),'-I',str(root/'megadrive/src'),str(source),'-o',str(out/'native.dll')],capture_output=True,text=True,env=env)
(out/'compile.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
native=c.CDLL(str(out/'native.dll')).source_intro_sprite_flags;native.argtypes=[c.POINTER(c.c_uint8)]*3;native.restype=c.c_uint8
build=json.loads((root/'validation/v319-chip-status-observer01/report.json').read_bytes());core=Path(build['core']);assert sha(core.read_bytes())==build['core_sha256']
dll=c.CDLL(str(core));dll.gaw_chip_reset.restype=None
for name in ('gaw_chip_size','gaw_chip_stride','gaw_chip_errors_get'):getattr(dll,name).restype=c.c_uint
dll.gaw_chip_data.restype=c.POINTER(c.c_uint8);stride=dll.gaw_chip_stride();assert stride==16424
manifest=json.loads((root/'analysis/v319-psg-write-spacing/manifest.json').read_bytes())
raw_cases=[];unique={};rows=[];results=[];trace=bytearray();frequencies=Counter();mismatches=[];unsupported=[]
for region in ('ntsc','pal'):
 dll.gaw_chip_reset();psg=bytearray();counts=Counter();start_cases=len(raw_cases)
 def observe(frame,ram):
  count=dll.gaw_chip_size();assert dll.gaw_chip_errors_get()==0
  raw=c.string_at(dll.gaw_chip_data(),count*stride);dll.gaw_chip_reset()
  for n in range(count):
   record=raw[n*stride:(n+1)*stride];status,hardware,lines,line,delta,height=struct.unpack_from('<6I',record)
   key=struct.pack('<2I',hardware,height)+record[24:]+bytes([status&0x60])
   if key not in unique:
    unique[key]=len(raw_cases);raw_cases.append(record)
    regs=(c.c_uint8*16).from_buffer_copy(record[24:40]);vram=(c.c_uint8*16384).from_buffer_copy(record[40:]);flags=c.c_uint8()
    supported=hardware==0x21 and height==192 and bool(native(vram,regs,c.byref(flags)))
    row=dict(index=unique[key],region_first_seen=region,frame_first_seen=frame,status=status,expected=status&0x60,predicted=flags.value,supported=supported,
     hardware=hardware,height=height,regs=list(record[24:40]),record_sha256=sha(record))
    rows.append(row)
    if not supported:unsupported.append(row)
    elif flags.value!=(status&0x60):mismatches.append(row)
   index=unique[key];frequencies[index]+=1;row=rows[index]
   counts['irq_samples']+=1;counts['matched' if row['supported'] and row['predicted']==row['expected'] else 'mismatch' if row['supported'] else 'unsupported']+=1
   trace.extend(struct.pack('<4I',0 if region=='ntsc' else 1,frame,index,status))
 with contextlib.redirect_stdout(io.StringIO()):
  run(root/'input/original.sms',14000,out/region,set(),[],skip_intro=False,core=core,ram_observer=observe,
   psg_observer=lambda frame,values:psg.extend(struct.pack('<8H',*values)),core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
 item=manifest['compressed'][f'validation/v319-psg-writes01/{region}-sms/exposed-psg-states.bin'];encoded=(root/'analysis/v319-psg-write-spacing'/item['stored']).read_bytes();assert sha(encoded)==item['stored_sha256']
 prior=gzip.decompress(encoded);assert sha(prior)==item['raw_sha256'] and prior==psg
 (out/region/'psg-states.bin').write_bytes(psg)
 result=dict(region=region,**counts,new_unique_cases=len(raw_cases)-start_cases,observer_psg_exact_frames=14000);results.append(result);print(json.dumps(result),flush=True)
(out/'cases.bin').write_bytes(b''.join(raw_cases));(out/'irq-case-trace.bin').write_bytes(trace)
for row in rows:row['occurrences']=frequencies[row['index']]
(out/'cases.json').write_text(json.dumps(rows,indent=2)+'\n')
report=dict(passed=not mismatches and not unsupported,static_frame_candidate=True,results=results,unique_cases=len(rows),unique_mismatches=len(mismatches),unique_unsupported=len(unsupported),mismatches=mismatches,unsupported=unsupported,
 core_sha256=sha(core.read_bytes()),source_sha256=sha((root/'input/original.sms').read_bytes()),native_source_sha256=sha(source.read_bytes()),
 limits=['Static current VRAM/register evaluator, no mid-frame write history,flag latching or status-read timing. Not a live production binding.','Original no-input14000 frames per region; PSG noninterference matched prior immutable captures.'],oracle_ram_writes=0,sram_imports=0)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(unique_cases=len(rows),mismatches=len(mismatches),unsupported=len(unsupported))),flush=True)
