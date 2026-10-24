"""Read-only entry/RTS timing of the incremental SGDK renderer."""
import contextlib,ctypes as c,gzip,io,json,re,subprocess
from run_core import ROOT,run
from archive_lossless_evidence import sha
def restore(folder):
 archive=ROOT/'analysis/md-source-room-delta-v0275';m=json.loads((archive/'manifest.json').read_bytes());base='validation/md-source-room-delta/out/release/'
 for n in ['rom.bin','rom.out','symbol.txt']:
  name=base+n
  if name in m['files']:raw=(archive/name).read_bytes();assert sha(raw)==m['files'][name]
  else:
   item=m['compressed'][name];encoded=(archive/item['stored']).read_bytes();assert sha(encoded)==item['stored_sha256'];raw=gzip.decompress(encoded);assert sha(raw)==item['raw_sha256']
  (folder/n).write_bytes(raw)
 return json.loads((ROOT/'analysis/md_source_room_delta_report.json').read_bytes())
def profile(folder,reference):
 sy={m[2]:int(m[1],16) for line in (folder/'symbol.txt').read_text().splitlines() if(m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
 name=next(n for n in sy if n.startswith('md_source_room_frame_update'));entry=sy[name]
 dump=subprocess.check_output([str(ROOT.parents[1]/'work/sgdk/bin/objdump.exe'),'-d','--disassemble='+name,str(folder/'rom.out')],text=True);(folder/'renderer.asm').write_bytes(dump.encode())
 returns=[int(m[1],16) for line in dump.splitlines() if(m:=re.match(r'\s*([0-9a-fA-F]+):.*\trts\s*$',line))];assert returns
 helper_labels={};helper_functions={};watched=[entry,*returns]
 for prefix in ['source_sms_sprite8_prepare','source_sms_sprite8_update','VDP_loadTileData','VDP_setTileMapDataRow','DMA_doCPUCopyDirect']:
  function=next((n for n in sy if n.startswith(prefix)),None)
  if not function:continue
  assembly=subprocess.check_output([str(ROOT.parents[1]/'work/sgdk/bin/objdump.exe'),'-d','--disassemble='+function,str(folder/'rom.out')],text=True)
  exits=[int(m[1],16) for line in assembly.splitlines() if(m:=re.match(r'\s*([0-9a-fA-F]+):.*\trts\s*$',line))]
  if not exits:continue
  helper_functions[function]=dict(entry=sy[function],returns=exits);helper_labels[sy[function]]=(function,True)
  for pc in exits:helper_labels[pc]=(function,False)
 watched += list(helper_labels);assert len(watched)<=32
 core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_clock_libretro.dll';dll=c.CDLL(str(core));dll.gaw_md_config.argtypes=[c.c_uint,c.POINTER(c.c_uint)];dll.gaw_md_event_count.restype=c.c_uint;dll.gaw_md_event_data.restype=c.POINTER(c.c_uint)
 results=[]
 for region,lines in [('auto',262),('pal',313)]:
  period=lines*3420;pcs=(c.c_uint*len(watched))(*watched);dll.gaw_md_config(len(watched),pcs);events=[];pending=[];captures={};seen=set();state={}
  def observe(f,r):
   count=dll.gaw_md_event_count();assert count<8192;ptr=dll.gaw_md_event_data()
   events.extend([int(ptr[n*3]),(f-1)*period+int(ptr[n*3+1]),int(ptr[n*3+2])] for n in range(count));dll.gaw_md_config(len(watched),pcs)
   value=lambda n:int.from_bytes(bytes(r[((sy[n]&65535)+i)^1] for i in range(2)),'big');state['done']=value('gaw_done')
   if value('gaw_ready'):
    i=value('gaw_case');assert not value('gaw_status')
    if i not in seen:seen.add(i);captures[i]=f+1
    if f==captures[i]:pending[:]=[(f+1,sy['gaw_request']&65535,b'\0\1')]
  with contextlib.redirect_stdout(io.StringIO()):run(folder/'rom.bin',3000,folder/region,set(),[],skip_intro=False,ram_observer=observe,ram_writes=pending,stop_when=lambda:bool(state.get('done')),core=core,core_options={'genesis_plus_gx_region_detect':region})
  spans=[];active=None;child_pending={};child_cost={};child_calls={}
  for pc,t,sp in events:
   if pc in helper_labels:
    if not active:continue
    function,is_entry=helper_labels[pc];key=(function,sp)
    if is_entry:assert key not in child_pending,(key,hex(pc),t,child_pending.get(key),helper_functions[function]);child_pending[key]=t
    else:
     # A tail-called copy helper can return directly from the row/tile API.
     # Its final RTS completes every pending helper at this original SP.
     for key in [key for key in child_pending if key[1]==sp]:
      function=key[0];child_cost[function]=child_cost.get(function,0)+t+112-child_pending.pop(key);child_calls[function]=child_calls.get(function,0)+1
    continue
   if pc==entry:assert active is None;active=(t,sp);child_cost={};child_calls={}
   else:
    assert active and active[1]==sp;start=active[0];end=t+112;elapsed=end-start
    #112master is the16cycle RTS, which is observed before execution.
    spans.append(dict(return_pc=pc,start_master=start,end_master=end,elapsed_master=elapsed,elapsed_lines=elapsed/3420,start_phase_line=(start%period)//3420,end_phase_line=(end%period)//3420,start_physical_line=((start%period)//3420+224)%lines,end_physical_line=((end%period)//3420+224)%lines,overlapped_frames=end//period-start//period,helper_master=dict(child_cost),helper_calls=dict(child_calls)));assert not child_pending;active=None
  expected=[v for v in reference['results'] if v['region']==region];assert len(spans)==len(expected)-1 and not active
  for v,case in zip(spans,expected[1:]):v.update(name=case['name'],uploaded_patterns=case['uploaded_patterns'],uploaded_words=case['uploaded_words'],uploaded_clones=case['uploaded_clones'])
  results.append(dict(region=region,spans=spans,max_lines=max(v['elapsed_lines'] for v in spans),scroll=[v for v in spans if v['name'].startswith('scroll-')],animation=[v for v in spans if v['name'].startswith('sequence-')]))
  print(region,'maximum lines',results[-1]['max_lines'],'scroll max',max(v['elapsed_lines'] for v in results[-1]['scroll']),flush=True)
 return dict(passed=True,regions=results,renderer=name,entry=entry,returns=returns,helper_functions=helper_functions,test_rom_sha256=sha((folder/'rom.bin').read_bytes()),observer_core_sha256=sha(core.read_bytes()),limits=['Helper durations can be nested and must not be summed without accounting for overlap. Read-only function entry/RTS observations on the previously pixel-checked diagnostic ROM. RTS16cycles/112master added; renderer IRQs masked. Memory writes only advance the fixture request handshake.','GPG frame phase starts at physical line224 in H32/224. Includes CPU preparation and VDP stalls, no sound workload. Not natural campaign, waveform or complete physical publication proof.'])
def main():
 folder=ROOT/'validation/md-source-room-budget-baseline';folder.mkdir(exist_ok=True);reference=restore(folder);assert sha((folder/'rom.bin').read_bytes())==reference['test_rom_sha256'];report=profile(folder,reference);(ROOT/'analysis/md_source_room_budget_baseline_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
if __name__=='__main__':main()
