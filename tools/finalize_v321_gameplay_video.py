"""Join the actual V321 intro and continuous campaign; verify the MP4 deliverable."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import cv2
from PIL import Image, ImageDraw
from run_core import ROOT

sys.path.insert(0, str(ROOT.parents[1] / 'work/video-tools'))
import imageio_ffmpeg


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def stamp(seconds):
    hours, rest = divmod(int(seconds), 3600)
    minutes, seconds = divmod(rest, 60)
    return f'{hours}:{minutes:02}:{seconds:02}' if hours else f'{minutes}:{seconds:02}'


def main():
    reports = [json.loads((ROOT / f'validation/v321-video-{part}01/report.json').read_bytes()) for part in ['intro', 'gameplay']]
    intro, game = reports
    assert all(r['passed'] and r['rom_sha256'] == '89c5833351312ffaa591efb1939161910a298af06437080e2cf84fb3fb8ac86e' for r in reports)
    assert game['complete_campaign'] and game['ending_seen'] and game['frames'] == 403488
    assert game['final'] == dict(game=0, room=332, health=60, crystals=9, audio_error=0)
    assert game['approach_guard_writes'] == 190764 and not game['boss_assistance']
    out = ROOT / 'videos/v0321'
    assert not out.exists()
    out.mkdir()
    movie = out / 'golden-axe-warrior-md-v0321-gameplay-complet-ntsc.mp4'
    for report in reports:
        assert sha(Path(report['movie'])) == report['movie_sha256']
    segments = out / 'segments.txt'
    segments.write_text(''.join("file '" + Path(r['movie']).as_posix().replace("'", "'\\''") + "'\n" for r in reports))
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    title = 'Golden Axe Warrior sur Mega Drive — Gameplay complet + intro | Portage natif V321'
    command = [ffmpeg, '-hide_banner', '-nostdin', '-f', 'concat', '-safe', '0', '-i', str(segments),
               '-map', '0:v:0', '-map', '0:a:0', '-c', 'copy', '-movflags', '+faststart',
               '-metadata', 'title=' + title, '-metadata',
               'comment=Development V321. Complete intro plus uncut New Game-to-credits campaign. Approach-only test protection removed before bosses. Exhaustive NPC coverage remains in progress.', str(movie)]
    with (out / 'assembly.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    cap = cv2.VideoCapture(str(movie))
    assert cap.isOpened()
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    size = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    assert frames == sum(r['frames'] for r in reports) and size == (960, 720)
    assert abs(fps - game['fps']) < 1e-5
    duration = frames / fps
    offset = intro['duration_seconds']
    receipt = json.loads((ROOT / 'analysis/cold_palace_final_c0046_report.json').read_bytes())
    chapters = [(0, 'Introduction et titre'), (offset, 'Nouvelle partie')]
    chapters += [(offset + m['frame'] / fps, f'Cristal {m["crystals"]} obtenu') for m in game['milestones']]
    chapters += [(offset + receipt['first_final_combat']['frame'] / fps, 'Combat final — Death Adder'),
                 (offset + receipt['credits_started_frame'] / fps, 'Épilogue et générique')]
    description = '''Golden Axe Warrior, porté de la Master System vers la Mega Drive en code natif 68000 avec SGDK.

Capture de la V321, version de développement : introduction et titre, puis nouvelle partie jusqu’au combat final et au générique. Deux captures sont assemblées : l’introduction et le parcours de jeu. Le parcours de jeu est continu, sans coupe ni accélération.

Le parcours utilise une protection de test pendant certaines approches, retirée avant les combats de boss. Aucun import de sauvegarde, de progression, de vie ou d’inventaire. Partie assistée par des entrées enregistrées ; ce n’est pas une performance réalisée manette en main.

Cette vidéo montre la campagne jusqu’à la fin, pas tous les dialogues. La visite exhaustive des PNJ et de leurs variantes SMS/MD reste en cours. La fidélité graphique et sonore n’est pas encore certifiée complète.

NTSC, cadence d’origine (~59,92 images/s), image 4:3 en 720p, son du jeu, sans commentaire.

Projet : https://github.com/spamkenny02/goldenaxe

Chapitres :
''' + ''.join(stamp(t) + ' ' + label + '\n' for t, label in chapters) + '''
Golden Axe Warrior et ses éléments originaux appartiennent à leurs ayants droit respectifs. Portage non officiel.
'''
    (out / 'youtube-title.txt').write_text(title + '\n', encoding='utf-8')
    (out / 'youtube-description.txt').write_text(description, encoding='utf-8')
    samples = [12, 55, 105, offset - 1, offset + 1, offset + 150,
               offset + 1800, offset + 3600, chapters[-2][0] + 10,
               chapters[-1][0] + 30, duration - 20, duration - 2]
    sheet = Image.new('RGB', (960, 1040))
    draw = ImageDraw.Draw(sheet)
    for i, seconds in enumerate(samples):
        cap.set(cv2.CAP_PROP_POS_MSEC, seconds * 1000)
        ok, bgr = cap.read()
        assert ok, seconds
        im = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        sheet.paste(im.resize((320, 240)), ((i % 3) * 320, (i // 3) * 260))
        draw.text(((i % 3) * 320 + 5, (i // 3) * 260 + 242), stamp(seconds), fill='white')
    cap.release()
    sheet.save(out / 'apercu-gameplay.jpg', quality=94)
    scan = subprocess.run([ffmpeg, '-hide_banner', '-nostdin', '-i', str(movie), '-map', '0:v:0',
                           '-c', 'copy', '-f', 'null', '-', '-progress', 'pipe:1'], capture_output=True, text=True)
    (out / 'video-packet-check.log').write_text(scan.stderr)
    assert scan.returncode == 0 and int(re.findall(r'^frame=(\d+)', scan.stdout, re.M)[-1]) == frames
    audio = subprocess.run([ffmpeg, '-hide_banner', '-nostdin', '-i', str(movie), '-vn', '-af',
                            'astats=metadata=0:reset=0', '-f', 'null', '-'], capture_output=True, text=True)
    (out / 'audio-check.log').write_text(audio.stderr)
    assert audio.returncode == 0 and 'RMS level dB: -inf' not in audio.stderr
    report = dict(passed=True, movie=str(movie), bytes=movie.stat().st_size, sha256=sha(movie),
                  rom_sha256=game['rom_sha256'], frames=frames, fps=fps, duration_seconds=duration,
                  width=size[0], height=size[1], full_audio_decoded=True, all_video_packets_read=True,
                  campaign_completed=True, all_npcs_covered=False, approach_protection_disclosed=True,
                  boss_assistance=False, uploaded=False, segments=reports,
                  chapters=[dict(seconds=t, label=label) for t, label in chapters])
    (out / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('segments', 'chapters')}), flush=True)


if __name__ == '__main__':
    main()
