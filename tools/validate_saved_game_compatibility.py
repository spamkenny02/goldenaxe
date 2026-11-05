"""Cold-load an actual previously verified game-written save on another build."""
import argparse, contextlib, io, json
from pathlib import Path
from run_core import ROOT, run
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated
from natural_dungeon_combat import walk


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace', type=Path, default=ROOT)
    p.add_argument('--source-report', type=Path, required=True)
    p.add_argument('--trial', required=True)
    p.add_argument('--pal', action='store_true')
    a = p.parse_args(); project = a.workspace.resolve()
    donor_path = a.source_report.resolve(); donor = json.loads(donor_path.read_bytes())
    assert donor['passed'] and donor['game_written_save'] and not donor['synthetic_sram_fixture']
    assert donor['raw_sram_fixed_replay_exact'] and donor['save_whole_ram_png_exact']
    service = ROOT/'validation'/donor['source_trace']
    service_report = json.loads((service/'report.json').read_bytes())
    sram = ROOT/service_report['sram_file']; payload = (service/'serialized-payload.bin').read_bytes()
    assert sha(sram.read_bytes()) == donor['source_sram_sha256'] == service_report['sram_sha256']
    assert len(payload) == 592 and sha(payload) == service_report['serialized_payload_sha256']
    assert sram.read_bytes()[1::2].ljust(8192, b'\xff')[0x400:0x650] == payload
    rom = project/'gaw-megadrive.bin'; sy = symbols(project/'megadrive/out/release/symbol.txt')
    target = int.from_bytes(payload[0x12:0x14], 'little')
    out = project/'validation/save-compatibility'/(a.trial+('-pal' if a.pal else '-ntsc'))
    assert not out.exists()
    fields = {'hero_health':0x29,'hero_max_health':0x2a,'hero_magic':0x2b,
              'hero_max_magic':0x2c,'hero_gold':0x2d,'hero_keys':0x2e,
              'hero_selected_item':0x2f,'hero_basic_level':0x30,'hero_weapon_level':0x31,
              'hero_armor_level':0x41,'hero_shield_level':0x42}
    state = {}; controls = []; ready = None; moved = None; origin = None; direction = None
    captures = set()
    def reader(raw):
        def data(n, count): return bytes(raw[(sy[n]+i)^1] for i in range(count))
        return data, lambda n: int.from_bytes(data(n, 2), 'big')
    def observe(frame, raw):
        nonlocal ready, moved, origin
        data, word = reader(raw)
        state.update(room=word('room_id'), game=word('game_state'), hero=word('hero_state'),
                     counter=word('hero_counter'), x=word('hero_x')>>8, y=word('hero_y')>>8,
                     health=word('hero_health'), hurt=word('hero_hurt'),
                     tilemap=data('sms_vram',16384)[0x3800:0x3e00])
        assert not word('sound_unhandled_command')
        if ready is None and state['game'] == 12 and state['hero'] == 1 and state['room'] == target:
            for name, offset in fields.items(): assert word(name) == payload[offset], name
            assert data('hero_items',17) == payload[0x30:0x41]
            assert data('game_save_state',592)[0x1f:0x28] == payload[0x1f:0x28]
            assert state['health'] and state['hurt'] <= 128
            ready = frame; origin = state['x'], state['y']; captures.add(frame+1)
        if ready is not None:
            assert state['health'] and state['game'] != 20 and state['hurt'] <= 128
            if moved is None and state['game'] == 12 and state['hero'] == 1 and not state['counter'] and state['room'] == target:
                if abs(state['x']-origin[0])+abs(state['y']-origin[1]) >= 8:
                    moved = frame; captures.add(frame+100)
    def choose(frame):
        nonlocal direction
        if ready is None:
            if 200 <= frame <= 220 or 920 <= frame <= 935: return [0]
            if 1050 <= frame <= 1065 or 1300 <= frame <= 1310: return [8]
            return []
        if moved is not None or state['room'] != target or state['game'] != 12 or state['hero'] not in (0,1): return []
        if state['counter']: return [4+direction] if direction is not None else []
        at = state['x'], state['y']
        if at != origin: return []
        if direction is None:
            for dx, dy in ((0,-8),(0,8),(-8,0),(8,0)):
                point = at[0]+dx, at[1]+dy
                if not (16 <= point[0] <= 240 and 16 <= point[1] <= 160): continue
                route = walk(state['tilemap'], at, lambda q: q == point)
                if route and len(route) == 1:
                    direction = route[0]; break
        return [4+direction] if direction is not None else []
    def provider(frame):
        buttons = choose(frame)
        if not controls or controls[-1]['buttons'] != buttons:
            controls.append(dict(frame=frame, buttons=buttons))
        return buttons
    options = {'genesis_plus_gx_region_detect':'pal' if a.pal else 'auto'}
    with contextlib.redirect_stdout(io.StringIO()):
        run(rom,1800,out,captures,[],skip_intro=False,sram_in=sram,
            core_options=options,ram_observer=observe,input_provider=provider)
    assert ready is not None and moved is not None
    frame = max(captures); raw = (out/f'ram_{frame:05d}.bin').read_bytes()
    data, _ = reader(raw); sms = data('sms_vram',16384)
    vram = (out/f'vram_{frame:05d}.bin').read_bytes(); regs = (out/f'vdp_regs_{frame:05d}.bin').read_bytes()
    base = (regs[2]&56)<<10; width = [32,64,32,128][regs[16]&3]
    for n in range(128):
        at = base+((n//32+22)*width+n%32)*2
        assert int.from_bytes(vram[at:at+2],'little') == translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
    original = (ROOT/'input/original.sms').read_bytes(); markers = 0
    for n, gem in enumerate(payload[0x1f:0x28]):
        if gem:
            tile, off = original[0x1edc+n*2:0x1ede+n*2]
            assert sms[0x3d00+off:0x3d02+off] == bytes([tile,0x59]); markers += 1
    (out/'controls.json').write_text(json.dumps(controls)+'\n',encoding='utf-8')
    result = dict(passed=True, md_sha256=sha(rom.read_bytes()), donor_rom_sha256=donor['rom_sha256'],
        source_report=donor_path.relative_to(ROOT).as_posix(), source_report_sha256=sha(donor_path.read_bytes()),
        source_sram_sha256=sha(sram.read_bytes()), synthetic_sram_fixture=False,
        region='pal' if a.pal else 'ntsc', source_payload_bytes=592,
        restored_source_fields=fields, items_and_crystals_restored=True, normal_continue=True,
        initial_sram_imports=1, ram_writes=0, actors_cleared=False,
        ready_frame=ready, movement_frame=moved, checkpoint_room=target,
        physical_hud_words_exact=128, source_crystal_markers_exact=markers,
        core_sha256=sha((ROOT.parents[1]/'work/libretro/genesis_plus_gx_libretro.dll').read_bytes()),
        driver_sha256=sha(Path(__file__).read_bytes()), full_game_validated=False,
        limits=['This is normal Continue from an actual earlier-build save, not a new-game campaign or proof of save writing on the receiving build.',
                'Slot0 compatibility, restored fields, inventory, crystal markers, physical HUD and movement only; other slots and hardware remain outside this proof.'])
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Saved-game compatibility verified:', result['region'], 'ready', ready, 'movement', moved)


if __name__ == '__main__': main()
