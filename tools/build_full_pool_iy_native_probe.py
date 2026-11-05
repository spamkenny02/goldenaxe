"""Build an isolated M68K fixture from the unchanged production routine bodies."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha

def function(text,token):
    start=text.index(token);op=text.index('{',start);level=0
    for i in range(op,len(text)):
        if text[i]=='{':level+=1
        if text[i]=='}':
            level-=1
            if not level:return text[start:i+1]
    raise AssertionError('Unclosed function')

def main():
    project=ROOT/'validation/full-pool-iy-v0314-native01/megadrive';src=project/'src';src.mkdir(parents=True,exist_ok=False)
    actor=(ROOT/'megadrive/src/actors.c').read_bytes();text=actor.decode();bodies={name:function(text,token) for name,token in [('allocator','static u8 *create_projectile_type('),('boss','void first_boss_behavior(')]}
    prefix='#include <genesis.h>\nstatic u8 arena[8192];\n#define world_actor_state (arena+0x600)\nextern const u8 first_boss_movement[];\nvolatile u16 probe_ready,probe_after_pool;\nu8 probe_results[768];\n'
    main_code='\nint main(bool hardReset)\n{\n    u8 *e=world_actor_state;\n    VDP_setEnable(FALSE);SYS_disableInts();\n    memset(arena,0,sizeof(arena));memset(world_actor_state,0xa7,768);\n    e[0]=0x64;e[1]=10;e[4]=0;e[10]=1;e[0x11]=96;e[0x13]=128;e[0x18]=60;\n    arena[0x90a]=0x5a;\n    first_boss_behavior(e,0,0);\n    memcpy(probe_results,world_actor_state,768);probe_after_pool=arena[0x90a];probe_ready=0xa531;\n    SYS_enableInts();while(TRUE) SYS_doVBlankProcess();return 0;\n}\n'
    (src/'main.c').write_bytes((prefix+bodies['allocator']+'\n'+bodies['boss']+'\n'+main_code).encode())
    data=(ROOT/'megadrive/src/first_boss_data.c').read_bytes();(src/'first_boss_data.c').write_bytes(data)
    index=dict(production_rom_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),actors_sha256=sha(actor),first_boss_data_sha256=sha(data),unchanged_body_sha256={k:sha(v.encode()) for k,v in bodies.items()},fixture_source_sha256=sha((src/'main.c').read_bytes()),scope='Controlled native routine fixture; no production source or ROM edits. Same full-pool actor input as the unmodified SMS routine fixture.')
    (project.parent/'source_index.json').write_text(json.dumps(index,indent=2)+'\n')
    print(project)
if __name__=='__main__':main()
