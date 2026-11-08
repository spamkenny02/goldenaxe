"""Read-only IRQ handshake, original PSG and production reader-state checks for private candidates."""
import argparse
import contextlib
import gzip
import io
import json
import re
import struct
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from run_core import run
from archive_lossless_evidence import sha
p = argparse.ArgumentParser()
p.add_argument('--work', required=True)
a = p.parse_args()
work = root / 'validation' / a.work
assert work.resolve().is_relative_to(root / 'validation')
out = work / 'state'
assert not out.exists()
out.mkdir()
project = work / 'project'
core = root.parents[1] / 'work/genesis-plus-gx/genesis_plus_gx_libretro.dll'
archive = root / 'analysis/v319-psg-write-spacing'
manifest = json.loads((archive / 'manifest.json').read_bytes())
def sy(path):
    return {m[2].split('.lto_priv.')[0]: int(m[1], 16) & 65535 for line in path.read_text().splitlines()
            if (m := re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)', line))}
audio_fields = [('sound_ram', 400), ('sound_source_de', 2), ('sound_source_work', 8),
                ('sound_effect_request', 2), ('sound_request', 2), ('sound_request_delay', 2),
                ('sound_current_track', 2), ('sound_track_started_frame', 2)]
intro_fields = ['intro_logic_clock', 'intro_counter', 'intro_line', 'intro_timer', 'intro_scene']
stride = sum(size for _, size in audio_fields)
cases = []
for region in ('ntsc', 'pal'):
    streams = {}; stats = {}; errors = []
    for tag, rom, symbols in [('baseline', root / 'gaw-megadrive.bin', root / 'megadrive/out/release/symbol.txt'),
            ('candidate', project / 'out/release/rom.bin', project / 'out/release/symbol.txt')]:
        symbols = sy(symbols); audio = bytearray(); intro = bytearray(); psg = bytearray()
        def ram(frame, raw):
            def data(name, size): return bytes(raw[(symbols[name] + n) ^ 1] for n in range(size))
            audio.extend(b''.join(data(name, size) for name, size in audio_fields))
            intro.extend(b''.join(data(name, 2) for name in intro_fields))
            for name in ('sound_unhandled_command', 'intro_full_irq_error', 'sound_prepared_clock_error'):
                if name in symbols and int.from_bytes(data(name, 2), 'big'):
                    errors.append(dict(frame=frame, tag=tag, name=name, value=int.from_bytes(data(name, 2), 'big')))
            if tag == 'candidate':
                for name in ('intro_full_irq_requests', 'intro_full_irq_acks'):
                    if name in symbols: stats[name] = int.from_bytes(data(name, 4), 'big')
                stats['pending'] = int.from_bytes(data('intro_full_irq_request', 2), 'big')
        with contextlib.redirect_stdout(io.StringIO()):
            run(rom, 14000, out / (region + '-' + tag), set(), [], skip_intro=False, core=core,
                ram_observer=ram, psg_observer=lambda frame, regs: psg.extend(struct.pack('<8H', *regs)),
                core_options={'genesis_plus_gx_region_detect': 'pal' if region == 'pal' else 'auto'})
        assert len(audio) == 14000 * stride
        folder = out / (region + '-' + tag)
        (folder / 'reader-state.bin').write_bytes(audio)
        (folder / 'intro-state.bin').write_bytes(intro)
        (folder / 'psg-states.bin').write_bytes(psg)
        streams[tag] = (audio, intro, psg)
        print(region, tag, 'captured', flush=True)
    item = manifest['compressed'][f'validation/v319-psg-writes01/{region}-sms/exposed-psg-states.bin']
    encoded = (archive / item['stored']).read_bytes()
    assert sha(encoded) == item['stored_sha256']
    source = gzip.decompress(encoded)
    assert sha(source) == item['raw_sha256'] and streams['baseline'][2] == source
    def diffs(left, right, width):
        return [n + 1 for n in range(14000) if left[n*width:(n+1)*width] != right[n*width:(n+1)*width]]
    reader = diffs(streams['baseline'][0], streams['candidate'][0], stride)
    psg = diffs(streams['candidate'][2], source, 16)
    intro = diffs(streams['baseline'][1], streams['candidate'][1], len(intro_fields)*2)
    case = dict(region=region, frames=14000, runtime_errors=len(errors), first_errors=errors[:10],
        counters=stats, reader_state_difference_frames=len(reader), first_reader_differences=reader[:12],
        source_psg_difference_frames=len(psg), first_psg_differences=psg[:12],
        intro_state_difference_frames=len(intro), first_intro_differences=intro[:12])
    cases.append(case)
    print(json.dumps(case), flush=True)
result = dict(diagnostic_only=True, promoted=False, cases=cases, audio_fields=audio_fields,
    intro_fields=intro_fields, ram_writes=0, sram_imports=0, md_sha256=sha((project / 'out/release/rom.bin').read_bytes()),
    baseline_sha256=sha((root / 'gaw-megadrive.bin').read_bytes()),
    scope='Natural no-input cold opening only. Every-frame native reader state/work/DE/requests/track compared '
          'to production; exposed PSG compared directly to source. Separate video checks required.')
(out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
