"""Read-only native render entry/return timestamps in a controlled burst."""
import argparse
import ctypes as c
import json
import re
import subprocess
import sys
import validate_burst_boss_gameplay as fixture
from run_core import ROOT
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--label', required=True); a = parser.parse_args()
    core = ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_clock_libretro.dll'
    dll = c.CDLL(str(core)); syfile = ROOT/'megadrive/out/release/symbol.txt'; ram_sy = symbols(syfile)
    sy = {m[2].split('.lto_priv.')[0]:int(m[1],16) for line in syfile.read_text().splitlines()
          if (m := re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)', line))}
    wanted = ['tick_world_simulation','tick_world_actors.constprop.0','world_vint',
              'prepare_world_sms_sprite_overflow','update_hero_sprites_for_frame','add_world_sprite_scene']
    watched = {sy[n]:n for n in wanted}
    asm = subprocess.check_output([str(ROOT.parents[1]/'work/sgdk/bin/objdump.exe'),'-d',
                                   '--disassemble=update_hero_sprites_for_frame.lto_priv.0',
                                   str(ROOT/'megadrive/out/release/rom.out')],text=True)
    lines = [(int(m[1],16),m[2]) for line in asm.splitlines()
             if (m := re.match(r'\s*([0-9a-f]+):\s+(.*)',line))]
    calls = [i for i,(_,s) in enumerate(lines) if 'jsr' in s and '<prepare_world_sms_sprite_overflow' in s]
    assert calls
    for i in calls:watched[lines[i+1][0]]='mask_return'
    dll.gaw_md_config.argtypes=[c.c_uint,c.POINTER(c.c_uint)]
    dll.gaw_md_event_count.restype=c.c_uint;dll.gaw_md_event_data.restype=c.POINTER(c.c_uint)
    pcs=(c.c_uint*len(watched))(*watched); original=fixture.run; results=[]

    def wrapped(rom,frames,folder,*args,**kwargs):
        if rom.suffix.lower()=='.sms':return original(rom,frames,folder,*args,**kwargs)
        observer=kwargs['ram_observer'];events=[];samples=[]
        def observe(f,r):
            observer(f,r);count=dll.gaw_md_event_count();assert count<8192;p=dll.gaw_md_event_data()
            if f>=2880:
                for n in range(count):events.append(dict(frame=f,function=watched[int(p[n*3])],cycles=int(p[n*3+1])))
                word=lambda name:int.from_bytes(bytes(r[(ram_sy[name]+i)^1] for i in range(2)),'big')
                samples.append(dict(frame=f,jobs=word('world_tile_job_count'),sprites=word('world_video_sat_count'),
                                    overflow=word('world_video_next_overflow')))
            dll.gaw_md_config(len(watched),pcs)
        kwargs.update(core=core,ram_observer=observe);dll.gaw_md_config(len(watched),pcs)
        result=original(rom,frames,folder,*args,**kwargs)
        region=kwargs['core_options']['genesis_plus_gx_region_detect'];period=3420*(313 if region=='pal' else 262)
        spans=[];pending=None
        for e in events:
            if e['function']=='prepare_world_sms_sprite_overflow':pending=e
            elif e['function']=='mask_return' and pending is not None:
                spans.append(dict(begin=pending['frame'],end=e['frame'],master=(e['frame']-pending['frame'])*period+e['cycles']-pending['cycles']));pending=None
        ticks=[e['frame'] for e in events if e['function']=='tick_world_simulation']
        gaps=[dict(before=x,after=y,frames=y-x) for x,y in zip(ticks,ticks[1:]) if y-x!=1]
        results.append(dict(region=region,events=events,samples=samples,mask_spans=spans,gaps=gaps))
        return result

    fixture.run=wrapped
    sys.argv=[sys.argv[0],'--variant7c','--type7c-only','--diagnose','--label',a.label]
    fixture.main()
    report=dict(md_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),read_only_timing=True,
                controlled_actor_hero_and_initial_clock=True,core_sha256=sha(core.read_bytes()),results=results)
    (ROOT/f'analysis/burst_render_cost_{a.label}_report.json').write_text(json.dumps(report,indent=2)+'\n')
    for row in results:
        print(row['region'],'gaps',len(row['gaps']),'mask spans near burst',[r for r in row['mask_spans'] if 2907<=r['begin']<=2912])
        print('samples',[r for r in row['samples'] if 2907<=r['frame']<=2912])


if __name__=='__main__':main()
