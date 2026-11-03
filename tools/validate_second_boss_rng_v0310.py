"""Compare the production type65 dispatch fragment and RNG adapter with SMS.

The fragment is extracted unchanged from actors.c; actor contact/common tails
are outside this test. The original boss instructions consume explicit test
draws. Native seed recurrence and conditional provider calls execute normally.
"""
import contextlib, io, itertools, json, os, re, subprocess
from pathlib import Path
import validate_second_boss as fixture
from run_core import ROOT, run
from source_rng_reference import source_rng
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols

def main():
    base=ROOT/'validation/second-boss-rng-v0310-02';assert not base.exists();base.mkdir()
    native=ROOT/'megadrive/src';sdk=(ROOT.parents[1]/'work/sgdk').resolve()
    rows=[]
    for gate,select in itertools.product(range(256),[0,1]):
        rows.append((0,6,0,0,[0,3,8][gate%3],128,96,3,select,[0,31,32,127][gate%4],gate,16,0))
    for gate,pause in itertools.product(range(8),[0,1,63,64,127]):
        rows.append((0,6,0,0,3,128,96,3,pause,0,gate,16,0))
    for kind,state,timer,flash,pool in itertools.product([0,2],[0,2,4,6,8],[0,1,32],[0,1],[0,3,8]):
        rows.append((kind,state,timer,flash,pool,128,96,3,[0,1,32,127][len(rows)%4],127,255,16,0))
    private=base/'fixture-root';(private/'input').mkdir(parents=True);(private/'tools').mkdir();(private/'validation').mkdir()
    original=(ROOT/'input/original.sms').read_bytes();(private/'input/original.sms').write_bytes(original)
    fixture.ROOT=private;fixture.ROWS=rows;_,sms_image,sms_folder=fixture.generate()
    source=(native/'actors.c').read_bytes().decode();start=source.index('            else if(entity[0]==0x65)')
    end=source.index('            else if(entity[0]==0x66)',start)
    fragment=source[start:end].replace('else if','if',1)
    src=base/'src';src.mkdir()
    for p in native.iterdir():
        if not p.is_file():continue
        name={'main.c':'game_main.inc','actors.c':'actors.inc','source_rng_runtime.c':'runtime.inc'}.get(p.name,p.name)
        (src/name).write_bytes(p.read_bytes())
    (src/'dispatch.inc').write_bytes(fragment.encode())
    (src/'second_boss_cases.inc').write_bytes((private/'tools/second_boss_cases.inc').read_bytes())
    metadata=[]
    for row in rows:
        kind,state,timer,flash,pool,x,y,previous,select,turn,gate,radius,phase=row
        seed=0 if gate<128 else 64;before=seed;draws=[];move=state==4
        if state==6 and not timer:
            if kind==2:move=True
            else:
                next_seed=source_rng(seed,0)['seed'];refresh=gate^(next_seed&255);assert refresh<128
                draws.append(refresh);step=source_rng(seed,refresh);assert step['value']==gate;seed=step['seed']
                if gate<8:draws.append(select)
                else:move=True
        if move:
            draws.append(select)
            if not select&1:draws.append(turn)
        assert len(draws)<=3
        metadata.append([before,seed,len(draws),*(draws+[0]*(3-len(draws)))])
    (src/'metadata.inc').write_bytes(('static const u16 metadata[][6]={\n'+''.join('{'+','.join(map(str,r))+'},\n'for r in metadata)+'};\n').encode())
    (src/'main.c').write_bytes(b'''#define main gaw_game_main
#include "game_main.inc"
#undef main
#include "actors.inc"
#include "second_boss_cases.inc"
#include "metadata.inc"
static u16 fixture_values[3],fixture_count;
volatile u16 harness_case,harness_ready,harness_done,harness_calls,harness_overread,harness_seed;
u16 gaw_fixture_random(void){u16 n=harness_calls++;if(n>=fixture_count){harness_overread=1;return 0;}return fixture_values[n];}
#define random gaw_fixture_random
#include "runtime.inc"
#undef random
int main(bool hardReset){u16 test;VDP_setEnable(FALSE);
for(test=0;test<sizeof(second_boss_cases)/sizeof(second_boss_cases[0]);test++){
 const u8 *r=second_boss_cases[test];u8 *entity=world_actor_state;u16 n;u32 started;u16 hero_x=224,hero_y=144;
 harness_ready=0;memset(world_actor_state,0xa7,768);entity[0]=0x65;entity[0x13]=r[5];entity[0x11]=r[6];
 for(n=8;n<16;n++)world_actor_state[n*48]=n<8+r[4]?0x66:0;
 entity[1]=r[1];entity[4]=entity[0x2f]=r[2];entity[5]=r[3];entity[0x20]=r[7];entity[0x2a]=r[7]&1;
 entity[0x2b]=r[4];entity[0x28]=r[11];entity[0x29]=r[12];entity[0x2e]=r[0]==2?20:0;
 game_rng_seed=metadata[test][0];fixture_count=metadata[test][2];harness_calls=harness_overread=0;
 for(n=0;n<3;n++)fixture_values[n]=metadata[test][3+n];
#include "dispatch.inc"
 harness_seed=game_rng_seed;harness_case=test;harness_ready=1;started=vtimer;
 while(vtimer-started<3)SYS_doVBlankProcess();
}harness_done=1;while(TRUE)SYS_doVBlankProcess();return 0;}
''')
    env=dict(os.environ);env['PATH']=str(sdk/'bin')+';'+env['PATH'];sdkpath=str(sdk).replace('\\','/');sdkunix='/'+sdkpath[0].lower()+sdkpath[2:]
    cmd=[str(sdk/'bin/sh.exe'),'-c','export PATH="$2/bin:$PATH"; make -f "$1/makefile.gen" "GDK=$1" "JAVA=$3" -j2','build',sdkpath,sdkunix,'D:/jdk-25.0.1/bin/java.exe']
    built=subprocess.run(cmd,cwd=base,env=env,capture_output=True);(base/'build.log').write_bytes(built.stdout+built.stderr);assert built.returncode==0,built.stderr[-3000:]
    cartridge=base/'out/release/rom.bin';sy=symbols(base/'out/release/symbol.txt');results=[]
    for region in ['auto','pal']:
        expected={};done=[];frames=len(rows)*5+100
        def sms(f,ram):
            if ram[4]:done.append(f)
            if ram[2]:expected.setdefault(int.from_bytes(ram[:2],'little'),bytes(ram[0x600:0x900]))
        with contextlib.redirect_stdout(io.StringIO()):run(sms_folder/'source.sms',frames,base/(region+'-sms'),set(),[],skip_intro=False,ram_observer=sms,stop_when=lambda:bool(done),core_options={'genesis_plus_gx_region_detect':region})
        assert done and len(expected)==len(rows),(region,len(expected),len(rows))
        checked={};done=[]
        def md(f,ram):
            def data(n,k):return bytes(ram[(sy[n]+i)^1]for i in range(k))
            def word(n):return int.from_bytes(data(n,2),'big')
            if word('harness_done'):done.append(f)
            if not word('harness_ready'):return
            case=word('harness_case')
            if case in checked:return
            actual=data('world_actor_state',768);assert actual==expected[case],(region,case,rows[case],[(i,a,b)for i,(a,b)in enumerate(zip(actual,expected[case]))if a!=b][:15])
            assert not word('harness_overread') and word('harness_calls')==metadata[case][2] and word('harness_seed')==metadata[case][1],(region,case,metadata[case],word('harness_calls'),word('harness_seed'))
            checked[case]=actual
        with contextlib.redirect_stdout(io.StringIO()):run(cartridge,frames,base/(region+'-md'),set(),[],skip_intro=False,ram_observer=md,stop_when=lambda:bool(done),core_options={'genesis_plus_gx_region_detect':region})
        assert done and len(checked)==len(rows),(region,len(checked),len(rows))
        output=b''.join(checked[i]for i in range(len(rows)));(base/(region+'-actors.bin')).write_bytes(output)
        results.append(dict(region=region,cases=len(checked),all_768_actor_bytes_exact=True,conditional_provider_counts_exact=True,seed_after_dispatch_exact=True,actors_sha256=sha(output)))
        print(region,len(checked),'production dispatch/RNG/core cases exact vs SMS',flush=True)
    files=['main.c','actors.c','source_rng.c','source_rng_runtime.c','source_rng_runtime.h']
    result=dict(passed=True,md_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),original_sms_sha256=sha(original),controlled_sms_sha256=sha(sms_image),test_cartridge_sha256=sha(cartridge.read_bytes()),native_source_sha256={n:sha((native/n).read_bytes())for n in files},dispatch_fragment_sha256=sha(fragment.encode()),results=results,distinct_cases=len(rows),full_8bit_gates_covered=256,draw_count_distribution={str(n):sum(r[2]==n for r in metadata)for n in range(4)},trace=base.relative_to(ROOT).as_posix(),full_game_validated=False,limits=['Production type65 dispatch fragment extracted unchanged from actors.c and compiled with actual runtime adapter/core. Surrounding contact/damage/common actor tails are outside this test.','Original boss/chooser/boundary/orbit instructions run with three R sites and04E1 replaced by explicit supplied inputs. Native seed and raw provider are controlled at case entry; this is not natural R/IRQ phase equivalence.','Whole768 actor bytes,conditional provider call counts and final seed checked. No natural boss fight,pixels/audio or hardware claim.'])
    (ROOT/'analysis/second_boss_rng_v0310_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())

if __name__=='__main__':main()
