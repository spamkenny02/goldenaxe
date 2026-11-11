"""Film the verified genuine-save Continue branches separately from campaigns."""
import json,subprocess,sys
from run_core import ROOT


def main():
    paths=set()
    for row in json.loads((ROOT/'analysis/sms_save_locations_campaign.json').read_bytes())['completed_locations']:
        paths.add(row['continue_report'])
    for row in json.loads((ROOT/'analysis/sms_actual_save_slots_report.json').read_bytes())['slots']:
        paths.add(row['report'])
    paths.add(json.loads((ROOT/'analysis/sms_save_overwrite_report.json').read_bytes())['continue_report'])
    completed=[]
    for path in sorted(paths):
        source=(ROOT/path).parent;trial=source.name
        assert source.is_relative_to(ROOT/'validation/sms-save-continue')
        original=json.loads((source/'report.json').read_bytes());assert original['passed']
        name='continuer-'+trial;out='sms-video-continue-'+trial+'-2026-11-11'
        base_out=out;attempt=1
        while (ROOT/'validation'/out).exists() and not (ROOT/'validation'/out/'report.json').exists():
            attempt+=1;out=base_out+f'-attempt{attempt:02d}'
        archived=ROOT/'videos/sms/annexes-2026-11-11'/name/'report.json'
        if not archived.exists():
            if not (ROOT/'validation'/out/'report.json').exists():
                with (ROOT/'validation'/(out+'.log')).open('w',encoding='utf-8') as log:
                    subprocess.run([sys.executable,str(ROOT/'tools/record_sms_gameplay.py'),
                        '--persistence-source',source.relative_to(ROOT/'validation').as_posix(),'--out',out],
                        cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
            with (ROOT/'validation'/('archive-'+out+'.log')).open('w',encoding='utf-8') as log:
                subprocess.run([sys.executable,str(ROOT/'tools/archive_sms_video_annex.py'),
                    '--source',out,'--name',name,'--description',
                    f'Redemarrage SMS et Continuer : {trial}. SRAM reelle de {original["source_recording"]}, slot {original["slot"]}. Aucun edit de RAM, etat synthetique ni savestate.'],
                    cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        artifact=json.loads(archived.read_bytes());capture=artifact['source_capture_report']
        assert artifact['passed'] and artifact['full_audio_video_decoded'] and capture['final_ram_and_pixels_exact']
        assert capture['separate_persistence_branch'] and capture['game_written_sram_sha256']==original['source_sram_sha256']
        completed.append(dict(source_report=path,video_report=archived.relative_to(ROOT).as_posix(),
            movie=artifact['movie'],movie_sha256=artifact['movie_sha256'],slot=original['slot'],
            resume_room=original['final_room'],duration_seconds=artifact['duration_seconds']))
        (ROOT/'analysis/sms_persistence_video_collection.json').write_text(json.dumps(dict(
            expected_branches=len(paths),completed_branches=completed,complete=len(completed)==len(paths),
            actual_game_written_sram_only=True,synthetic_fixtures=False,emulator_savestate_imports=0,
            continuous_campaign=False),indent=2)+'\n')
        print('PERSISTENCE VIDEO VERIFIED',len(completed),len(paths),trial,flush=True)


if __name__=='__main__':main()
