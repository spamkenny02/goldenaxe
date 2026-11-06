"""Read-only source instruction boundaries for the closing story and first reveal."""
import contextlib,ctypes as c,io,json
from run_core import ROOT,run
from archive_lossless_evidence import sha
from validate_actor_tick import PRESSES


def main():
    core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_clock_libretro.dll'
    dll=c.CDLL(str(core));dll.gaw_timing_events.restype=c.POINTER(c.c_uint64);dll.gaw_timing_count.restype=c.c_uint
    base=ROOT/'validation/initial-world-source-v0315';assert not base.exists();base.mkdir()
    cases=[]
    for pal in (False,True):
      for ack in (2400,2480):
        region='pal'if pal else'auto';out=base/(region+'-'+str(ack));events=[];previous=0
        def observe(frame,raw):
            nonlocal previous
            if frame==ack-50:dll.gaw_timing_reset();previous=0
            if frame<ack-50:return
            count=dll.gaw_timing_count();assert count<32768
            values=dll.gaw_timing_events()
            for n in range(previous,count):
                pc,cycles,irq,room,clock,hl,de,bc=[int(values[n*8+i])for i in range(8)]
                if pc in (0x11b7,0x0b12,0x0b56,0x16d0,0x1780,0x18e1,0x0aa4,0x1fa4):events.append(dict(frame=frame,pc=pc,master_cycles=cycles,irq_master_cycles=irq,clock=clock,room=room))
            previous=count
        inputs=[row if row[0]!=2400 else(ack,ack+10,row[2])for row in PRESSES[:8]]
        with contextlib.redirect_stdout(io.StringIO()):run(ROOT/'input/original.sms',ack+200,out,set(),[(200,220,0)]+inputs,core=core,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':region})
        (out/'events.json').write_text(json.dumps(events,indent=2)+'\n')
        print(region,ack,[(hex(e['pc']),e['frame'],e['clock'])for e in events],flush=True)
        cases.append(dict(region=region,last_ack=ack,events=events))
    (base/'report.json').write_text(json.dumps(dict(source_sha256=sha((ROOT/'input/original.sms').read_bytes()),core_sha256=sha(core.read_bytes()),driver_sha256=sha((ROOT/'tools/profile_initial_world_source.py').read_bytes()),natural_input_only=True,cases=cases),indent=2)+'\n')


if __name__=='__main__':main()
