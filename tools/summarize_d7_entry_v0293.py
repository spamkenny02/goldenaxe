"""Extend evidence to D6 stack depth and the ordinary D7 approach."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    refs = {}
    def read(name):
        raw = evidence(ROOT / name); refs[name] = sha(raw); return raw
    def load(name):
        return json.loads(read(name))
    digest = sha(read('gaw-megadrive.bin'))
    campaign = load('analysis/d6_campaign_v0293_report.json')
    assert campaign['passed'] and campaign['md_sha256'] == digest and campaign['dungeon6_completed']
    exit_root = 'validation/natural-dungeon-combat/md-auto-v0293-d6-exit03'
    stack_root = 'validation/stack-v0293-d6-exit-all02'
    s = load(stack_root + '/stack_report.json')
    assert s['md_sha256'] == digest and s['frames'] == campaign['frames'] == 151975
    assert s['all_instructions'] and s['read_only'] and s['logged_assistance_replayed'] and not s['invalid_heap_examples']
    minimum = min(x['sp'] for x in s['instruction_minima'])
    boundary = max(x['end'] + 2 for x in s['heap_changes'])
    assert minimum >= boundary
    for stem, ext in [('ram','bin'), ('frame','png')]:
        assert read(stack_root + f'/{stem}_151975.{ext}') == read(exit_root + f'/{stem}_151975.{ext}')
    root = 'validation/natural-dungeon-route/md-v0293-d7-route01'
    c = load(root + '/capture.json'); r = load(root + '/route_report.json')
    p = load(root + f'-assisted-fixed-replay-{c["frames"]}/replay_report.json')
    assert c['rom_sha256'] == p['rom_sha256'] == digest and c['sram_input'] is None
    assert p['passed'] and p['whole_ram_bytes'] == 65536 and p['final_png_exact'] and not p['feedback_reads']
    for name, expected in p['evidence'].items():
        assert sha(read(root + '/' + name)) == expected
    ec = load(exit_root + '/capture.json')
    _, ew = recording(ROOT / exit_root, ec)
    _, w = recording(ROOT / root, c)
    assert w == ew
    assert r['failure'] is None and r['reached_entrance'] and r['door_index'] == 7
    assert r['directional_probe_succeeded'] and r['rendered_final_frame_nonblack'] and not r['normal_continues']
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    raw = read(root + f'/ram_{c["frames"]:05d}.bin'); read(root + f'/frame_{c["frames"]:05d}.png')
    data = lambda name, n: bytes(raw[(sy[name]+i)^1] for i in range(n))
    word = lambda name: int.from_bytes(data(name,2),'big')
    assert word('room_id') == 0x1db and word('world_dungeon_number') == 7
    assert word('hero_health') == 16 and word('hero_max_health') == 80 and word('game_state') == 12
    assert data('game_save_state',592)[0x1f:0x25] == bytes([128]*6)
    assert data('hero_items',17)[10] == 1 and not word('sound_unhandled_command')
    for name in ['summarize_d7_entry_v0293.py', 'natural_dungeon_route.py', 'profile_playable_stack.py', 'replay_assisted_prefix.py']:
        read('tools/'+name)
    result = dict(passed=True, version=293, md_sha256=digest, production_rom_unchanged=True,
                  native_six_crystals=True, dungeon7_entered=True, dungeon7_completed=False,
                  frames=c['frames'], room=0x1db, health=16, max_health=80,
                  new_approach_assistance_writes=0, cold_replay=True, whole_ram_bytes=65536, final_png_exact=True,
                  stack=dict(frames=s['frames'], all_instructions=True, minimum_sp=minimum,
                             heap_boundary=boundary, observed_margin_bytes=minimum-boundary,
                             heap_valid=True, whole_ram_png_exact=True), evidence=refs,
                  full_game_validated=False, source_campaign_compared=False,
                  limits=['Historical hurt-counter help is retained on earlier approaches; the exterior route after D6 adds no help. D7 arrival has16HP and no claimed dungeon completion.',
                          'Stack observation covers this cold route through D6 exit, not all future paths. Ordinary m68k instructions are observed after initialization from frame14.',
                          'Original SMS full campaign, all intermediate images, audio waves, hardware timing, dungeons7-10 and ending remain unproven.'])
    (ROOT/'analysis/d7_entry_v0293_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('D7 entered with16/80HP, exact replay, no new aid; D6 all-instruction stack margin',minimum-boundary)


if __name__ == '__main__':
    main()
