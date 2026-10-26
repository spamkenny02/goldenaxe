"""Official cold replay of approach assistance, including prefixes before the boss."""
import argparse
import contextlib
import io
import time
import json
from run_core import ROOT, run, FrameWrites
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trace', required=True)
    parser.add_argument('--trial', help='Additional independent replay suffix; canonical proof remains unchanged')
    parser.add_argument('--observe-water',action='store_true',help='Read canoe ownership,water terrain and ordinary movement during the fixed replay')
    parser.add_argument('--observe-grabs',action='store_true',help='Read actual thief attachment and live release during fixed replay')
    args = parser.parse_args()
    folder = (ROOT / 'validation' / args.trace).resolve()
    assert folder.is_relative_to(ROOT / 'validation')
    capture = json.loads((folder / 'capture.json').read_bytes())
    controls = json.loads((folder / 'controls.json').read_bytes())
    assist, writes = recording(folder, capture)
    sms = folder.name.startswith('sms')
    rom = ROOT / 'input/original.sms' if sms else ROOT / 'gaw-megadrive.bin'
    assert capture['rom_sha256'] == sha(rom.read_bytes()) and capture['sram_input'] is None
    sy=None if sms else symbols(ROOT/'megadrive/out/release/symbol.txt')
    allowed_address = 0x305 if sms else sy['hero_hurt']
    assert all(address == allowed_address for _, address, _ in writes)
    end = capture['frames']
    for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
        assert (folder / f'{stem}_{end:05d}.{ext}').exists()
    presses = [tuple(row) for row in capture['presses']]
    for i, row in enumerate(controls):
        stop = controls[i + 1]['frame'] - 1 if i + 1 < len(controls) else end
        presses.extend((row['frame'], min(stop, end), key) for key in row['buttons'] if row['frame'] <= end)
    out = folder.with_name(folder.name + f'-assisted-fixed-replay-{end}' + ('-'+args.trial if args.trial else ''))
    assert not out.exists()
    water=[];grabs=[];releases=[];previous_grab=None
    def observe_water(frame,raw):
        nonlocal previous_grab
        if sms:
            room=int.from_bytes(raw[0xb9:0xbb],'little');game=raw[0x1d];owned=raw[0xec];terrain=raw[0x41];hero=raw[0x301];x=int.from_bytes(raw[0x312:0x314],'little');y=int.from_bytes(raw[0x310:0x312],'little')
        else:
            data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
            room=word('room_id');game=word('game_state');owned=data('hero_items',17)[12];terrain=word('hero_terrain_context');hero=word('hero_state');x=word('hero_x');y=word('hero_y')
        if args.observe_grabs:
            health=raw[0x318] if sms else word('hero_health')
            actors=raw[0x600:0x900] if sms else data('world_actor_state',768)
            owners=[dict(slot=i,escape_count=actors[i*48+0x20],steal_countdown=actors[i*48+0x21]) for i in range(8) if actors[i*48]==0x5b and actors[i*48+1]==12]
            attached=hero==12 and bool(owners) and game==12
            if previous_grab and not attached and health and hero!=12:releases.append(dict(frame=frame,room=room,hero=hero,health=health,previous_frame=previous_grab['frame']))
            if attached:
                previous_grab=dict(frame=frame,room=room,hero=hero,health=health,owners=owners);grabs.append(previous_grab)
            else:previous_grab=None
        if args.observe_water and owned and game==12:
            off=((((y>>8)-4)&248)*8)+(((((x>>8)-4)&255)>>2)&62)
            if sms:flags=(raw[0x1601+off]|raw[0x1603+off])&32
            else:flags=(raw[(sy['sms_vram']+0x3801+off)^1]|raw[(sy['sms_vram']+0x3803+off)^1])&32
            if flags:water.append(dict(frame=frame,room=room,owned=owned,terrain=terrain,water_flag=flags,hero=hero,x=x,y=y))
    started=time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):
        run(rom, end, out, {end}, presses, ram_writes=FrameWrites(writes), skip_intro=False, core_options=capture['core_options'],ram_observer=observe_water if args.observe_water or args.observe_grabs else None)
    for stem, ext in [('ram', 'bin'), ('frame', 'png')]:
        filename = f'{stem}_{end:05d}.{ext}'
        assert (folder / filename).read_bytes() == (out / filename).read_bytes(), filename
    report = dict(elapsed_seconds=time.perf_counter()-started,indexed_writes=True,passed=True, assisted_route=True, natural_campaign_proof=False,
                  rom_sha256=capture['rom_sha256'], frames=end, feedback_reads=False,
                  ram_injections=True, injection_count=len(writes),
                  last_injection_frame=writes[-1][0], release_write_frame=assist['release_write_frame'],
                  first_boss_combat=assist['first_boss_combat'], boss_assistance=False,
                  approach_only=assist['first_boss_combat'] is None,
                  whole_ram_bytes=8192 if sms else 65536, final_png_exact=True,
                  evidence={name: sha((folder / name).read_bytes()) for name in
                            ['capture.json', 'controls.json', 'assistance.json']})
    if args.observe_water:
        moving=[b for a,b in zip(water,water[1:]) if b['frame']==a['frame']+1 and a['room']==b['room'] and a['hero']==b['hero']==1 and (a['x'],a['y'])!=(b['x'],b['y']) and max(abs(a['x']-b['x']),abs(a['y']-b['y']))<=1024]
        assert moving,'No actual canoe-water walking observed'
        (out/'water_samples.json').write_text(json.dumps(water,indent=2)+'\n')
        report.update(water_observer=True,water_frames=len(water),water_moving_frames=len(moving),water_rooms=sorted({r['room'] for r in water}),water_positions_fixed8_8=True,water_terrain_classes=sorted({r['terrain'] for r in water}),shallow_water_flag=32)
    if args.observe_grabs:
        assert grabs and releases,'No live thief grab/release observed'
        (out/'grab_samples.json').write_text(json.dumps(grabs,indent=2)+'\n')
        (out/'grab_releases.json').write_text(json.dumps(releases,indent=2)+'\n')
        report.update(grab_observer=True,grab_frames=len(grabs),grab_alive_release_events=len(releases),grab_rooms=sorted({r['room'] for r in grabs}))
    (out / 'replay_report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
