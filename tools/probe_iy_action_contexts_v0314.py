"""Observe source IY across controlled timing and ordinary hero action contexts."""
import contextlib,ctypes as c,io,json
from run_core import ROOT,run
from validate_actor_tick import PRESSES
from archive_lossless_evidence import sha

def main():
    base=ROOT/'validation/iy-action-contexts-v0314-01';base.mkdir(exist_ok=False)
    core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_iytrace_libretro.dll';dll=c.CDLL(str(core));dll.gaw_iytrace_size.restype=c.c_uint;dll.gaw_iytrace_data.restype=c.POINTER(c.c_uint)
    result=[]
    for action in ('idle','melee','fire','earth'):
        for offset in (0,1,3):
            birth=2800+offset;e=bytearray(768);e[0]=0x64;e[1]=10;e[3]=0x43;e[4]=1;e[8]=0x13;e[9]=0x99;e[10]=1;e[12]=2;e[13]=40;e[0x11]=96;e[0x13]=128;e[0x18]=60;e[0x19]=20;e[0x1a]=4;e[0x20]=5
            for slot in range(8,16):
                at=slot*48;e[at]=0x73;e[at+0x11]=96;e[at+0x13]=128;e[at+10]=(slot-8)%5
            writes=[(birth,0x600,bytes(e)),(birth,0x310,(144<<8).to_bytes(2,'little')+(224<<8).to_bytes(2,'little')+bytes(4)),(birth,0xa2,b'\x09')]
            presses=[(200,220,0)]+PRESSES[:8]
            if action!='idle':presses += [(2794,2808,8)]
            if action in ('fire','earth'):
                item=4 if action=='fire' else 5
                writes += [(2793,0xdf,bytes([item])),(2793,0xe0+item,b'\x01'),(2793,0xdb,b'\x18\x18')]
            out=base/f'{action}-{offset}';dll.gaw_iytrace_reset();events=[];seen=0;states=[]
            def observe(frame,raw):
                nonlocal seen
                if frame==2792:assert raw[0x1d]==12
                if frame in (birth-1,birth,birth+1,birth+8):states.append(dict(frame=frame,game=raw[0x1d],hero=raw[0x301],spell=raw[0x330],selected=raw[0xdf],magic=raw[0xdb]))
                n=dll.gaw_iytrace_size();p=dll.gaw_iytrace_data()
                for i in range(seen,n):events.append(dict(frame=frame,iy=p[i*8+2],value=p[i*8+3],ix=p[i*8+1]))
                seen=n
            with contextlib.redirect_stdout(io.StringIO()):run(ROOT/'input/original.sms',birth+12,out,{birth-1,birth+1,birth+12},presses,skip_intro=False,core=core,ram_writes=sorted(writes),ram_observer=observe)
            row=dict(action=action,birth_frame=birth,events=events,unique_iy=sorted({r['iy']for r in events}),hero_states=states,incoming_iy_overridden=False)
            result.append(row);print(action,offset,row['unique_iy'],len(events),flush=True)
    report=dict(probe_passed=True,production_rom_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),trace_core_sha256=sha(core.read_bytes()),cases=result,controlled_fixture=True,natural_gameplay_proof=False,all_observed_iy_in_rom=all(e['iy']<0xc000 for r in result for e in r['events']),scope='Controlled source game-loop cases; boss/pool, hero position and optional spell ownership are fixture inputs. Actions use normal buttons. IY is never injected. These finite observations do not establish a universal caller invariant.')
    (ROOT/'analysis/iy_action_contexts_v0314_report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
