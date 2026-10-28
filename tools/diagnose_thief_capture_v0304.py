"""Read-only fixed replay of the bounded v304 D4 thief-route diagnostic."""
import contextlib
import io
import json
from run_core import ROOT, run, FrameWrites
from assisted_prefix import recording
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols


def main():
    source = ROOT/'validation/natural-dungeon-combat/md-auto-v0304-d4-a1-key01'
    capture = json.loads((source/'capture.json').read_bytes())
    controls = json.loads((source/'controls.json').read_bytes())
    rom = ROOT/'versions/v0304-b7b4e150/gaw-megadrive-v0304.bin'
    assert sha(rom.read_bytes()) == capture['rom_sha256']
    assist, writes = recording(source, capture)
    end = capture['frames']
    presses = [tuple(row) for row in capture['presses']]
    for i, row in enumerate(controls):
        stop = controls[i+1]['frame']-1 if i+1 < len(controls) else end
        presses.extend((row['frame'], min(stop, end), key) for key in row['buttons'] if row['frame'] <= end)
    sy = symbols(ROOT/'validation/stack-v0304-d3-all/symbol.txt')
    out = source.with_name(source.name+'-thief-diagnostic')
    assert not out.exists()
    rows = []
    last = None
    def observe(frame, raw):
        nonlocal last
        if frame < 71000:
            return
        data = lambda name, count: bytes(raw[(sy[name]+i)^1] for i in range(count))
        word = lambda name: int.from_bytes(data(name, 2), 'big')
        if word('room_id') != 0x1a1:
            return
        actors = data('world_actor_state', 768)
        thieves = [dict(slot=i, raw=actors[48*i:48*(i+1)].hex()) for i in range(16) if actors[48*i] == 0x5b]
        row = dict(hero=word('hero_state'), counter=word('hero_counter'), health=word('hero_health'),
                   input=word('input'), previous_input=word('world_previous_input'), thieves=thieves)
        if row != last:
            rows.append(dict(frame=frame, **row))
            last = row
    with contextlib.redirect_stdout(io.StringIO()):
        run(rom, end, out, {end}, presses, ram_writes=FrameWrites(writes), skip_intro=False,
            core_options=capture['core_options'], ram_observer=observe)
    (out/'thief_samples.json').write_text(json.dumps(rows, indent=2)+'\n', encoding='utf-8')
    transitions=[]
    for a,b in zip(rows,rows[1:]):
        if a['hero'] != b['hero']:
            transitions.append(dict(before=a,after=b))
    result=dict(rom_sha256=capture['rom_sha256'],frames=end,feedback_reads=False,
                new_state_writes=0,inherited_approach_writes=len(writes),hero_transitions=transitions,
                final_sample=rows[-1],source_hashes={n:sha((source/n).read_bytes()) for n in ['capture.json','controls.json','assistance.json']})
    (out/'diagnostic_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
