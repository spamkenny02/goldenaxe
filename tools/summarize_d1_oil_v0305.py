"""Audit the current-ROM Oil -> first crystal -> exterior cold campaign."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    refs = {}
    def read(name):
        raw = evidence(ROOT / name)
        refs[name] = sha(raw)
        return raw
    def load(name):
        return json.loads(read(name))
    digest = sha((ROOT/'gaw-megadrive.bin').read_bytes())
    prior = load('analysis/indoor_stairs_v0305_report.json')
    assert prior['passed'] and prior['md_sha256'] == digest and prior['natural_oil_and_exterior_return']
    sy = symbols(ROOT/'megadrive/out/release/symbol.txt')
    stages = []
    latest_writes = []
    for family, name, kind in [
        ('natural-dungeon-route','md-v0305-d1-route-oil01','entry'),
        ('natural-dungeon-combat','md-auto-v0305-d1-oil-key01','key'),
        ('natural-dungeon-combat','md-auto-v0305-d1-oil-boss01','crystal'),
        ('natural-dungeon-combat','md-auto-v0305-d1-oil-exit01','exit')]:
        root = f'validation/{family}/{name}'
        c = load(root+'/capture.json')
        r = load(root+('/route_report.json' if kind == 'entry' else '/report.json'))
        f = c['frames']
        assert c['rom_sha256'] == r['rom_sha256'] == digest and c['sram_input'] is None
        assert r['failure'] is None and not r['sram_checkpoint_injection']
        if kind == 'entry':
            proof = root+'-fixed-replay'
            assert not c['test_ram_writes'] and r['reached_entrance'] and r['directional_probe_succeeded']
            assert not r['normal_continues'] and r['recorded_service_prefix'] == 'md-v0305-oil-stairs02'
        else:
            a, writes = recording(ROOT/root,c)
            read(root+'/assistance.json')
            assert a['boss_room'] == 0x175 and len(a['episodes']) == 1
            assert not a['health_refills'] and not a['primary_state_imports'] and not a['boss_assistance']
            assert a['activation_after_frame'] == stages[0]['frames']
            assert all(addr == sy['hero_hurt'] for _,addr,_ in writes)
            assert writes[:len(latest_writes)] == latest_writes
            if kind == 'exit':
                assert writes == latest_writes and r['dungeon_exit_verified'] and r['full_dungeon_cleared']
                assert a['unassisted_extension'] and not a['new_assistance_writes']
            latest_writes = writes
            assert not r['deaths'] and r['room_cleared']
            if kind == 'key':
                assert r['new_key_verified'] and r['last_state']['keys'] == 1
                assert a['first_boss_entry'] is None and a['first_boss_combat'] is None
            else:
                first = a['first_boss_combat']
                assert first == dict(frame=14907,health=24,hurt=0)
                assert writes[-1][0] == a['release_write_frame'] == 14835
                assert writes[-1][2] == b'\0\0' and a['release_write_frame'] < first['frame']
                assert r['last_state']['first_gem'] == 128
                assert r['last_state']['max_health'] == 32
            proof = root+f'-assisted-fixed-replay-{f}'
        p = load(proof+'/replay_report.json')
        assert p['passed'] and p['rom_sha256'] == digest and p['whole_ram_bytes'] == 65536
        assert p['final_png_exact'] and not p['feedback_reads']
        for n,h in p['evidence'].items():
            assert sha(read(root+'/'+n)) == h
        raw = read(root+f'/ram_{f:05d}.bin')
        for stem,ext in [('ram','bin'),('frame','png')]:
            file = f'/{stem}_{f:05d}.{ext}'
            assert read(root+file) == read(proof+file)
        data = lambda n,k: bytes(raw[(sy[n]+i)^1] for i in range(k))
        word = lambda n: int.from_bytes(data(n,2),'big')
        assert data('hero_items',17)[8] == 1
        assert data('game_save_state',592)[0x117] & 2
        assert word('sound_unhandled_command') == 0
        if kind == 'crystal':
            plan = load(root+'/planning_partial.json')
            assert plan['verified_windows'] == plan['full_ram_matches'] == 31
            assert not plan['stack_only_difference_windows'] and not plan['primary_state_imports']
            assert word('room_id') == 0x175 and word('hero_health') == 32
        if kind == 'exit':
            assert word('room_id') == 0xb9 and word('hero_health') == 28
            assert not word('world_dungeon_number') and word('game_state') == 12
            assert r['last_state']['completed_dungeon_progress'] == 128
        stages.append(dict(trace=root,kind=kind,frames=f,room=word('room_id'),
                           health=word('hero_health'),max_health=word('hero_max_health'),
                           oil_owned=True,whole_ram_png_exact=True,approach_assisted=kind!='entry'))
    stack = 'validation/stack-v0305-d1-oil-all'
    s = load(stack+'/stack_report.json')
    assert s['md_sha256'] == digest and s['frames'] == stages[-1]['frames']
    assert s['read_only'] and s['all_instructions'] and s['logged_assistance_replayed']
    assert not s['invalid_heap_examples']
    assert s['minimum_instruction_sp'] == min(x['sp'] for x in s['instruction_minima'])
    assert s['minimum_sp'] == min(s['minimum_instruction_sp'],s['minimum_sampled_sp'])
    boundary = max(x['end']+2 for x in s['heap_changes'])
    margin = s['minimum_sp']-boundary
    assert margin == 466
    for stem,ext in [('ram','bin'),('frame','png')]:
        file = f'/{stem}_{s["frames"]:05d}.{ext}'
        assert read(stack+file) == read(stages[-1]['trace']+file)
    read('tools/summarize_d1_oil_v0305.py')
    result = dict(passed=True,version=305,md_sha256=digest,production_rom_unchanged=True,
                  first_crystal_and_exterior_return=True,oil_preserved=True,stages=stages,
                  boss_guard_release=14835,first_boss_combat=14907,boss_start_health=24,
                  boss_prediction_windows=31,boss_full_ram_matches=31,
                  instruction_stack_margin_bytes=margin,stack_frames=s['frames'],
                  full_game_validated=False,evidence=refs,limits=[
                      'New-game C7 stairs/Oil prefix is unassisted. First dungeon approach is explicitly assisted through only the hero_hurt field;no HP,inventory,actor or progression fixtures.',
                      'Protection ends72 frames before first main-boss simulation. No new assistance during the boss or exterior return. Whole65536RAM and finalPNG cold replay is exact for all four stages.',
                      'First crystal and return only on v305. Historical v304 seven-crystal/thief-key progress is not promoted. Later campaign,ending,saves,source RNG/global phase and complete SMS audio/video/hardware fidelity remain unproved.',
                      'Instruction-stack profile covers17482 frames of this recorded branch,not every game path.'])
    (ROOT/'analysis/d1_oil_v0305_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print('v305 Oil retained,first crystal and B9 return:four cold RAM/PNG replays exact;observed stack margin466 bytes')


if __name__ == '__main__':
    main()
