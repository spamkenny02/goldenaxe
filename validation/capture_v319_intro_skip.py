"""Normal controller inputs; compare observer runs to an independent source core."""
import contextlib,ctypes as c,io,json,struct
from pathlib import Path
from run_core import run
from archive_lossless_evidence import sha

def capture(root,dll,core,out,region):
 baseline=root.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_v319_psg_writes_libretro.dll'
 build=json.loads((root/'validation/v319-psg-write-observer01/build-report.json').read_bytes())
 assert sha(baseline.read_bytes())==build['core_sha256']
 for name in ('gaw_skip_target','gaw_skip_events','gaw_skip_return'):getattr(dll,name).restype=c.c_uint
 plain=c.CDLL(str(baseline));plain.gaw_psg_writes_reset.restype=None
 records={};states=bytearray();runs=[];stride=dll.gaw_poll_stride()
 for target in (0xf36,0xf37,0x1055):
  for stage in range(7):
   for button in (0,8):
    name=f'{target:04x}-stage{stage}-button{button}';folder=out/name
    dll.gaw_poll_reset();pressed=[];psg=bytearray()
    def input_provider(frame):
     if not pressed and dll.gaw_skip_target()==target and dll.gaw_skip_events()>=stage*6912:pressed.append(frame)
     return {button} if pressed and pressed[0]<=frame<pressed[0]+3 else set()
    with contextlib.redirect_stdout(io.StringIO()):
     run(root/'input/original.sms',14000,folder/'observer',set(),[],skip_intro=False,core=core,
      input_provider=input_provider,stop_when=lambda:dll.gaw_skip_return()==0xd0b,
      psg_observer=lambda frame,values:psg.extend(struct.pack('<8H',*values)),
      core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
    assert pressed and dll.gaw_skip_return()==0xd0b and dll.gaw_poll_errors()==0,(region,name,pressed)
    count=dll.gaw_poll_size();raw=c.string_at(dll.gaw_poll_data(),count*stride)
    (folder/'source-records.bin').write_bytes(raw);(folder/'observer-psg.bin').write_bytes(psg)
    prior=bytearray();plain.gaw_psg_writes_reset()
    def baseline_psg(frame,values):
     prior.extend(struct.pack('<8H',*values));plain.gaw_psg_writes_reset()
    with contextlib.redirect_stdout(io.StringIO()):
     run(root/'input/original.sms',len(psg)//16,folder/'reference',set(),[(pressed[0],pressed[0]+2,button)],
      skip_intro=False,core=baseline,psg_observer=baseline_psg,
      core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
    assert prior==psg,(region,name,'observer interference')
    for index in range(count):
     record=raw[index*stride:(index+1)*stride];records.setdefault(vector_key(record),record)
    states.extend(psg)
    row=dict(target=target,stage=stage,button=button,press_frame=pressed[0],frames=len(psg)//16,
      source_entries=count,psg_sha256=sha(psg),reference_psg_equal=True,records_sha256=sha(raw))
    runs.append(row);(folder/'report.json').write_text(json.dumps(row,indent=2)+'\n')
    print(json.dumps(dict(region=region,scenario=name,frames=row['frames'],entries=count)),flush=True)
 out.mkdir(parents=True,exist_ok=True)
 report=dict(passed=True,scenarios=runs,unique_vectors=len(records),reference_core=str(baseline),
  reference_core_sha256=sha(baseline.read_bytes()),oracle_ram_writes=0,sram_imports=0)
 (out/'capture-report.json').write_text(json.dumps(report,indent=2)+'\n')
 return b''.join(records.values()),states,report

def vector_key(record):
 # Deduplicate unchanged normal prefixes across cold runs; omit only the two
 # absolute diagnostic time origins, retaining both measured time differences.
 snapshot=1664
 first_master,first_irq=struct.unpack_from('<2Q',record)
 last_master,last_irq=struct.unpack_from('<2Q',record,snapshot)
 return record[16:snapshot]+record[snapshot+16:]+struct.pack('<2Q',last_master-first_master,last_irq-first_irq)

def reuse(root,source,out):
 report=json.loads((source/'capture-report.json').read_bytes());assert report['passed']
 assert sha(Path(report['reference_core']).read_bytes())==report['reference_core_sha256']
 records={};states=bytearray();stride=446224
 for row in report['scenarios']:
  name=f"{row['target']:04x}-stage{row['stage']}-button{row['button']}";folder=source/name
  raw=(folder/'source-records.bin').read_bytes();psg=(folder/'observer-psg.bin').read_bytes()
  assert sha(raw)==row['records_sha256'] and sha(psg)==row['psg_sha256']
  assert len(raw)==row['source_entries']*stride and len(psg)==row['frames']*16 and row['reference_psg_equal']
  for index in range(row['source_entries']):
   record=raw[index*stride:(index+1)*stride];records.setdefault(vector_key(record),record)
  states.extend(psg)
 out.mkdir(parents=True,exist_ok=True)
 report=dict(report,unique_vectors=len(records),reused_from=source.relative_to(root).as_posix(),
  normalization='Dedup key excludes absolute observer master/IRQ origins only; raw representative and measured differences retained unchanged.')
 (out/'capture-report.json').write_text(json.dumps(report,indent=2)+'\n')
 return b''.join(records.values()),states,report
