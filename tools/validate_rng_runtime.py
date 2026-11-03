"""Check the stateful production RNG adapter on host and actual 68000 code.

Controlled refresh inputs test integration, not source instruction-clock fidelity.
"""
import contextlib, ctypes as c, hashlib, io, json, os, re, subprocess
from pathlib import Path
from run_core import ROOT, run
from source_rng_reference import source_rng

def sha(data): return hashlib.sha256(data).hexdigest()

def main():
    folder=ROOT/'validation/rng-runtime-v0310';folder.mkdir(exist_ok=True)
    sdk=(ROOT.parents[1]/'work/sgdk').resolve();native=ROOT/'megadrive/src'
    env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+str(sdk/'bin')+';'+env['PATH']
    shim=folder/'provider.inc'
    shim.write_bytes(b'#include <types.h>\nu16 test_raw;u32 test_calls;u16 gaw_test_random(void){test_calls++;return test_raw;}\n')
    args=['C:/msys64/ucrt64/bin/gcc.exe','-O3','-Wall','-Wextra','-Werror','-shared','-Drandom=gaw_test_random','-I',str(sdk/'inc'),str(native/'source_rng.c'),str(native/'source_rng_runtime.c'),'-x','c',str(shim),'-o',str(folder/'runtime.dll')]
    built=subprocess.run(args,env=env,capture_output=True);(folder/'host-build.log').write_bytes(built.stdout+built.stderr);assert built.returncode==0,built.stderr
    dll=c.CDLL(str(folder/'runtime.dll'));raw=c.c_uint16.in_dll(dll,'test_raw');calls=c.c_uint32.in_dll(dll,'test_calls')
    dll.game_rng_reset.restype=None
    for name in ['game_rng_seeded','game_rng_read_refresh']:getattr(dll,name).restype=c.c_uint8
    seed=0;expected=[];dll.game_rng_reset();assert calls.value==0
    for i in range(65536):
        if i==32768:
            n=calls.value;dll.game_rng_reset();assert calls.value==n;seed=0
        n=calls.value;raw.value=i;assert dll.game_rng_read_refresh()==i&127
        raw.value=i^0xa55a;step=source_rng(seed,raw.value&127);seed=step['seed'];expected.append(step['value'])
        assert dll.game_rng_seeded()==step['value'],i
        raw.value=i^65535;assert dll.game_rng_read_refresh()==(i^65535)&127
        assert calls.value==n+3,i
    # Audit opcode-anchored seeded call sites separately from the adapter math.
    rom=(ROOT/'input/original.sms').read_bytes();assert sha(rom)=='852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9'
    sites=[i for i in range(len(rom)-2)if rom[i:i+3]==b'\xcd\xe1\x04']
    assert sites==[0x503,0x1c40,0x1c73,0x4b56,0x4c09,0x4db0,0x522f,0x671e,0xa921],sites
    assert b'\xed\x4f'not in rom and rom[0xa935:0xa937]==b'\xed\x5f'
    text={name:(native/name).read_bytes().decode()for name in ['main.c','actors.c','minigame.inc']}
    assert all(not re.search(r'\brandom\s*\(',s)for s in text.values())
    for name,bindings in {
        'main.c':['spawn_world_boss_particle(entity,game_rng_seeded())','(void)context;return game_rng_seeded();','JOY_init();game_rng_reset();save_init();'],
        'actors.c':['roll=game_rng_seeded();n=((roll&0xe0)>>4)','(roll?roll[4]:game_rng_seeded())>=8','choice=roll?roll[3]:game_rng_seeded();','gate=game_rng_seeded();if(gate<8) pause=game_rng_read_refresh()&127'],
        'minigame.inc':['minigame_draw(cells,cell,game_rng_seeded())']}.items():
        for binding in bindings:assert binding in text[name],(name,binding)
    assert sum(s.count('game_rng_seeded()')for s in text.values())==7
    # Dedicated cartridge includes the production adapter unchanged, renaming
    # only its external provisional provider to a deterministic fixture.
    src=folder/'src';src.mkdir(exist_ok=True)
    for name in ['source_rng.c','source_rng.h','source_rng_runtime.h']:(src/name).write_bytes((native/name).read_bytes())
    (src/'runtime.inc').write_bytes((native/'source_rng_runtime.c').read_bytes())
    (src/'expected.h').write_bytes(('static const u8 expected[65536]={\n'+','.join(map(str,expected))+'\n};\n').encode())
    (src/'main.c').write_bytes(b'''#include <genesis.h>
#include "expected.h"
static u16 test_raw;static u32 test_calls;
u16 gaw_test_random(void){test_calls++;return test_raw;}
#define random gaw_test_random
#include "runtime.inc"
#undef random
volatile u32 gaw_runtime_cases,gaw_runtime_failures,gaw_runtime_first_error;
volatile u16 gaw_runtime_done;
static void check(u8 ok,u32 i){if(!ok){if(!gaw_runtime_failures)gaw_runtime_first_error=i;gaw_runtime_failures++;}}
int main(bool hard_reset){u32 i,n;VDP_setEnable(FALSE);SYS_disableInts();game_rng_reset();check(test_calls==0,0);
for(i=0;i<65536UL;i++){
 if(i==32768UL){n=test_calls;game_rng_reset();check(test_calls==n,i);}
 n=test_calls;test_raw=(u16)i;check(game_rng_read_refresh()==(i&127),i);
 test_raw=(u16)i^0xa55a;check(game_rng_seeded()==expected[i],i);
 test_raw=(u16)i^65535;check(game_rng_read_refresh()==((i^65535)&127),i);
 check(test_calls==n+3,i);gaw_runtime_cases++;
}gaw_runtime_done=1;while(TRUE);return 0;}
''')
    sdkpath=str(sdk).replace('\\','/');sdkunix='/'+sdkpath[0].lower()+sdkpath[2:]
    args=[str(sdk/'bin/sh.exe'),'-c','export PATH="$2/bin:$PATH"; make -f "$1/makefile.gen" "GDK=$1" "JAVA=$3" -j2','build',sdkpath,sdkunix,'D:/jdk-25.0.1/bin/java.exe']
    built=subprocess.run(args,cwd=folder,env=env,capture_output=True);(folder/'build.log').write_bytes(built.stdout+built.stderr);assert built.returncode==0,built.stderr[-3000:]
    cartridge=folder/'out/release/rom.bin'
    sy={m[2]:int(m[1],16)&65535 for line in (folder/'out/release/symbol.txt').read_bytes().decode().splitlines()if(m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
    results=[]
    for region in ['auto','pal']:
        observed={}
        def observe(f,ram):
            def value(name,n):return int.from_bytes(bytes(ram[(sy[name]+i)^1]for i in range(n)),'big')
            observed.update(frame=f,done=value('gaw_runtime_done',2),cases=value('gaw_runtime_cases',4),failures=value('gaw_runtime_failures',4),first_error=value('gaw_runtime_first_error',4))
        with contextlib.redirect_stdout(io.StringIO()):run(cartridge,6000,folder/region,set(),[],skip_intro=False,ram_observer=observe,stop_when=lambda:bool(observed.get('done')),core_options={'genesis_plus_gx_region_detect':region})
        assert observed['done']and observed['cases']==65536 and not observed['failures'],(region,observed)
        results.append(dict(region=region,**observed));print(region,observed,flush=True)
    report=dict(passed=True,host_interleaved_cases=65536,host_provider_calls=calls.value,results_68000=results,seeded_call_pcs=[hex(i)for i in sites],utility_04fe_site='0x503',native_seeded_expressions=7,original_sha256=sha(rom),source_sha256={name:sha((native/name).read_bytes())for name in ['source_rng.c','source_rng.h','source_rng_runtime.c','source_rng_runtime.h','main.c','actors.c','minigame.inc']},test_rom_sha256=sha(cartridge.read_bytes()),limits=['Controlled provider values exercise the production state adapter; source R/IRQ instruction phase is still provisional.','The 04FE utility call is inventoried separately; literal opcode audit is not a whole-ROM reachability proof.','Separate test cartridge; gameplay and hardware are not established by this test.'])
    (ROOT/'analysis/rng_runtime_v0310_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('Stateful RNG adapter passed host and 68000 PAL/NTSC',flush=True)

if __name__=='__main__':main()
