"""Archive a verified SMS branch clip without presenting it as continuous 100%."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
import cv2,imageio_ffmpeg
from PIL import Image,ImageDraw
from run_core import ROOT


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--name',required=True)
    p.add_argument('--description',required=True);a=p.parse_args()
    assert a.name and all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in a.name)
    source=(ROOT/'validation'/a.source).resolve();assert source.is_relative_to(ROOT/'validation')
    r=json.loads((source/'report.json').read_bytes())
    assert r['passed'] and r['final_ram_and_pixels_exact'] and r['first_emulated_video_frame']>1
    folder=ROOT/'videos/sms/annexes-2026-11-11'/a.name;folder.mkdir(parents=True,exist_ok=True)
    movie=folder/(a.name+'.mp4')
    if not movie.exists():
        original=Path(r['movie']).resolve();assert original.is_relative_to(source)
        shutil.move(str(original),str(movie))
    assert hashlib.sha256(movie.read_bytes()).hexdigest()==r['movie_sha256']
    with (source/'full-decode.log').open('wb') as log:
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-v','error','-xerror',
            '-i',str(movie),'-map','0:v:0','-map','0:a:0','-f','null','-'],
            stdout=subprocess.DEVNULL,stderr=log,check=True)
    assert not (source/'full-decode.log').read_bytes()
    cap=cv2.VideoCapture(str(movie));assert int(cap.get(cv2.CAP_PROP_FRAME_COUNT))==r['frames']
    sheet=Image.new('RGB',(960,504),(24,24,24));draw=ImageDraw.Draw(sheet)
    for i in range(6):
        frame=int((r['frames']-1)*(i+.5)/6);cap.set(cv2.CAP_PROP_POS_FRAMES,frame);ok,bgr=cap.read();assert ok
        thumb=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)).resize((320,240),Image.Resampling.NEAREST)
        x,y=i%3*320,i//3*252;sheet.paste(thumb,(x,y));draw.text((x+5,y+240),f'{frame/r["fps"]:.1f} s',fill='white')
    cap.release();sheet.save(folder/'apercu.jpg',quality=94)
    report=dict(passed=True,description=a.description,movie=str(movie),movie_sha256=r['movie_sha256'],
        duration_seconds=r['duration_seconds'],full_audio_video_decoded=True,separate_branch=True,
        all_npcs_complete=False,all_side_quests_complete=False,source_capture_report=r)
    (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (folder/'LISEZ-MOI.txt').write_text(a.description+'\n\nBranche annexe distincte de la campagne continue.\n'
        'Toutes les images précédentes sont rejouées depuis le démarrage, sans import de progression ; seul cet extrait est encodé.\n'
        'La couverture globale de tous les PNJ et de toutes les variantes reste ouverte.\n'
        f'Durée : {r["duration_seconds"]:.3f} secondes.\nSHA-256 : {r["movie_sha256"]}\n',encoding='utf-8')
    # These two files are generated intermediates, never source evidence.
    for name in ('audio.wav','video-silent.mp4'):
        path=(source/name).resolve();assert path.is_relative_to(ROOT/'validation')
        if path.is_file():path.unlink()
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
