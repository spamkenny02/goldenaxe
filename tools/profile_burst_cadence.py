"""Read-only function entry timing of the controlled type7C projectile cycle."""
import ctypes as c
import hashlib
import json
import re
import sys
import validate_burst_boss_gameplay as fixture
from actor_reference import ROOT


def main():
    core = ROOT.parents[1] / 'work/genesis-plus-gx/genesis_plus_gx_clock_libretro.dll'
    dll = c.CDLL(str(core))
    symbols = {m[2]: int(m[1], 16)
               for line in (ROOT / 'megadrive/out/release/symbol.txt').read_text().splitlines()
               if (m := re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)', line))}
    names = ['tick_world_simulation', 'tick_world_actors', 'world_vint',
             'prepare_world_sms_sprite_overflow', 'update_hero_sprites_for_frame',
             'add_world_sprite_scene', 'sound_tick']
    watched = {pc: name for name, pc in symbols.items()
               if name.split('.constprop.')[0].split('.lto_priv.')[0] in names}
    assert len(watched) <= 32 and len(watched) >= 6
    pcs = (c.c_uint * len(watched))(*watched)
    dll.gaw_md_config.argtypes = [c.c_uint, c.POINTER(c.c_uint)]
    dll.gaw_md_event_count.restype = c.c_uint
    dll.gaw_md_event_data.restype = c.POINTER(c.c_uint)
    original = fixture.run
    results = []

    def profiled(rom, frames, folder, *args, **kwargs):
        if rom.suffix.lower() == '.sms':
            return original(rom, frames, folder, *args, **kwargs)
        observe = kwargs['ram_observer']
        events = []

        def sample(frame, raw):
            observe(frame, raw)
            count = dll.gaw_md_event_count()
            assert count < 8192
            data = dll.gaw_md_event_data()
            if frame >= 2880:
                for n in range(count):
                    pc, cycles, sp = [int(data[n * 3 + k]) for k in range(3)]
                    events.append(dict(frame=frame, function=watched[pc],
                                       master_cycles=cycles, sp=sp & 65535))
            dll.gaw_md_config(len(watched), pcs)

        kwargs.update(core=core, ram_observer=sample)
        dll.gaw_md_config(len(watched), pcs)
        result = original(rom, frames, folder, *args, **kwargs)
        ticks = [row['frame'] for row in events if row['function'] == 'tick_world_simulation']
        gaps = [dict(before=a, after=b, frames=b-a) for a, b in zip(ticks, ticks[1:]) if b-a != 1]
        results.append(dict(region=kwargs['core_options']['genesis_plus_gx_region_detect'],
                            gaps=gaps, events=events, simulation_entries=len(ticks)))
        return result

    fixture.run = profiled
    sys.argv = [sys.argv[0], '--variant7c', '--type7c-only', '--diagnose']
    fixture.main()
    report = dict(md_sha256=hashlib.sha256((ROOT/'gaw-megadrive.bin').read_bytes()).hexdigest(),
                  core_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),
                  read_only_timing_observer=True, controlled_fixture=True, results=results,
                  limits=['Initial actor/hero and initial world clock are controlled by the fixture. '
                          'Function entries measure native physical cadence; no SMS cycle or '
                          'complete framebuffer/audio equivalence is claimed.'])
    (ROOT/'analysis/burst_cadence_v0295_report.json').write_text(json.dumps(report, indent=2)+'\n')
    for row in results:
        print(row['region'], 'simulation entries', row['simulation_entries'], 'gaps', len(row['gaps']))


if __name__ == '__main__':
    main()
