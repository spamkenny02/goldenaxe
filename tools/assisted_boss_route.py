"""Test-only invulnerability on the approach; ordinary damage during the boss.

This deliberately injects RAM and must never be labelled a natural campaign.
The released ROM is not patched. The boss planner starts after assistance ends.
"""
import argparse
import json
import sys
from pathlib import Path

import natural_combat_beam as beam
from run_core import ROOT
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha
from assisted_prefix import prefix_writes, recording


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--boss-room', type=lambda value: int(value, 0), required=True)
    parser.add_argument('--planner', choices=['beam', 'navigation', 'ordinary', 'side', 'escape'], default='beam')
    parser.add_argument('--boss-frames', type=int, help='Bound this diagnostic after normal combat starts')
    parser.add_argument('--world-route', action='store_true', help='Apply the same guard to an exterior route')
    args, remaining = parser.parse_known_args()
    sms = '--sms' in remaining
    assert not sms or args.planner in ('ordinary', 'beam', 'navigation'), 'Side/escape wrappers currently write MD report paths'
    assert '--lookahead-rooms' not in remaining, 'Planning is restricted to the unassisted boss'
    assert args.boss_frames is None or args.boss_frames > 0
    if args.world_route:
        choices = [('--prefix-service', 'natural-service-route'), ('--prefix-combat', 'natural-dungeon-combat')]
        flag, family = next((flag, family) for flag, family in choices if flag in remaining)
    else:
        flag = '--continuation' if '--continuation' in remaining else '--prefix'
        family = 'natural-dungeon-combat' if flag == '--continuation' else 'natural-dungeon-route'
    name = remaining[remaining.index(flag) + 1]
    prefix_folder = ROOT / 'validation' / family / name
    prefix = json.loads((prefix_folder / 'capture.json').read_bytes())
    writes = list(prefix_writes(prefix_folder, prefix, '--assisted-prefix' in remaining))
    inherited = recording(prefix_folder, prefix)[0] if prefix['test_ram_writes'] else None
    assert not inherited or inherited['boss_room'] == args.boss_room, 'A new boss requires a separate assistance episode'
    start = prefix['frames']
    sy = None if sms else symbols(ROOT / 'megadrive/out/release/symbol.txt')
    hurt_address = 0x305 if sms else sy['hero_hurt']
    zero, guard = (b'\x00', b'\x81') if sms else (b'\x00\x00', b'\x00\x81')
    if args.world_route:
        import natural_dungeon_route as game
    else:
        game = beam.generic.base.game
    original = game.run
    original_walk = getattr(game, 'walk', None)
    approach_active = False
    result = dict(assisted_route=True, ram_injections=True, rom_modifications=False,
                  invulnerability_value=129, health_refills=0,
                  activation_after_frame=start, boss_room=args.boss_room,
                  first_boss_entry=None, release_write_frame=None,
                  first_boss_combat=None, first_boss_damage=None,
                  primary_state_imports=0, boss_assistance=False)
    result.update(prefix_trace=prefix_folder.relative_to(ROOT / 'validation').as_posix(),
                  prefix_capture_sha256=sha((prefix_folder / 'capture.json').read_bytes()),
                  stage_activation_after_frame=start)
    if inherited:
        for key in ['activation_after_frame', 'first_boss_entry', 'release_write_frame', 'first_boss_combat', 'first_boss_damage']:
            result[key] = inherited[key]
    previous_health = None
    folder = None
    driver = Path(__file__).read_bytes()

    def wrapped(*run_args, **kwargs):
        nonlocal folder
        folder = Path(run_args[2])
        assert list(kwargs.get('ram_writes', ())) == writes
        observer = kwargs['ram_observer']
        stop = kwargs.get('stop_when')
        boss_budget_done = False
        budget_deadline = None

        def observe(frame, ram):
            nonlocal previous_health, approach_active, boss_budget_done, budget_deadline
            if sms:
                fields = dict(room_id=int.from_bytes(ram[0xb9:0xbb], 'little'), game_state=ram[0x1d],
                              hero_health=ram[0x318], hero_hurt=ram[0x305])
                word = lambda name: fields[name]
            else:
                word = lambda name: int.from_bytes(bytes(ram[(sy[name] + i) ^ 1] for i in range(2)), 'big')
            room, state, health, hurt = (word(name) for name in
                                       ['room_id', 'game_state', 'hero_health', 'hero_hurt'])
            if frame >= start:
                if room == args.boss_room and result['first_boss_entry'] is None:
                    # Room changes during scrolling, before normal boss simulation.
                    assert state != 12, 'Boss combat began before invulnerability was released'
                    result['first_boss_entry'] = dict(frame=frame, game=state, health=health, hurt=hurt)
                    result['release_write_frame'] = frame + 1
                    writes.append((frame + 1, hurt_address, zero))
                elif result['first_boss_entry'] is None:
                    # The contact pass also collects dropped keys. Release the
                    # guard after the last enemy/projectile so loot still works.
                    actor = (lambda slot, offset: ram[0x600 + slot * 48 + offset]) if sms else (
                        lambda slot, offset: ram[(sy['world_actor_state'] + slot * 48 + offset) ^ 1])
                    danger = any(actor(slot, 0) >= 0x10 and actor(slot, 3) & 2 for slot in range(16))
                    writes.append((frame + 1, hurt_address, guard if danger else zero))
                approach_active = result['first_boss_entry'] is None
                if room == args.boss_room and state == 12:
                    assert result['release_write_frame'] < frame
                    if result['first_boss_combat'] is None:
                        assert hurt == 0, ('Invulnerability remained active', frame, hurt)
                        result['first_boss_combat'] = dict(frame=frame, health=health, hurt=hurt)
                    if previous_health is not None and health < previous_health and result['first_boss_damage'] is None:
                        result['first_boss_damage'] = dict(frame=frame, before=previous_health, after=health, hurt=hurt)
                previous_health = health
            observer(frame, ram)
            first = result['first_boss_combat']
            if args.boss_frames and first and budget_deadline is None:
                budget_deadline = max(start, first['frame']) + args.boss_frames
                result['boss_budget_deadline'] = budget_deadline
                run_args[3].add(budget_deadline)
            if budget_deadline is not None and frame >= budget_deadline:
                boss_budget_done = True
                result['test_stop_reason'] = 'boss_frame_budget'

        kwargs.update(ram_writes=writes, ram_observer=observe,
                      stop_when=lambda: boss_budget_done or bool(stop and stop()))
        return original(*run_args, **kwargs)

    game.run = wrapped
    def walk(tilemap, start, goal, enemies=(), geometry=False):
        return original_walk(tilemap, start, goal, () if approach_active else enemies, geometry)
    if original_walk is not None:
        game.walk = walk
    sys.argv = [sys.argv[0]] + ([] if args.world_route or args.planner == 'ordinary' else
                               ['--lookahead-rooms', hex(args.boss_room)]) + remaining
    try:
        if args.world_route:
            game.main()
        elif args.planner == 'escape':
            import natural_boss_escape_planner
            natural_boss_escape_planner.main()
        elif args.planner == 'side':
            import natural_boss_side_planner
            natural_boss_side_planner.main()
        elif args.planner == 'navigation':
            import natural_combat_navigation
            natural_combat_navigation.main()
        elif args.planner == 'ordinary':
            game.main()
        else:
            beam.main()
    finally:
        game.run = original
        if original_walk is not None:
            game.walk = original_walk
        if folder is not None:
            result.update(driver_sha256=sha(driver), planner=args.planner,
                          writes=[dict(frame=f, address=a, data_hex=data.hex()) for f, a, data in writes])
            (folder / 'assisted_route_driver.py').write_bytes(driver)
            if result['release_write_frame'] is not None:
                assert all(f <= result['release_write_frame'] for f, _, _ in writes)
            (folder / 'assistance.json').write_text(json.dumps(result, indent=2) + '\n')
            path = folder / ('route_report.json' if args.world_route else 'report.json')
            if path.exists():
                report = json.loads(path.read_bytes())
                report.update(assisted_route=True, ram_injections=True, boss_assistance=False,
                              primary_extra_state_writes=len(writes),
                              assistance_manifest='assistance.json', natural_campaign_proof=False)
                path.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
