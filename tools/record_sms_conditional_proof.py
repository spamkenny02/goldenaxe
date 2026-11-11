"""Build a clearly labeled video appendix for the nine played conditional variants."""
import hashlib,json,subprocess,sys
from pathlib import Path
import cv2
from run_core import ROOT
sys.path.insert(0,str(ROOT.parents[1]/'work/video-tools'))
import imageio_ffmpeg


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    jobs=[('npc-pre4-22-earth','Avant le quatrième cristal','sms-video-pre4-dialogue01'),
          ('npc-pre9-ce-mainland','Trois habitants avant le neuvième cristal','sms-video-pre9-ce-dialogues01'),
          ('npc-post9-22-main','Récompense réelle de 100 pièces','sms-video-gold100-dialogue01'),
          ('npc-post9-22-return-main','Retour après la récompense','sms-video-gold100-return01'),
          ('npc-post9-ce-main','Trois habitants après le neuvième cristal','sms-video-post9-ce-dialogues01')]
    segments=[];offset=0;chapters=[]
    for label,title,name in jobs:
        branch=json.loads((ROOT/f'analysis/sms-conditional-{label}.json').read_bytes());assert branch['passed']
        source=ROOT/'validation'/branch['trace'];played=json.loads((source/'report.json').read_bytes())
        folder=ROOT/'validation'/name
        if not (folder/'report.json').exists():
            assert not folder.exists(),'Keep incomplete trials; select a new output name'
            command=[sys.executable,str(ROOT/'tools/record_sms_gameplay.py'),'--trace',branch['trace'],
                '--from-frame',str(played['prefix_end']+1),'--out',name]
            with (ROOT/f'validation/{name}.log').open('w') as log:subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        report=json.loads((folder/'report.json').read_bytes());assert report['passed'] and report['final_ram_and_pixels_exact']
        assert not report['save_imports'] and sha(Path(report['movie']))==report['movie_sha256']
        chapters.append(dict(start_seconds=offset,title=title,branch=label,dialogs=branch['visits']))
        offset+=report['duration_seconds'];segments.append(report)
        print('PROOF CLIP VERIFIED',label,report['frames'],flush=True)
    out=(ROOT/'videos/sms/conditions-2026-11-10').resolve();assert not out.exists();out.mkdir(parents=True)
    index=out/'concat-input.txt';index.write_text(''.join("file '"+Path(r['movie']).as_posix().replace("'","'\\''")+"'\n" for r in segments))
    movie=out/'golden-axe-warrior-sms-neuf-dialogues-conditionnels.mp4';ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    command=[ffmpeg,'-hide_banner','-nostdin','-f','concat','-safe','0','-i',str(index),'-map','0:v:0','-map','0:a:0',
        '-c','copy','-movflags','+faststart','-metadata','title=Golden Axe Warrior SMS - Nine conditional dialogue proofs',
        '-metadata','comment=Five excerpts from explicitly different cold-boot branches. All nine selected conditional variants. Not an all-NPC or full side-quest run.',str(movie)]
    with (out/'mux.log').open('w') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    cap=cv2.VideoCapture(str(movie));assert cap.isOpened();count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));cap.release()
    assert count==sum(r['frames'] for r in segments)
    with (out/'decode.log').open('w') as log:
        subprocess.run([ffmpeg,'-hide_banner','-nostdin','-v','error','-xerror','-i',str(movie),'-map','0:v:0','-map','0:a:0','-f','null','-'],stdout=log,stderr=subprocess.STDOUT,check=True)
    text='''Preuves SMS : neuf variantes des quatre PNJ conditionnels recensés.

Cinq extraits de branches identifiées : avant le quatrième cristal, les trois
habitants avant le neuvième cristal, la récompense réelle de 100 pièces, le
retour après cette récompense et les trois habitants après le neuvième cristal.
Le fichier chapters.json donne les repères et les frames sources. Les textes
sont affichés à la vitesse du jeu ; mettre la vidéo en pause pour les lire.

Chaque extrait rejoue réellement toutes les entrées depuis le démarrage avant
d'enregistrer son intervalle. Aucun import de sauvegarde ou de quête. Protection
d'approche enregistrée, retirée avant les boss ; son réel du cœur officiel.
RAM et capture brute finales identiques à la preuve indépendante de chaque
branche. Les flux concaténés sont décodés en entier sans erreur.

Il s'agit d'une annexe de preuves montée à partir de cinq extraits, pas d'une
partie continue ni d'un parcours 100 % de tous les PNJ et quêtes secondaires.
'''
    (out/'LISEZ-MOI.txt').write_text(text,encoding='utf-8');(out/'chapters.json').write_text(json.dumps(chapters,indent=2,ensure_ascii=False)+'\n')
    report=dict(passed=True,movie=str(movie),movie_sha256=sha(movie),movie_bytes=movie.stat().st_size,frames=count,
        source_clips=segments,conditional_variants=9,conditional_npc_contexts=4,full_av_decoded=True,
        all_npcs_complete=False,all_side_quests_complete=False,scope='Five disclosed branch excerpts; the nine selected conditional variants only.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'analysis/sms_conditional_video_report.json').write_text(json.dumps(report,indent=2)+'\n')
    assert sha(movie)==report['movie_sha256']
    for segment in segments:
        folder=Path(segment['movie']).resolve().parent
        assert folder.is_relative_to((ROOT/'validation').resolve())
        for name in ['video-silent.mp4','audio.wav']:
            p=(folder/name).resolve();assert p.is_relative_to(folder)
            if p.exists():p.unlink()
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
