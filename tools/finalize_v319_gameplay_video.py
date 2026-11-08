"""Assemble intro + audited full campaign, validate streams and prepare YouTube text."""
import json,re,subprocess,sys,time
from pathlib import Path
import cv2
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT.parents[1]/'work/video-tools'))
import imageio_ffmpeg
from archive_lossless_evidence import sha
intro=ROOT/'validation/v319-video-intro-complete02';game=ROOT/'validation/v319-video-gameplay01'
ir=json.loads((intro/'report.json').read_bytes());gr=json.loads((game/'report.json').read_bytes())
assert ir['passed'] and ir['complete_intro'] and gr['passed'] and gr['final_campaign_ram_and_picture_exact'] and gr['frames']==403488
assert ir['fps']==gr['fps'] and ir['rom_sha256']==gr['rom_sha256']=='d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e'
assert not gr['boss_assistance'] and gr['approach_guard_writes']==190764 and gr['save_state_imports']==0
out=ROOT/'videos/v0319';assert not out.exists();out.mkdir(parents=True)
f=imageio_ffmpeg.get_ffmpeg_exe();movie=out/'golden-axe-warrior-md-v0319-gameplay-complet-ntsc.mp4'
for report in (ir,gr):assert sha(Path(report['movie']).read_bytes())==report['movie_sha256']
(out/'segments.txt').write_text(''.join("file '"+Path(r['movie']).as_posix().replace("'","'\\''")+"'\n" for r in (ir,gr)))
title='Golden Axe Warrior sur Mega Drive — Gameplay complet + intro | Portage natif V319'
command=[f,'-hide_banner','-nostdin','-f','concat','-safe','0','-i',str(out/'segments.txt'),'-map','0:v:0','-map','0:a:0','-c','copy','-movflags','+faststart','-metadata','title='+title,'-metadata','comment=Development V319 native Mega Drive port. Full intro plus complete audited New Game-to-credits campaign. Approach-only protection removed before boss combat; no progression or health imports.',str(movie)]
with (out/'assembly.log').open('w') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
cap=cv2.VideoCapture(str(movie));assert cap.isOpened();frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS);w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
assert frames==ir['frames']+gr['frames'] and abs(fps-gr['fps'])<0.00001 and (w,h)==(960,720),(frames,fps,w,h)
duration=frames/fps
receipt=json.loads((ROOT/'analysis/cold_palace_final_c0046_report.json').read_bytes());assert receipt['ending_complete'] and receipt['campaign_from_new_game_completed']
def stamp(seconds):
 seconds=int(seconds);hours,rem=divmod(seconds,3600);minutes,secs=divmod(rem,60)
 return f'{hours}:{minutes:02}:{secs:02}' if hours else f'{minutes}:{secs:02}'
chapters=[(0,'Introduction complète'),(ir['duration_seconds'],'Nouvelle partie — parcours complet'),(ir['duration_seconds']+receipt['first_final_combat']['frame']/fps,'Combat final — Death Adder'),(ir['duration_seconds']+receipt['credits_started_frame']/fps,'Épilogue et générique de fin')]
description='''Golden Axe Warrior, porté de la Master System vers la Mega Drive en code natif 68000 avec SGDK.

Cette vidéo montre la V319 publiée, une VERSION DE DÉVELOPPEMENT : introduction et animation du titre, puis nouvelle partie jusqu’à Death Adder et au générique complet. L’intro et le parcours sont deux captures assemblées ; le parcours lui-même est continu, sans coupe.

Le parcours de validation utilise une protection de test pendant certaines approches. Elle est retirée avant les combats de boss. Aucun import de sauvegarde, de progression, de vie ou d’inventaire n’est utilisé. Ce n’est donc pas une partie entièrement sans assistance.

Capture NTSC à la cadence d’origine (~59,92 images/s), 720p, son stéréo. Les travaux natifs les plus récents sur le timing vidéo ne sont pas encore activés dans cette ROM. Des écarts de fidélité et des validations restent ouverts ; cette vidéo ne présente pas une version finale.

Projet et ROM numérotée : https://github.com/spamkenny02/goldenaxe

Chapitres :
'''+''.join(stamp(t)+' '+label+'\n' for t,label in chapters)+'''
Golden Axe Warrior et ses éléments originaux appartiennent à leurs ayants droit respectifs. Projet de portage non officiel.
'''
(out/'youtube-title.txt').write_text(title+'\n',encoding='utf-8');(out/'youtube-description.txt').write_text(description,encoding='utf-8')
# Samples are taken from the final encoded deliverable, including its join,
# game,final fight and credits. No emulator framebuffer is substituted.
sample_times=[12,55,105,ir['duration_seconds']-1,ir['duration_seconds']+1,ir['duration_seconds']+150,ir['duration_seconds']+1800,ir['duration_seconds']+3600,chapters[2][0]+10,chapters[3][0]+30,duration-20,duration-2]
sheet=Image.new('RGB',(960,4*260));draw=ImageDraw.Draw(sheet);samples=[]
for i,t in enumerate(sample_times):
 cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);accepted,bgr=cap.read();assert accepted,(i,t)
 rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB);im=Image.fromarray(rgb);path=out/f'qa-{i:02}.jpg';im.save(path,quality=94)
 sheet.paste(im.resize((320,240)),((i%3)*320,(i//3)*260));draw.text(((i%3)*320+5,(i//3)*260+242),stamp(t),fill='white');samples.append(dict(seconds=t,path=path.name))
cap.release();sheet.save(out/'apercu-gameplay.jpg',quality=94)
# Parse every video packet without reencoding or decoding2hours of footage.
scan=subprocess.run([f,'-hide_banner','-nostdin','-i',str(movie),'-map','0:v:0','-c','copy','-f','null','-','-progress','pipe:1'],capture_output=True,text=True);(out/'video-packet-check.log').write_text(scan.stderr);(out/'video-packet-check.txt').write_text(scan.stdout);assert scan.returncode==0
counts=re.findall(r'^frame=(\d+)',scan.stdout,re.M);assert counts and int(counts[-1])==frames
audio_check=subprocess.run([f,'-hide_banner','-nostdin','-i',str(movie),'-vn','-af','astats=metadata=0:reset=0','-f','null','-'],capture_output=True,text=True);(out/'audio-check.log').write_text(audio_check.stderr);assert audio_check.returncode==0 and 'RMS level dB: -inf' not in audio_check.stderr
report=dict(passed=True,movie=str(movie),movie_sha256=sha(movie.read_bytes()),movie_bytes=movie.stat().st_size,rom_sha256=ir['rom_sha256'],frames=frames,fps=fps,duration_seconds=duration,width=w,height=h,stereo_audio=True,segments=[ir,gr],chapters=[dict(seconds=t,label=l) for t,l in chapters],encoded_frame_samples=samples,all_video_packets_read=True,full_audio_decoded=True,final_campaign_ram_and_picture_exact=True,channel='@KennYMcCormick-m2b',visibility='awaiting user choice',upload_status='not uploaded; local browser control disabled in Work settings',limits=['DevelopmentV319,not finalROM.','Approach-only protection disclosed; all boss combat without it.','Two segments:complete intro/title followed by complete uncut campaign.'])
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('segments','encoded_frame_samples')}),flush=True)
