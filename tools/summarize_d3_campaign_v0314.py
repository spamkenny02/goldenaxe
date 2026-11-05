"""Audit v314's third crystal, unprotected boss69 and exterior return."""
import json
from pathlib import Path

from archive_lossless_evidence import sha
from assisted_prefix import prefix_writes, recording
from run_core import ROOT
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated


def main():
    references = {}

    def read(name):
        raw = (ROOT / name).read_bytes()
        references[name] = sha(raw)
        return raw

    def load(name):
        return json.loads(read(name))

    digest = sha((ROOT / 'gaw-megadrive.bin').read_bytes())
    assert digest == 'c53381c459a1e6254a8c9f1cfad1b8cda482cc0614697ad566133b28335e07a7'
    prior = load('analysis/d3_progress_v0314_report.json')
    assert prior['passed'] and prior['md_sha256'] == digest
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    original=read('input/original.sms')
    assert original[0x3234e+0x1c3*8]==0x69 and original[0x320ea+(0x69-0x20)*4]==32
    source_root='validation/v0314-d3-sources02'
    source_index=load(source_root+'/source_index.json')
    for name,digest_source in source_index.items():
        assert sha(read(source_root+'/'+name.split('/')[-1]))==digest_source

    # Verify the early release as its own actual checkpoint before any boss inputs.
    pre_root='validation/natural-dungeon-combat/md-auto-v0314-d3-pre-boss01'
    rel_root='validation/natural-dungeon-combat/md-auto-v0314-d3-release01'
    pc=load(pre_root+'/capture.json');pr=load(pre_root+'/report.json')
    rc=load(rel_root+'/capture.json');rr=load(rel_root+'/report.json')
    pa,pw=recording(ROOT/pre_root,pc);ra,rw=recording(ROOT/rel_root,rc)
    assert pr['failure'] is None and pr['room_cleared'] and pr['last_state']['room']==0x1d3
    assert rr['passed'] and ra['closed_before_room']==0x1c3 and ra['first_boss_entry'] is None
    assert rc['frames']==pc['frames']+1 and rw==pw+[(rc['frames'],sy['hero_hurt'],b'\0\0')]
    for name,c in [(pre_root,pc),(rel_root,rc)]:
        f=c['frames'];q=name+f'-assisted-fixed-replay-{f}';proof=load(q+'/replay_report.json')
        assert c['rom_sha256']==digest and c['sram_input'] is None
        assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads']
        for stem,extension in [('ram','bin'),('frame','png')]:
            filename=f'/{stem}_{f:05d}.{extension}';assert read(name+filename)==read(q+filename)
    released=read(rel_root+f'/ram_{rc["frames"]:05d}.bin')
    def release_word(n):return int.from_bytes(bytes(released[(sy[n]+i)^1]for i in range(2)),'big')
    assert release_word('room_id')==0x1d3 and release_word('hero_hurt')==0

    stages, first_writes, combat, release, damage = [], None, None, None, None
    for kind in ('boss', 'exit'):
        root = f'validation/natural-dungeon-combat/md-auto-v0314-d3-{kind}01'
        capture, report = load(root + '/capture.json'), load(root + '/report.json')
        end = capture['frames']
        replay = root + f'-assisted-fixed-replay-{end}'
        proof = load(replay + '/replay_report.json')
        assist, writes = recording(ROOT / root, capture)
        read(root + '/assistance.json')
        assert prefix_writes(ROOT / root, capture, True) == writes
        assert capture['rom_sha256'] == proof['rom_sha256'] == digest
        assert capture['sram_input'] is None and not assist['primary_state_imports']
        assert not assist['boss_assistance'] and not assist['health_refills']
        assert len(assist['episodes']) == 3 and assist['boss_room'] == 0x1c3
        assert all(address == sy['hero_hurt'] for _, address, _ in writes)
        assert assist['release_write_frame'] < assist['first_boss_combat']['frame']
        assert assist['first_boss_combat']['hurt'] == 0
        assert max(frame for frame, _, _ in writes) == assist['release_write_frame'] == rc['frames']
        assert writes==rw
        assert report['failure'] is None and not report['deaths']
        assert proof['passed'] and proof['whole_ram_bytes'] == 65536
        assert proof['final_png_exact'] and not proof['feedback_reads']
        for name, expected in proof['evidence'].items():
            assert sha(read(root + '/' + name)) == expected
        for stem, extension in [('ram', 'bin'), ('frame', 'png')]:
            name = f'/{stem}_{end:05d}.{extension}'
            assert read(root + name) == read(replay + name)
        raw = read(root + f'/ram_{end:05d}.bin')
        data = lambda name, size: bytes(raw[(sy[name] + i) ^ 1] for i in range(size))
        word = lambda name: int.from_bytes(data(name, 2), 'big')
        save, items = data('game_save_state', 592), data('hero_items', 17)
        assert save[0x1f:0x28] == bytes([128] * 3 + [0] * 6)
        assert items[8] == items[13] == 1
        assert word('hero_max_health') == 56 and word('hero_health') > 0
        assert word('hero_selected_item') == word('hero_weapon_level') == 1
        assert word('sound_unhandled_command') == 0 and word('game_state') == 12
        if kind == 'boss':
            assert report['room_cleared'] and word('room_id') == 0x1c3
            assert report['planning_step'] == 16 and report['full_ram_prediction_matches'] == report['verified_persistent_prediction_windows'] > 0
            assert not report['stack_only_difference_windows']
            events = load(root + '/events.json')
            assert any(event.get('room') == 0x1c3 and any(
                actor['type'] == 0x69 and actor['hp'] == 32 for actor in event.get('actors', [])) for event in events)
            first_writes = writes
            damage = report['first_extension_damage']
            combat, release = assist['first_boss_combat'], assist['release_write_frame']
        else:
            assert writes == first_writes and assist['first_boss_combat'] == combat
            assert report['full_dungeon_cleared'] and report['dungeon_exit_verified']
            assert report['unassisted_extension'] and report['new_assistance_writes'] == 0
            assert word('room_id') == 0x62 and word('world_dungeon_number') == 0
        sms = data('sms_vram', 16384)
        vram = read(root + f'/vram_{end:05d}.bin')
        regs = read(root + f'/vdp_regs_{end:05d}.bin')
        base, width = (regs[2] & 56) << 10, [32, 64, 32, 128][regs[16] & 3]
        for n in range(128):
            at = base + ((n // 32 + 22) * width + n % 32) * 2
            assert int.from_bytes(vram[at:at+2], 'little') == translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2], 'little'))
        source = (ROOT / 'input/original.sms').read_bytes()
        for n in range(3):
            tile, offset = source[0x1edc+n*2:0x1ede+n*2]
            assert sms[0x3d00+offset:0x3d02+offset] == bytes([tile, 0x59])
        stages.append(dict(kind=kind, trace=root, frames=end, room=word('room_id'),
                           health=word('hero_health'), max_health=word('hero_max_health'),
                           keys=word('hero_keys'), crystals=3, rope_owned=True, oil_owned=True,
                           whole_ram_bytes=65536, final_png_exact=True,
                           prediction_windows=report.get('full_ram_prediction_matches', 0)))
    result = dict(passed=True, version=314, md_sha256=digest, production_rom_unchanged=True,
                  cold_new_game_chain=True, three_crystals_and_exterior_return=True,
                  boss_type=0x69, source_boss_initial_hp=32, guard_release_frame=release,
                  first_boss_combat=combat, observed_boss_damage=damage, boss_assistance=False, resource_writes=0,
                  primary_state_imports=0, exit_new_assistance_writes=0,
                  physical_hud_words_exact_each=128, crystal_markers_exact_each=3,
                  stages=stages, full_game_validated=False, evidence=references,
                  driver_sha256=sha(Path(__file__).read_bytes()),
                  limits=['One NTSC campaign with explicit approach-only hurt writes; ordinary unprotected boss combat.',
                          'The verified key01 route passes the opened mechanism without deleting actors. The boss receives ordinary controls, with a separately verified early guard release in1D3.',
                          'D4 onward on this ROM, global source R/IRQ, complete audiovisual/optional coverage and console hardware remain unverified.'])
    (ROOT / 'analysis/d3_campaign_v0314_report.json').write_bytes((json.dumps(result, indent=2) + '\n').encode())
    print('v314 third crystal and exterior return audited:', stages[-1]['frames'])


if __name__ == '__main__':
    main()
