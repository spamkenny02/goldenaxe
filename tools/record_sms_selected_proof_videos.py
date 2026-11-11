"""Record the planned branch clips; only completed decoded artifacts count."""
import argparse,concurrent.futures,hashlib,json,subprocess,sys,time
from pathlib import Path
from run_core import ROOT


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=1);args=parser.parse_args()
    assert 1<=args.workers<=4
    plan=json.loads((ROOT/'analysis/sms_selected_proof_video_plan.json').read_bytes())
    folder=ROOT/'videos/sms/annexes-2026-11-11';started=time.monotonic();completed=[]
    capture_parent=ROOT/'validation/sms-selected-videos-2026-11-11';capture_parent.mkdir(exist_ok=True)
    collection=ROOT/'analysis/sms_selected_proof_video_collection.json'
    closure=json.loads((ROOT/'analysis/sms_points_3_4_closure.json').read_bytes())
    def save():
        covered=set(plan['covered_by_main'])
        for r in completed:covered.update(r['covered_receipts'])
        collection.write_text(json.dumps(dict(source_sha256=plan['source_sha256'],
            main_movie=plan['main_movie'],main_covers=plan['covered_by_main'],completed_clips=completed,
            covered_selected_receipts=len(covered),required_selected_receipts=plan['selected_receipts'],
            all_selected_receipts_video_covered=len(covered)==plan['selected_receipts'],
            all_npcs_complete=False,all_side_quests_complete=False,
            scope='Selected point 3/4 replay receipts, not a global 100% NPC certificate.',
            wall_seconds=round(time.monotonic()-started,1)),indent=2)+'\n')
    existing=[(p,json.loads(p.read_bytes())) for p in folder.glob('*/report.json')]
    def record_one(i,clip):
        artifact=None
        for p,r in existing:
            source=r.get('source_capture_report',{})
            if (r.get('passed') and source.get('route')==clip['trace'] and
                source.get('emulated_frames_from_boot')==clip['end_frame'] and
                source.get('first_emulated_video_frame',10**9)<=clip['common_boot_prefix_frames']+1):
                artifact=(p,r);break
        if artifact is None:
            name=f'preuve-{i:03d}-'+clip['trace'].split('/')[-1].removeprefix('sms-npc-')
            source=f'sms-selected-videos-2026-11-11/clip-{i:03d}'
            out=ROOT/'validation'/source
            print('RECORD',i,len(plan['clips']),clip['trace'],flush=True)
            if not (out/'report.json').exists():
                with (capture_parent/f'clip-{i:03d}.log').open('w',encoding='utf-8') as log:
                    subprocess.run([sys.executable,str(ROOT/'tools/record_sms_gameplay.py'),
                        '--trace',clip['trace'],'--from-frame',str(clip['from_frame']),'--out',source,
                        *(['--economic-component'] if clip['currency_assisted_component_test'] else [])],
                        cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
            description=('Branche SMS distincte : '+clip['trace']+'. '+
                ('Test monetaire assiste : achats reels, argent infini declare, aucun objet ni etat de quete injecte.'
                 if clip['currency_assisted_component_test'] else 'Commandes reelles et aide approche declaree, retiree avant les boss.'))
            with (capture_parent/f'archive-{i:03d}.log').open('w',encoding='utf-8') as log:
                subprocess.run([sys.executable,str(ROOT/'tools/archive_sms_video_annex.py'),
                    '--source',source,'--name',name,'--description',description],cwd=ROOT,
                    stdout=log,stderr=subprocess.STDOUT,check=True)
            p=folder/name/'report.json';artifact=(p,json.loads(p.read_bytes()))
        p,r=artifact;source=r['source_capture_report'];movie=Path(r['movie'])
        assert r['passed'] and r['full_audio_video_decoded'] and source['final_ram_and_pixels_exact']
        assert source.get('currency_assisted_component_test',False)==clip['currency_assisted_component_test']
        assert source['rom_sha256']==plan['source_sha256'] and movie.is_file()
        with movie.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==r['movie_sha256']
        result=dict(number=i,trace=clip['trace'],report=p.relative_to(ROOT).as_posix(),
            movie=str(movie),movie_sha256=r['movie_sha256'],duration_seconds=r['duration_seconds'],
            currency_assisted_component_test=clip['currency_assisted_component_test'],
            covered_receipts=clip['covered_receipts'])
        chapters=[]
        for trace in clip['covered_receipts']:
            frame=closure['selected_receipts'][trace]['frame']
            assert source['first_emulated_video_frame']<=frame<=source['emulated_frames_from_boot']
            seconds=(frame-source['first_emulated_video_frame'])/source['fps']
            chapters.append(dict(trace=trace,frame=frame,seconds=seconds,
                meaning='End of the selected verified interaction, not necessarily its first dialogue image'))
        chapters.sort(key=lambda r:r['frame'])
        (p.parent/'CHAPITRES.json').write_text(json.dumps(chapters,indent=2)+'\n')
        chapter_lines=['# Repères de cette branche','',
            'Ces repères marquent la fin de chaque interaction vérifiée. Revenir quelques secondes en arrière pour son début.','',
            '| Temps vidéo | Preuve |','| --- | --- |']
        for chapter in chapters:
            seconds=int(chapter['seconds']);m,s=divmod(seconds,60)
            chapter_lines.append(f"| {m:02}:{s:02} | {chapter['trace']} |")
        (p.parent/'CHAPITRES.md').write_text('\n'.join(chapter_lines)+'\n',encoding='utf-8')
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        pending=[executor.submit(record_one,i,clip) for i,clip in enumerate(plan['clips'],1)]
        for future in concurrent.futures.as_completed(pending):
            result=future.result();completed.append(result);completed.sort(key=lambda r:r['number'])
            save();print('VERIFIED VIDEO',result['number'],len(plan['clips']),len(result['covered_receipts']),flush=True)
    save()
    playlist=ROOT/'videos/sms/PARCOURS-ET-ANNEXES.m3u8'
    rows=['#EXTM3U','#EXTINF:-1,Campagne continue jusqu au generique',
        Path(plan['main_movie']).relative_to(playlist.parent).as_posix()]
    for r in completed:
        rows.extend([f"#EXTINF:{round(r['duration_seconds'])},Branche {r['number']:03d} - {r['trace']}",
            Path(r['movie']).relative_to(playlist.parent).as_posix()])
    playlist.write_text('\n'.join(rows)+'\n',encoding='utf-8')
    print('SELECTED VIDEO COLLECTION COMPLETE',len(completed),flush=True)


if __name__=='__main__':main()
