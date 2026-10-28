"""Attribute one baseline296 mask call's wall time to read-only CPU PC bins."""
import ctypes as c
import json
import re
import subprocess
import sys
import validate_burst_boss_gameplay as fixture
from run_core import ROOT
from archive_lossless_evidence import sha


def main():
    current='--current' in sys.argv
    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());version=next(e['version'] for e in json.loads((ROOT/'versions/index.json').read_bytes()) if e['sha256']==digest)
    label=f'v{version:04d}' if current else 'v0296'
    rom=ROOT/('gaw-megadrive.bin' if current else 'versions/v0296-3446f41f/gaw-megadrive-v0296.bin')
    syfile=ROOT/('megadrive/out/release/symbol.txt' if current else 'validation/stack-v0296-d2-all02/symbol.txt')
    sy={m[2].split('.lto_priv.')[0]:int(m[1],16) for line in syfile.read_text().splitlines()
        if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
    begin=sy['prepare_world_sms_sprite_overflow'];start=sy['update_hero_sprites_for_frame']
    asm=subprocess.check_output([str(ROOT.parents[1]/'work/sgdk/bin/objdump.exe'),'-D','-b','binary','-m','m68k',
                                 f'--start-address={start}',f'--stop-address={start+8192}',str(rom)],text=True)
    lines=[(int(m[1],16),m[2]) for line in asm.splitlines() if (m:=re.match(r'\s*([0-9a-f]+):\s+(.*)',line))]
    stops=[lines[i+1][0] for i,(_,text) in enumerate(lines) if 'jsr' in text and f'(0x{begin:x})' in text]
    assert stops
    core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_cost_libretro.dll';dll=c.CDLL(str(core))
    dll.gaw_cost_config.argtypes=[c.c_uint,c.c_uint,c.c_uint]
    dll.gaw_cost_master_data.restype=c.POINTER(c.c_ulonglong)
    dll.gaw_cost_instruction_data.restype=c.POINTER(c.c_uint)
    dll.gaw_cost_cases.restype=dll.gaw_cost_errors.restype=c.c_uint
    dll.gaw_md_config.argtypes=[c.c_uint,c.POINTER(c.c_uint)]
    dll.gaw_md_event_count.restype=c.c_uint;dll.gaw_md_event_data.restype=c.POINTER(c.c_uint)
    pcs=(c.c_uint*(1+len(stops)))(begin,*stops);original=fixture.run;results=[]

    def wrapped(path,frames,folder,*args,**kwargs):
        if path.suffix.lower()=='.sms':return original(path,frames,folder,*args,**kwargs)
        observe=kwargs['ram_observer'];region=kwargs['core_options']['genesis_plus_gx_region_detect']
        period=3420*(313 if region=='pal' else 262);selected=None;events=[];bins=[]
        dll.gaw_md_config(len(pcs),pcs);dll.gaw_cost_config(0xffffff,0xffffff,period)
        def sample(f,r):
            nonlocal selected,bins
            observe(f,r);count=dll.gaw_md_event_count();data=dll.gaw_md_event_data()
            if f==2907:
                previous=[int(data[i*3]) for i in range(count) if int(data[i*3]) in stops]
                assert previous;selected=previous[-1];dll.gaw_cost_config(begin,selected,period)
            if 2908<=f<=2909:
                for n in range(count):events.append(dict(frame=f,pc=int(data[n*3]),cycles=int(data[n*3+1])))
            if not bins and f>=2908 and any(e['pc']==selected for e in events):
                assert dll.gaw_cost_cases()==1 and not dll.gaw_cost_errors(),(region,dll.gaw_cost_cases(),dll.gaw_cost_errors())
                master=dll.gaw_cost_master_data();instructions=dll.gaw_cost_instruction_data()
                bins=[dict(pc=i*64,master=int(master[i]),instructions=int(instructions[i])) for i in range(4097) if master[i] or instructions[i]]
                dll.gaw_cost_config(0xffffff,0xffffff,period)
            dll.gaw_cost_next_frame();dll.gaw_md_config(len(pcs),pcs)
        kwargs.update(core=core,ram_observer=sample)
        result=original(path,frames,folder,*args,**kwargs)
        a=next(e for e in events if e['pc']==begin)
        b=next(e for e in events if e['pc']==selected and e['frame']>=a['frame'])
        elapsed=(b['frame']-a['frame'])*period+b['cycles']-a['cycles']
        assert sum(row['master'] for row in bins)==elapsed
        functions=sorted((pc,name) for name,pc in sy.items() if pc<0x40000)
        for row in bins:row['nearest_symbol']=next(name for pc,name in reversed(functions) if pc<=row['pc'])
        hottest=sorted(bins,key=lambda row:row['master'],reverse=True)
        results.append(dict(region=region,elapsed_master=elapsed,bins=bins,hottest=hottest))
        return result

    fixture.run=wrapped;sys.argv=[sys.argv[0],'--variant7c','--type7c-only','--diagnose','--label','instruction-'+label]+([] if current else ['--baseline-v0296'])
    fixture.main()
    report=dict(md_sha256=sha(rom.read_bytes()),core_sha256=sha(core.read_bytes()),read_only=True,results=results,
                limits=['One controlled type7C first burst mask entry/return per region. Wall cycles include interrupt and VDP contention;64-byte bins can straddle functions. Exact histogram sums equal observed entry/return spans.'])
    (ROOT/f'analysis/burst_instruction_cost_{label}_report.json').write_text(json.dumps(report,indent=2)+'\n')
    for row in results:print(row['region'],row['elapsed_master'],row['hottest'][:10])


if __name__=='__main__':main()
