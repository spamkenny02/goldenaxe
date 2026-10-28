"""Compare native physical sprite pixels for old/current masked tile reuse."""
import contextlib
import io
import json
from run_core import ROOT,run,FrameWrites
from archive_lossless_evidence import sha
from validate_actor_tick import PRESSES
from validate_playable_sprite_limit import symbols,reference


def main():
    source=(ROOT/'validation/sms-vertical-check/ram_03120.bin').read_bytes()[0x600:0x630]
    baseline=ROOT/'versions/v0295-b71a6bc6/gaw-megadrive-v0295.bin'
    current=ROOT/'gaw-megadrive.bin';results=[]
    root=ROOT/'validation/sprite-mask-cache-gameplay-v0296';assert not root.exists()
    for region in ['auto','pal']:
        for name,count,y in [('empty',0,64),('overlap',12,64),('full_pool',16,64),
                             ('top_clip',12,1),('bottom_clip',12,188),('terminator',1,225)]:
            planes={};jobs={}
            for tag,rom,symbol_file in [('old',baseline,ROOT/'validation/stack-v0295-d2-all/symbol.txt'),
                                        ('new',current,ROOT/'megadrive/out/release/symbol.txt')]:
                sy=symbols(symbol_file);writes=FrameWrites();rows={};counts={}
                actors=bytearray(768)
                for slot in range(count):
                    e=bytearray(source);e[3]=1;e[4]=120;e[5]=0;e[6]=255
                    e[0x11]=y+(slot%3)*3 if count>1 else y;e[0x13]=16+slot*14
                    actors[slot*48:(slot+1)*48]=e
                def observe(f,r):
                    if 3126<=f<3142:
                        word=lambda n:int.from_bytes(bytes(r[(sy[n]+i)^1] for i in range(2)),'big')
                        timer=int.from_bytes(bytes(r[(sy['vtimer']+i)^1] for i in range(4)),'big')
                        writes.append((f+1,sy['world_clock_shift'],(timer+1).to_bytes(4,'big')))
                        for key,data in [('world_actor_state',actors),('world_loot_state',bytes(336)),('world_spell_state',bytes(48))]:
                            writes.append((f+1,sy[key],data))
                        for key,value in [('hero_x',128<<8),('hero_y',144<<8),('hero_hurt',0),('hero_flags',3),('hero_state',1),('hero_counter',0),('hero_dx',0),('hero_dy',0),('hero_direction',1)]:
                            writes.append((f+1,sy[key],value.to_bytes(2,'big')))
                        if f>=3134:counts[f]=word('world_tile_job_count')
                def video(f,v):
                    if f>=3134:rows[f]=reference(v,0xf400,16)[0]
                with contextlib.redirect_stdout(io.StringIO()):
                    run(rom,3142,root/f'{region}-{name}-{tag}',{3134,3142},PRESSES,
                        ram_writes=writes,ram_observer=observe,vram_observer=video,
                        core_options={'genesis_plus_gx_region_detect':region})
                planes[tag]=rows;jobs[tag]=counts
            assert planes['old']==planes['new'],(region,name,'physical sprite pixels differ')
            result=dict(region=region,case=name,physical_sprite_frames=len(planes['new']),
                        sprite_pixels_per_frame=49152,all_pixels_exact=True,observed_jobs=jobs)
            results.append(result);print(region,name,len(planes['new']),'physical sprite frames exact',flush=True)
    report=dict(passed=True,md_sha256=sha(current.read_bytes()),baseline_sha256=sha(baseline.read_bytes()),
                cases=results,limits=['Real native ROMs after cold boot,with controlled actor/hero records refreshed each frame and explicit zero clock phase. Compare decoded physical VRAM sprite output after masking,not clone tile identities.',
                                     'Six selected overlap/clipping/list cases per region. This does not prove complete framebuffer,audio,natural fight timing or every actor pattern combination.'])
    (ROOT/'analysis/sprite_mask_cache_gameplay_v0296_report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
