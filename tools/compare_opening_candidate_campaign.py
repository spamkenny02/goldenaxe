"""Replay the completed campaign on v315 and the opening candidate, without state imports."""
import contextlib
import hashlib
import io
import json

from archive_lossless_evidence import sha
from assisted_prefix import recording
from run_core import ROOT, run, FrameWrites
from validate_playable_sprite_limit import symbols


def main():
    source=ROOT/'validation/natural-dungeon-combat/md-auto-v0314-cold-palace-ending01'
    capture=json.loads((source/'capture.json').read_bytes())
    assistance,writes=recording(source,capture)
    controls=json.loads((source/'controls.json').read_bytes())
    assert capture['sram_input'] is None and not assistance['boss_assistance']
    end=capture['frames'];presses=[tuple(row) for row in capture['presses']]
    for i,row in enumerate(controls):
        stop=controls[i+1]['frame']-1 if i+1<len(controls) else end
        presses.extend((row['frame'],min(stop,end),button) for button in row['buttons'] if row['frame']<=end)
    base=ROOT/'validation/opening-return-v0315'
    out=base/'campaign-comparison06'
    out.mkdir(exist_ok=False)
    fields={name:2 for name in ('room_id','game_state','hero_state','hero_x','hero_y',
        'hero_health','hero_max_health','hero_magic','hero_max_magic','hero_gold',
        'hero_keys','hero_hurt','hero_selected_item','hero_weapon_level','game_rng_seed',
        'randbase','transition_stage','transition_direction','transition_step')}
    fields.update(world_actor_state=768,world_loot_state=336,game_save_state=592,
                  hero_items=17,sms_vram=16384)
    fields.update({name:2 for name in ('hero_direction','hero_animation','hero_counter','hero_pending','hero_dx','hero_dy','hero_flags','world_graphics_class','world_dungeon_number','hero_basic_level','hero_armor_level','hero_shield_level','sound_unhandled_command')})
    old_symbols=symbols(ROOT/'validation/merchant-panel-v0314/previous-production/symbol.txt')
    assert all(address==old_symbols['hero_hurt'] for _,address,_ in writes)
    hashes=bytearray();differences=[];runs=[]
    for tag,rom,symbol_file in [
        ('v315',ROOT/'versions/v0315-004b593b/gaw-megadrive-v0315.bin',ROOT/'megadrive/out/release/symbol.txt'),
        ('candidate06',base/'candidate06/out/release/rom.bin',base/'candidate06/out/release/symbol.txt')]:
        sy=symbols(symbol_file)
        assert set(fields)<=sy.keys()
        assert all(sy[name]%2==0 for name in fields), 'Use aligned host-word spans only'
        segments=[(sy[name],size) for name,size in fields.items()]
        remapped=FrameWrites((frame,sy['hero_hurt'],data) for frame,address,data in writes)
        checked=0;boss_frames=0
        def observe(frame,raw):
            nonlocal checked,boss_frames
            hurt=int.from_bytes(raw[sy['hero_hurt']:sy['hero_hurt']+2],'little')
            actors=sy['world_actor_state']
            if any(raw[(actors+i*48)^1] in (*range(0x63,0x6e),*range(0x78,0x7d)) and raw[(actors+i*48+24)^1] for i in range(16)):
                assert hurt<=128,(tag,frame,'approach guard active during boss')
                boss_frames+=1
            assert int.from_bytes(raw[sy['sound_unhandled_command']:sy['sound_unhandled_command']+2],'little')==0
            if frame<3000:return
            digest=hashlib.sha256()
            for address,size in segments:
                # Host words have identical byte order on both cores. An odd
                # final byte is fetched at its actual swapped logical address.
                count=size&~1
                digest.update(raw[address:address+count])
                if size&1:
                    tail=(address+count)^1
                    digest.update(raw[tail:tail+1])
            value=digest.digest()
            if tag=='v315':hashes.extend(value)
            elif value!=hashes[(frame-3000)*32:(frame-2999)*32] and len(differences)<20:
                differences.append(frame)
            checked+=1
        folder=out/tag
        with contextlib.redirect_stdout(io.StringIO()):
            run(rom,end,folder,{end},presses,skip_intro=False,ram_writes=remapped,
                ram_observer=observe,core_options=capture['core_options'])
        runs.append(dict(tag=tag,rom_sha256=sha(rom.read_bytes()),compared_frames=checked,
            live_boss_frames_checked=boss_frames,capture_sha256=sha((folder/'capture.json').read_bytes())))
        print('Campaign comparison run finished',tag,checked,flush=True)
    (out/'baseline-semantic-hashes.bin').write_bytes(hashes)
    result=dict(passed=not differences,frames=end,compared_frames=end-2999,
        compared_fields=fields,first_difference_frames=differences,runs=runs,
        initial_sram=False,primary_state_imports=0,only_recorded_approach_hurt_writes=True,
        source_capture_sha256=sha((source/'capture.json').read_bytes()),
        driver_sha256=sha((ROOT/'tools/compare_opening_candidate_campaign.py').read_bytes()),
        scope='Same completed New Game controls and recorded approach guards on both binaries. Semantic game/actors/save/items/software-VRAM fields compared every frame from3000; CPU stack,absolute code pointers and physical framebuffer and deliberately resynchronized audio state are excluded. This is a cross-build regression check,not whole-source fidelity.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Cross-build campaign differences',differences,flush=True)


if __name__=='__main__':
    main()
