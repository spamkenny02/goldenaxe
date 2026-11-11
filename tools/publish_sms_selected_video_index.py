"""Index only actually finished branch movies, with explicit coverage limits."""
import json
from pathlib import Path
from run_core import ROOT


def stamp(seconds):
    seconds=int(seconds);h,rest=divmod(seconds,3600);m,s=divmod(rest,60)
    return f'{h:02}:{m:02}:{s:02}'


def main():
    ledger=json.loads((ROOT/'analysis/sms_selected_proof_video_collection.json').read_bytes())
    closure=json.loads((ROOT/'analysis/sms_points_3_4_closure.json').read_bytes())
    folder=ROOT/'videos/sms/annexes-2026-11-11'
    lines=['# Annexes vidéo SMS','',
        'Chaque extrait est une branche distincte, rejouée depuis le démarrage. Les extraits ne forment pas une partie continue. Les deux tests monétaires assistés sont signalés.','',
        '| Annexe | Durée | Aide monétaire |','| --- | --- | --- |']
    for p in sorted(folder.glob('*/report.json')):
        r=json.loads(p.read_bytes())
        if not r.get('passed'):continue
        source=r.get('source_capture_report',{})
        lines.append(f"| [{p.parent.name}]({p.parent.name}/LISEZ-MOI.txt) | {stamp(r['duration_seconds'])} | {'Oui, achats réels avec argent infini déclaré' if source.get('currency_assisted_component_test') else 'Non'} |")
    lines+=['','RAM et pixels finaux comparés à une relecture indépendante ; audio et vidéo décodés intégralement. Les MP4 restent locaux.','',
        'Les extraits « continuer » sont des redémarrages avec la SRAM réellement écrite par le jeu, distincts de la campagne continue. Aucun état synthétique ni savestate n’est utilisé.','',
        f"Le plan des points 3/4 retient 145 preuves. La campagne principale et les {len(ledger['completed_clips'])} extraits actuellement terminés en couvrent **{ledger['covered_selected_receipts']}/145**. Les clips seulement prévus ne sont pas comptés.",'',
        'Cette couverture des preuves sélectionnées ne certifie pas tous les PNJ et toutes les variantes du jeu. Le point 5 reste ouvert.','',
        '[Relevé des vidéos effectivement terminées](../../../analysis/sms_selected_proof_video_collection.json).']
    (folder/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    for clip in ledger['completed_clips']:
        p=ROOT/clip['report'];report=json.loads(p.read_bytes());source=report['source_capture_report'];chapters=[]
        for trace in clip['covered_receipts']:
            frame=closure['selected_receipts'][trace]['frame']
            assert source['first_emulated_video_frame']<=frame<=source['emulated_frames_from_boot']
            chapters.append(dict(trace=trace,frame=frame,seconds=(frame-source['first_emulated_video_frame'])/source['fps'],
                meaning='End of selected verified interaction; rewind for its beginning'))
        chapters.sort(key=lambda r:r['frame'])
        (p.parent/'CHAPITRES.json').write_text(json.dumps(chapters,indent=2)+'\n')
        text=['# Repères de cette branche','',
            'Les repères marquent la fin de chaque interaction vérifiée. Revenir quelques secondes en arrière pour son début.','',
            '| Temps vidéo | Preuve |','| --- | --- |']
        text += [f"| {stamp(c['seconds'])} | {c['trace']} |" for c in chapters]
        (p.parent/'CHAPITRES.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    persistence_path=ROOT/'analysis/sms_persistence_video_collection.json'
    persistence=json.loads(persistence_path.read_bytes()) if persistence_path.exists() else None
    rows=['#EXTM3U','#EXTINF:-1,Campagne continue jusqu au generique',
        Path(ledger['main_movie']).relative_to(ROOT/'videos/sms').as_posix()]
    for clip in ledger['completed_clips']:
        rows += [f"#EXTINF:{round(clip['duration_seconds'])},Branche {clip['number']:03d} - {clip['trace']}",
            Path(clip['movie']).relative_to(ROOT/'videos/sms').as_posix()]
    if persistence:
        for clip in persistence['completed_branches']:
            rows += [f"#EXTINF:{round(clip['duration_seconds'])},Redemarrage Continuer - {clip['source_report']}",
                Path(clip['movie']).relative_to(ROOT/'videos/sms').as_posix()]
    (ROOT/'videos/sms/PARCOURS-ET-ANNEXES.m3u8').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    print(json.dumps(dict(completed_clips=len(ledger['completed_clips']),covered_receipts=ledger['covered_selected_receipts'],
        all_selected_receipts_video_covered=ledger['all_selected_receipts_video_covered'])))


if __name__=='__main__':main()
