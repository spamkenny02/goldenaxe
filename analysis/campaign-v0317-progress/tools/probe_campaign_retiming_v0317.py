"""Diagnose a shifted historical controller recording; never certify a campaign."""
import argparse, contextlib, io, json
from pathlib import Path
from run_core import ROOT, run, FrameWrites
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--frames',type=int,default=8000)
    p.add_argument('--delay',type=int,default=7)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    out=a.out.resolve(); assert out.is_relative_to(ROOT/'validation')
    out.mkdir(parents=True,exist_ok=False)
    source=ROOT/'validation/natural-dungeon-combat/md-auto-v0314-cold-palace-ending01'
    c=json.loads(evidence(source/'capture.json'))
    assist,writes=recording(source,c)
    controls=json.loads(evidence(source/'controls.json'))
    assert c['sram_input'] is None and not assist['boss_assistance']
    presses=[tuple(row) for row in c['presses']]
    for i,row in enumerate(controls):
        stop=controls[i+1]['frame']-1 if i+1<len(controls) else c['frames']
        presses.extend((row['frame'],stop,b) for b in row['buttons'])
    names=('room_id','game_state','hero_state','hero_x','hero_y','hero_health',
           'hero_max_health','hero_magic','hero_max_magic','hero_gold','hero_keys',
           'hero_hurt','hero_selected_item','hero_weapon_level','game_rng_seed',
           'randbase','hero_counter','world_dungeon_number')
    sizes={n:2 for n in names}
    sizes.update(world_actor_state=768,world_loot_state=336,game_save_state=592,hero_items=17)
    baseline={}; reports=[]; mismatch_counts={n:0 for n in sizes}; first_differences=[]
    for tag,rom,sym,delay in [
        ('v315',ROOT/'versions/v0315-004b593b/gaw-megadrive-v0315.bin',
         ROOT/'validation/merchant-panel-v0314/candidate03/out/release/symbol.txt',0),
        ('v317',ROOT/'gaw-megadrive.bin',ROOT/'megadrive/out/release/symbol.txt',a.delay)]:
        sy=symbols(sym)
        assert all(sy[n]%2==0 for n in sizes)
        shifted=lambda f:f+delay if f>=2501 else f
        inputs=[(shifted(start),shifted(stop),key) for start,stop,key in presses if start<=a.frames]
        injections=FrameWrites((shifted(f),sy['hero_hurt'],data) for f,addr,data in writes if f<=a.frames)
        rooms=[];last_room=None;boss_checks=0;final=None;ready=None
        def observe(frame,raw):
            nonlocal last_room,boss_checks,final,ready
            word=lambda n:int.from_bytes(raw[sy[n]:sy[n]+2],'little')
            assert word('sound_unhandled_command')==0
            actors=sy['world_actor_state']
            if any(raw[(actors+i*48)^1] in (*range(0x63,0x6e),*range(0x78,0x7d))
                   and raw[(actors+i*48+24)^1] for i in range(16)):
                assert word('hero_hurt')<=128,('guard during boss',tag,frame)
                boss_checks+=1
            if frame<2400:return
            state={n:word(n) for n in names}
            if ready is None and state['room_id']==149 and state['game_state']==12 and state['hero_state']==1:
                ready=frame
            if state['room_id']!=last_room:
                rooms.append(dict(frame=frame,**state));last_room=state['room_id']
            final=state
            if frame<2508+delay:return
            values={n:bytes(raw[sy[n]:sy[n]+(size&~1)])+
                    (bytes([raw[(sy[n]+size-1)^1]]) if size&1 else b'') for n,size in sizes.items()}
            if tag=='v315':baseline[frame]=values
            else:
                reference=baseline[frame-delay]
                bad=[n for n in sizes if values[n]!=reference[n]]
                for n in bad:mismatch_counts[n]+=1
                if bad and len(first_differences)<12:
                    first_differences.append(dict(frame=frame,baseline_frame=frame-delay,fields=bad,state=state,
                        reference={n:int.from_bytes(reference[n],'little') for n in names}))
        folder=out/tag
        with contextlib.redirect_stdout(io.StringIO()):
            run(rom,a.frames+delay,folder,{a.frames+delay},inputs,skip_intro=False,
                ram_writes=injections,ram_observer=observe,core_options=c['core_options'])
        reports.append(dict(tag=tag,rom_sha256=sha(rom.read_bytes()),symbols_sha256=sha(evidence(sym)),
            ready_frame=ready,rooms=rooms,final=final,boss_frames_checked=boss_checks,
            gameplay_input_delay=delay,recorded_approach_writes=len(injections)))
        print(tag,'completed',a.frames+delay,'frames; ready',ready,flush=True)
    result=dict(diagnostic_only=True,full_campaign_verified=False,runs=reports,
        compared_fields=sizes,mismatch_counts=mismatch_counts,first_differences=first_differences,
        initial_sram=False,primary_state_imports=0,driver_sha256=sha(Path(__file__).read_bytes()),
        source_capture_sha256=sha(evidence(source/'capture.json')),
        scope='Historical ordinary inputs and logged approach guards shifted after frame2501. '
              'Differences diagnose input/clock divergence and do not prove a game bug or completion.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Mismatch counts:',mismatch_counts,flush=True)


if __name__=='__main__':main()
