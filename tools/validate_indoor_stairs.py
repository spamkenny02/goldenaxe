"""Real C7->1F doorway, ordinary indoor stairs, oil gift and return.

Controlled exterior/hero-position fixture. No inventory, actor or outside-context
mutation after the actual door; source and production cartridges are unpatched.
"""
import argparse
import contextlib
import io
import json
from run_core import ROOT, run
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols
from validate_actor_tick import PRESSES
from validate_key_door_gameplay import initial_room, rle_planes, maps
from natural_dungeon_combat import walk


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--trial', required=True)
    p.add_argument('--expect-blocked', action='store_true')
    p.add_argument('--pal', action='store_true')
    a = p.parse_args()
    sy = symbols(ROOT/'megadrive/out/release/symbol.txt')
    source = ROOT/'input/original.sms'
    original = source.read_bytes()
    _, meta, _, _, arrays, _ = initial_room(original)
    doors = json.loads((ROOT/'analysis/doors_reference.json').read_bytes())
    door = next(d for d in doors['direct_unconditional_doors'] if d['room'] == 0xc7 and d['target'] == 0x1f)
    cells = bytearray(160)
    offset = int.from_bytes(arrays['world_room_index'][0xc7*2:0xc7*2+2], 'little')
    rle_planes(arrays['world_room_streams'], offset, cells, 0, 1)
    sms_map, _ = maps(cells, meta)
    base = ROOT/'validation'/('indoor-stairs-'+a.trial+('-pal' if a.pal else ''))
    assert not base.exists()
    results = {}
    for tag, rom in [('sms', source), ('md', ROOT/'gaw-megadrive.bin')]:
        folder = base/tag
        state, events, controls = {}, [], []
        captures = {3300, 3401, 3600, 4000, 4400, 4800, 5400}
        previous = None
        done = None
        observed = 0
        cached_frame, cached_buttons, last_direction = -1, [], 0
        if tag == 'sms':
            writes = [(3120, 0xb9, b'\xc7\0'), (3120, 0xa4, door['script_entry'].to_bytes(2, 'little')),
                      (3120, 0x1c00, bytes(cells)), (3120, 0x1600, sms_map),
                      (3120, 0x301, b'\1'), (3120, 0x303, b'\3\1'),
                      (3120, 0x310, (128<<8).to_bytes(2, 'little')+((168-1)<<8).to_bytes(2, 'little')+bytes(2)+(256).to_bytes(2, 'little')),
                      (3400, 0x310, (40<<8).to_bytes(2, 'little')+(104<<8).to_bytes(2, 'little')+bytes(4)),
                      (3400, 0x301, b'\1'), (3400, 0x303, b'\3\0'), (3400, 0x30a, b'\0')]
        else:
            word_write = lambda f, n, v: (f, sy[n], v.to_bytes(2, 'big'))
            writes = [word_write(3120, n, v) for n, v in [('room_id',0xc7),('hero_state',1),
                      ('hero_flags',3),('hero_counter',1),('hero_y',128<<8),('hero_x',(168-1)<<8),('hero_dy',0),('hero_dx',256)]]
            writes += [(3120, sy['scratch']+0x800, bytes(cells)), (3120, sy['sms_vram']+0x3800, sms_map)]
            writes += [word_write(3400, n, v) for n, v in [('hero_y',40<<8),('hero_x',104<<8),
                       ('hero_dy',0),('hero_dx',0),('hero_state',1),('hero_flags',3),('hero_counter',0),('hero_direction',0)]]

        def observe(f, raw):
            nonlocal previous, done, observed
            observed = f
            if f < 3200:
                return
            if tag == 'sms':
                state.update(room=int.from_bytes(raw[0xb9:0xbb], 'little'), game=raw[0x1d], hero=raw[0x301],
                             counter=raw[0x304], x=raw[0x313], y=raw[0x311], oil=raw[0xe8],
                             outside=int.from_bytes(raw[0xbb:0xbd], 'little'), flags=raw[0x1c7],
                             modal=raw[0x1d] == 22, health=raw[0x318], tilemap=bytes(raw[0x1600:0x1c00]))
            else:
                data = lambda n,k: bytes(raw[(sy[n]+i)^1] for i in range(k))
                word = lambda n: int.from_bytes(data(n,2),'big')
                state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),
                             x=word('hero_x')>>8,y=word('hero_y')>>8,oil=data('hero_items',17)[8],
                             outside=word('house_return_room'),flags=data('game_save_state',592)[0x117],
                             modal=word('house_dialogue_active'),health=word('hero_health'),tilemap=data('sms_vram',16384)[0x3800:0x3e00])
            if f == 3300:
                assert state['room'] == 0x1f and state['outside'] == 0xc7 and not state['oil'], {k:v for k,v in state.items() if k!='tilemap'}
            if state['room'] == 0xc7 and state['game'] == 12 and state['hero'] == 1 and state['oil'] and done is None:
                done=f;captures.add(f+60)
            key = tuple(state[n] for n in ['room','game','oil','flags','modal'])
            if key != previous:
                events.append(dict(frame=f,**{k:v for k,v in state.items() if k!='tilemap'}))
                captures.add(f+1);previous=key

        def controller(f):
            nonlocal cached_frame, cached_buttons, last_direction
            if f == cached_frame:
                return cached_buttons
            cached_frame = f
            value = []
            if f > 3410 and state:
                if done is not None:
                    value=[]
                elif state['oil'] and f%40 == 0:
                    value=[8]
                elif state['modal'] or state['game'] == 22:
                    value = [8] if f % 40 == 0 else []
                elif state['game'] == 12 and state['hero'] == 1:
                    if not state['oil']:
                        last_direction=0;value=[4]
                    elif state['room'] == 0xf:
                        last_direction=1;value=[5]
                    elif state['room'] == 0x1f:
                        if state['counter']:
                            value=[4+last_direction]
                        elif (state['x'],state['y']) == (136,152):
                            last_direction=1;value=[5]
                        else:
                            path=walk(state['tilemap'],(state['x'],state['y']),lambda q:q==(136,152))
                            if path:last_direction=path[0];value=[4+last_direction]
            if not controls or controls[-1]['buttons'] != value:
                controls.append(dict(frame=f,buttons=value))
            cached_buttons=value
            return value

        with contextlib.redirect_stdout(io.StringIO()):
            run(rom,5400,folder,captures,([(200,220,0)] if tag=='sms' else [])+PRESSES[:8],
                skip_intro=True,ram_writes=writes,ram_observer=observe,input_provider=controller,
                stop_when=lambda:done is not None and observed>=done+60,
                core_options={'genesis_plus_gx_region_detect':'pal' if a.pal else 'auto'})
        final={k:v for k,v in state.items() if k!='tilemap'}
        visited=sorted({e['room'] for e in events})
        result=dict(rom_sha256=sha(rom.read_bytes()),visited=visited,final=final,events=events)
        (folder/'observations.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
        (folder/'controls.json').write_bytes((json.dumps(controls,indent=2)+'\n').encode())
        results[tag]=result
        print(tag,'visited',[hex(r) for r in visited],'oil',final['oil'],'final',hex(final['room']),flush=True)
    assert 0xf in results['sms']['visited'] and results['sms']['final']['oil'] == 1
    if a.expect_blocked:
        assert 0xf not in results['md']['visited'] and not results['md']['final']['oil']
    else:
        assert 0xf in results['md']['visited'] and results['md']['final']['oil'] == 1
        assert results['sms']['final']['room'] == results['md']['final']['room'] == 0xc7
        assert results['sms']['final']['outside'] == results['md']['final']['outside'] == 0xc7
        assert results['sms']['final']['flags'] == results['md']['final']['flags']
    report=dict(passed=True,baseline_block_reproduced=a.expect_blocked,controlled_pose_fixture=True,
                actual_c7_door_used=True,post_door_outside_context_mutation=False,
                inventory_or_actor_fixtures=False,region='pal' if a.pal else 'auto',results=results,
                limits=['Controlled real exterior doorway and one interior pose fixture;not a natural whole-world route.',
                        'Normal walking,scrolling,oil interaction and return run unmodified. Exact global phase/audio/whole-frame fidelity is not asserted.'])
    (base/'report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())


if __name__ == '__main__':
    main()
