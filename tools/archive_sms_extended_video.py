"""Decode and archive the continuous extended SMS campaign video, with honest scope."""
import hashlib,json,shutil,subprocess
from pathlib import Path
import cv2,imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
from run_core import ROOT


def main():
    source=ROOT/'validation/sms-video-extended-2026-11-11'
    report=json.loads((source/'report.json').read_bytes())
    ending=ROOT/'validation'/report['route']/'report.json'
    end=json.loads(ending.read_bytes())
    assert report['passed'] and report['ending_seen'] and report['final_ram_and_pixels_exact'] and report['first_emulated_video_frame']==1
    assert end['ending_complete'] and report['frames']==report['emulated_frames_from_boot']==564131
    folder=ROOT/'videos/sms/campagne-etendue-2026-11-11';folder.mkdir(parents=True,exist_ok=True)
    movie=folder/'golden-axe-warrior-sms-campagne-etendue-ntsc.mp4'
    if not movie.exists():
        original=Path(report['movie']).resolve();assert original.is_relative_to(ROOT/'validation')
        shutil.move(str(original),str(movie))
    assert hashlib.sha256(movie.read_bytes()).hexdigest()==report['movie_sha256']
    log=source/'full-decode.log'
    with log.open('wb') as output:
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-v','error','-xerror',
            '-i',str(movie),'-map','0:v:0','-map','0:a:0','-f','null','-'],stdout=subprocess.DEVNULL,stderr=output,check=True)
    assert not log.read_bytes(),log.read_text(errors='replace')
    samples=[(2500,'Début de partie'),(434195,'PNJ O3'),(444000,'Magie Eau'),
        (466800,'Dernière fée'),(482000,'Bouclier du chevalier'),(490000,'Récompense annexe'),
        (500000,'Corrosion et remède'),(554000,'Death Adder'),(560000,'Générique')]
    sheet=Image.new('RGB',(3*320,3*264),(24,24,24));draw=ImageDraw.Draw(sheet)
    font_path=Path('C:/Windows/Fonts/arial.ttf')
    font=ImageFont.truetype(str(font_path),16) if font_path.exists() else ImageFont.load_default()
    cap=cv2.VideoCapture(str(movie));assert int(cap.get(cv2.CAP_PROP_FRAME_COUNT))==report['frames']
    for i,(frame,label) in enumerate(samples):
        cap.set(cv2.CAP_PROP_POS_FRAMES,frame-1);ok,bgr=cap.read();assert ok
        thumb=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)).resize((320,240),Image.Resampling.NEAREST)
        x,y=i%3*320,i//3*264;sheet.paste(thumb,(x,y))
        seconds=frame/report['fps'];h=int(seconds//3600);m=int(seconds%3600//60);s=int(seconds%60)
        draw.text((x+5,y+242),f'{h:02}:{m:02}:{s:02} — {label}',font=font,fill='white')
    cap.release();sheet.save(folder/'apercu.jpg',quality=94)
    summary=dict(passed=True,movie=str(movie),movie_sha256=report['movie_sha256'],movie_bytes=movie.stat().st_size,
        frames=report['frames'],fps=report['fps'],duration_seconds=report['duration_seconds'],
        continuous_campaign_from_boot_through_credits=True,all_npcs_complete=False,all_side_quests_complete=False,
        full_audio_video_decoded=True,save_imports=0,boss_assistance=False,final_ram_and_pixels_exact=True,
        source_capture_report=report,ending_report_sha256=hashlib.sha256(ending.read_bytes()).hexdigest(),
        limits='Main campaign and additional acquired quests. Separate service, dialogue and side-quest branches are not silently inserted into this continuous video.')
    (folder/'report.json').write_text(json.dumps(summary,indent=2)+'\n')
    (ROOT/'analysis/sms_extended_campaign_video_report.json').write_text(json.dumps(summary,indent=2)+'\n')
    (folder/'LISEZ-MOI.txt').write_text(
        'Golden Axe Warrior — Master System, parcours maison étendu\n\n'
        'Vidéo continue : 564131 images, environ 2 h 36 min 54 s, NTSC, son original.\n'
        'Depuis le démarrage jusqu’à Death Adder, générique terminé et retour à l’introduction.\n'
        '65 contextes ordinaires connus, quatre magies aux niveaux 2/2/2/1, huit récompenses de fées,\n'
        'capacités vie/magie 128/128, boucliers chevalier puis dragon, pomme J9, huile cachée et vrai remède.\n'
        'Les introductions sont passées par les commandes enregistrées. Certains dialogues sont brefs : utiliser pause.\n'
        'Protection enregistrée sur les approches, retirée avant les boss et pour le contrôle de corrosion.\n'
        'Aucun import de sauvegarde ni modification de progression, d’objets, de vie ou d’argent.\n\n'
        'Cette vidéo principale ne certifie pas à elle seule TOUS les PNJ/services et toutes les variantes.\n'
        'Les branches annexes restent identifiées séparément. Ne pas la présenter comme une certification 100 %.\n'
        'Le rapport source générique nomme tout --trace « excerpt » ; la continuité et la fin complètes\n'
        'sont établies ici par l’intervalle depuis la première image, la victoire observée et la preuve de fin.\n',encoding='utf-8')
    # Only the two generated, decoded encoder intermediates are discarded.
    removed=[]
    for name in ('audio.wav','video-silent.mp4'):
        path=(source/name).resolve();assert path.parent==source.resolve()
        if path.exists():removed.append(dict(file=name,bytes=path.stat().st_size));path.unlink()
    (source/'removed-encoder-intermediates.json').write_text(json.dumps(removed,indent=2)+'\n')
    print(json.dumps(dict(movie=str(movie),bytes=movie.stat().st_size,full_decode=True,removed=removed)))


if __name__=='__main__':main()
