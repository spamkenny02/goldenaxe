"""Instruction-bin attribution for selected real incremental video updates."""
import contextlib,ctypes as c,io,json,re
from run_core import ROOT,run
from archive_lossless_evidence import sha
def main():
 folder=ROOT/'validation/md-source-room-budget-profile';reference=json.loads((ROOT/'analysis/md_source_room_budget_pixels_report.json').read_bytes());timing=json.loads((ROOT/'analysis/md_source_room_budget_current_report.json').read_bytes());assert sha((folder/'rom.bin').read_bytes())==reference['test_rom_sha256']==timing['test_rom_sha256']
 sy={m[2]:int(m[1],16) for line in (folder/'symbol.txt').read_text().splitlines() if(m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
 begin=timing['entry'];core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_cost_libretro.dll';dll=c.CDLL(str(core));dll.gaw_cost_config.argtypes=[c.c_uint,c.c_uint,c.c_uint];dll.gaw_cost_next_frame.restype=None;dll.gaw_cost_cases.restype=dll.gaw_cost_errors.restype=c.c_uint;dll.gaw_cost_master_data.restype=c.POINTER(c.c_ulonglong);dll.gaw_cost_instruction_data.restype=c.POINTER(c.c_uint);rows=[]
 for region,lines in [('auto',262),('pal',313)]:
  cases=[v for v in reference['results'] if v['region']==region]
  for selected in ['scroll-3051','sequence-3102','noop-0']:
   target=next(n for n,v in enumerate(cases) if v['name']==selected);end=next(v['return_pc'] for r in timing['regions'] if r['region']==region for v in r['spans'] if v['name']==selected);dll.gaw_cost_config(0xffffffff,0xffffffff,lines*3420);pending=[];schedule={};state={};armed=[False]
   def observe(f,r):
    word=lambda n:int.from_bytes(bytes(r[((sy[n]&65535)+i)^1] for i in range(2)),'big')
    if word('gaw_ready'):
     i=word('gaw_case');assert not word('gaw_status')
     if i not in schedule:schedule[i]=f+1
     if f==schedule[i]:
      pending[:]=[(f+1,sy['gaw_request']&65535,b'\0\1')]
      if i==target-1:dll.gaw_cost_config(begin,end,lines*3420);armed[0]=True
     state['done']=i==target
    if armed[0]:dll.gaw_cost_next_frame()
   with contextlib.redirect_stdout(io.StringIO()):run(folder/'rom.bin',3000,folder/f'cost-{region}-{selected}',set(),[],skip_intro=False,ram_writes=pending,ram_observer=observe,stop_when=lambda:bool(state.get('done')),core=core,core_options={'genesis_plus_gx_region_detect':region})
   assert dll.gaw_cost_cases()==1 and not dll.gaw_cost_errors(),(region,selected,dll.gaw_cost_cases(),dll.gaw_cost_errors())
   master=dll.gaw_cost_master_data();instructions=dll.gaw_cost_instruction_data();bins=[dict(pc=n*64,master=int(master[n]),instructions=int(instructions[n])) for n in range(4097) if master[n] or instructions[n]];total=sum(v['master'] for v in bins)
   expected=next(v for r in timing['regions'] if r['region']==region for v in r['spans'] if v['name']==selected)['elapsed_master'];assert total+112==expected,(region,selected,total,expected)
   row=dict(region=region,name=selected,total_master=total,bins=bins,hottest=sorted(bins,key=lambda v:v['master'],reverse=True)[:12]);rows.append(row);print(region,selected,[(hex(v['pc']),round(v['master']/3420,1)) for v in row['hottest'][:8]],flush=True)
 report=dict(passed=True,rows=rows,test_rom_sha256=reference['test_rom_sha256'],observer_core_sha256=sha(core.read_bytes()),limits=['64-byte instruction PC bins, selected unmodified held-frame fixture updates. Measured totals equal independent entry/RTS timings excluding RTS. Not a complete real-time or game proof.']);(ROOT/'analysis/md_source_room_cost_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
if __name__=='__main__':main()
