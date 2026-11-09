"""Fresh-process V320/candidate controls, gameplay start and PCM regression."""
import argparse
import contextlib
import hashlib
import io
import json
import re
import subprocess
import struct
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from run_core import ROOT, run


def probe(options):
    from validate_actor_tick import PRESSES
    symbols = {m[2].split('.lto_priv.')[0]: int(m[1], 16) & 65535
               for line in (ROOT/'megadrive/out/release/symbol.txt').read_text().splitlines()
               if (m := re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)', line))}
    out = ROOT/'validation'/options.out
    assert not out.exists()
    case = options.case
    if case == 'walk':
        presses = [(200, 220, 0)] + PRESSES
        frames = 3900
    else:
        first = dict(cape=6100, logo=6360, prompt=6600)[case]
        presses = [(first, first+14, 0)]
        frames = first+300
    fields = ['game_state', 'room_id', 'hero_x', 'hero_y', 'hero_direction', 'hero_health']
    transitions = []
    last = None
    final = None
    pcm = hashlib.sha256()
    psg = hashlib.sha256()
    sound = hashlib.sha256()
    def observe(frame, raw):
        nonlocal last, final
        def word(name):
            n = symbols[name]
            return raw[n] | raw[n+1] << 8
        values = [word(n) for n in fields]
        if values[:2] != last:
            transitions.append([frame] + values[:2])
            last = values[:2]
        final = dict(zip(fields, values))
        n = symbols['sound_ram']
        sound.update(raw[n:n+0x190])
        sound.update(struct.pack('>HHH', word('sound_current_track'), word('sound_request'), word('sound_request_delay')))
    def psg_observe(frame, registers):
        psg.update(struct.pack('<8i', *registers))
    image = hashlib.sha256()
    def video(frame, data, width, height, pitch, mode):
        if frame == frames:
            assert data is not None
            image.update(data)
    with contextlib.redirect_stdout(io.StringIO()):
        run(options.rom, frames, out/'capture', {frames}, presses, core=options.core,
            skip_intro=False, ram_observer=observe, video_observer=video,
            audio_observer=pcm.update, audio_out=out/'audio.wav' if options.dump_audio else None,
            psg_observer=psg_observe if options.core else None,
            core_options={'genesis_plus_gx_region_detect': 'pal' if options.region == 'pal' else 'auto'})
    report = dict(rom_sha256=hashlib.sha256(options.rom.read_bytes()).hexdigest(),
                  region=options.region, case=case, frames=frames, transitions=transitions,
                  final=final, final_video_sha256=image.hexdigest(), pcm_sha256=pcm.hexdigest(),
                  psg_registers_sha256=psg.hexdigest() if options.core else None,
                  sound_state_sha256=sound.hexdigest(),
                  no_ram_writes=True)
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--case', choices=['walk', 'cape', 'logo', 'prompt'])
    p.add_argument('--region', choices=['ntsc', 'pal'])
    p.add_argument('--dump-audio', action='store_true')
    p.add_argument('--core', type=Path)
    options = p.parse_args()
    if options.case:
        probe(options)
        return
    folder = ROOT/'validation'/options.out
    assert options.core and options.core.is_file(), 'Read-only PSG observer core required'
    assert not folder.exists()
    folder.mkdir()
    tasks = [(region, case, label, rom) for region in ['ntsc', 'pal']
             for case in ['walk', 'cape', 'logo', 'prompt']
             for label, rom in [('base', ROOT/'versions/v0320-9e5b0abe/gaw-megadrive-v0320.bin'), ('candidate', options.rom.resolve())]]
    def launch(task):
        region, case, label, rom = task
        name = options.out+'/'+region+'-'+case+'-'+label
        subprocess.run([sys.executable, __file__, '--rom', str(rom), '--out', name,
                        '--case', case, '--region', region, '--core', str(options.core.resolve())], check=True, capture_output=True)
        return task
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(launch, tasks))
    results = []
    for region in ['ntsc', 'pal']:
        for case in ['walk', 'cape', 'logo', 'prompt']:
            def read(label):
                return json.loads((folder/(region+'-'+case+'-'+label)/'report.json').read_text())
            base, candidate = read('base'), read('candidate')
            for field in ['transitions', 'final', 'final_video_sha256', 'psg_registers_sha256', 'sound_state_sha256']:
                assert base[field] == candidate[field], (region, case, field)
            results.append(dict(region=region, case=case, frames=candidate['frames'],
                                state_transitions_exact=True, final_fields_exact=True,
                                final_video_exact=True, psg_registers_every_frame_exact=True,
                                sound_reader_state_every_frame_exact=True,
                                pcm_exact=base['pcm_sha256']==candidate['pcm_sha256'], final=candidate['final']))
    report = dict(passed=True, md_sha256=hashlib.sha256(options.rom.read_bytes()).hexdigest(),
                  fresh_process_runs=len(tasks), no_ram_writes=True, cases=results,
                  core_sha256=hashlib.sha256(options.core.read_bytes()).hexdigest(),
                  scope='Controller-only title exit in cape, logo and prompt; early skip plus existing walking/new-game route. Exact V320 control-state transitions, final video, per-frame PSG registers and sound-reader state. PCM phase equality is reported separately; CPU publication changes subframe work. Not a full campaign replay.')
    (folder/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Eight PAL/NTSC control routes: state, final video, per-frame PSG and sound-reader state exact. See separate PCM results.')


if __name__ == '__main__':
    main()
