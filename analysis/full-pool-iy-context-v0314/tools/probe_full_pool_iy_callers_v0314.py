"""Read original IY in a controlled production-loop full-pool scenario."""
import contextlib,ctypes as c,io,json
from run_core import ROOT,run
from validate_actor_tick import PRESSES
from archive_lossless_evidence import sha

def main():
    folder=ROOT/'validation/full-pool-iy-callers-v0314-01';folder.mkdir(exist_ok=False)
    core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_iytrace_libretro.dll';dll=c.CDLL(str(core))
    dll.gaw_iytrace_size.restype=c.c_uint;dll.gaw_iytrace_data.restype=c.POINTER(c.c_uint)
    source=ROOT/'validation/full-pool-iy-v0314-source02/iy-c6f0/controlled-original-routine.sms'
    dll.gaw_iytrace_reset()
    with contextlib.redirect_stdout(io.StringIO()):run(source,20,folder/'direct-core-check',{20},[],skip_intro=False,core=core)
    raw=(folder/'direct-core-check/ram_00020.bin').read_bytes();assert raw==(source.parent/'ram_00020.bin').read_bytes()
    n=dll.gaw_iytrace_size();ptr=dll.gaw_iytrace_data();direct=[[ptr[i*8+j] for j in range(8)]for i in range(n)]
    assert n==5 and all(e[0]==0xa82f and e[1]==0xc600 and e[2]==0xc6f0 for e in direct)
    assert [e[3]for e in direct]==[4,3,2,1,0]
    e=bytearray(768);e[0]=0x64;e[1]=10;e[3]=0x43;e[4]=1;e[8]=0x13;e[9]=0x99;e[10]=1;e[12]=2;e[13]=40;e[0x11]=96;e[0x13]=128;e[0x18]=60;e[0x19]=20;e[0x1a]=4;e[0x20]=5
    for slot in range(8,16):
        at=slot*48;e[at]=0x73;e[at+0x11]=96;e[at+0x13]=128;e[at+10]=(slot-8)%5
    writes=[(2800,0x600,bytes(e)),(2800,0x310,(144<<8).to_bytes(2,'little')+(224<<8).to_bytes(2,'little')+bytes(4)),(2800,0xa2,b'\x09')]
    dll.gaw_iytrace_reset();events=[];seen=0;before=None
    def observe(frame,raw):
        nonlocal seen,before
        if frame==2799:before=dict(game=raw[0x1d],room=int.from_bytes(raw[0xb9:0xbb],'little'),hero=raw[0x301]);assert raw[0x1d]==12
        count=dll.gaw_iytrace_size();ptr=dll.gaw_iytrace_data()
        for i in range(seen,count):events.append(dict(frame=frame,pc=ptr[i*8],ix=ptr[i*8+1],iy=ptr[i*8+2],value=ptr[i*8+3],boss_type=ptr[i*8+4],boss_state=ptr[i*8+5],room_class=ptr[i*8+6],actor_count=ptr[i*8+7]))
        seen=count
    with contextlib.redirect_stdout(io.StringIO()):run(ROOT/'input/original.sms',2820,folder/'game-loop',{2799,2800,2801,2820},[(200,220,0)]+PRESSES[:8],skip_intro=False,core=core,ram_writes=writes,ram_observer=observe)
    assert before and events
    report=dict(probe_passed=True,production_rom_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),trace_core_sha256=sha(core.read_bytes()),direct_core_check_full_ram_exact=True,direct_events=direct,source_before_fixture=before,source_game_loop_events=events,incoming_iy_overridden=False,controlled_fixture=True,natural_gameplay_proof=False,scope='Original source game loop receives one controlled boss, a full pool of valid73 projectiles and a distant hero. IY is not injected. Read-only observations identify the original caller value; this is not a naturally reached boss or proof that every real caller has that value.')
    (ROOT/'analysis/full_pool_iy_callers_v0314_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
