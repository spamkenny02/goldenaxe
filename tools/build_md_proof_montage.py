"""Join the actual campaign and selected annexes with visible branch title cards.

This deliverable is not labelled a global 100% NPC certificate. Gameplay video
packets are copied; audio timestamps are aligned at the explicitly marked cuts.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
import cv2,imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
from run_core import ROOT


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def title(trace):
    if 'saylun-owned' in trace:return 'Saylun : pomme deja possedee'
    if 'key-capacity' in trace:return 'Marchand : limite de 99 cles'
    if 'magic64' in trace:return 'Tournee des services et achat de magie'
    if 'equipment-returns' in trace:return 'Equipements : huit retours apres recompense'
    if 'passage-refuse' in trace:return 'Passage payant : refus et retour'
    if 'passage-poor' in trace:return 'Passage payant : argent insuffisant'
    if 'passage-census' in trace:return 'Passage payant : paiement et destination'
    if 'owned-quest-j9' in trace:return 'Quete J9 : pomme deja possedee'
    if 'owned-quest-kari' in trace:return 'Kari-Kari : huile deja possedee'
    if 'inn-repeat' in trace:return 'Auberge : revenir avec la vie pleine'
    if 'inn20-poor' in trace or 'inn40-poor' in trace:return 'Auberge : argent insuffisant'
    if 'save-overwrite' in trace:return 'Sauvegarde : ecrasement reel du slot'
    if 'save-' in trace:return 'Sauvegarde : ecriture reelle'
    if 'inn-location' in trace or 'paid-healer' in trace:return 'Auberge : paiement et soin'
    if 'minigame' in trace:return 'Jeu : tirages, gains, pertes et choix'
    if 'no-lightning' in trace:return 'Equipement : absence de Foudre'
    if 'low-capacity' in trace:return 'Equipement : vie maximale insuffisante'
    if 'shield-before-crystal' in trace:return 'Bouclier : avant le sixieme cristal'
    if 'shield-after-crystal' in trace:return 'Bouclier : indice apres le sixieme cristal'
    if 'quest-hint' in trace:return 'Equipement : indice avant la recompense'
    if 'merchant-variant' in trace:return 'Marchand : achat et variante de refus'
    return 'Branche annexe : '+trace.split('/')[-1].removeprefix('sms-npc-')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reuse-mux',action='store_true');args=parser.parse_args()
    ledger=json.loads((ROOT/'analysis/md_selected_proof_video_collection.json').read_bytes())
    assert ledger['passed'] and not ledger['missing_selected_goal_movies']
    main_report=json.loads((ROOT/'videos/v0322-rc1/report.json').read_bytes())
    assert main_report['passed'] and main_report['full_audio_decoded'] and main_report['full_video_decoded']
    main_report['movie_sha256']=main_report['sha256']
    folder=ROOT/'videos/md/parcours-et-annexes-2026-11-13';folder.mkdir(exist_ok=True,parents=True)
    work=ROOT/'validation/md-proof-montage-2026-11-13';work.mkdir(exist_ok=True)
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe();fps=main_report['fps'];rate=44100
    segments=[];chapters=[];cursor=0.0;source_rows=[]
    def append(path,frames,caption):
        nonlocal cursor
        assert "'" not in str(path)
        duration=frames/fps
        segments.append(dict(path=str(path),frames=frames,duration=duration))
        if caption:chapters.append(dict(seconds=cursor,title=caption))
        cursor+=duration
    def card(number,heading,economic=False,persistence_branch=False):
        frames=300 if economic else 180
        path=work/f'carte-{number:03d}.mp4';picture=path.with_suffix('.png')
        partial=path.with_name(path.stem+'.partial.mp4')
        if not path.exists():
            image=Image.new('RGB',(960,720),(12,18,28));draw=ImageDraw.Draw(image)
            font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',30)
            small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
            draw.text((42,80),f'ANNEXE {number:02d}',font=font,fill=(240,190,70))
            words=heading.split();lines=[];line=''
            for word in words:
                candidate=(line+' '+word).strip()
                if draw.textlength(candidate,font=font)>680 and line:lines.append(line);line=word
                else:line=candidate
            lines.append(line)
            for i,line in enumerate(lines):draw.text((42,155+i*44),line,font=font,fill='white')
            draw.text((42,330),'Branche distincte de la campagne continue',font=small,fill=(190,205,220))
            if economic:
                draw.text((42,385),'ARGENT INFINI DE TEST DECLARE',font=small,fill=(255,195,90))
                draw.text((42,422),'Achats reels ; aucun objet ni etat de quete injecte',font=small,fill='white')
            elif persistence_branch:
                draw.text((42,385),'Redemarrage puis Continuer normal',font=small,fill='white')
                draw.text((42,422),'Sauvegarde reellement ecrite par le jeu',font=small,fill='white')
            else:draw.text((42,385),'Aide sur les approches ; retiree avant les boss',font=small,fill='white')
            image.save(picture)
            with (work/f'carte-{number:03d}.log').open('wb') as log:
                subprocess.run([ffmpeg,'-hide_banner','-nostdin','-y','-loop','1','-framerate',f'{fps:.12f}',
                    '-i',str(picture),'-f','lavfi','-i','anullsrc=r=44100:cl=stereo','-frames:v',str(frames),
                    '-t',f'{frames/fps:.12f}','-c:v','libx264','-preset','veryfast','-threads','2','-crf','18',
                    '-pix_fmt','yuv420p','-vf','setsar=1','-c:a','aac','-b:a','192k',str(partial)],
                    stdout=log,stderr=subprocess.STDOUT,check=True)
            partial.replace(path)
        append(path,frames,heading)
    main_movie=Path(main_report['movie']);assert sha(main_movie)==main_report['movie_sha256']
    append(main_movie,main_report['frames'],'Campagne continue : nouvelle partie, quetes et generique')
    items=ledger['completed_clips']
    for number,row in enumerate(items,1):
        movie=Path(row['movie']);assert sha(movie)==row['movie_sha256']
        card(number,row['title'],row['currency_assisted_component_test'],row['persistence_branch'])
        append(movie,row['frames'],None)
        source_rows.append(dict(number=number,title=row['title'],trace=row['trace'],movie=str(movie),movie_sha256=row['movie_sha256'],video_report=row['report'],persistence_branch=row['persistence_branch'],currency_assisted_component_test=row['currency_assisted_component_test']))
        print('MONTAGE SOURCE VERIFIED',number,len(items),flush=True)
    concat=work/'segments.ffconcat';rows=['ffconcat version 1.0']
    for segment in segments:rows += ["file '"+Path(segment['path']).as_posix()+"'",f"duration {segment['duration']:.12f}"]
    concat.write_text('\n'.join(rows)+'\n',encoding='utf-8')
    metadata=work/'chapters.ffmetadata';rows=[';FFMETADATA1','title=Golden Axe Warrior MD - Campagne et annexes',
        'comment=Campagne continue puis branches distinctes. Couverture des preuves selectionnees ; certification globale 100 pour cent ouverte.']
    for i,chapter in enumerate(chapters):
        end=chapters[i+1]['seconds'] if i+1<len(chapters) else cursor
        rows += ['[CHAPTER]','TIMEBASE=1/1000',f"START={round(chapter['seconds']*1000)}",f'END={round(end*1000)}','title='+chapter['title']]
    metadata.write_text('\n'.join(rows)+'\n',encoding='utf-8')
    final_movie=folder/'gaw-md-campagne-et-annexes.mp4'
    movie=final_movie if final_movie.exists() else folder/'gaw-md-campagne-et-annexes.partial.mp4'
    if args.reuse_mux:assert movie.exists()
    assert abs(fps-152024/2537)<1e-10,'Packet timebase is specific to the verified native NTSC recordings'
    if not final_movie.exists() and not args.reuse_mux:
        with (work/'mux.log').open('wb') as log:
            subprocess.run([ffmpeg,'-hide_banner','-nostdin','-y','-f','concat','-safe','0','-i',str(concat),
                '-i',str(metadata),'-map','0:v:0','-map','0:a:0','-map_metadata','1','-map_chapters','-1',
                '-c:v','copy','-bsf:v','setts=dts=(N-2)*2537:pts=(N-2)*2537+floor((PTS-DTS)/2537+0.5)*2537:duration=2537:time_base=1/152024','-af','aresample=async=1:first_pts=0','-c:a','aac','-b:a','192k',
                '-t',f'{cursor:.12f}','-movflags','+faststart','-progress',str(work/'mux-progress.txt'),str(movie)],stdout=log,stderr=subprocess.STDOUT,check=True)
    expected_frames=sum(r['frames'] for r in segments)
    cap=cv2.VideoCapture(str(movie));assert cap.isOpened()
    assert int(cap.get(cv2.CAP_PROP_FRAME_COUNT))==expected_frames
    cap.release();audio_bytes=0
    with (work/'full-av-decode.log').open('wb') as log:
        process=subprocess.Popen([ffmpeg,'-hide_banner','-nostdin','-v','error','-xerror','-i',str(movie),
            '-map','0:v:0','-f','null','NUL','-map','0:a:0','-c:a','pcm_s16le','-f','s16le','pipe:1'],
            stdout=subprocess.PIPE,stderr=log)
        bucket=0
        while chunk:=process.stdout.read(1024*1024):
            audio_bytes+=len(chunk)
            if audio_bytes//(256*1024*1024)>bucket:
                bucket=audio_bytes//(256*1024*1024)
                (work/'progress.json').write_text(json.dumps(dict(stage='full_audio_video_decode',
                    decoded_seconds=audio_bytes/4/rate,total_seconds=cursor))+'\n')
        assert process.wait()==0
    assert not (work/'full-av-decode.log').read_bytes() and audio_bytes%4==0
    delta=audio_bytes/4/rate-cursor;assert abs(delta)<.1,(delta,audio_bytes,cursor)
    if movie!=final_movie:movie.replace(final_movie);movie=final_movie
    report=dict(passed=True,movie=str(movie),movie_sha256=sha(movie),movie_bytes=movie.stat().st_size,
        frames=expected_frames,fps=fps,duration_seconds=cursor,audio_samples=audio_bytes//4,
        audio_rate=rate,audio_video_delta_seconds=delta,full_audio_video_decoded=True,
        gameplay_video_packets_copied=True,packet_timestamps_normalized_to_native_fps=True,packet_timestamp_timebase='1/152024',packet_timestamp_ticks_per_frame=2537,branch_title_cards=len(items),chapters=chapters,
        embedded_chapters=False,external_chapters_file='LISEZ-MOI-ET-CHAPITRES.txt',
        selected_receipts_covered=145,separate_persistence_branches=sum(r['persistence_branch'] for r in items),
        all_npcs_complete=False,all_side_quests_complete=False,global_unused_strings_proven=False,
        main_campaign_sha256=main_report['movie_sha256'],sources=source_rows,
        description='Continuous campaign, then visibly labelled independent branches. One currency-assisted key-limit component explicitly identified. Not a global 100% certificate.')
    (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'analysis/md_proof_montage_report.json').write_text(json.dumps(report,indent=2)+'\n')
    text=['Golden Axe Warrior MD — campagne et annexes','',
        'Campagne continue depuis le demarrage jusqu au generique, puis branches annexes clairement indiquees.',
        'Les 145 objectifs retenus des points 3/4 ont des preuves MD. Les contextes de progression peuvent differer de la SMS.',
        'Le test99cles avec aide monetaire a un carton explicite. Les Continuer utilisent des SRAM reellement ecrites par le jeu.',
        'Les branches sont distinctes. Les trois textes SMS non declenches, deux entrees monétaires sans acces et la fidelite raster restent ouverts.',
        'Certains dialogues sont brefs : mettre la video en pause pour lire le texte integral.',
        'Aucun envoi sur YouTube. Audio/video entierement decodes, nombre d images et synchronisation verifies.','']
    for chapter in chapters:
        seconds=int(chapter['seconds']);h,rest=divmod(seconds,3600);m,s=divmod(rest,60)
        text.append(f"{h:02}:{m:02}:{s:02} {chapter['title']}")
    (folder/'LISEZ-MOI-ET-CHAPITRES.txt').write_text('\n'.join(text)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,movie=str(movie),duration_seconds=cursor,frames=expected_frames,sha256=report['movie_sha256'])),flush=True)


if __name__=='__main__':main()
