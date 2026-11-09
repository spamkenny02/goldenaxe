"""Stream real V321 frames/audio from the distributed NTSC controller route."""
import argparse
import contextlib
import csv
import hashlib
import io
import json
import subprocess
import sys
import time
import wave
from pathlib import Path

from run_core import ROOT, FrameWrites, run

sys.path.insert(0, str(ROOT.parents[1] / 'work/video-tools'))
import imageio_ffmpeg
import cv2
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('part', choices=['intro', 'gameplay'])
    parser.add_argument('--out', required=True)
    parser.add_argument('--frames', type=int)
    args = parser.parse_args()
    out = (ROOT / 'validation' / args.out).resolve()
    assert out.is_relative_to(ROOT / 'validation') and not out.exists()
    out.mkdir()
    rom = ROOT / 'versions/v0321-89c58333/gaw-megadrive-v0321.bin'
    digest = hashlib.sha256(rom.read_bytes()).hexdigest()
    assert digest == '89c5833351312ffaa591efb1939161910a298af06437080e2cf84fb3fb8ac86e'
    core = ROOT.parents[1] / 'work/libretro/genesis_plus_gx_libretro.dll'
    core_sha = hashlib.sha256(core.read_bytes()).hexdigest()
    assert core_sha == 'd17f2392115b3cd54258a1fa6c4195ddadc19b0805ebcca400db5162b1793516'
    manifest = json.loads((ROOT / 'testkit/manifest.json').read_bytes())
    route = manifest['routes']['md_ntsc']
    end = 6725 if args.part == 'intro' else route['frames']
    if args.frames:
        assert 0 < args.frames <= end
        end = args.frames
    presses = []
    writes = FrameWrites()
    if args.part == 'gameplay':
        csvpath = ROOT / 'testkit/routes' / route['csv']
        assert hashlib.sha256(csvpath.read_bytes()).hexdigest() == route['csv_sha256']
        with csvpath.open(newline='') as stream:
            for row in csv.DictReader(stream):
                first, last, mask, guard = (int(row[k]) for k in ['start', 'end', 'mask', 'guard'])
                last = min(last, end)
                if first > last:
                    continue
                presses.extend((first, last, key) for key in range(16) if mask & (1 << key))
                if guard != -1:
                    writes.extend((f, 0x2b1a, guard.to_bytes(2, 'big')) for f in range(first, last + 1))
    fps = 59.92274340431231
    rate = 44100
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    silent = out / 'video-silent.mp4'
    wav = out / 'audio.wav'
    movie = out / ('gaw-v0321-' + args.part + '.mp4')
    video_log = (out / 'video-encode.log').open('w')
    progress_log = (out / 'video-encode-progress.txt').open('w')
    process = None
    sent = 0
    audio_bytes = 0
    last_data = None
    started = time.monotonic()
    state = {}
    ending_seen = False
    milestones = []
    audio_file = wave.open(str(wav), 'wb')
    audio_file.setparams((2, 2, rate, 0, 'NONE', 'not compressed'))

    def audio(raw):
        nonlocal audio_bytes
        assert len(raw) % 4 == 0
        audio_file.writeframesraw(raw)
        audio_bytes += len(raw)

    def video(frame, data, width, height, pitch, mode):
        nonlocal process, sent, last_data
        if frame == 0:
            return
        assert frame == sent + 1 and mode == 2
        if data is not None:
            raw = data if pitch == width * 2 else b''.join(data[y * pitch:y * pitch + width * 2] for y in range(height))
            if (width, height) != (256, 224):
                raw = cv2.resize(np.frombuffer(raw, dtype='<u2').reshape(height, width), (256, 224), interpolation=cv2.INTER_NEAREST).tobytes()
            last_data = raw
        else:
            assert last_data is not None
            raw = last_data
        if process is None:
            command = [ffmpeg, '-hide_banner', '-nostdin', '-filter_threads', '1',
                       '-f', 'rawvideo', '-pixel_format', 'rgb565le', '-video_size', '256x224',
                       '-framerate', f'{fps:.12f}', '-i', 'pipe:0', '-an',
                       '-vf', 'scale=960:720:flags=neighbor,setsar=1',
                       '-c:v', 'libx264', '-preset', 'veryfast', '-threads', '4',
                       '-crf', '18', '-g', '120', '-bf', '2', '-pix_fmt', 'yuv420p',
                       '-movflags', '+faststart', '-progress', 'pipe:1', str(silent)]
            (out / 'encoder-command.json').write_text(json.dumps(command, indent=2) + '\n')
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=progress_log, stderr=video_log)
        assert len(raw) == 256 * 224 * 2
        process.stdin.write(raw)
        sent += 1
        if frame % 8192 == 0:
            progress = dict(part=args.part, frame=frame, total=end, percent=round(frame * 100 / end, 1),
                            wall_seconds=round(time.monotonic() - started, 1), state='recording')
            (out / 'progress.json').write_text(json.dumps(progress, indent=2) + '\n')
            print(json.dumps(progress), flush=True)

    def observe(frame, raw):
        nonlocal ending_seen
        word = lambda n: raw[n] | (raw[n + 1] << 8)
        previous = state.get('crystals', 0)
        crystals = sum(bool(raw[(0x28be + 0x1f + n) ^ 1] & 128) for n in range(9))
        state.update(game=word(0x74c), room=word(0x28b4), health=word(0x2b16), crystals=crystals, audio_error=word(0x2d12))
        if crystals > previous:
            milestones.append(dict(frame=frame, crystals=crystals))
        ending_seen |= state['game'] == 14
        assert not state['audio_error'], (frame, state)

    captures = {n for n in (600, 3000, 6358, 10000, 100000, 200000, 300000, 389961, 395935, 403000, end) if n <= end}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            run(rom, end, out / 'capture', captures, presses, core=core,
                skip_intro=False, ram_writes=writes, video_observer=video,
                audio_observer=audio, ram_observer=observe,
                core_options={'genesis_plus_gx_region_detect': 'auto'})
    finally:
        audio_file.close()
        if process is not None:
            process.stdin.close()
            status = process.wait()
            assert status == 0, status
        video_log.close()
        progress_log.close()
    assert sent == end
    cap = json.loads((out / 'capture/capture.json').read_bytes())
    assert abs(cap['fps'] - fps) < 1e-9 and round(cap['sample_rate']) == rate
    av_delta = audio_bytes / 4 / rate - sent / fps
    assert abs(av_delta) < .1, av_delta
    complete = args.part == 'gameplay' and end == route['frames']
    if complete:
        assert ending_seen and all(state[k] == v for k, v in route['expected_final'].items()), state
        assert len(writes) == route['approach_writes']
    command = [ffmpeg, '-hide_banner', '-nostdin', '-i', str(silent), '-i', str(wav),
               '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
               '-movflags', '+faststart', '-metadata', 'title=Golden Axe Warrior - Mega Drive native port V321',
               '-metadata', 'comment=Development build. Recorded approach-only protection, removed before boss combat. No save or progression imports.', str(movie)]
    with (out / 'mux.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    report = dict(passed=True, part=args.part, movie=str(movie), movie_bytes=movie.stat().st_size,
                  movie_sha256=hashlib.file_digest(movie.open('rb'), 'sha256').hexdigest(),
                  rom_sha256=digest, core_sha256=core_sha, frames=sent, fps=fps,
                  duration_seconds=sent / fps, audio_samples=audio_bytes // 4, audio_rate=rate,
                  audio_video_duration_difference_seconds=av_delta, final=state,
                  complete_campaign=complete, ending_seen=ending_seen, milestones=milestones,
                  approach_guard_writes=len(writes), boss_assistance=False, save_imports=0,
                  output_geometry=[960, 720], wall_seconds=time.monotonic() - started)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
