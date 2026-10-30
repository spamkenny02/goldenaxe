"""Test-only invulnerability on the approach; ordinary damage during the boss.

This deliberately injects RAM and must never be labelled a natural campaign.
The released ROM is not patched. The boss planner starts after assistance ends.
"""
import argparse
import json
import sys
from pathlib import Path

import natural_combat_beam as beam
from run_core import ROOT, FrameWrites
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import prefix_writes, recording, episodes, EPISODE_KEYS


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--boss-room', type=lambda value: int(value, 0), required=True)
    parser.add_argument('--planner', choices=['beam', 'navigation', 'ordinary', 'side', 'escape', 'cautious', 'evasive', 'exit', 'earth', 'contact', 'item'], default='beam')
    parser.add_argument('--boss-frames', type=int, help='Bound this diagnostic after normal combat starts')
    parser.add_argument('--retarget-pending-boss', action='store_true', help='Correct an unreached approach target; cold-prefix audit forbids either boss having been entered')
    parser.add_argument('--world-route', action='store_true', help='Apply the same guard to an exterior route')
    parser.add_argument('--unassisted-plan-rooms', help='Plan ordinary input in these rooms after the inherited boss guard has ended')
    parser.add_argument('--new-assistance-episode', action='store_true', help='Start the next approach after a verified dungeon exit')
    parser.add_argument('--preserve-floor-hurt', action='store_true', help='Release only a held test guard; preserve ordinary floor-damage cooldown when no enemies are active')
    parser.add_argument('--completed-exit-proof', help='Verified same-ROM exit before intervening service visits; no new assistance may have been added')
    args, remaining = parser.parse_known_args()
    assert not args.completed_exit_proof or args.new_assistance_episode
    sms = '--sms' in remaining
    assert not sms or args.planner in ('ordinary', 'beam', 'navigation', 'cautious', 'earth', 'side', 'escape', 'evasive', 'contact'), 'The selected wrapper does not support SMS report paths'
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
    writes = FrameWrites(prefix_writes(prefix_folder, prefix, '--assisted-prefix' in remaining))
    inherited_writes = writes[:]
    inherited = recording(prefix_folder, prefix)[0] if prefix['test_ram_writes'] else None
    if args.retarget_pending_boss:
        assert inherited and not args.new_assistance_episode and not args.world_route and not args.unassisted_plan_rooms
        assert inherited['boss_room'] != args.boss_room
        assert all(inherited[k] is None for k in ['first_boss_entry','release_write_frame','first_boss_combat','first_boss_damage'])
    start = prefix['frames']
    closed = []
    sy = None if sms else symbols(ROOT / 'megadrive/out/release/symbol.txt')
    if args.new_assistance_episode:
        assert inherited and inherited['first_boss_combat'] and inherited['release_write_frame'] < start
        assert inherited['boss_room'] != args.boss_room
        prior = json.loads((prefix_folder / 'report.json').read_bytes())
        if args.completed_exit_proof:
            assert prior['passed'] and prior['failure'] is None
            exit_folder=(ROOT/'validation'/args.completed_exit_proof).resolve()
            assert exit_folder.is_relative_to(ROOT/'validation')
            ec=json.loads((exit_folder/'capture.json').read_bytes())
            er=json.loads((exit_folder/'report.json').read_bytes())
            assert er['full_dungeon_cleared'] and er['failure'] is None and not er['deaths']
            assert ec['rom_sha256']==prefix['rom_sha256'] and ec['frames']<start
            assert prefix_writes(exit_folder,ec,True)==inherited_writes
            raw=evidence(prefix_folder/f'ram_{start:05d}.bin')
            old_raw=evidence(exit_folder/f'ram_{ec["frames"]:05d}.bin')
            if sms:
                assert raw[0x1d]==12 and raw[0xba]==0 and raw[0x318]>0 and raw[0x37]==0
                assert raw[0xcf:0xd8]==old_raw[0xcf:0xd8] and raw[0xda]>=er['last_state']['max_health']
            else:
                data=lambda r,n,k:bytes(r[(sy[n]+i)^1] for i in range(k))
                word=lambda n:int.from_bytes(data(raw,n,2),'big')
                assert word('game_state')==12 and word('room_id')<256 and word('hero_health')>0 and word('world_dungeon_number')==0
                assert data(raw,'game_save_state',592)[0x1f:0x28]==data(old_raw,'game_save_state',592)[0x1f:0x28]
                assert word('hero_max_health')>=er['last_state']['max_health']
        else:
            assert prior['full_dungeon_cleared'] and prior['failure'] is None and not prior['deaths']
            assert prior['last_state']['dungeon'] == 0 and prior['last_state']['game'] == 12 and prior['last_state']['health']
        closed = json.loads(json.dumps(episodes(inherited, prefix)))
        closed[-1]['end_frame'] = start
    elif inherited:
        assert inherited['boss_room'] == args.boss_room or args.retarget_pending_boss, 'A new boss requires --new-assistance-episode after its predecessor exits'
        closed = json.loads(json.dumps(episodes(inherited, prefix)[:-1]))
    plan_rooms = [int(room,0) for room in args.unassisted_plan_rooms.split(',')] if args.unassisted_plan_rooms else [args.boss_room]
    if args.unassisted_plan_rooms:
        assert not args.world_route and not args.new_assistance_episode
        assert inherited and inherited['first_boss_combat'] and inherited['release_write_frame'] < start
        assert all(256 <= room < 512 for room in plan_rooms)
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
    result.update(completed_exit_proof=args.completed_exit_proof,
                  preserve_floor_hurt_requested=args.preserve_floor_hurt,
                  prefix_trace=prefix_folder.relative_to(ROOT / 'validation').as_posix(),
                  prefix_capture_sha256=sha((prefix_folder / 'capture.json').read_bytes()),
                  stage_activation_after_frame=start)
    if inherited and not args.new_assistance_episode:
        for key in ['activation_after_frame', 'first_boss_entry', 'release_write_frame', 'first_boss_combat', 'first_boss_damage']:
            result[key] = inherited[key]
    result['retarget_audit'] = inherited.get('retarget_audit') if inherited and not args.new_assistance_episode else None
    if args.retarget_pending_boss:
        source = (ROOT/'input/original.sms').read_bytes()
        kinds = [kind for kind in source[0x3234e+args.boss_room*8:0x32356+args.boss_room*8]
                 if kind >= 0x20 and source[0x320ea+(kind-0x20)*4+3]&0x40]
        assert kinds, 'The new target must contain an original boss record'
        result['retarget_audit'] = dict(from_room=inherited['boss_room'],to_room=args.boss_room,
                                       checked_prefix_frame=start,source_boss_kinds=kinds,
                                       prefix_verified=False,no_prior_entry=False)
    previous_health = None
    last_frame = 0
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
            nonlocal previous_health, approach_active, boss_budget_done, budget_deadline, last_frame
            last_frame = frame
            if sms:
                fields = dict(room_id=int.from_bytes(ram[0xb9:0xbb], 'little'), game_state=ram[0x1d],
                              hero_health=ram[0x318], hero_hurt=ram[0x305])
                word = lambda name: fields[name]
            else:
                word = lambda name: int.from_bytes(bytes(ram[(sy[name] + i) ^ 1] for i in range(2)), 'big')
            room, state, health, hurt = (word(name) for name in
                                       ['room_id', 'game_state', 'hero_health', 'hero_hurt'])
            if args.retarget_pending_boss and result['activation_after_frame'] < frame <= start:
                assert room not in [inherited['boss_room'],args.boss_room], ('A retarget cannot conceal prior boss assistance',frame,room)
                if frame == start:
                    result['retarget_audit'].update(prefix_verified=True,no_prior_entry=True)
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
                    # Repeated zero writes also erase the game's ordinary
                    # terrain-hit cooldown. In this mode only remove our
                    # held129 guard; leave natural0..128 counters untouched.
                    if danger or not args.preserve_floor_hurt or hurt > 128:
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
    sys.argv = [sys.argv[0]] + ([] if args.world_route or args.planner in ('ordinary','earth','contact','item') else
                               ['--lookahead-rooms', ','.join(hex(room) for room in plan_rooms)]) + remaining
    try:
        if args.world_route:
            game.main()
        elif args.planner == 'escape':
            import natural_boss_escape_planner
            natural_boss_escape_planner.main()
        elif args.planner == 'side':
            import natural_boss_side_planner
            natural_boss_side_planner.main()
        elif args.planner == 'exit':
            import natural_exit_planner
            natural_exit_planner.main()
        elif args.planner == 'evasive':
            import natural_boss_evasive_planner
            natural_boss_evasive_planner.main()
        elif args.planner == 'cautious':
            import natural_boss_cautious_planner
            natural_boss_cautious_planner.main()
        elif args.planner == 'navigation':
            import natural_combat_navigation
            natural_combat_navigation.main()
        elif args.planner == 'contact':
            import natural_contact_passage
            natural_contact_passage.main()
        elif args.planner == 'earth':
            import natural_earth_passage
            natural_earth_passage.main()
        elif args.planner == 'item':
            import natural_item_acquisition
            natural_item_acquisition.main()
        elif args.planner == 'ordinary':
            game.main()
        else:
            beam.main()
    finally:
        game.run = original
        if original_walk is not None:
            game.walk = original_walk
        if folder is not None:
            if args.unassisted_plan_rooms:
                assert writes == inherited_writes, 'Post-boss planning cannot add any assistance writes'
                result.update(unassisted_extension=True, extension_planning_rooms=plan_rooms, new_assistance_writes=0)
            result.update(driver_sha256=sha(driver), planner=args.planner,
                          writes=[dict(frame=f, address=a, data_hex=data.hex()) for f, a, data in writes])
            result['episodes'] = closed + [dict(**{key: result[key] for key in EPISODE_KEYS}, end_frame=last_frame + 1)]
            (folder / 'assisted_route_driver.py').write_bytes(driver)
            (folder / 'assistance.json').write_text(json.dumps(result, indent=2) + '\n')
            if (folder / 'capture.json').exists():
                recording(folder, json.loads((folder / 'capture.json').read_bytes()))
            path = folder / ('route_report.json' if args.world_route else 'report.json')
            if path.exists():
                report = json.loads(path.read_bytes())
                report.update(assisted_route=True, ram_injections=True, boss_assistance=False,
                              primary_extra_state_writes=len(writes),
                              assistance_manifest='assistance.json', natural_campaign_proof=False)
                path.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
