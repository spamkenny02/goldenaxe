"""Publish the campaign-only SMS proof video; do not label it an NPC 100% run."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
import cv2
from PIL import Image,ImageDraw
from run_core import ROOT
sys.path.insert(0,str(ROOT.parents[1]/'work/video-tools'))
import imageio_ffmpeg


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    source=(ROOT/'validation/sms-video-campaign01').resolve()
    report=json.loads((source/'report.json').read_bytes())
    assert report['passed'] and report['full_campaign_replayed'] and report['final_ram_and_pixels_exact']
    assert report['ending_seen'] and report['frames']==436161 and not report['all_npcs_complete']
    original=Path(report['movie']).resolve()
    assert original.is_relative_to(source) and original.is_file() and sha(original)==report['movie_sha256']
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    command=[ffmpeg,'-hide_banner','-nostdin','-v','error','-xerror','-i',str(original),'-map','0:v:0','-map','0:a:0','-f','null','-']
    with (source/'full-av-decode.log').open('w') as log:
        subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    output=(ROOT/'videos/sms/campagne-2026-11-10').resolve()
    assert output.is_relative_to(ROOT.resolve()) and not output.exists()
    output.mkdir(parents=True)
    movie=output/'golden-axe-warrior-sms-campagne-ntsc-pnj-partiels.mp4'
    assert not movie.exists();shutil.move(str(original),str(movie))
    assert sha(movie)==report['movie_sha256']
    duration=report['duration_seconds'];samples=[12,55,120,300,900,1800,2700,3600,4500,6000,duration-120,duration-10]
    cap=cv2.VideoCapture(str(movie));assert cap.isOpened()
    sheet=Image.new('RGB',(960,1040));draw=ImageDraw.Draw(sheet)
    for i,seconds in enumerate(samples):
        cap.set(cv2.CAP_PROP_POS_MSEC,seconds*1000);ok,bgr=cap.read();assert ok
        picture=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)).resize((320,240),Image.Resampling.NEAREST)
        x=(i%3)*320;y=(i//3)*260;sheet.paste(picture,(x,y))
        h,rest=divmod(int(seconds),3600);m,s=divmod(rest,60);draw.text((x+5,y+243),f'{h}:{m:02}:{s:02}',fill='white')
    cap.release();sheet.save(output/'apercu.jpg',quality=94)
    text='''Golden Axe Warrior — Master System — Campagne jusqu’au générique

Cette vidéo n’est PAS le parcours 100 % PNJ et quêtes demandé.
Elle prouve la campagne enregistrée de la nouvelle partie au générique et au
retour à l’intro : neuf cristaux, hache d’or et Death Adder. Les visites de PNJ
supplémentaires et les branches conditionnelles sont encore en cours et ne
figurent pas dans cette capture.

Capture continue à la cadence NTSC réelle, sans coupe ni accélération, avec le
son du cœur officiel. Protection de test enregistrée sur certaines approches,
retirée avant les boss. Aucun import de sauvegarde, vie, inventaire ou quête.
Entrées rejouées depuis le démarrage, RAM finale de 8192 octets et capture brute
de la dernière image identiques à la preuve indépendante. Le MP4 utilise une
compression H.264/AAC. Les flux vidéo et audio sont décodés en
entier sans erreur avant livraison. Aucun envoi sur YouTube.
'''
    (output/'LISEZ-MOI.txt').write_text(text,encoding='utf-8')
    report.update(movie=str(movie),full_audio_and_video_decoded=True,all_npcs_complete=False,
        all_side_quests_complete=False,description=str(output/'LISEZ-MOI.txt'),preview=str(output/'apercu.jpg'))
    removed=[]
    for name in ['video-silent.mp4','audio.wav']:
        path=(source/name).resolve();assert path.is_relative_to(source) and path.is_file() and path!=movie
        removed.append(dict(path=str(path),bytes=path.stat().st_size));path.unlink()
    report['removed_generated_intermediates']=removed
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (source/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'analysis/sms_campaign_video_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
