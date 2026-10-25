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


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--boss-room', type=lambda value: int(value, 0), required=True)
    parser.add_argument('--planner', choices=['beam', 'navigation', 'ordinary', 'side', 'escape'], default='beam')
    parser.add_argument('--boss-frames', type=int, help='Bound this diagnostic after normal combat starts')
    args, remaining = parser.parse_known_args()
    assert '--sms' not in remaining, 'This test helper currently supports native MD RAM only'
    assert '--lookahead-rooms' not in remaining, 'Planning is restricted to the unassisted boss'
    flag = '--continuation' if '--continuation' in remaining else '--prefix'
    name = remaining[remaining.index(flag) + 1]
    family = 'natural-dungeon-combat' if flag == '--continuation' else 'natural-dungeon-route'
    prefix = json.loads((ROOT / 'validation' / family / name / 'capture.json').read_bytes())
    assert not prefix['test_ram_writes'], 'Use a verified unassisted prefix'
    start = prefix['frames']
    sy = symbols(ROOT / 'megadrive/out/release/symbol.txt')
    game = beam.generic.base.game
    original = game.run
    original_walk = game.walk
    approach_active = False
    writes = []
    result = dict(assisted_route=True, ram_injections=True, rom_modifications=False,
                  invulnerability_value=129, health_refills=0,
                  activation_after_frame=start, boss_room=args.boss_room,
                  first_boss_entry=None, release_write_frame=None,
                  first_boss_combat=None, first_boss_damage=None,
                  primary_state_imports=0, boss_assistance=False)
    previous_health = None
    folder = None
    driver = Path(__file__).read_bytes()

    def wrapped(*run_args, **kwargs):
        nonlocal folder
        folder = Path(run_args[2])
        assert not kwargs.get('ram_writes')
        observer = kwargs['ram_observer']
        stop = kwargs.get('stop_when')
        boss_budget_done = False

        def observe(frame, ram):
            nonlocal previous_health, approach_active, boss_budget_done
            word = lambda name: int.from_bytes(bytes(ram[(sy[name] + i) ^ 1] for i in range(2)), 'big')
            room, state, health, hurt = (word(name) for name in
                                       ['room_id', 'game_state', 'hero_health', 'hero_hurt'])
            if frame >= start:
                if room == args.boss_room and result['first_boss_entry'] is None:
                    # Room changes during scrolling, before normal boss simulation.
                    assert state != 12, 'Boss combat began before invulnerability was released'
                    result['first_boss_entry'] = dict(frame=frame, game=state, health=health, hurt=hurt)
                    result['release_write_frame'] = frame + 1
                    writes.append((frame + 1, sy['hero_hurt'], b'\x00\x00'))
                elif result['first_boss_entry'] is None:
                    # The contact pass also collects dropped keys. Release the
                    # guard after the last enemy/projectile so loot still works.
                    actor = lambda slot, offset: ram[(sy['world_actor_state'] + slot * 48 + offset) ^ 1]
                    danger = any(actor(slot, 0) >= 0x10 and actor(slot, 3) & 2 for slot in range(16))
                    writes.append((frame + 1, sy['hero_hurt'], b'\x00\x81' if danger else b'\x00\x00'))
                approach_active = result['first_boss_entry'] is None
                if room == args.boss_room and state == 12:
                    assert result['release_write_frame'] < frame
                    if result['first_boss_combat'] is None:
                        assert hurt == 0, ('Invulnerability remained active', frame, hurt)
                        result['first_boss_combat'] = dict(frame=frame, health=health, hurt=hurt)
                        if args.boss_frames:
                            # Video callback runs before the RAM observer.
                            run_args[3].add(frame + args.boss_frames)
                    if previous_health is not None and health < previous_health and result['first_boss_damage'] is None:
                        result['first_boss_damage'] = dict(frame=frame, before=previous_health, after=health, hurt=hurt)
                previous_health = health
            observer(frame, ram)
            first = result['first_boss_combat']
            if args.boss_frames and first and frame >= first['frame'] + args.boss_frames:
                boss_budget_done = True
                result['test_stop_reason'] = 'boss_frame_budget'

        kwargs.update(ram_writes=writes, ram_observer=observe,
                      stop_when=lambda: boss_budget_done or bool(stop and stop()))
        return original(*run_args, **kwargs)

    game.run = wrapped
    def walk(tilemap, start, goal, enemies=(), geometry=False):
        return original_walk(tilemap, start, goal, () if approach_active else enemies, geometry)
    game.walk = walk
    sys.argv = [sys.argv[0]] + ([] if args.planner == 'ordinary' else
                               ['--lookahead-rooms', hex(args.boss_room)]) + remaining
    try:
        if args.planner == 'escape':
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
        game.walk = original_walk
        if folder is not None:
            result.update(driver_sha256=sha(driver), planner=args.planner,
                          writes=[dict(frame=f, address=a, data_hex=data.hex()) for f, a, data in writes])
            (folder / 'assisted_route_driver.py').write_bytes(driver)
            if result['release_write_frame'] is not None:
                assert all(f <= result['release_write_frame'] for f, _, _ in writes)
            (folder / 'assistance.json').write_text(json.dumps(result, indent=2) + '\n')
            path = folder / 'report.json'
            if path.exists():
                report = json.loads(path.read_bytes())
                report.update(assisted_route=True, ram_injections=True, boss_assistance=False,
                              primary_extra_state_writes=len(writes),
                              assistance_manifest='assistance.json', natural_campaign_proof=False)
                path.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
